"""FAISS Cosine Similarity Index, Metadata Filtering & Precision@K / Recall@K Evaluator."""

from __future__ import annotations

import os
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import joblib
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split

# Import torch (via feature_extractor) before faiss to avoid macOS OpenMP libomp collision
from src.catalog import BASE_DIR, build_or_load_catalog
from src.feature_extractor import ResNetVisualFeatureExtractor
import faiss
faiss.omp_set_num_threads(1)

FAISS_INDEX_PATH = BASE_DIR / "models" / "visual_index.faiss"
BUNDLE_PATH = BASE_DIR / "models" / "visual_bundle.joblib"
METRICS_JSON_PATH = BASE_DIR / "reports" / "evaluation_metrics.json"


class VisualSearchEngine:
    """Amazon-style visual product similarity engine backed by PyTorch ResNet50 + FAISS IndexFlatIP."""

    def __init__(
        self,
        catalog: pd.DataFrame,
        extractor: ResNetVisualFeatureExtractor,
        embeddings: np.ndarray,
        index: faiss.IndexFlatIP,
        metrics: Dict[str, Any],
    ) -> None:
        self.catalog = catalog.reset_index(drop=True)
        self.extractor = extractor
        self.embeddings = embeddings.astype(np.float32)
        self.index = index
        self.metrics = metrics

    @classmethod
    def build_and_save(
        cls,
        index_path: Path = FAISS_INDEX_PATH,
        bundle_path: Path = BUNDLE_PATH,
        metrics_path: Path = METRICS_JSON_PATH,
    ) -> "VisualSearchEngine":
        catalog = build_or_load_catalog()
        img_paths = [BASE_DIR / rel for rel in catalog["image_rel_path"].tolist()]
        labels = catalog["category"].to_numpy()

        extractor = ResNetVisualFeatureExtractor(random_state=42)
        raw_feats = extractor.extract_raw_batch(img_paths)

        # Stratified 80/20 train/test split so quantitative Precision@K is measured strictly out-of-sample
        idx_all = np.arange(len(catalog))
        train_idx, test_idx = train_test_split(idx_all, test_size=0.20, random_state=42, stratify=labels)
        extractor.fit_projection(raw_feats[train_idx], labels[train_idx])

        embeddings = np.ascontiguousarray(extractor.project(raw_feats), dtype=np.float32)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)  # Cosine similarity on L2-normalized vectors
        index.add(embeddings)

        metrics = cls._evaluate_retrieval(index, embeddings, catalog, test_idx)

        index_path.parent.mkdir(parents=True, exist_ok=True)
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(index_path))
        joblib.dump(
            {
                "catalog": catalog,
                "scaler": extractor.scaler,
                "svd": extractor.svd,
                "projector": extractor.projector,
                "embeddings": embeddings,
                "metrics": metrics,
            },
            bundle_path,
        )
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        return cls(catalog=catalog, extractor=extractor, embeddings=embeddings, index=index, metrics=metrics)

    @classmethod
    def load_or_build(cls) -> "VisualSearchEngine":
        if not FAISS_INDEX_PATH.exists() or not BUNDLE_PATH.exists():
            return cls.build_and_save()
        saved = joblib.load(BUNDLE_PATH)
        index = faiss.read_index(str(FAISS_INDEX_PATH))
        extractor = ResNetVisualFeatureExtractor(random_state=42)
        extractor.scaler = saved["scaler"]
        extractor.svd = saved.get("svd")
        extractor.projector = saved["projector"]
        return cls(
            catalog=saved["catalog"],
            extractor=extractor,
            embeddings=saved["embeddings"],
            index=index,
            metrics=saved["metrics"],
        )

    @staticmethod
    def _evaluate_retrieval(
        index: faiss.IndexFlatIP,
        embeddings: np.ndarray,
        catalog: pd.DataFrame,
        test_indices: np.ndarray,
    ) -> Dict[str, Any]:
        cats = catalog["category"].to_numpy()
        cat_totals = pd.Series(cats).value_counts().to_dict()

        p_at_1, p_at_5, p_at_10, r_at_10, latencies_ms = [], [], [], [], []
        per_cat_p5: Dict[str, list[float]] = {}

        for q_idx in test_indices:
            q_vec = embeddings[q_idx:q_idx + 1]
            t0 = time.perf_counter()
            scores, neighbors = index.search(q_vec, 11)
            latencies_ms.append((time.perf_counter() - t0) * 1000.0)

            # Exclude exact self-match
            cand = [int(i) for i in neighbors[0] if int(i) != int(q_idx)][:10]
            true_cat = cats[q_idx]
            matches = [1 if cats[c] == true_cat else 0 for c in cand]

            p1 = float(matches[0])
            p5 = float(np.mean(matches[:5]))
            p10 = float(np.mean(matches[:10]))
            denom = max(1, cat_totals[true_cat] - 1)
            r10 = float(np.sum(matches[:10]) / denom)

            p_at_1.append(p1)
            p_at_5.append(p5)
            p_at_10.append(p10)
            r_at_10.append(r10)
            per_cat_p5.setdefault(str(true_cat), []).append(p5)

        return {
            "total_catalog_images": int(len(catalog)),
            "embedding_dimension": int(embeddings.shape[1]),
            "num_categories": int(len(cat_totals)),
            "holdout_queries": int(len(test_indices)),
            "precision_at_1": round(float(np.mean(p_at_1)), 4),
            "precision_at_5": round(float(np.mean(p_at_5)), 4),
            "precision_at_10": round(float(np.mean(p_at_10)), 4),
            "recall_at_10": round(float(np.mean(r_at_10)), 4),
            "avg_faiss_latency_ms": round(float(np.mean(latencies_ms)), 4),
            "category_precision_at_5": {k: round(float(np.mean(v)), 4) for k, v in sorted(per_cat_p5.items())},
        }

    def search(
        self,
        query: Union[int, str, Path, Image.Image],
        top_k: int = 8,
        categories: Optional[list[str]] = None,
        price_range: Optional[Tuple[float, float]] = None,
        in_stock_only: bool = False,
        min_rating: float = 0.0,
    ) -> Tuple[pd.DataFrame, float]:
        """Executes ANN cosine similarity search in FAISS and applies optional e-commerce metadata filters."""
        exclude_idx: Optional[int] = None
        if isinstance(query, int):
            exclude_idx = query
            q_vec = self.embeddings[query:query + 1]
        elif isinstance(query, str) and query in set(self.catalog["product_id"]):
            exclude_idx = int(self.catalog.index[self.catalog["product_id"] == query][0])
            q_vec = self.embeddings[exclude_idx:exclude_idx + 1]
        else:
            q_vec = np.ascontiguousarray(self.extractor.encode_images([query]), dtype=np.float32)

        t0 = time.perf_counter()
        scores, indices = self.index.search(q_vec, len(self.catalog))
        latency_ms = round((time.perf_counter() - t0) * 1000.0, 3)

        cand_idx = []
        cand_scores = []
        for s, idx in zip(scores[0], indices[0]):
            i = int(idx)
            if i < 0 or i == exclude_idx:
                continue
            cand_idx.append(i)
            cand_scores.append(float(s))

        res = self.catalog.iloc[cand_idx].copy()
        res["cosine_similarity"] = np.round(cand_scores, 4)

        if categories:
            res = res[res["category"].isin(categories)]
        if price_range is not None:
            res = res[(res["price_inr"] >= price_range[0]) & (res["price_inr"] <= price_range[1])]
        if in_stock_only:
            res = res[res["in_stock"] == True]  # noqa: E712
        if min_rating > 0.0:
            res = res[res["rating"] >= min_rating]

        return res.head(top_k).reset_index(drop=True), latency_ms

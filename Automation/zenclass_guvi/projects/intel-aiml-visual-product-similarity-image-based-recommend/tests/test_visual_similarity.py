"""Automated tests for Visual Product Similarity & FAISS Recommendation System."""

from PIL import Image

from src.catalog import BASE_DIR
from src.vector_engine import VisualSearchEngine


def test_faiss_index_and_holdout_precision_metrics() -> None:
    engine = VisualSearchEngine.load_or_build()
    assert engine.metrics["total_catalog_images"] == 500
    assert engine.metrics["precision_at_5"] >= 0.75
    assert engine.metrics["avg_faiss_latency_ms"] < 50.0


def test_similarity_search_and_metadata_filters() -> None:
    engine = VisualSearchEngine.load_or_build()
    recs, latency_ms = engine.search(
        query="PRD-0001",
        top_k=6,
        categories=["backpack"],
        price_range=(500.0, 5000.0),
        in_stock_only=True,
    )
    assert len(recs) == 6
    assert "PRD-0001" not in set(recs["product_id"])
    assert (recs["category"] == "backpack").all()
    assert recs["in_stock"].all()
    assert latency_ms < 100.0


def test_custom_uploaded_pil_image_query() -> None:
    engine = VisualSearchEngine.load_or_build()
    sample_img = Image.open(BASE_DIR / engine.catalog.iloc[0]["image_rel_path"])
    recs, _ = engine.search(query=sample_img, top_k=5)
    assert len(recs) == 5
    assert recs.iloc[0]["cosine_similarity"] > 0.5

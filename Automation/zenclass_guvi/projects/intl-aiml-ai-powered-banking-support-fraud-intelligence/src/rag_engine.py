"""FAISS Vector RAG Engine Grounded in Official Banking Policies & Past Resolved Cases."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import faiss
import numpy as np
import pandas as pd
import requests
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import Normalizer

from src.database import BASE_DIR, DATA_DIR, BankingDatabase
from src.nlp_fraud_models import (
    URGENT_FRAUD_TERMS,
    extract_banking_entities,
    load_or_train_models,
)


class BankingRAGEngine:
    """Retrieves banking policy clauses & past ticket precedents via FAISS and synthesizes grounded guidance."""

    def __init__(self, data_dir: Optional[Path] = None, db: Optional[BankingDatabase] = None) -> None:
        self.data_dir = Path(data_dir) if data_dir else DATA_DIR
        self.db = db or BankingDatabase(data_dir=self.data_dir)
        self.models = load_or_train_models()
        self.documents: List[Dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")
        self.svd: Optional[TruncatedSVD] = None
        self.normalizer = Normalizer(copy=False)
        self.index: Optional[faiss.IndexFlatIP] = None
        self._build_knowledge_index()

    def _build_knowledge_index(self) -> None:
        docs: List[Dict[str, Any]] = []

        # 1. Chunk official retail banking policy documents
        for policy_file in sorted(self.data_dir.glob("*_policy.txt")):
            raw_txt = policy_file.read_text(encoding="utf-8")
            paragraphs = [p.strip() for p in raw_txt.split("\n\n") if len(p.strip()) >= 40]
            for idx, para in enumerate(paragraphs):
                docs.append({
                    "doc_id": f"{policy_file.stem}#sec{idx+1}",
                    "source": policy_file.name,
                    "doc_type": "Policy Document",
                    "category_hint": policy_file.stem.split("_")[0].capitalize(),
                    "content": para,
                })

        # 2. Index QA pairs
        qa_path = self.data_dir / "04_qa_pairs.json"
        if qa_path.exists():
            qa_raw = json.loads(qa_path.read_text(encoding="utf-8"))
            items = qa_raw if isinstance(qa_raw, list) else qa_raw.get("qa_pairs", [])
            for idx, item in enumerate(items):
                q = item.get("question") or item.get("query") or ""
                a = item.get("answer") or item.get("response") or ""
                cat = item.get("category") or "Banking FAQ"
                if q and a:
                    docs.append({
                        "doc_id": f"qa_pair_{idx+1:03d}",
                        "source": "04_qa_pairs.json",
                        "doc_type": "Verified Banking Q&A",
                        "category_hint": str(cat),
                        "content": f"Question: {q}\nOfficial Guidance: {a}",
                    })

        # 3. Index representative resolved support tickets
        tickets = pd.read_csv(self.data_dir / "01_support_tickets.csv")
        for _, row in tickets.drop_duplicates(subset=["category", "resolution_text"]).head(60).iterrows():
            docs.append({
                "doc_id": str(row["ticket_id"]),
                "source": "01_support_tickets.csv",
                "doc_type": "Resolved Precedent",
                "category_hint": str(row["category"]),
                "content": f"Customer Issue ({row['category']}): {row['query_text']}\nStandard Resolution: {row['resolution_text']}",
            })

        self.documents = docs
        corpus = [f"{d['category_hint']} {d['content']}" for d in docs]
        tfidf_mat = self.vectorizer.fit_transform(corpus)
        n_comp = min(96, tfidf_mat.shape[0] - 1, tfidf_mat.shape[1] - 1)
        self.svd = TruncatedSVD(n_components=n_comp, random_state=42)
        dense = self.normalizer.fit_transform(self.svd.fit_transform(tfidf_mat)).astype(np.float32)
        dense = np.ascontiguousarray(dense, dtype=np.float32)

        self.index = faiss.IndexFlatIP(dense.shape[1])
        self.index.add(dense)

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
        assert self.svd is not None and self.index is not None
        q_tfidf = self.vectorizer.transform([query])
        q_vec = self.normalizer.transform(self.svd.transform(q_tfidf)).astype(np.float32)
        q_vec = np.ascontiguousarray(q_vec, dtype=np.float32)
        scores, indices = self.index.search(q_vec, min(top_k, len(self.documents)))

        results = []
        for sc, idx in zip(scores[0], indices[0]):
            if int(idx) < 0:
                continue
            doc = dict(self.documents[int(idx)])
            doc["relevance_score"] = round(float(sc), 4)
            results.append(doc)
        return results

    def answer_customer_query(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        cleaned = (query or "").strip()
        if not cleaned:
            raise ValueError("Please provide a non-empty banking support query.")

        entities = extract_banking_entities(cleaned)
        intent_model = self.models["intent_model"]
        probs = intent_model.predict_proba([cleaned])[0]
        pred_idx = int(np.argmax(probs))
        predicted_intent = str(intent_model.classes_[pred_idx])
        intent_confidence = round(float(probs[pred_idx]), 4)

        sentiment = str(self.models["sentiment_model"].predict([cleaned])[0])
        risk_level = str(self.models["risk_model"].predict([cleaned])[0])

        lower_q = cleaned.lower()
        if any(term in lower_q for term in URGENT_FRAUD_TERMS):
            if "fraud" in " ".join(intent_model.classes_).lower():
                for cls_name in intent_model.classes_:
                    if "fraud" in cls_name.lower() or "unauthor" in cls_name.lower():
                        predicted_intent = str(cls_name)
                        break
            risk_level = "High"
            sentiment = "Urgent"
        elif entities["amount_inr"] and entities["amount_inr"] >= 25000 and risk_level == "Low":
            risk_level = "Medium"

        retrieved = self.retrieve(f"{predicted_intent}: {cleaned}", top_k=top_k)
        suggested_action = self._determine_next_action(predicted_intent, risk_level, entities)
        response_text = self._synthesize_grounded_reply(cleaned, predicted_intent, risk_level, entities, retrieved, suggested_action)

        top_src = retrieved[0]["doc_id"] if retrieved else "none"
        self.db.log_interaction(
            query_text=cleaned,
            predicted_intent=predicted_intent,
            sentiment=sentiment,
            risk_level=risk_level,
            suggested_action=suggested_action,
            top_policy_source=top_src,
        )

        return {
            "query": cleaned,
            "predicted_intent": predicted_intent,
            "intent_confidence": intent_confidence,
            "sentiment": sentiment,
            "risk_level": risk_level,
            "entities": entities,
            "suggested_action": suggested_action,
            "response": response_text,
            "retrieved_context": retrieved,
        }

    @staticmethod
    def _determine_next_action(intent: str, risk_level: str, entities: Dict[str, Any]) -> str:
        low_i = intent.lower()
        amt_txt = f" (₹{entities['amount_inr']:,.0f})" if entities.get("amount_inr") else ""
        if "fraud" in low_i or "unauthor" in low_i or risk_level == "High":
            return f"Block card/net-banking channel immediately{amt_txt}, raise Fraud Dispute Ticket, and escalate to Tier-2 Fraud Investigation."
        if "kyc" in low_i:
            return "Request PAN + Aadhaar/OVD upload via secure portal and trigger Video-KYC verification workflow."
        if "loan" in low_i:
            return "Verify CIBIL/income documents in LOS and share current sanction/disbursement SLA status."
        if "refund" in low_i or "dispute" in low_i:
            return f"Log chargeback/merchant dispute{amt_txt} and track T+5 / 7–10 business day provisional credit SLA."
        return "Verify registered mobile OTP, check core-banking account status, and assist customer with self-service workflow."

    def _synthesize_grounded_reply(
        self,
        query: str,
        intent: str,
        risk_level: str,
        entities: Dict[str, Any],
        retrieved: List[Dict[str, Any]],
        suggested_action: str,
    ) -> str:
        # Optional live FreeLLMAPI endpoint if explicitly enabled
        if os.getenv("USE_FREELLM_ENDPOINT", "0") == "1":
            try:
                ctx_str = "\n\n".join(f"[{c['doc_id']}] {c['content']}" for c in retrieved[:3])
                resp = requests.post(
                    "http://127.0.0.1:31415/v1/chat/completions",
                    json={
                        "model": "fast",
                        "messages": [
                            {"role": "system", "content": "You are a compliant retail banking AI assistant. Ground your reply strictly in the provided policy context."},
                            {"role": "user", "content": f"Customer Query: {query}\nIntent: {intent} | Risk: {risk_level}\nContext:\n{ctx_str}"},
                        ],
                        "max_tokens": 220,
                    },
                    timeout=5,
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"].strip()
            except Exception:
                pass

        amt_clause = f" involving **₹{entities['amount_inr']:,.2f}**" if entities.get("amount_inr") else ""
        txn_clause = f" (Ref `{entities['transaction_id']}`)" if entities.get("transaction_id") else ""
        policy_snippets = []
        for chunk in retrieved[:2]:
            clean_body = chunk["content"].replace("\n", " ").strip()
            policy_snippets.append(f"- **[{chunk['doc_id']}]**: {clean_body[:260]}...")

        joined_policies = "\n".join(policy_snippets) if policy_snippets else "- Standard Retail Banking SOP applied."
        return (
            f"We have classified your request under **{intent}**{amt_clause}{txn_clause} with **{risk_level} Risk** priority.\n\n"
            f"**Immediate Guidance & Policy Summary:**\n{joined_policies}\n\n"
            f"**Next Action Initiated:** {suggested_action}"
        )

    def evaluate_rag_relevance(self) -> Dict[str, Any]:
        qa_path = self.data_dir / "04_qa_pairs.json"
        if not qa_path.exists():
            return {"evaluated_queries": 0, "avg_top1_score": 0.0, "hit_rate_at_3": 0.0}
        qa_raw = json.loads(qa_path.read_text(encoding="utf-8"))
        items = qa_raw if isinstance(qa_raw, list) else qa_raw.get("qa_pairs", [])
        top1_scores = []
        hits = 0
        for item in items:
            q = item.get("question") or item.get("query") or ""
            if not q:
                continue
            res = self.retrieve(q, top_k=3)
            if res:
                top1_scores.append(res[0]["relevance_score"])
                if any(r["relevance_score"] >= 0.35 for r in res):
                    hits += 1
        n = max(1, len(top1_scores))
        return {
            "evaluated_queries": len(top1_scores),
            "avg_top1_cosine_relevance": round(float(np.mean(top1_scores)) if top1_scores else 0.0, 4),
            "hit_rate_at_3": round(float(hits / n), 4),
        }

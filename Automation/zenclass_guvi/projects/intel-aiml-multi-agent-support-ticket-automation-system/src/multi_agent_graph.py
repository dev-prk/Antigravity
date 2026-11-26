"""Stateful 6-Agent Support Ticket Orchestration Graph (Intake -> Classify -> RAG -> Respond -> Escalate -> Learn)."""

from __future__ import annotations

import os
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import re
import time
import uuid
from typing import Any, Dict, List, Optional
import faiss
faiss.omp_set_num_threads(1)

import numpy as np

from src.classifiers_and_rag import load_or_train_bundle
from src.memory_db import SupportMemoryDB

ORDER_REGEX = re.compile(r"#?(ORD[-_]?\d{4,10})", re.IGNORECASE)
AMOUNT_REGEX = re.compile(r"(?:₹|\$|INR|USD|Rs\.?\s*)\s*([\d,]+(?:\.\d{1,2})?)", re.IGNORECASE)
KNOWN_PRODUCTS = [
    "laptop", "headphones", "smartwatch", "smartphone", "lipstick", "sneakers",
    "backpack", "blender", "keyboard", "monitor", "earbuds", "charger", "camera", "chair",
]
ANGRY_ESCALATION_CUES = [
    "lawyer", "legal", "consumer court", "scam", "fraud", "unacceptable",
    "furious", "worst", "third time", "damaged", "never arrived", "police", "sue",
]


class MultiAgentSupportOrchestrator:
    """Executes the 6-agent customer support workflow with full observability and continuous learning."""

    def __init__(self, db: Optional[SupportMemoryDB] = None, bundle: Optional[Dict[str, Any]] = None) -> None:
        self.db = db or SupportMemoryDB()
        self.bundle = bundle or load_or_train_bundle()
        self.kb_entries: List[Dict[str, Any]] = list(self.bundle["kb_entries"])
        self.kb_embeddings: np.ndarray = np.ascontiguousarray(self.bundle["kb_embeddings"], dtype=np.float32)
        self.index = faiss.IndexFlatIP(self.kb_embeddings.shape[1])
        self.index.add(self.kb_embeddings)
        self._sync_learned_feedback()

    def _encode_texts(self, texts: List[str]) -> np.ndarray:
        tfidf = self.bundle["rag_vectorizer"].transform(texts)
        svd = self.bundle["rag_svd"].transform(tfidf)
        normed = self.bundle["rag_normalizer"].transform(svd)
        return np.ascontiguousarray(normed, dtype=np.float32)

    def _sync_learned_feedback(self) -> None:
        learned = self.db.get_learned_feedback()
        existing_ids = {e["kb_id"] for e in self.kb_entries}
        new_entries = []
        for row in learned:
            kid = f"LEARNED-{row['feedback_id']}"
            if kid not in existing_ids:
                new_entries.append({
                    "kb_id": kid,
                    "source_type": "Learned Feedback",
                    "category": row["category"],
                    "question": row["ticket_text"],
                    "answer": row["approved_resolution"],
                })
        if new_entries:
            vecs = self._encode_texts([f"{e['category']}: {e['question']} -> {e['answer']}" for e in new_entries])
            self.kb_entries.extend(new_entries)
            self.index.add(vecs)

    # ------------------------------------------------------------------
    # 1. Intake Agent
    # ------------------------------------------------------------------
    @staticmethod
    def _intake_agent(raw_text: str) -> Dict[str, Any]:
        cleaned = re.sub(r"\s+", " ", (raw_text or "").strip())
        if not cleaned:
            raise ValueError("Ticket text cannot be empty.")

        ord_m = ORDER_REGEX.search(cleaned)
        amt_m = AMOUNT_REGEX.search(cleaned)
        lower = cleaned.lower()
        detected_product = next((p for p in KNOWN_PRODUCTS if p in lower), "order item")
        angry_hits = [w for w in ANGRY_ESCALATION_CUES if w in lower]

        return {
            "cleaned_text": cleaned,
            "order_id": ord_m.group(1).upper() if ord_m else None,
            "product_name": detected_product,
            "amount_mentioned": amt_m.group(0) if amt_m else None,
            "angry_cues_detected": angry_hits,
            "word_count": len(cleaned.split()),
        }

    # ------------------------------------------------------------------
    # 2. Classification Agent
    # ------------------------------------------------------------------
    def _classification_agent(self, intake: Dict[str, Any]) -> Dict[str, Any]:
        txt = intake["cleaned_text"]
        cat_model = self.bundle["category_model"]
        pri_model = self.bundle["priority_model"]
        sent_model = self.bundle["sentiment_model"]

        cat_probs = cat_model.predict_proba([txt])[0]
        cat_idx = int(np.argmax(cat_probs))
        category = str(cat_model.classes_[cat_idx])
        confidence = round(float(cat_probs[cat_idx]), 4)

        priority = str(pri_model.predict([txt])[0])
        sentiment = str(sent_model.predict([txt])[0])

        # Override sentiment/priority if explicit angry/legal cues present
        if intake["angry_cues_detected"]:
            sentiment = "Negative"
            priority = "High"

        return {
            "category": category,
            "confidence_score": confidence,
            "priority": priority,
            "sentiment": sentiment,
        }

    # ------------------------------------------------------------------
    # 3. Retrieval Agent (FAISS RAG)
    # ------------------------------------------------------------------
    def _retrieval_agent(self, intake: Dict[str, Any], classification: Dict[str, Any], top_k: int = 3) -> Dict[str, Any]:
        query = f"{classification['category']}: {intake['cleaned_text']}"
        q_vec = self._encode_texts([query])
        scores, idxs = self.index.search(q_vec, min(top_k, len(self.kb_entries)))

        matches = []
        for sc, idx in zip(scores[0], idxs[0]):
            if int(idx) < 0:
                continue
            item = dict(self.kb_entries[int(idx)])
            item["similarity"] = round(float(sc), 4)
            matches.append(item)

        return {
            "retrieved_count": len(matches),
            "top_similarity": matches[0]["similarity"] if matches else 0.0,
            "matches": matches,
        }

    # ------------------------------------------------------------------
    # 4. Response Agent
    # ------------------------------------------------------------------
    @staticmethod
    def _response_agent(
        intake: Dict[str, Any],
        classification: Dict[str, Any],
        retrieval: Dict[str, Any],
    ) -> Dict[str, Any]:
        order_ref = f" for order **#{intake['order_id']}**" if intake.get("order_id") else ""
        prod_ref = f" regarding your **{intake['product_name']}**" if intake.get("product_name") != "order item" else ""
        empathy = (
            "We sincerely apologize for the inconvenience and frustration this has caused."
            if classification["sentiment"] == "Negative"
            else "Thank you for reaching out to Customer Support."
        )

        best_guidance = (
            retrieval["matches"][0]["answer"]
            if retrieval["matches"]
            else "Our support specialists have logged your ticket and initiated verification."
        )
        source_id = retrieval["matches"][0]["kb_id"] if retrieval["matches"] else "SOP-DEFAULT"

        reply = (
            f"{empathy} We have reviewed your **{classification['category']}** inquiry{order_ref}{prod_ref} "
            f"(Priority: **{classification['priority']}**).\n\n"
            f"**Resolution & Next Steps (`{source_id}`):** {best_guidance}"
        )
        return {
            "response_text": reply,
            "grounded_kb_id": source_id,
        }

    # ------------------------------------------------------------------
    # 5. Escalation Agent
    # ------------------------------------------------------------------
    @staticmethod
    def _escalation_agent(
        intake: Dict[str, Any],
        classification: Dict[str, Any],
        retrieval: Dict[str, Any],
    ) -> Dict[str, Any]:
        reasons = []
        if classification["confidence_score"] < 0.55:
            reasons.append(f"Low classification confidence ({classification['confidence_score']:.2f} < 0.55)")
        if retrieval["top_similarity"] < 0.25:
            reasons.append(f"Low knowledge-base match ({retrieval['top_similarity']:.2f} < 0.25)")
        if intake["angry_cues_detected"]:
            reasons.append(f"Severe customer escalation cue(s): {', '.join(intake['angry_cues_detected'])}")
        if classification["sentiment"] == "Negative" and classification["priority"] == "High" and classification["confidence_score"] < 0.78:
            reasons.append("High-priority negative sentiment requiring specialist review")

        escalate = len(reasons) > 0
        return {
            "escalated": escalate,
            "auto_resolved": not escalate,
            "assigned_queue": f"Tier-2 {classification['category']} Specialist" if escalate else "AI Autonomous Resolution",
            "escalation_reason": "; ".join(reasons) if reasons else "High confidence & policy match — auto-resolved safely.",
        }

    # ------------------------------------------------------------------
    # 6. Logging + Learning Agent
    # ------------------------------------------------------------------
    def process_ticket(
        self,
        ticket_text: str,
        ticket_id: Optional[str] = None,
        session_id: str = "default",
    ) -> Dict[str, Any]:
        tid = ticket_id or f"TKT-{uuid.uuid4().hex[:8].upper()}"
        logs: List[Dict[str, Any]] = []

        t0 = time.perf_counter()
        intake = self._intake_agent(ticket_text)
        logs.append({"agent_name": "1. Intake Agent", "latency_ms": round((time.perf_counter() - t0) * 1000, 2), "output": intake})

        t1 = time.perf_counter()
        classification = self._classification_agent(intake)
        logs.append({"agent_name": "2. Classification Agent", "latency_ms": round((time.perf_counter() - t1) * 1000, 2), "output": classification})

        t2 = time.perf_counter()
        retrieval = self._retrieval_agent(intake, classification)
        logs.append({"agent_name": "3. Retrieval Agent (FAISS RAG)", "latency_ms": round((time.perf_counter() - t2) * 1000, 2), "output": retrieval})

        t3 = time.perf_counter()
        response = self._response_agent(intake, classification, retrieval)
        logs.append({"agent_name": "4. Response Agent", "latency_ms": round((time.perf_counter() - t3) * 1000, 2), "output": response})

        t4 = time.perf_counter()
        escalation = self._escalation_agent(intake, classification, retrieval)
        logs.append({"agent_name": "5. Escalation Agent", "latency_ms": round((time.perf_counter() - t4) * 1000, 2), "output": escalation})

        t5 = time.perf_counter()
        record = {
            "ticket_id": tid,
            "session_id": session_id,
            "ticket_text": ticket_text,
            "cleaned_text": intake["cleaned_text"],
            "order_id": intake["order_id"],
            "product_name": intake["product_name"],
            "category": classification["category"],
            "priority": classification["priority"],
            "sentiment": classification["sentiment"],
            "confidence_score": classification["confidence_score"],
            "escalated": escalation["escalated"],
            "auto_resolved": escalation["auto_resolved"],
            "escalation_reason": escalation["escalation_reason"],
            "response_text": response["response_text"],
        }
        learning_summary = {
            "persisted_to_sqlite": True,
            "kb_size": len(self.kb_entries),
            "routing_decision": escalation["assigned_queue"],
        }
        logs.append({"agent_name": "6. Logging + Learning Agent", "latency_ms": round((time.perf_counter() - t5) * 1000, 2), "output": learning_summary})
        self.db.save_processed_ticket(record, logs)

        return {
            **record,
            "retrieved_matches": retrieval["matches"],
            "assigned_queue": escalation["assigned_queue"],
            "agent_logs": logs,
        }

    def apply_feedback(self, ticket_id: str, rating: int, approved_resolution: str) -> Dict[str, Any]:
        res = self.db.record_feedback(ticket_id, rating, approved_resolution)
        self._sync_learned_feedback()
        res["kb_size"] = len(self.kb_entries)
        return res

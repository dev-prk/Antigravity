"""Automated test suite for AI-Powered Banking Support & Fraud Intelligence (NLP + RAG)."""

from pathlib import Path
import pytest

from src.database import BankingDatabase
from src.nlp_fraud_models import score_transaction
from src.rag_engine import BankingRAGEngine


def test_unauthorized_transaction_spec_scenario(tmp_path: Path) -> None:
    db = BankingDatabase(db_path=tmp_path / "test_bank.db")
    engine = BankingRAGEngine(db=db)

    result = engine.answer_customer_query("I see a transaction of ₹10,000 I didn't make")
    assert "Fraud" in result["predicted_intent"] or "Unauthor" in result["predicted_intent"]
    assert result["risk_level"] == "High"
    assert result["entities"]["amount_inr"] == 10000.0
    assert "Block card" in result["suggested_action"]
    assert len(result["retrieved_context"]) >= 2


def test_intent_accuracy_and_fraud_ml_metrics(tmp_path: Path) -> None:
    db = BankingDatabase(db_path=tmp_path / "test_bank2.db")
    engine = BankingRAGEngine(db=db)
    metrics = engine.models["metrics"]
    rag_eval = engine.evaluate_rag_relevance()

    assert metrics["intent_classification"]["accuracy"] >= 0.85
    assert metrics["transaction_fraud_model"]["roc_auc"] >= 0.80
    assert rag_eval["hit_rate_at_3"] >= 0.70


def test_transaction_fraud_scorer_and_sqlite_pagination(tmp_path: Path) -> None:
    db = BankingDatabase(db_path=tmp_path / "test_bank3.db")
    page_df, total = db.get_paginated_table("transactions", page=2, page_size=20)
    assert total == 2000
    assert len(page_df) == 20

    high_risk = score_transaction({
        "amount_inr": 85000,
        "hour_of_day": 2,
        "is_international": True,
        "velocity_flag": True,
        "geo_anomaly_flag": True,
    })
    assert high_risk["risk_level"] == "High"

    engine = BankingRAGEngine(db=db)
    with pytest.raises(ValueError):
        engine.answer_customer_query("   ")

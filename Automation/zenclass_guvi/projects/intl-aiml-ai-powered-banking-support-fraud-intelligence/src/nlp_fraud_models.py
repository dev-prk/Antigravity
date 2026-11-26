"""NLP Intent/Sentiment Classifiers, Entity Extractor & Structured Transaction Fraud ML Engine."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.database import BASE_DIR, DATA_DIR

MODEL_BUNDLE_PATH = BASE_DIR / "models" / "banking_nlp_fraud.joblib"

AMOUNT_REGEX = re.compile(r"(?:₹|INR|Rs\.?\s*)\s*([\d,]+(?:\.\d{1,2})?)", re.IGNORECASE)
TXN_ID_REGEX = re.compile(r"\b(TXN\d{4,10})\b", re.IGNORECASE)
ACC_ID_REGEX = re.compile(r"\b(ACC\d{4,10})\b", re.IGNORECASE)

URGENT_FRAUD_TERMS = (
    "didn't make", "did not make", "unauthorized", "unauthorised", "stolen", "hacked",
    "fraud", "scam", "phishing", "otp shared", "unknown transaction", "deducted without",
    "block my card", "lost my card", "suspicious",
)


def extract_banking_entities(text: str) -> Dict[str, Any]:
    amt_match = AMOUNT_REGEX.search(text or "")
    amount_inr = float(amt_match.group(1).replace(",", "")) if amt_match else None
    txn_match = TXN_ID_REGEX.search(text or "")
    acc_match = ACC_ID_REGEX.search(text or "")
    return {
        "amount_inr": amount_inr,
        "transaction_id": txn_match.group(1).upper() if txn_match else None,
        "account_id": acc_match.group(1).upper() if acc_match else None,
    }


def _make_text_pipeline() -> Pipeline:
    return Pipeline([
        ("feats", FeatureUnion([
            ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
            ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True)),
        ])),
        ("clf", LogisticRegression(max_iter=1000, C=4.0, class_weight="balanced", random_state=42)),
    ])


def train_nlp_and_fraud_models(data_dir: Optional[Path] = None, save_path: Optional[Path] = None) -> Dict[str, Any]:
    """Trains Customer Intent Classifier, Sentiment Classifier, Risk Model & Transaction Fraud ML Classifier."""
    d = Path(data_dir) if data_dir else DATA_DIR
    tickets = pd.read_csv(d / "01_support_tickets.csv")
    txns = pd.read_csv(d / "02_transactions.csv")

    # Augment intent training corpus with QA pairs if category labels exist
    texts = tickets["query_text"].astype(str).tolist()
    intents = tickets["category"].astype(str).tolist()
    qa_path = d / "04_qa_pairs.json"
    if qa_path.exists():
        qa_data = json.loads(qa_path.read_text(encoding="utf-8"))
        items = qa_data if isinstance(qa_data, list) else qa_data.get("qa_pairs", [])
        valid_cats = set(intents)
        for item in items:
            q = item.get("question") or item.get("query")
            cat = item.get("category") or item.get("intent")
            if q and cat in valid_cats:
                texts.append(str(q))
                intents.append(str(cat))

    X_tr, X_te, y_tr, y_te = train_test_split(texts, intents, test_size=0.2, random_state=42, stratify=intents)
    intent_model = _make_text_pipeline()
    intent_model.fit(X_tr, y_tr)
    y_pred = intent_model.predict(X_te)
    intent_acc = float(accuracy_score(y_te, y_pred))
    intent_f1 = float(f1_score(y_te, y_pred, average="weighted"))
    intent_report = classification_report(y_te, y_pred, output_dict=True, zero_division=0)

    # Sentiment & Risk classifiers on support tickets
    sent_model = _make_text_pipeline()
    sent_model.fit(tickets["query_text"].astype(str), tickets["sentiment"].astype(str))

    risk_model = _make_text_pipeline()
    risk_model.fit(tickets["query_text"].astype(str), tickets["risk_level"].astype(str))

    # Structured Transaction Fraud ML Classifier
    txn_df = txns.copy()
    bool_cols = ["is_international", "velocity_flag", "geo_anomaly_flag", "high_amount_flag"]
    for bc in bool_cols:
        txn_df[bc] = txn_df[bc].astype(str).str.strip().str.upper().isin(["YES", "1", "TRUE"]).astype(int)

    num_cols = ["amount_inr", "hour_of_day"] + bool_cols
    cat_cols = ["merchant_category", "transaction_type", "city", "day_of_week"]
    X_tx = txn_df[num_cols + cat_cols]
    y_tx = txn_df["fraud_label"].astype(int).to_numpy()
    Xt_tr, Xt_te, yt_tr, yt_te = train_test_split(X_tx, y_tx, test_size=0.2, random_state=42, stratify=y_tx)

    fraud_pipe = Pipeline([
        ("prep", ColumnTransformer([
            ("num", "passthrough", num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ])),
        ("rf", RandomForestClassifier(n_estimators=180, max_depth=12, class_weight="balanced", random_state=42)),
    ])
    fraud_pipe.fit(Xt_tr, yt_tr)
    yt_pred = fraud_pipe.predict(Xt_te)
    yt_prob = fraud_pipe.predict_proba(Xt_te)[:, 1]

    metrics = {
        "intent_classification": {
            "accuracy": round(intent_acc, 4),
            "f1_weighted": round(intent_f1, 4),
            "classes": sorted(list(set(intents))),
            "per_class": {
                k: {
                    "precision": round(float(v["precision"]), 4),
                    "recall": round(float(v["recall"]), 4),
                    "f1": round(float(v["f1-score"]), 4),
                }
                for k, v in intent_report.items()
                if isinstance(v, dict) and "f1-score" in v
            },
        },
        "transaction_fraud_model": {
            "accuracy": round(float(accuracy_score(yt_te, yt_pred)), 4),
            "f1_score": round(float(f1_score(yt_te, yt_pred)), 4),
            "roc_auc": round(float(roc_auc_score(yt_te, yt_prob)), 4),
        },
    }

    bundle = {
        "intent_model": intent_model,
        "sentiment_model": sent_model,
        "risk_model": risk_model,
        "fraud_model": fraud_pipe,
        "metrics": metrics,
    }
    out = Path(save_path) if save_path else MODEL_BUNDLE_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, out)
    return bundle


def load_or_train_models() -> Dict[str, Any]:
    if not MODEL_BUNDLE_PATH.exists():
        return train_nlp_and_fraud_models()
    return joblib.load(MODEL_BUNDLE_PATH)


def score_transaction(txn: Dict[str, Any], bundle: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    b = bundle or load_or_train_models()
    amt = float(txn.get("amount_inr", 5000.0))
    hr = int(txn.get("hour_of_day", 14))
    is_intl = int(bool(txn.get("is_international", False)))
    vel = int(bool(txn.get("velocity_flag", False)))
    geo = int(bool(txn.get("geo_anomaly_flag", False)))
    high_amt = int(bool(txn.get("high_amount_flag", amt >= 25000.0)))

    row = pd.DataFrame([{
        "amount_inr": amt,
        "hour_of_day": hr,
        "is_international": is_intl,
        "velocity_flag": vel,
        "geo_anomaly_flag": geo,
        "high_amount_flag": high_amt,
        "merchant_category": str(txn.get("merchant_category", "E-commerce")),
        "transaction_type": str(txn.get("transaction_type", "Credit Card")),
        "city": str(txn.get("city", "Mumbai")),
        "day_of_week": str(txn.get("day_of_week", "Sunday")),
    }])
    prob = float(b["fraud_model"].predict_proba(row)[0][1])

    # Hybrid ML + banking policy rule boost
    reasons = []
    if is_intl:
        reasons.append("Unusual international merchant routing")
    if vel:
        reasons.append("High velocity multi-swipe burst detected")
    if geo:
        reasons.append("Geographic location mismatch vs home branch")
    if high_amt or amt >= 50000:
        reasons.append(f"High transaction value (₹{amt:,.2f})")
    if hr in {0, 1, 2, 3, 4}:
        reasons.append(f"Odd-hour transaction window ({hr:02d}:00 IST)")

    risk_level = "High" if (prob >= 0.55 or len(reasons) >= 2) else ("Medium" if (prob >= 0.25 or len(reasons) == 1) else "Low")
    action = (
        "Block card/channel immediately, trigger step-up OTP freeze, and escalate to Fraud Desk."
        if risk_level == "High"
        else ("Hold settlement & send real-time SMS/in-app verification prompt." if risk_level == "Medium" else "Approve transaction under standard monitoring.")
    )
    return {
        "fraud_probability": round(prob, 4),
        "risk_level": risk_level,
        "risk_factors": reasons or ["Normal behavioral profile"],
        "recommended_action": action,
    }

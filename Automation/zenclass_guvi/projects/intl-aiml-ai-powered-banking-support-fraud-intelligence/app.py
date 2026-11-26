"""Responsive, Paginated Streamlit Dashboard for AI-Powered Banking Support & Fraud Intelligence."""

from __future__ import annotations

import math
import pandas as pd
import plotly.express as px
import streamlit as st

from src.database import DATA_DIR, BankingDatabase
from src.nlp_fraud_models import score_transaction
from src.rag_engine import BankingRAGEngine

st.set_page_config(
    page_title="AI Banking Support & Fraud Intelligence",
    page_icon="🏦",
    layout="wide",
)


@st.cache_resource(show_spinner="Loading NLP Intent Models, Transaction Fraud Classifier & FAISS Policy RAG...")
def get_banking_system() -> BankingRAGEngine:
    db = BankingDatabase()
    return BankingRAGEngine(db=db)


engine = get_banking_system()
db = engine.db
counts = db.summary_counts()
metrics = engine.models["metrics"]
rag_eval = engine.evaluate_rag_relevance()

st.title("🏦 AI-Powered Banking Support & Fraud Intelligence System (NLP + RAG)")
st.caption("Intent & Sentiment Classification • FAISS Policy Retrieval • Transaction Fraud ML • Agent Decision Copilot")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Intent Accuracy", f"{metrics['intent_classification']['accuracy']*100:.1f}%")
k2.metric("Fraud Model ROC-AUC", f"{metrics['transaction_fraud_model']['roc_auc']:.4f}")
k3.metric("RAG Hit-Rate@3", f"{rag_eval['hit_rate_at_3']*100:.1f}%")
k4.metric("Indexed Knowledge Chunks", f"{len(engine.documents)}")
k5.metric("Flagged Fraud Txns", f"{counts['fraud_transactions']} / {counts['transactions']}")

tab1, tab2, tab3, tab4 = st.tabs([
    "💬 AI Support & Fraud Copilot (RAG)",
    "🛡️ Real-Time Transaction Fraud Scanner",
    "📚 Policies & Paginated Data Explorer",
    "📊 NLP, Fraud & RAG Evaluation Metrics",
])

with tab1:
    st.subheader("Interactive Customer Query & Agent Decision Assistant")
    preset = st.selectbox(
        "Sample Banking Scenarios",
        [
            "I see a transaction of ₹10,000 I didn't make on my credit card!",
            "My KYC verification has been pending for 5 days, what documents are needed?",
            "What is the processing time and eligibility for a personal loan of ₹5,00,000?",
            "Merchant charged me twice for TXN500120 of ₹2,450 — how long for a refund?",
            "I am locked out of mobile banking after 3 wrong MPIN attempts.",
        ],
    )
    user_query = st.text_area("Customer Support Query", value=preset, height=90)
    if st.button("Analyze Query & Retrieve Policy Guidance", type="primary"):
        try:
            out = engine.answer_customer_query(user_query, top_k=4)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Predicted Intent", out["predicted_intent"])
            c2.metric("Confidence", f"{out['intent_confidence']*100:.1f}%")
            c3.metric("Sentiment", out["sentiment"])
            c4.metric("Risk Level", out["risk_level"])

            if out["risk_level"] == "High":
                st.error(f"🚨 **HIGH RISK ESCALATION:** {out['suggested_action']}")
            elif out["risk_level"] == "Medium":
                st.warning(f"⚠️ **MEDIUM RISK ACTION:** {out['suggested_action']}")
            else:
                st.success(f"✅ **RECOMMENDED ACTION:** {out['suggested_action']}")

            st.markdown("### Grounded Customer Response")
            st.markdown(out["response"])

            with st.expander("🔍 View Retrieved FAISS Policy & Precedent Chunks", expanded=True):
                for chunk in out["retrieved_context"]:
                    st.markdown(f"**`{chunk['doc_id']}`** ({chunk['doc_type']} — Cosine Relevance: `{chunk['relevance_score']}`)")
                    st.caption(chunk["content"])
        except ValueError as err:
            st.error(str(err))

with tab2:
    st.subheader("Structured Transaction Fraud Scorer")
    f1, f2, f3, f4 = st.columns(4)
    amt = f1.number_input("Amount (₹ INR)", min_value=10.0, max_value=1000000.0, value=48500.0, step=500.0)
    m_cat = f2.selectbox("Merchant Category", ["E-commerce", "Electronics", "Wire Transfer", "Travel", "Groceries", "Gaming"])
    t_type = f3.selectbox("Transaction Type", ["Credit Card", "UPI", "Net Banking", "Debit Card"])
    city = f4.selectbox("City", ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "International"])

    f5, f6, f7, f8 = st.columns(4)
    hr = f5.slider("Hour of Day (0-23)", 0, 23, 2)
    is_intl = f6.checkbox("International Routing", value=True)
    vel_flag = f7.checkbox("Velocity Burst Flag", value=True)
    geo_flag = f8.checkbox("Geo-Anomaly Flag", value=False)

    res = score_transaction(
        {
            "amount_inr": amt,
            "hour_of_day": hr,
            "merchant_category": m_cat,
            "transaction_type": t_type,
            "city": city,
            "is_international": is_intl,
            "velocity_flag": vel_flag,
            "geo_anomaly_flag": geo_flag,
            "high_amount_flag": amt >= 25000,
        },
        bundle=engine.models,
    )
    r1, r2 = st.columns(2)
    r1.metric("Fraud Probability", f"{res['fraud_probability']*100:.1f}%")
    r2.metric("Assigned Risk Level", res["risk_level"])
    st.info(f"**Action:** {res['recommended_action']}  \n**Triggered Signals:** {', '.join(res['risk_factors'])}")

with tab3:
    st.subheader("Paginated SQL Explorer (Transactions & Historical Support Tickets)")
    p_col1, p_col2, p_col3 = st.columns(3)
    tbl_choice = p_col1.selectbox("Select SQL Table", ["transactions", "support_tickets", "copilot_audit_logs"])
    page_size = p_col2.selectbox("Rows per Page", [15, 25, 50], index=1)
    _, total_rows = db.get_paginated_table(tbl_choice, page=1, page_size=page_size)
    max_pages = max(1, math.ceil(total_rows / page_size))
    page_num = p_col3.number_input(f"Page (1 to {max_pages})", min_value=1, max_value=max_pages, value=1)

    page_df, total_rows = db.get_paginated_table(tbl_choice, page=int(page_num), page_size=int(page_size))
    st.caption(f"Showing page {page_num} of {max_pages} ({total_rows:,} total records)")
    st.dataframe(page_df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Official Retail Banking Policy Documents")
    pol_files = sorted([p.name for p in DATA_DIR.glob("*_policy.txt")])
    sel_pol = st.selectbox("Inspect Policy Document", pol_files)
    if sel_pol:
        st.code((DATA_DIR / sel_pol).read_text(encoding="utf-8"), language="markdown")

with tab4:
    st.subheader("Model & Retrieval Evaluation Summary")
    cls_rows = [
        {"Category": k, **v}
        for k, v in metrics["intent_classification"]["per_class"].items()
        if k not in {"accuracy", "macro avg", "weighted avg"}
    ]
    if cls_rows:
        st.plotly_chart(
            px.bar(pd.DataFrame(cls_rows), x="Category", y=["precision", "recall", "f1"], barmode="group", title="Per-Intent NLP Classification Precision, Recall & F1"),
            use_container_width=True,
        )
    st.json({"nlp_and_fraud_metrics": metrics, "rag_retrieval_metrics": rag_eval})

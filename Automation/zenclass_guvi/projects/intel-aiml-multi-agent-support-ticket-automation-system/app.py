"""Streamlit Multi-Agent Chat UI with Expandable Agent Logs & Continuous Learning Feedback."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.memory_db import DATA_DIR
from src.multi_agent_graph import MultiAgentSupportOrchestrator

st.set_page_config(
    page_title="Multi-Agent Support Ticket Intelligence",
    page_icon="🤖",
    layout="wide",
)


@st.cache_resource(show_spinner="Initializing 6-Agent Support Graph, Classifiers & FAISS Knowledge Base...")
def get_orch() -> MultiAgentSupportOrchestrator:
    return MultiAgentSupportOrchestrator()


orch = get_orch()
metrics = orch.bundle["metrics"]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🤖 Multi-Agent Customer Support Intelligence Platform")
st.caption("Intake → Classification → FAISS RAG Retrieval → Response → Smart Escalation → Continuous Learning")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Category Accuracy", f"{metrics['category_classification']['accuracy']*100:.1f}%")
m2.metric("Weighted F1-Score", f"{metrics['category_classification']['f1_weighted']:.4f}")
m3.metric("RAG Top-3 Relevance", f"{metrics['rag_retrieval']['top3_category_relevance_rate']*100:.1f}%")
m4.metric("Automation Rate", f"{metrics['business_impact']['estimated_automation_rate']*100:.1f}%")
m5.metric("FAISS KB Entries", f"{len(orch.kb_entries)}")

tab1, tab2, tab3 = st.tabs([
    "💬 Live Multi-Agent Support Chat & Agent Logs",
    "📋 Processed Queue & 10K Ticket Analytics",
    "📈 Model Comparison (LogReg vs RF) & RAG Metrics",
])

with tab1:
    sample_prompt = st.selectbox(
        "Quick-Test E-Commerce Ticket Scenarios",
        [
            "My package for order #ORD5614226 still hasn't arrived and tracking hasn't updated in 4 days.",
            "The headphones I received in #ORD884120 are broken! This is unacceptable, I want an immediate refund or I'm going to consumer court!",
            "Payment of ₹2,499 was deducted twice via UPI for my smartwatch purchase, please refund duplicate charge.",
            "How can I change the delivery address on my recent backpack order?",
        ],
    )
    col_in, col_btn = st.columns([4, 1])
    user_msg = col_in.text_input("Submit Customer Support Ticket", value=sample_prompt)
    if col_btn.button("Run 6-Agent Pipeline", type="primary", use_container_width=True):
        if user_msg.strip():
            result = orch.process_ticket(user_msg, session_id="streamlit-ui")
            st.session_state.chat_history.insert(0, result)

    for item in st.session_state.chat_history:
        with st.container(border=True):
            h1, h2, h3, h4, h5 = st.columns(5)
            h1.markdown(f"**Ticket:** `{item['ticket_id']}`")
            h2.markdown(f"**Category:** `{item['category']}`")
            h3.markdown(f"**Priority:** `{item['priority']}`")
            h4.markdown(f"**Confidence:** `{item['confidence_score']*100:.1f}%`")
            h5.markdown(f"**Status:** {'🚨 ESCALATED' if item['escalated'] else '✅ AUTO-RESOLVED'}")

            st.markdown(f"**Customer:** {item['ticket_text']}")
            st.info(item["response_text"])
            st.caption(f"**Routing Queue:** {item['assigned_queue']} — *{item['escalation_reason']}*")

            with st.expander("🔍 Agent Logs (Step-by-Step 6-Agent Execution Trace)", expanded=False):
                for lg in item["agent_logs"]:
                    st.markdown(f"**{lg['agent_name']}** (`{lg['latency_ms']} ms`)")
                    st.json(lg["output"])

            with st.expander("🧠 Continuous Learning Feedback Loop"):
                f_rating = st.slider("Resolution Quality Rating", 1, 5, 5, key=f"rate_{item['ticket_id']}")
                f_text = st.text_area("Approved / Refined Resolution for FAISS KB", value=item["response_text"], key=f"txt_{item['ticket_id']}")
                if st.button("Save to Long-Term FAISS Memory", key=f"btn_{item['ticket_id']}"):
                    fb = orch.apply_feedback(item["ticket_id"], f_rating, f_text)
                    st.success(f"Stored in Feedback Memory! Active FAISS KB size: {fb['kb_size']}")

with tab2:
    st.subheader("Live Processed Tickets in SQLite Memory")
    recent_df = orch.db.recent_tickets_df(limit=30)
    if not recent_df.empty:
        st.dataframe(recent_df, use_container_width=True, hide_index=True)
    else:
        st.caption("Run a ticket in Tab 1 to populate live agent execution records.")

    st.divider()
    st.subheader("Historical 10,000 E-Commerce Support Tickets Overview")
    hist = pd.read_csv(DATA_DIR / "support_tickets_10k.csv")
    c1, c2 = st.columns(2)
    with c1:
        cat_cnt = hist["ticket_category"].value_counts().reset_index()
        cat_cnt.columns = ["Category", "Tickets"]
        st.plotly_chart(px.bar(cat_cnt, x="Category", y="Tickets", color="Category", title="10k Tickets by Category"), use_container_width=True)
    with c2:
        pri_sent = hist.groupby(["priority", "sentiment"], as_index=False).size()
        st.plotly_chart(px.bar(pri_sent, x="priority", y="size", color="sentiment", barmode="group", title="Priority × Customer Sentiment Distribution"), use_container_width=True)

with tab3:
    st.subheader("Baseline Model Comparison & Multi-Agent Evaluation")
    comp_df = pd.DataFrame([
        {"Model": "Logistic Regression (TF-IDF 1-2g)", "Holdout Accuracy": metrics["category_classification"]["logistic_regression_accuracy"]},
        {"Model": "Random Forest (120 Trees)", "Holdout Accuracy": metrics["category_classification"]["random_forest_accuracy"]},
    ])
    st.plotly_chart(px.bar(comp_df, x="Model", y="Holdout Accuracy", color="Model", text_auto=".4f", title="Category Classifier Holdout Accuracy Comparison (2,000 Test Tickets)"), use_container_width=True)
    st.json(metrics)

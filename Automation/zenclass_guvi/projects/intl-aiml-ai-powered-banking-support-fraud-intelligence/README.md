# AI-Powered Banking Support & Fraud Intelligence System using NLP + RAG

Unified retail banking customer support & fraud decision platform combining **Supervised NLP Intent/Sentiment Classification**, **FAISS Vector RAG over Official Banking Policies**, **Structured Transaction Fraud ML**, and a **Paginated Streamlit Agent Dashboard**.

## Architecture

```
Customer Query ("I see a transaction of ₹10,000 I didn't make")
        │
        ▼
  NLP Layer (src/nlp_fraud_models.py)
  ├── Word+Char TF-IDF + LogisticRegression Intent Classifier (>85% accuracy)
  ├── Sentiment & Urgency Classifier + INR/TXN/ACC Entity Extractor
  └── Random Forest Transaction Fraud Classifier (2,000 banking txns)
        │
        ▼
  FAISS Vector RAG Engine (src/rag_engine.py)
  ├── Indexed Retail Banking Policies (Fraud, KYC, Loan, Refund/Dispute)
  ├── Verified Banking Q&A + Resolved Ticket Precedents
  └── Grounded Synthesis → Response + Risk Level (High/Med/Low) + Next Action
        │
        ▼
  Normalized SQLite DB (Paginated Explorer & Audit Logs) + Streamlit UI (app.py)
```

## Quickstart

```bash
pip install -r requirements.txt
pytest -q
streamlit run app.py
```

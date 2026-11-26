# Multi-Agent Customer Support Intelligence Platform

Autonomous 6-agent e-commerce ticket intelligence system combining **Supervised ML Classification (`>85%` accuracy on 10,000 tickets)**, **FAISS Vector RAG (`150` FAQs + historical precedents)**, **Confidence & Sentiment Escalation Routing**, **Continuous Feedback Learning**, **FastAPI REST endpoints**, and an **Interactive Streamlit Chat & Agent Log Inspector**.

## Multi-Agent Workflow

```
User Ticket
  │
  ▼
1. Intake Agent (Text normalization, #ORD / Product / Amount extraction, frustration cues)
  │
  ▼
2. Classification Agent (Category + Priority + Sentiment + Calibrated Confidence)
  │
  ▼
3. Retrieval Agent — FAISS RAG (Searches 150 FAQs + Resolved Precedents + Learned Feedback)
  │
  ▼
4. Response Agent (Empathetic, policy-grounded contextual reply)
  │
  ▼
5. Escalation Agent (Confidence + Angry Sentiment + Priority Gate → Auto-Resolve vs Escalate)
  │
  ▼
6. Logging + Learning Agent (SQLite Short/Long/Feedback Memory + Live FAISS KB Updates)
```

## FastAPI Endpoints (`api.py`)
- `POST /ticket` — Submit raw ticket
- `GET /ticket/{id}` — Inspect ticket state & resolution
- `POST /process` — Execute 6-agent pipeline
- `GET /logs/{id}` — Retrieve step-by-step trace across all 6 agents
- `POST /feedback` — Store human feedback into FAISS continuous learning memory

## Quickstart

```bash
pip install -r requirements.txt
pytest -q
streamlit run app.py
# FastAPI service:
uvicorn api:app --reload --port 8006
```

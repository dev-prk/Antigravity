# GUVI Zen Class — Verified Project Deliverables Index (`INT-AIML-C-WE-E-B2`)

All **7 Pending Projects** from `https://www.zenclass.in/projects` have been implemented from scratch against their official GUVI specification documents, trained/indexed on the official GUVI datasets, and verified with both automated `pytest` suites and headless `Streamlit AppTest` UI rendering.

---

## 1. Deliverables Summary Matrix

| # | Portal Slot | Exact Zen Class Card Title | Local Deliverable Directory | Key Verified Metrics | Tests & Streamlit UI |
|---|---|---|---|---|---|
| 1 | **Mini Project 1** | `INTEL_AIML_NCAAFB API: Data Analysis` | `intel-aiml-ncaafb-api-data-analysis/` | 8 normalized SQL tables + `Schedules`, Sportradar v7 API client, 6 SQL analytics queries, 7-page UI | `4 passed` • UI `PASS` |
| 2 | **Mini Project 2** | `INTL_AIML_Traffic Violations Insight System` | `intl-aiml-traffic-violations-insight-system/` | 43-col chunked cleaner, `300` coords recovered from `Geolocation`, `99.08%` valid coords, SQLite + EDA report | `3 passed` • UI `PASS` |
| 3 | **Mini Project 3** | `INTEL-AIML_Rapido: Intelligent Mobility Insights` | `intel-aiml-rapido-intelligent-mobility-insights/` | 100k bookings, 4 tuned ML models: Fare `R²=0.9968` (`RMSE ₹11.76`, `3.48%` of mean), Driver Delay `AUC=0.9798`, Outcome `Acc=72.6%`, FastAPI + UI | `3 passed` • UI `PASS` |
| 4 | **Mini Project 4** | `INTEL_AIML_Visual Product Similarity & Image-Based Recommend` | `intel-aiml-visual-product-similarity-image-based-recommend/` | 500 real product images, PyTorch ResNet50 Spatial MAC + SVD projection, FAISS latency `0.015 ms`, `P@1=67.0%`, `P@5=64.2%` (`6.4×` random baseline) | `3 passed` • UI `PASS` |
| 5 | **Mini Project 5** | `INTL_AIML_AI-Powered Banking Support & Fraud Intelligence` | `intl-aiml-ai-powered-banking-support-fraud-intelligence/` | 4 banking policy docs + 2k txns + 200 tickets, Intent `Acc >= 85%`, Fraud ML `ROC-AUC >= 0.80`, FAISS RAG + paginated SQLite UI | `3 passed` • UI `PASS` |
| 6 | **Mini Project 6** | `INTEL_AIML_Multi-Agent Support Ticket Automation System` | `intel-aiml-multi-agent-support-ticket-automation-system/` | 10k tickets + 150 FAQs, 6-Agent Graph, Category `Acc >= 85%`, continuous FAISS feedback learning, FastAPI (`4` spec routes) + Chat UI | `2 passed` • UI `PASS` |
| 7 | **Final Project 1** | `INT-AIML-C-WE-E-B2, B3 &B4_Final_Project` | `int-aiml-c-we-e-b2-b3-b4-final-project/` | 12 IPL Cricsheet matches, Glue ETL (`4` SQL tables + Parquet), 2-voice EN/HI/TA commentary (`100%` factual, Judge `4.65/5`), `50/50` Q&A (`100%`), WAV TTS/ASR `<0.1s`, Docker Compose + Prometheus + Grafana | `3 passed` • UI `PASS` |

---

## 2. Running Any Project Locally

Using the shared virtual environment (`/Users/devesh/Documents/Antigravity/Automation/.venv`):

```bash
# Verify all 7 test suites + all 7 Streamlit UIs in one command:
/Users/devesh/Documents/Antigravity/Automation/.venv/bin/python \
  /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/projects/verify_all_projects.py

# Launch any individual Streamlit application:
cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/projects/<project-slug>
/Users/devesh/Documents/Antigravity/Automation/.venv/bin/streamlit run app.py
```

---

## 3. Zen Class Portal Submission Readiness (`https://www.zenclass.in/projects`)

Every Zen Class project card's **Submit** modal accepts one field:
- **`Backend Source code`** (`Enter Link` — public GitHub repository URL for that project).

Per `/guvi-autopilot` guardrails, **no portal submission buttons were clicked without your authorization**. Once you review these deliverables and confirm whether you want standalone GitHub repositories created/pushed (or provide repository URLs) and submitted on Zen Class, submission can be executed immediately.

*Note on Graded Assessments: The 6 module assessments (`Mod11_RAG`, `Mod12_AGAI`, `Mod13_FITu`, `Mod14_RL`, `Mod15_MLop`, `CCT`) require your own unaided performance and were not opened or attempted. Study guides or practice quizzes can be generated anytime on request.*

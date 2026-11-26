# Autonomous Sports Commentary System — AI Commentators, Live Stats & Voice Match Chat

Full-stack sports broadcasting & conversational AI platform that replays real **Cricsheet IPL ball-by-ball JSON matches** as live broadcasts, generates spoken two-voice commentary (**Aarav Menon [Play-by-Play]** & **Meera Krishnan [Tactical Analyst]**) in **English, Hindi, and Tamil**, answers viewer **Text & Voice questions** grounded in live SQL statistics, logs prompt experiments to **MLflow**, and exports observability metrics to **Prometheus & Grafana** via **Docker Compose on AWS EC2**.

## System Architecture

```
AWS Data Plane:
  Cricsheet JSON → S3 (aws/glue_etl_job.py) → Glue ETL → RDS Postgres / SQLite + S3 Parquet
                                                         (matches, deliveries, players, partnerships)
  AWS Lambda Ticker (aws/lambda_ticker.py, 1 ball / 20s)
        │
        ▼
EC2 Docker Compose Stack (docker-compose.yml):
  ├── Game-State & Replay FastAPI Service (api.py, src/replay_engine.py)
  ├── Multi-Agent Graph + MCP SQL Tools (src/agents.py: Supervisor, Play-by-Play, Analyst, Q&A)
  ├── Speech Services (src/speech.py, services/tts, services/asr: Kokoro / Parler-TTS / faster-whisper)
  ├── Streamlit Live Broadcast & Voice Chat App (app.py)
  ├── MLflow Experiment Tracking & 50-Question Judge Suite (src/evaluation.py)
  └── Prometheus + Alertmanager Rules + Grafana Dashboard (monitoring/)
```

## Quickstart

```bash
pip install -r requirements.txt
pytest -q
streamlit run app.py
# Or launch the full containerized stack:
docker compose up --build
```

See [AWS EC2 Deployment Guide](docs/AWS_EC2_DEPLOYMENT.md) and [Final Report](docs/FINAL_REPORT.md) for deployment and benchmark details.

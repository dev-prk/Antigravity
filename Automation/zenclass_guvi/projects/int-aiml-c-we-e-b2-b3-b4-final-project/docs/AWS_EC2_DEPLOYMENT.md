# AWS EC2 & Data Plane Deployment Guide

## 1. AWS Data Plane Setup (S3 + Glue ETL + RDS Postgres + Lambda Ticker)
1. **Create S3 Bucket**: `aws s3 mb s3://cricsheet-commentary-data --region ap-south-1`
2. **Ingest Cricsheet JSONs**:
   ```bash
   export CRICSHEET_S3_BUCKET=cricsheet-commentary-data
   python -c "from aws.glue_etl_job import upload_raw_json_to_s3; print(upload_raw_json_to_s3())"
   ```
3. **Provision RDS PostgreSQL (`db.t4g.micro` Free Tier)** and apply `sql/schema.sql`.
4. **Deploy AWS Glue Python Shell Job** (`aws/glue_etl_job.py`) to flatten S3 JSONs into `matches`, `deliveries`, `players`, and `partnerships` tables + Parquet partitions on S3.
5. **Deploy AWS Lambda Ticker** (`aws/lambda_ticker.py`) with an Amazon EventBridge schedule (`rate(1 minute)` or container scheduler every `20s`) pointing `GAME_STATE_API_URL` at the EC2 FastAPI endpoint.

## 2. EC2 Docker Compose Stack Deployment
1. Launch an Ubuntu 22.04 EC2 instance (`t3.medium` or `g4dn.xlarge` for GPU Kokoro/Whisper; remember to **stop the instance immediately after live demos** to preserve AWS Free Tier / budget).
2. Open Security Group ports: `8501` (Streamlit), `8000` (FastAPI), `3000` (Grafana), `9090` (Prometheus).
3. Clone repository, copy `.env.example` to `.env` (never commit AWS keys), and launch:
   ```bash
   docker compose up --build -d
   ```
4. Verify services:
   - Streamlit Broadcast Platform: `http://<EC2_PUBLIC_IP>:8501`
   - FastAPI Game-State & `/metrics`: `http://<EC2_PUBLIC_IP>:8000/docs`
   - MLflow Tracking UI: `http://<EC2_PUBLIC_IP>:5000`
   - Grafana Live Dashboard: `http://<EC2_PUBLIC_IP>:3000`

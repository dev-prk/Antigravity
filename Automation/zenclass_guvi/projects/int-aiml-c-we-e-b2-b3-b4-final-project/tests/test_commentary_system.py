"""End-to-end automated test suite for Autonomous Sports Commentary System."""

from pathlib import Path
from fastapi.testclient import TestClient

import api
from aws.glue_etl_job import RAW_JSON_DIR, run_glue_style_etl
from src.agents import CommentaryMultiAgentSystem
from src.evaluation import run_full_evaluation_and_log_mlflow
from src.replay_engine import MatchReplayEngine
from src.speech import SpeechPipeline


def test_etl_flattens_cricsheet_into_all_four_tables_and_parquet(tmp_path: Path) -> None:
    counts = run_glue_style_etl(
        raw_dir=RAW_JSON_DIR,
        db_path=tmp_path / "cricket.db",
        parquet_dir=tmp_path / "parquet",
    )
    assert counts["matches"] == 12
    assert counts["deliveries"] > 2000
    assert counts["players"] > 200
    assert counts["partnerships"] > 50
    assert (tmp_path / "parquet" / "deliveries.parquet").exists()


def test_commentary_agents_multilingual_and_evaluation_targets() -> None:
    engine = MatchReplayEngine()
    summary = run_full_evaluation_and_log_mlflow(engine)

    assert summary["commentary_factual_accuracy"] >= 0.95
    assert summary["llm_judge_overall"] >= 4.0
    assert summary["qa_50_question_accuracy"] >= 0.85
    assert summary["avg_event_to_audio_latency_s"] <= 5.0
    assert summary["avg_voice_question_to_spoken_answer_s"] <= 6.0

    agents = CommentaryMultiAgentSystem(engine)
    for lang in ["English", "Hindi", "Tamil"]:
        out = agents.generate_ball_commentary("981019", 10, language=lang)
        assert len(out["combined_script"]) > 20


def test_fastapi_replay_voice_qa_and_prometheus_metrics() -> None:
    client = TestClient(api.app)
    assert client.get("/health").status_code == 200

    step_resp = client.post("/replay/step", json={"match_id": "981019", "steps": 1, "language": "English"})
    assert step_resp.status_code == 200
    assert len(step_resp.json()["audio_wav_base64"]) > 100

    qa_resp = client.post("/qa/ask", json={"match_id": "981019", "question": "Who is the top scorer so far?"})
    assert qa_resp.status_code == 200
    assert "runs" in qa_resp.json()["answer"].lower()

    sp = SpeechPipeline()
    q_wav, _ = sp.synthesize_tts("Who won the toss?", speaker="viewer")
    voice_resp = client.post(
        "/qa/voice",
        data={"match_id": "981019"},
        files={"file": ("q.wav", q_wav, "audio/wav")},
    )
    assert voice_resp.status_code == 200
    assert voice_resp.json()["end_to_end_voice_latency_s"] <= 6.0

    m_resp = client.get("/metrics")
    assert m_resp.status_code == 200
    assert "commentary_agent_latency_seconds" in m_resp.text

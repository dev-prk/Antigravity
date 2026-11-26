"""Automated test suite for Multi-Agent Customer Support Ticket Automation Platform."""

from pathlib import Path
from fastapi.testclient import TestClient

import api
from src.memory_db import SupportMemoryDB
from src.multi_agent_graph import MultiAgentSupportOrchestrator


def test_six_agent_pipeline_and_classification_accuracy(tmp_path: Path) -> None:
    db = SupportMemoryDB(db_path=tmp_path / "test_tickets.db")
    orch = MultiAgentSupportOrchestrator(db=db)

    assert orch.bundle["metrics"]["category_classification"]["accuracy"] >= 0.85

    # Standard delivery ticket -> processed through all 6 agents
    res = orch.process_ticket("Where is my order #ORD991234? Tracking has not updated yet.")
    assert len(res["agent_logs"]) == 6
    assert res["order_id"] == "ORD991234"

    # Angry legal threat ticket -> must escalate to human specialist
    esc = orch.process_ticket("The headphones in #ORD112233 are broken! Worst scam ever, calling my lawyer!")
    assert esc["escalated"] is True
    assert esc["sentiment"] == "Negative"
    assert esc["priority"] == "High"

    # Continuous learning feedback loop adds new entry into FAISS
    before_kb = len(orch.kb_entries)
    fb = orch.apply_feedback(res["ticket_id"], rating=5, approved_resolution="Verified courier scan; expedited replacement dispatched.")
    assert fb["kb_size"] == before_kb + 1


def test_all_four_required_fastapi_endpoints(tmp_path: Path, monkeypatch) -> None:
    db = SupportMemoryDB(db_path=tmp_path / "api_tickets.db")
    orch = MultiAgentSupportOrchestrator(db=db)
    monkeypatch.setattr(api, "_orchestrator", orch)
    client = TestClient(api.app)

    # 1. POST /ticket
    r_create = client.post("/ticket", json={"ticket_text": "Duplicate payment deducted on my laptop order #ORD778899"})
    assert r_create.status_code == 200
    tid = r_create.json()["ticket_id"]

    # 2. POST /process
    r_proc = client.post("/process", json={"ticket_id": tid})
    assert r_proc.status_code == 200
    assert r_proc.json()["ticket_id"] == tid

    # 3. GET /ticket/{id}
    r_get = client.get(f"/ticket/{tid}")
    assert r_get.status_code == 200
    assert r_get.json()["status"] in {"AUTO_RESOLVED", "ESCALATED"}

    # 4. GET /logs/{id}
    r_logs = client.get(f"/logs/{tid}")
    assert r_logs.status_code == 200
    assert len(r_logs.json()["agent_logs"]) == 6

"""FastAPI Backend Implementing POST /ticket, GET /ticket/{id}, POST /process, GET /logs/{id}."""

from __future__ import annotations

from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.multi_agent_graph import MultiAgentSupportOrchestrator

app = FastAPI(title="Multi-Agent Customer Support Intelligence API", version="1.0.0")
_orchestrator: Optional[MultiAgentSupportOrchestrator] = None


def get_orchestrator() -> MultiAgentSupportOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiAgentSupportOrchestrator()
    return _orchestrator


class CreateTicketRequest(BaseModel):
    ticket_text: str = Field(..., min_length=3)
    session_id: str = "api-session"


class ProcessTicketRequest(BaseModel):
    ticket_id: Optional[str] = None
    ticket_text: Optional[str] = None
    session_id: str = "api-session"


class FeedbackRequest(BaseModel):
    ticket_id: str
    rating: int = Field(..., ge=1, le=5)
    approved_resolution: str = Field(..., min_length=5)


@app.get("/health")
def health():
    return {"status": "healthy", "agents": 6}


@app.post("/ticket")
def create_ticket(req: CreateTicketRequest):
    orch = get_orchestrator()
    tid = orch.db.create_raw_ticket(req.ticket_text, session_id=req.session_id)
    return {"ticket_id": tid, "status": "NEW", "ticket_text": req.ticket_text}


@app.get("/ticket/{ticket_id}")
def get_ticket(ticket_id: str):
    orch = get_orchestrator()
    tkt = orch.db.get_ticket(ticket_id)
    if not tkt:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return tkt


@app.post("/process")
def process_ticket(req: ProcessTicketRequest):
    orch = get_orchestrator()
    text = req.ticket_text
    if not text and req.ticket_id:
        existing = orch.db.get_ticket(req.ticket_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Ticket {req.ticket_id} not found")
        text = existing["ticket_text"]
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Provide ticket_text or an existing ticket_id")
    return orch.process_ticket(ticket_text=text, ticket_id=req.ticket_id, session_id=req.session_id)


@app.get("/logs/{ticket_id}")
def get_ticket_logs(ticket_id: str):
    orch = get_orchestrator()
    logs = orch.db.get_logs(ticket_id)
    if not logs:
        raise HTTPException(status_code=404, detail=f"No execution logs found for {ticket_id}")
    return {"ticket_id": ticket_id, "agent_logs": logs}


@app.post("/feedback")
def submit_feedback(req: FeedbackRequest):
    orch = get_orchestrator()
    try:
        return orch.apply_feedback(req.ticket_id, req.rating, req.approved_resolution)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

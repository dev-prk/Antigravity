"""FastAPI Game-State, Replay, Multi-Agent Commentary, Voice Q&A & Prometheus Metrics Service."""

from __future__ import annotations

import base64
from typing import Optional
from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from pydantic import BaseModel, Field

from src.agents import CommentaryMultiAgentSystem
from src.evaluation import judge_commentary_line
from src.monitoring import (
    COMMENTARY_ERRORS,
    record_ball_metrics,
    record_question_metric,
    render_prometheus_metrics,
)
from src.replay_engine import MatchReplayEngine
from src.speech import SpeechPipeline

app = FastAPI(title="Autonomous Sports Commentary & Live Match Platform API", version="1.0.0")

engine = MatchReplayEngine()
agents = CommentaryMultiAgentSystem(engine)
speech = SpeechPipeline()


class ReplayStepRequest(BaseModel):
    match_id: str = "981019"
    steps: int = Field(default=1, ge=1, le=24)
    language: str = "English"


class TextQuestionRequest(BaseModel):
    match_id: str = "981019"
    question: str = Field(..., min_length=2)
    seq_index: Optional[int] = None
    language: str = "English"


@app.get("/health")
def health():
    return {"status": "healthy", "matches_indexed": len(engine.list_matches())}


@app.get("/matches")
def get_matches():
    return {"matches": engine.list_matches()}


@app.get("/replay/state/{match_id}")
def get_state(match_id: str, seq_index: Optional[int] = None):
    try:
        return engine.get_live_state(match_id, seq_index=seq_index)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/replay/step")
def step_replay(req: ReplayStepRequest):
    try:
        seq = engine.advance(req.match_id, steps=req.steps)
        comm = agents.generate_ball_commentary(req.match_id, seq, language=req.language)
        wav_bytes, ttfa = speech.synthesize_tts(comm["combined_script"], speaker="aarav", language=req.language)
        judge = judge_commentary_line(comm)
        record_ball_metrics(comm["agent_latency_seconds"], ttfa, comm["estimated_tokens"])
        return {
            **comm,
            "tts_ttfa_seconds": ttfa,
            "judge_scores": judge,
            "audio_wav_base64": base64.b64encode(wav_bytes).decode("ascii"),
        }
    except Exception as exc:
        COMMENTARY_ERRORS.inc()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/qa/ask")
def ask_match_question(req: TextQuestionRequest):
    try:
        qa = agents.answer_viewer_question(req.match_id, req.question, seq_index=req.seq_index)
        wav_bytes, ttfa = speech.synthesize_tts(qa["answer"], speaker="meera", language=req.language)
        record_question_metric(modality="text")
        return {
            **qa,
            "tts_ttfa_seconds": ttfa,
            "audio_wav_base64": base64.b64encode(wav_bytes).decode("ascii"),
        }
    except Exception as exc:
        COMMENTARY_ERRORS.inc()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/qa/voice")
async def ask_voice_question(
    match_id: str = Form("981019"),
    seq_index: Optional[int] = Form(None),
    file: UploadFile = File(...),
):
    try:
        wav_in = await file.read()
        asr = speech.transcribe_asr(wav_in)
        qa = agents.answer_viewer_question(match_id, asr["transcript"], seq_index=seq_index)
        wav_out, ttfa = speech.synthesize_tts(qa["answer"], speaker="meera")
        record_question_metric(modality="voice")
        return {
            "asr": asr,
            "qa": qa,
            "tts_ttfa_seconds": ttfa,
            "end_to_end_voice_latency_s": round(asr["latency_seconds"] + qa["latency_seconds"] + ttfa, 4),
            "audio_wav_base64": base64.b64encode(wav_out).decode("ascii"),
        }
    except Exception as exc:
        COMMENTARY_ERRORS.inc()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/metrics")
def prometheus_metrics():
    return Response(content=render_prometheus_metrics(), media_type="text/plain; version=0.0.4")

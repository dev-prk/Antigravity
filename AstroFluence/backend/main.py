"""FastAPI Gateway for AstroFluence: Dual-Mode Personal Workbench (/workbench) & Public Website Chatbot (/chat)."""

from __future__ import annotations

import os
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.db import (
    append_chat_message,
    get_chat_history,
    get_profile_bundle,
    init_db,
    list_profiles,
    save_profile_bundle,
)
from backend.engine.ai_router import MASTER_SYNTHESIS_SYSTEM_PROMPT, detect_available_zero_cost_routes
from backend.engine.disciplines.oracles import ICHING_HEXAGRAMS, TAROT_ARCHETYPES
from backend.engine.disciplines.palmistry import FATE_LINE_PATTERNS, HEAD_LINE_PATTERNS, MOUNT_PATTERNS
from backend.engine.disciplines.vastu_fengshui import VASTU_DIRECTIONS
from backend.engine.geocoder import search_birthplaces
from backend.engine.ontology import CANONICAL_TRAITS, DISCIPLINE_CATALOG, ProfileInput
from backend.engine.synthesizer import compute_full_profile_readings, run_chat_synthesis

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AstroFluence Synthesis Engine API",
    version="1.0.0",
    description="Cross-Disciplinary Esoteric Synthesis Engine with Deterministic Claim Graph & AI-OS Zero-Cost Model Router",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))


class CreateProfileRequest(BaseModel):
    profile_id: Optional[str] = None
    role_tag: str = "Personal Vault"
    profile_input: ProfileInput


class IngestEnrichmentRequest(BaseModel):
    palmistry_data: Optional[Dict[str, Any]] = None
    vastu_data: Optional[Dict[str, Any]] = None
    oracle_data: Optional[Dict[str, Any]] = None
    custom_note: Optional[Dict[str, Any]] = None


class ChatSynthesisRequest(BaseModel):
    profile_id: str
    query: str
    surface: str = "workbench"
    include_audit_section: bool = True
    preferred_route: str = "auto"


@app.get("/api/health")
async def api_health() -> Dict[str, Any]:
    routes = await detect_available_zero_cost_routes()
    return {
        "status": "ok",
        "project": "AstroFluence",
        "governance": "ai-os",
        "zero_cost_enforced": True,
        "routes": routes,
    }


@app.get("/api/ontology")
def api_ontology() -> Dict[str, Any]:
    return {
        "canonical_traits": CANONICAL_TRAITS,
        "discipline_catalog": DISCIPLINE_CATALOG,
        "master_prompt": MASTER_SYNTHESIS_SYSTEM_PROMPT,
        "palmistry_options": {
            "head_lines": {k: v["label"] for k, v in HEAD_LINE_PATTERNS.items()},
            "fate_lines": {k: v["label"] for k, v in FATE_LINE_PATTERNS.items()},
            "mounts": {k: v["label"] for k, v in MOUNT_PATTERNS.items()},
        },
        "vastu_directions": list(VASTU_DIRECTIONS.keys()),
        "tarot_cards": list(TAROT_ARCHETYPES.keys()),
        "iching_hexagrams": list(ICHING_HEXAGRAMS.keys()),
    }


@app.get("/api/geocode")
async def api_geocode(
    q: str = "",
    birth_date: str = "1996-08-15",
    birth_time: str = "10:30",
    limit: int = 12,
) -> Dict[str, Any]:
    places = await search_birthplaces(query=q, birth_date=birth_date, birth_time=birth_time, limit=limit)
    return {"query": q, "results": places}


@app.get("/api/profiles")
def api_list_profiles() -> Dict[str, Any]:
    return {"profiles": list_profiles()}


@app.get("/api/profiles/{profile_id}")
def api_get_profile(profile_id: str) -> Dict[str, Any]:
    bundle = get_profile_bundle(profile_id)
    if not bundle:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")
    bundle["chat_history_workbench"] = get_chat_history(profile_id, "workbench")
    bundle["chat_history_chat"] = get_chat_history(profile_id, "chat")
    return bundle


@app.post("/api/profiles")
def api_create_or_update_profile(req: CreateProfileRequest) -> Dict[str, Any]:
    pid = req.profile_id or f"prf_{uuid.uuid4().hex[:8]}"
    bundle = compute_full_profile_readings(pid, req.profile_input)
    save_profile_bundle(pid, req.role_tag, bundle)
    return bundle


@app.post("/api/profiles/{profile_id}/enrich")
def api_enrich_profile(profile_id: str, req: IngestEnrichmentRequest) -> Dict[str, Any]:
    bundle = get_profile_bundle(profile_id)
    if not bundle:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

    raw_inp = bundle["profile_input"]
    if req.palmistry_data is not None:
        merged_palm = dict(raw_inp.get("palmistry_data") or {})
        merged_palm.update(req.palmistry_data)
        raw_inp["palmistry_data"] = merged_palm

    if req.vastu_data is not None:
        merged_vastu = dict(raw_inp.get("vastu_data") or {})
        merged_vastu.update(req.vastu_data)
        raw_inp["vastu_data"] = merged_vastu

    if req.oracle_data is not None:
        merged_oracle = dict(raw_inp.get("oracle_data") or {})
        merged_oracle.update(req.oracle_data)
        raw_inp["oracle_data"] = merged_oracle

    if req.custom_note is not None:
        notes: List[Dict[str, Any]] = list(raw_inp.get("custom_notes") or [])
        notes.append(req.custom_note)
        raw_inp["custom_notes"] = notes

    new_inp = ProfileInput(**raw_inp)
    updated_bundle = compute_full_profile_readings(profile_id, new_inp)
    save_profile_bundle(profile_id, bundle.get("role_tag", "Personal Vault"), updated_bundle)
    return updated_bundle


@app.post("/api/chat/synthesize")
async def api_chat_synthesize(req: ChatSynthesisRequest) -> Dict[str, Any]:
    bundle = get_profile_bundle(req.profile_id)
    if not bundle:
        raise HTTPException(status_code=404, detail=f"Profile {req.profile_id} not found")

    user_msg_id = f"msg_{uuid.uuid4().hex[:8]}"
    append_chat_message(
        msg_id=user_msg_id,
        profile_id=req.profile_id,
        surface=req.surface,
        role="user",
        content=req.query,
    )

    synth_res = await run_chat_synthesis(
        profile_bundle=bundle,
        user_query=req.query,
        include_audit_section=req.include_audit_section,
        preferred_route=req.preferred_route,
    )

    assistant_msg_id = f"msg_{uuid.uuid4().hex[:8]}"
    append_chat_message(
        msg_id=assistant_msg_id,
        profile_id=req.profile_id,
        surface=req.surface,
        role="assistant",
        content=synth_res["synthesis_markdown"],
        metadata={
            "served_by": synth_res["served_by"],
            "model_used": synth_res["model_used"],
            "verified_cost_usd": synth_res["verified_cost_usd"],
            "latency_ms": synth_res["latency_ms"],
        },
    )

    return {
        "message_id": assistant_msg_id,
        "profile_id": req.profile_id,
        "query": req.query,
        "synthesis_markdown": synth_res["synthesis_markdown"],
        "cross_validation_audit": bundle["cross_validation_audit"],
        "telemetry": {
            "served_by": synth_res["served_by"],
            "model_used": synth_res["model_used"],
            "verified_cost_usd": synth_res["verified_cost_usd"],
            "latency_ms": synth_res["latency_ms"],
        },
    }


# Serve Dual-Mode Web Frontend Routes
@app.get("/")
def root_redirect():
    return RedirectResponse(url="/workbench")


@app.get("/workbench")
def serve_workbench():
    return FileResponse(os.path.join(FRONTEND_DIR, "workbench.html"))


@app.get("/chat")
def serve_chat():
    return FileResponse(os.path.join(FRONTEND_DIR, "chat.html"))


if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

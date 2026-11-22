"""AstroPalm FastAPI server."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.chart import build_chart, search_places
from app.guide import ask_guide
from app.llm import ENV_PATH, get_api_key
from app.palm import analyze_palm_photo, build_palm_from_questions

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="AstroPalm", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class ApiKeyRequest(BaseModel):
    api_key: str


class ChartRequest(BaseModel):
    name: str = ""
    system: str = Field(pattern="^(vedic|western)$")
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: Optional[str] = Field(default=None, pattern=r"^(\d{2}:\d{2})?$")
    lat: float
    lon: float
    tz: str
    place_name: str = ""


class PalmQuestionsRequest(BaseModel):
    hand_side: str = "right"
    hand_role: str = "dominant"
    palm_shape: str = "square"
    finger_length: str = "medium"
    life_line: str = "clear_deep"
    head_line: str = "sloping"
    heart_line: str = "curved_jupiter"
    fate_line: str = "present_steady"
    prominent_mounts: list[str] = Field(default_factory=list)
    notable_marks: list[str] = Field(default_factory=list)


class GuideRequest(BaseModel):
    chart: dict
    palm: dict
    situation: str
    message: str
    previous_interaction_id: Optional[str] = None
    history: list[dict] = Field(default_factory=list)


@app.get("/")
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/status")
def status():
    return {"gemini_configured": bool(get_api_key())}


@app.post("/api/config/key")
def save_api_key(req: ApiKeyRequest):
    key = (req.api_key or "").strip()
    if len(key) < 10 or "\n" in key or "\r" in key:
        raise HTTPException(status_code=400, detail="Please enter a valid Gemini API key.")
    lines = []
    if ENV_PATH.exists():
        lines = [l for l in ENV_PATH.read_text().splitlines() if not l.startswith("GEMINI_API_KEY=")]
    lines.append(f"GEMINI_API_KEY={key}")
    ENV_PATH.write_text("\n".join(lines) + "\n")
    os.chmod(ENV_PATH, 0o600)
    os.environ["GEMINI_API_KEY"] = key
    return {"ok": True, "gemini_configured": True}


@app.get("/api/places")
def places(q: str):
    q = (q or "").strip()
    if len(q) < 2:
        return {"places": []}
    try:
        return {"places": search_places(q)}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Place lookup failed: {exc}")


@app.post("/api/chart")
def create_chart(req: ChartRequest):
    try:
        t = req.time.strip() if req.time else None
        chart = build_chart(req.system, req.date, t or None, req.lat, req.lon, req.tz)
        chart["person_name"] = req.name.strip() or "Seeker"
        chart["birth"]["place"] = req.place_name or f"{req.lat}, {req.lon}"
        return {"ok": True, "chart": chart}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not compute chart: {exc}")


@app.post("/api/palm/photo")
async def palm_photo(
    file: UploadFile = File(...),
    hand_role: str = Form("dominant"),
    hand_side: str = Form("right"),
    user_note: str = Form(""),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file (JPEG, PNG, or WebP).")
    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image is too large (max 10 MB).")
    if len(data) < 500:
        raise HTTPException(status_code=400, detail="Image file appears empty or corrupted.")
    try:
        return await run_in_threadpool(
            analyze_palm_photo,
            image_bytes=data,
            mime_type=file.content_type,
            hand_role=hand_role,
            hand_side=hand_side,
            user_note=user_note,
        )
    except Exception as exc:
        return {
            "ok": False,
            "error": "api_error",
            "message": f"Palm photo analysis failed: {exc}",
        }


@app.post("/api/palm/questions")
def palm_questions(req: PalmQuestionsRequest):
    return build_palm_from_questions(req.model_dump())


@app.post("/api/guide")
def guide(req: GuideRequest):
    if not req.situation.strip() or not req.message.strip():
        raise HTTPException(status_code=400, detail="Please describe your situation or question.")
    try:
        return ask_guide(
            chart=req.chart,
            palm=req.palm,
            situation=req.situation,
            message=req.message,
            previous_interaction_id=req.previous_interaction_id,
            history=req.history,
        )
    except Exception as exc:
        return {
            "ok": False,
            "error": "api_error",
            "message": f"Guidance call failed: {exc}",
        }

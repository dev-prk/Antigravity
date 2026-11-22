"""Palm reading via Gemini vision (photo) with guided-questions fallback."""
from __future__ import annotations

import base64
import os
from typing import Literal, Optional

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

MODEL = "gemini-4-hydrogen"


class PalmProfile(BaseModel):
    is_clear_palm: bool = Field(
        description="True only if the image clearly shows an open human palm with readable creases/lines."
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        description="If is_clear_palm is False, short plain reason (e.g., 'Not a palm photo', 'Too blurry or dark to see main lines', 'Fingers/palm closed or cropped').",
    )
    hand_side: str = Field(
        default="unknown",
        description="Left or right palm, plus dominant/non-dominant if provided.",
    )
    hand_element: str = Field(
        default="unknown",
        description="Classic chirognomy shape: Earth (square palm, short fingers), Air (square palm, long fingers), Fire (long palm, short fingers), or Water (long palm, long fingers).",
    )
    life_line: str = Field(
        default="",
        description="Observed curve, depth, continuity, or breaks/branches; say 'not clearly visible' if faint.",
    )
    head_line: str = Field(
        default="",
        description="Observed length, straight vs sloping toward Moon mount, joined or separated from life line, forks/breaks.",
    )
    heart_line: str = Field(
        default="",
        description="Observed curve, ending area (Jupiter, Saturn, or between), chains/depth if visible.",
    )
    fate_line: str = Field(
        default="",
        description="Presence, starting zone, continuity, breaks or shifts, or 'absent / not clearly visible'.",
    )
    prominent_mounts: list[str] = Field(
        default_factory=list,
        description="Clearly developed mounts (e.g., Venus, Jupiter, Saturn, Sun/Apollo, Mercury, Moon, Mars).",
    )
    notable_marks: list[str] = Field(
        default_factory=list,
        description="Only marks genuinely visible (islands, crosses, forks, travel/stress lines, Sun line). Empty if none clear.",
    )
    confidence: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="Confidence based on image lighting, focus, and crease clarity.",
    )


PALM_SYSTEM_INSTRUCTION = (
    "You are a disciplined palmistry analyst (chirognomy + chiromancy). "
    "Inspect the uploaded image strictly and honestly:\n"
    "1. First decide `is_clear_palm`: return False if the image is NOT an open human palm "
    "(e.g., face, object, back of hand, fist, screenshot, text, landscape) OR if it is too blurry, "
    "overexposed, dark, or cropped to reliably distinguish the Life, Head, and Heart lines.\n"
    "2. If `is_clear_palm` is False, set `rejection_reason` plainly and leave line fields brief or empty.\n"
    "3. If `is_clear_palm` is True, describe ONLY features you can actually see in the photo. "
    "Never invent rare marks (crosses, stars, mystic crosses, deep fate lines) when resolution or lighting "
    "does not support them—write 'not clearly visible' when uncertain."
)


def _get_api_key() -> str | None:
    load_dotenv(override=True)
    key = (os.getenv("GEMINI_API_KEY") or "").strip()
    return key or None


def analyze_palm_photo(
    image_bytes: bytes,
    mime_type: str,
    hand_role: str = "dominant",
    hand_side: str = "right",
    user_note: str = "",
) -> dict:
    """Read an uploaded palm photo using Gemini vision with structured JSON output."""
    api_key = _get_api_key()
    if not api_key:
        return {
            "ok": False,
            "error": "missing_api_key",
            "message": "GEMINI_API_KEY is not set in .env yet. Add your free Google AI Studio key to .env (or use the Guided Questions tab right now without an API key).",
        }

    client = genai.Client(api_key=api_key)
    prompt = (
        f"User states this is their {hand_role} hand ({hand_side} palm)."
        + (f" User note: {user_note}" if user_note.strip() else "")
        + "\nEvaluate photo clarity first, then extract only clearly visible palm features into the JSON schema."
    )

    interaction = client.interactions.create(
        model=MODEL,
        system_instruction=PALM_SYSTEM_INSTRUCTION,
        input=[
            {"type": "text", "text": prompt},
            {
                "type": "image",
                "data": base64.b64encode(image_bytes).decode("utf-8"),
                "mime_type": mime_type,
            },
        ],
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": PalmProfile.model_json_schema(),
        },
    )

    parsed = PalmProfile.model_validate_json(interaction.output_text)
    data = parsed.model_dump()
    if not parsed.is_clear_palm:
        return {
            "ok": False,
            "error": "unclear_or_invalid_palm",
            "message": parsed.rejection_reason or "Image does not show a clear, readable open palm.",
            "profile": data,
        }

    data["source"] = "photo"
    return {"ok": True, "profile": data}


def build_palm_from_questions(answers: dict) -> dict:
    """Build a structured PalmProfile from guided user answers (no photo / no API needed)."""
    hand_side = answers.get("hand_side", "right")
    hand_role = answers.get("hand_role", "dominant")
    palm_shape = answers.get("palm_shape", "square")
    finger_len = answers.get("finger_length", "medium")

    if palm_shape == "square":
        element = "Air (square palm, long fingers — analytical, restless mind)" if finger_len == "long" else "Earth (square palm, shorter fingers — practical, grounded, steady)"
    else:
        element = "Water (long palm, long fingers — sensitive, intuitive, emotionally deep)" if finger_len == "long" else "Fire (long palm, shorter fingers — energetic, action-driven, impatient)"

    life = answers.get("life_line", "clear_deep")
    life_map = {
        "clear_deep": "Deep, continuous sweep around the Venus mount — steady baseline vitality and resilience.",
        "wide_curve": "Wide arc reaching toward center of palm — outgoing energy, appetite for movement/change.",
        "close_to_thumb": "Runs close to thumb — cautious energy pacing, prefers security and familiar routines.",
        "broken_or_chained": "Shows breaks, chains, or overlaps — periods of physical/life-structure disruption or transition.",
        "faint_or_short": "Faint or short/branching — sensitive energy reserves; needs pacing and recovery during stress.",
    }

    head = answers.get("head_line", "sloping")
    head_map = {
        "straight": "Straight and firm across palm — practical, factual, structured decision-making.",
        "sloping": "Slopes down toward the Moon mount — imaginative, reflective, prone to overthinking under pressure.",
        "joined_life": "Joined closely to Life line at start — cautious, deliberate, considers family/safety before acting.",
        "separated_life": "Starts separated from Life line — independent thinker, acts quickly on own judgment.",
        "forked_or_broken": "Forked (writer's fork) or broken/islanded — dual perspectives or mental strain/pivot point.",
    }

    heart = answers.get("heart_line", "curved_jupiter")
    heart_map = {
        "curved_jupiter": "Curved upward ending toward Jupiter (index mount) — warm, idealistic, seeks meaningful commitment.",
        "ends_saturn": "Ends under Saturn (middle finger) — guarded or pragmatic in love, loyal through actions over words.",
        "ends_between": "Curved, ending between index and middle fingers — balanced empathy and boundaries.",
        "straight_flat": "Relatively straight/short — reserved emotionally, processes feelings privately.",
        "chained_or_broken": "Chained, feathered, or broken — emotional sensitivity, past heartache, or relationship stress.",
    }

    fate = answers.get("fate_line", "present_steady")
    fate_map = {
        "present_steady": "Clear, steady vertical Fate line — strong sense of duty, structured career/life path.",
        "starts_late_or_moon": "Starts from Moon mount or mid-palm — self-made path shaped by external changes or mid-life pivot.",
        "broken_or_shifting": "Broken, overlapping, or shifting direction — major career/direction changes and reinvention phases.",
        "faint_or_absent": "Faint or absent — self-directed, resists rigid roles; builds path step by step rather than one fixed track.",
    }

    mounts = answers.get("prominent_mounts") or []
    if isinstance(mounts, str):
        mounts = [m.strip() for m in mounts.split(",") if m.strip()]

    marks = answers.get("notable_marks") or []
    if isinstance(marks, str):
        marks = [m.strip() for m in marks.split(",") if m.strip()]

    profile = {
        "is_clear_palm": True,
        "rejection_reason": None,
        "hand_side": f"{hand_side} ({hand_role} hand)",
        "hand_element": element,
        "life_line": life_map.get(life, str(life)),
        "head_line": head_map.get(head, str(head)),
        "heart_line": heart_map.get(heart, str(heart)),
        "fate_line": fate_map.get(fate, str(fate)),
        "prominent_mounts": mounts,
        "notable_marks": marks,
        "confidence": "medium",
        "source": "guided_questions",
    }
    return {"ok": True, "profile": profile}

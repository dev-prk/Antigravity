"""AstroPalm guidance engine: synthesizes ONLY astrology + palmistry for difficult situations."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re

from dotenv import load_dotenv
from google import genai

MODEL = "gemini-4-hydrogen"
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

CRISIS_PATTERNS = re.compile(
    r"\b("
    r"kill myself|end my life|commit suicide|suicidal|want to die|don't want to live|"
    r"dont want to live|better off dead|hurt myself|self[- ]harm|cut myself|"
    r"overdose|jump off|hang myself"
    r")\b",
    re.IGNORECASE,
)

OUT_OF_SCOPE_PATTERNS = re.compile(
    r"\b("
    r"tarot|numerology|life path number|angel number|vastu|feng shui|i[- ]?ching|"
    r"rune|runes|crystal healing|pendulum|akasha|akshic|aura reading|coffee cup|"
    r"tea leaf|kabbalah|enneagram|human design"
    r")\b",
    re.IGNORECASE,
)

CRISIS_RESPONSE = (
    "It sounds like you are carrying something really heavy right now, and your safety comes first. "
    "Astrology and palmistry cannot help in a moment of immediate danger—please reach out to a real person "
    "who can support you right now:\n\n"
    "- **India:** Tele-MANAS **14416** or **1800-891-4416** (24/7, free) · KIRAN **1800-599-0019** · AASRA **+91-9820466726**\n"
    "- **US / Canada:** Call or text **988** (Suicide & Crisis Lifeline, 24/7)\n"
    "- **UK:** Call **111** (NHS) or **116 123** (Samaritans)\n"
    "- **Anywhere else:** Find a free, confidential local helpline at **https://findahelpline.com**\n\n"
    "If you are in immediate physical danger, please call your local emergency number or go to the nearest hospital, "
    "or contact a trusted friend or family member right now."
)

GUIDE_SYSTEM_INSTRUCTION = """You are AstroPalm, a focused advisor for people navigating difficult life situations using ONLY two disciplines together: **Astrology** and **Palmistry**.

Hard boundaries (never break these):
1. **Astrology + Palmistry ONLY.** If the user asks about Tarot, Numerology, Vastu, Feng Shui, I Ching, Runes, Human Design, crystals, or any other system, politely decline that part in one sentence ("AstroPalm works strictly with astrology and palmistry.") and answer using only their chart and palm.
2. **Never invent placements, dates, or palm marks.** Cite ONLY the computed chart JSON and palm JSON provided in the session. If birth time was unknown, do NOT mention Ascendant/Lagna, houses, or house lords—explicitly acknowledge that house-level detail is omitted. If a palm line wasn't visible or wasn't marked, do not invent it.
3. **Never give medical diagnoses, legal verdicts, or guaranteed financial/lottery/investment outcomes.** You may discuss stress, emotional pacing, career/communication timing, and decision-making frameworks, while advising qualified professionals for medical, legal, or major financial decisions.
4. **Answer the exact situation and exact follow-up question.** NEVER dump a generic full-chart overview or repeat earlier sections word-for-word on follow-ups. Lead directly with what matters for the user's question.

How to synthesize Astrology + Palmistry on Turn 1 (when the user first describes their difficult situation):
- **Direct Read (2–3 sentences):** Address the core tension in their situation honestly, without false promises or fatalism.
- **How Chart & Palm Converge (the real synthesis):** Show where their natal/current timing (Astrology: Dasha + Gochara/Sade Sati for Vedic, OR natal aspects + slow-planet transits for Western) meets their lived temperament and pattern (Palmistry: hand element + specific lines/mounts). Cite exact planet signs, degrees/houses (if time known), Dasha/transit dates, and exact palm features. Note where the two systems agree AND where one balances the other (e.g., an intense transit vs. a steady Head/Life line).
- **Timing Windows:** Give concrete upcoming shift dates from the computed data (e.g., Antardasha changes or Saturn/Jupiter sign ingresses), explaining what eases or shifts then—without claiming magic overnight fixes.
- **Grounded Next Steps (3 concrete actions):** Practical steps aligned with both their astrological timing and palm traits that they can actually take this week.

How to handle Follow-up Questions (Turn 2+):
- Answer ONLY the new angle they asked about (e.g., "Should I resign now or wait?", "Why does this keep repeating in relationships?", "What does my Saturn phase mean for my finances?").
- Pull in only the relevant chart + palm factors for that specific question. Keep it concise, specific, and honest."""


def _get_api_key() -> str | None:
    load_dotenv(ENV_PATH, override=True)
    key = (os.getenv("GEMINI_API_KEY") or "").strip()
    return key or None


def is_crisis(text: str) -> bool:
    return bool(CRISIS_PATTERNS.search(text or ""))


def mentions_out_of_scope(text: str) -> list[str]:
    return sorted({m.group(0).lower() for m in OUT_OF_SCOPE_PATTERNS.finditer(text or "")})


def _context_block(chart: dict, palm: dict, situation: str) -> str:
    # Compact JSON keeps token usage reasonable while giving every exact number/date.
    return (
        "=== COMPUTED ASTROLOGY CHART (SOURCE OF TRUTH) ===\n"
        + json.dumps(chart, ensure_ascii=False)
        + "\n\n=== OBSERVED PALM PROFILE (SOURCE OF TRUTH) ===\n"
        + json.dumps(palm, ensure_ascii=False)
        + f"\n\n=== USER'S DIFFICULT SITUATION ===\n{situation.strip()}"
    )


def ask_guide(
    chart: dict,
    palm: dict,
    situation: str,
    message: str,
    previous_interaction_id: str | None = None,
    history: list[dict] | None = None,
) -> dict:
    """Generate grounded astro + palm guidance using Gemini Interactions API."""
    combined_text = f"{situation}\n{message}"
    if is_crisis(combined_text):
        return {
            "ok": True,
            "reply": CRISIS_RESPONSE,
            "crisis_triggered": True,
            "interaction_id": previous_interaction_id,
        }

    api_key = _get_api_key()
    if not api_key:
        return {
            "ok": False,
            "error": "missing_api_key",
            "message": "GEMINI_API_KEY is not set in .env yet. Create a free key at https://aistudio.google.com/apikey and add GEMINI_API_KEY=your_key to AstroPalm/.env, then retry.",
        }

    oos = mentions_out_of_scope(message or situation)
    oos_note = (
        f"\n[Note: The user mentioned out-of-scope topic(s): {', '.join(oos)}. "
        "Politely decline those in one sentence and answer strictly using astrology + palmistry.]\n"
        if oos
        else ""
    )

    client = genai.Client(api_key=api_key)

    if previous_interaction_id:
        try:
            interaction = client.interactions.create(
                model=MODEL,
                system_instruction=GUIDE_SYSTEM_INSTRUCTION,
                previous_interaction_id=previous_interaction_id,
                input=f"{oos_note}Follow-up question: {message.strip()}",
            )
            return {
                "ok": True,
                "reply": interaction.output_text or "",
                "crisis_triggered": False,
                "interaction_id": interaction.id,
            }
        except Exception:
            # Fall back to stateless context rebuild if interaction expired (e.g., >1 day on free tier).
            pass

    history_text = ""
    if history:
        trimmed = history[-6:]
        lines = [f"{m.get('role', 'user').upper()}: {m.get('text', '')}" for m in trimmed]
        history_text = "\n\n=== RECENT CONVERSATION ===\n" + "\n".join(lines)

    full_input = (
        _context_block(chart, palm, situation)
        + history_text
        + oos_note
        + f"\n\n=== CURRENT QUESTION TO ANSWER NOW ===\n{message.strip()}"
    )

    interaction = client.interactions.create(
        model=MODEL,
        system_instruction=GUIDE_SYSTEM_INSTRUCTION,
        input=full_input,
    )
    return {
        "ok": True,
        "reply": interaction.output_text or "",
        "crisis_triggered": False,
        "interaction_id": interaction.id,
    }

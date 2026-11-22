# AstroPalm — Progress

**Goal:** A web app that guides people through difficult situations using ONLY astrology + palmistry, read together.

## Acceptance criteria
1. Birth details: name, date, time (or "unknown time"), **place of birth** searched and picked from real places → exact lat/lon + historical timezone/DST (LMT before standard time).
2. User picks **Vedic** (Lahiri, whole-sign, Nakshatra, Vimshottari Dasha, Sade Sati) or **Western** (tropical, Placidus, transits to natal). Chart matches known reference charts.
3. Palm: **photo** read by Gemini vision (rejects non-palm / blurry photos), with **guided questions** as a fallback.
4. Guidance chat answers the user's *specific* situation, citing real chart + palm factors, timing windows, practical steps. Follow-ups get new, specific answers (no repeated template).
5. Scope: astro + palmistry only; politely declines tarot/numerology/vastu etc. Crisis messages get helpline info. No medical/legal/financial certainty.
6. Runs locally with one command (`./run.sh`); API key lives in `.env` (never in chat).

## Done
- Python 3.12 venv (`.venv`, via uv) with google-genai 3.6.1, pyswisseph, timezonefinder, geopy, fastapi.

## Next
- Build chart engine, palm reader, guide, UI → verify each criterion.

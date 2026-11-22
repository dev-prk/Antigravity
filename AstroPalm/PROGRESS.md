# AstroPalm — Progress

**Goal:** A web app that guides people through difficult situations using ONLY astrology + palmistry, read together.

## Acceptance criteria
1. Birth details: name, date, time (or "unknown time"), **place of birth** searched and picked from real places → exact lat/lon + historical timezone/DST (LMT before standard time). — **DONE & VERIFIED**
2. User picks **Vedic** (Lahiri, whole-sign, Nakshatra, Vimshottari Dasha, Sade Sati) or **Western** (tropical, Placidus, transits to natal). Chart matches known reference charts. — **DONE & VERIFIED**
3. Palm: **photo** read by Gemini vision (rejects non-palm / blurry photos), with **guided questions** as a fallback. — **BUILT (photo path needs GEMINI_API_KEY in `.env` to verify live)**
4. Guidance chat answers the user's *specific* situation, citing real chart + palm factors, timing windows, practical steps. Follow-ups get new, specific answers (no repeated template). — **BUILT (needs GEMINI_API_KEY in `.env` to verify live)**
5. Scope: astro + palmistry only; politely declines tarot/numerology/vastu etc. Crisis messages get helpline info. No medical/legal/financial certainty. — **BUILT (crisis helpline verified; out-of-scope prompt rule needs live key)**
6. Runs locally with one command (`./run.sh`); API key lives in `.env` (never in chat). — **DONE & VERIFIED**

## Done
- Python 3.12 venv (`.venv`, via uv) with google-genai 3.6.1, pyswisseph, timezonefinder, geopy, fastapi.
- `app/chart.py`, `app/palm.py`, `app/guide.py`, `app/main.py`, `app/static/index.html`, `run.sh`, `.env.example`, `.gitignore`.
- Verified reference charts (Obama, Gandhi, Einstein, unknown birth time), place lookup, guided palm questions, crisis detection, missing-key handling.

## Next
- Visual & interactive browser check on `http://127.0.0.1:8780`.
- User adds free `GEMINI_API_KEY` to `AstroPalm/.env` for live palm photo + AI guidance testing.

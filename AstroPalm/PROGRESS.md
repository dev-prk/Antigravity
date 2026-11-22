# AstroPalm — Progress

**Goal:** A web app that guides people through difficult situations using ONLY astrology + palmistry, read together.

## Acceptance criteria
1. Birth details: name, date, time (or "unknown time"), **place of birth** searched and picked from real places → exact lat/lon + historical timezone/DST (LMT before standard time). — **DONE & VERIFIED**
2. User picks **Vedic** (Lahiri, whole-sign, Nakshatra, Vimshottari Dasha, Sade Sati) or **Western** (tropical, Placidus, transits to natal). Chart matches known reference charts. — **DONE & VERIFIED**
3. Palm: **photo** read by Gemini vision (rejects non-palm / blurry photos), with **guided questions** as a fallback. — **DONE & VERIFIED (non-palm photo rejection + guided questions verified)**
4. Guidance chat answers the user's *specific* situation, citing real chart + palm factors, timing windows, practical steps. Follow-ups get new, specific answers (no repeated template). — **DONE & VERIFIED (live Gemini Turn 1 + Turn 2 verified)**
5. Scope: astro + palmistry only; politely declines tarot/numerology/vastu etc. Crisis messages get helpline info. No medical/legal/financial certainty. — **DONE & VERIFIED (crisis helpline + live tarot/numerology refusal verified)**
6. Runs locally with one command (`./run.sh`); API key lives in `.env` (never in chat). — **DONE & VERIFIED**

## Done
- Fixed event-loop blocking in `app/main.py` (`run_in_threadpool` on `/api/palm/photo`).
- Added `app/llm.py` with `HttpRetryOptions(attempts=1)`, fast timeout, and cooldown-based failover (`gemini-4-hydrogen` → `gemini-3.5-flash-lite` → `gemini-3.1-flash-lite`).
- Verified live server running at `http://127.0.0.1:8780`.

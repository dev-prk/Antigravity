# AstroFluence — Cross-Disciplinary Esoteric Synthesis Engine

AstroFluence is a dual-interface **Cross-Disciplinary Esoteric & Spatial Synthesis Platform** built under `/ai-os` zero-cost governance. One shared **Synthesis Engine Backend** (`FastAPI` + `pyswisseph` Swiss Ephemeris + Deterministic Claim Graph + AI-OS Zero-Cost Model Router) powers two experiences:

1. **Personal Workbench (`/workbench`) — "The Chat You Use"**
   - **Multi-Profile Vault**: Switch between your own profile, family members, test cases, or clients.
   - **6 Core Discipline Pillars + Universal Custom Note Importer**:
     1. **Vedic & Western Astrology**: Exact Swiss Ephemeris Tropical & Sidereal (Lahiri) placements, Nakshatras, and Vimshottari Mahadasha timeline.
     2. **Pythagorean & Chaldean Numerology**: Life Path, Expression/Destiny, Soul Urge, Personality, Chaldean Compound Name number, Pinnacles, and Personal Year.
     3. **Locational Astrology (Astrocartography)**: Planetary Midheaven (MC), IC, Ascendant (ASC), and Descendant (DSC) longitudinal corridors mapped to world hubs.
     4. **Vastu Shastra & Classical Feng Shui**: 8-Direction elemental prana matrix analyzing main entrance, workspace quadrant, desk facing direction, and biomagnetic sleep orientation.
     5. **Palmistry (Chiromancy & Samudrika Shastra)**: Head Line (including Writer's Fork to Mount of Moon), Fate Line, Heart Line, Quadrangle Mystic Cross, and dominant Mount topography.
     6. **Symbolic Oracles & Custom Importer**: 78-Card Tarot & 64-Hexagram I Ching casting, plus a universal semantic parser for Graphology, Physiognomy, Gematria, Chronomancy, Runes, and raw notes.
   - **Live Cross-Validation & Recursive Triangulation Matrix**: Visual side-by-side audit cards showing **Verified Core Patterns** (confirmed across 2+ independent systems), **Constructive Tensions** (how to balance cautious physical traits against bold astrological transits), and **Recursive Deepening Triggers** (Mechanism + Timing + Environment).

2. **Public Website Chatbot (`/chat`) — "The Website Chatbot Version"**
   - **2-Second Progressive Onboarding**: Visitors enter only their Name, Birth Date, Birth Time, and Birth City to immediately compute their Natal/Vedic Chart, Numerology, and Astrocartography baseline.
   - **In-Chat Progressive Enrichment Drawers**: One-click drawers inside the chat let visitors add their Palmistry lines, Room Vastu directions, or a Tarot/I Ching cast on the fly.
   - **Unified Theme-Organized Narrative**: Delivers one cohesive synthesis organized strictly by Life Themes (never by discipline list).

---

## Quick Start

```bash
chmod +x start.sh
./start.sh
```

Then open:
- **Personal Workbench**: `http://127.0.0.1:8765/workbench`
- **Public Website Chatbot**: `http://127.0.0.1:8765/chat`
- **Interactive API Docs**: `http://127.0.0.1:8765/docs`

## Running Verification Tests

```bash
PYTHONPATH=. .venv/bin/pytest -v tests/test_astrofluence.py
```

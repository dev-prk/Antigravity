# AstroFluence Engineering & Esoteric Accuracy Rules

These rules govern all work inside `~/Documents/Antigravity/AstroFluence/`:

## 1. Mandatory Birthplace Geodesy & Historical Timezone/DST Resolution
- **Never Hardcode Timezone Offsets or Coordinates**: Place of birth is a foundational mathematical input. Never hardcode `timezone_offset = 5.5` or default coordinates when a user enters or changes a city.
- **Exact IANA Timezone & Historical DST**: Every birthplace must resolve its exact `(latitude, longitude)` and IANA timezone (`timezonefinder` + `zoneinfo.ZoneInfo`) and compute the historical UTC offset and Daylight Saving Time (DST) status on the exact `(birth_date, birth_time)` before calling Swiss Ephemeris (`swe.julday` / `swe.houses`).
- **Relocation Awareness**: Always distinguish between **Place of Birth** (Natal Lagna, D9, D10, Janma Nakshatra) and **Current City of Residence** (Relocated Ascendant/MC and Astrocartography angular line orbs).

## 2. Live Query-Driven Synthesis (Zero Static Template Repetition)
- **Answer the Exact Question Asked**: Follow-up questions in `/chat` and `/workbench` must NEVER dump or repeat the static 6-section full-profile overview.
- **Compute Live Temporal & Ephemeris Data for Time-Bound Questions**: When a user asks about future challenges, risks, or multi-year windows (e.g., "biggest critical challenges in the next 5 years" or "next 6 months priority"), dynamically compute the target timeframe's Sidereal planetary transits (Saturn Sade Sati/Ashtama/Kantaka, Jupiter, Rahu-Ketu nodal crossings), Vimshottari Mahadasha-Antardasha transitions, and Numerology Personal Year/Month progressions, and return a response structured specifically around that question.

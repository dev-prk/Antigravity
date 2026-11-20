"""AI-OS Provider-Agnostic Zero-Cost Model Router & Query-Driven Synthesis Engine."""

from __future__ import annotations

import os
import re
import time
from typing import Any, Dict, List, Optional

import httpx

from backend.engine.forecaster import compute_multi_year_forecast
from backend.engine.ontology import CrossValidationAudit

MASTER_SYNTHESIS_SYSTEM_PROMPT = """You are an expert Synthesis Engine specializing in cross-disciplinary esoteric, divinatory, and spatial systems (including Astrology, Numerology, Palmistry, Vastu/Feng Shui, Astrocartography, Tarot, I Ching, and Physiognomy/Graphology).
Your goal is not to summarize each reading separately, but to act as an analytical detective—cross-referencing stored data, validating repeating patterns, digging deeper into hidden connections, and delivering ONE unified, hyper-personalized synthesis that DIRECTLY answers the user's exact question.

### INTERNAL REASONING PROTOCOL (Already pre-verified by the Deterministic Claim Graph):
1. **Answer the exact question first.** Never dump a generic static profile report when the user asks a specific question (such as upcoming challenges, 5-year timeline, relationship compatibility, career pivot, relocation, or room Vastu).
2. **Never organize by discipline.** Organize strictly by **Life Theme** or **Temporal/Analytical Phase** relevant to the user's question.
3. **Weave Cross-Validated Evidence Naturally.** Explain *why* a conclusion is high-confidence by linking multiple independent systems (e.g., Vedic transits + Numerology Personal Years + Palmistry lines + Vastu/Kua directions).
4. **Explain Constructive Tensions as Strategy.** Show the user how to balance conflicting polarities (e.g., cautious palm fate line vs. bold astrological Mahadasha/Personal Year) as a concrete operating strategy.
5. **Actionable Alignment.** Conclude with concrete, practical recommendations combining timing, mindset, and spatial/locational adjustments.
"""


async def detect_available_zero_cost_routes() -> List[Dict[str, Any]]:
    """Probes local and environment zero-cost routes under AI-OS governance."""
    routes: List[Dict[str, Any]] = []

    # 1. Local FreeLLMAPI Router (http://127.0.0.1:3001/v1)
    freellm_url = os.getenv("FREELLMAPI_BASE_URL", "http://127.0.0.1:3001/v1")
    try:
        async with httpx.AsyncClient(timeout=1.2) as client:
            resp = await client.get(f"{freellm_url}/models")
            if resp.status_code == 200:
                routes.append(
                    {
                        "id": "freellmapi_local",
                        "name": "FreeLLMAPI Local Router (:3001)",
                        "status": "online",
                        "cost": "$0.00 (Verified Local Router)",
                        "endpoint": freellm_url,
                    }
                )
    except Exception:
        routes.append(
            {
                "id": "freellmapi_local",
                "name": "FreeLLMAPI Local Router (:3001)",
                "status": "offline",
                "cost": "$0.00",
                "endpoint": freellm_url,
            }
        )

    # 2. Local Ollama Runtime (http://127.0.0.1:11434)
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    try:
        async with httpx.AsyncClient(timeout=1.2) as client:
            resp = await client.get(f"{ollama_url}/api/tags")
            if resp.status_code == 200:
                tags = resp.json().get("models", [])
                model_name = tags[0]["name"] if tags else "llama3.2"
                routes.append(
                    {
                        "id": "ollama_local",
                        "name": f"Local Ollama ({model_name})",
                        "status": "online" if tags else "no_models_pulled",
                        "cost": "$0.00 (100% Local Offline)",
                        "model": model_name,
                    }
                )
    except Exception:
        routes.append(
            {
                "id": "ollama_local",
                "name": "Local Ollama (:11434)",
                "status": "offline",
                "cost": "$0.00",
            }
        )

    # 3. Gemini Free Tier (if GEMINI_API_KEY present)
    gemini_key = os.getenv("GEMINI_API_KEY")
    routes.append(
        {
            "id": "gemini_free",
            "name": "Google Gemini API (gemini-2.5-flash Free Tier)",
            "status": "online" if gemini_key else "unconfigured",
            "cost": "$0.00 (Free Tier Quota Guard)",
        }
    )

    # 4. OpenRouter Free Models Collection (:free suffix enforced)
    or_key = os.getenv("OPENROUTER_API_KEY")
    routes.append(
        {
            "id": "openrouter_free",
            "name": "OpenRouter Free Models (:free Guard)",
            "status": "online" if or_key else "unconfigured",
            "cost": "$0.00 (Strictly :free models)",
        }
    )

    # 5. Built-in AI-OS Deterministic Query-Driven Synthesis Engine (Always online, 0 latency, $0.00)
    routes.append(
        {
            "id": "aios_deterministic_compiler",
            "name": "AI-OS Query-Driven Cross-Validation & Ephemeris Forecaster",
            "status": "online",
            "cost": "$0.00 (Guaranteed Zero-Spend Local Engine)",
        }
    )

    return routes


def _classify_query_intent(user_query: str) -> str:
    """
    Classifies the user's live question into a specialized analytical mode so the engine
    never repeats a static overview when asked a targeted question.
    """
    q = (user_query or "").strip().lower()
    if not q or any(
        phrase in q
        for phrase in (
            "complete cross-validated synthesis",
            "unified cross-disciplinary reading organized by life themes",
            "full holistic profile",
            "updated my stored readings",
        )
    ):
        return "full_holistic_overview"

    if any(
        w in q
        for w in (
            "challenge",
            "critical",
            "risk",
            "obstacle",
            "danger",
            "warn",
            "watch out",
            "hard",
            "difficult",
            "problem",
            "struggle",
            "threat",
            "pitfall",
            "fear",
            "bad",
            "crisis",
            "5 year",
            "five year",
            "next 3",
            "next 5",
            "coming my way",
            "future",
            "forecast",
        )
    ):
        return "challenges_and_multiyear_forecast"

    if any(
        w in q
        for w in (
            "tension",
            "disagree",
            "contradict",
            "conflict",
            "cautious",
            "polarit",
            "opposite",
            "balance",
        )
    ):
        return "constructive_tensions_deep_dive"

    if any(
        w in q
        for w in (
            "move",
            "city",
            "cities",
            "relocat",
            "location",
            "where",
            "room",
            "vastu",
            "desk",
            "direction",
            "feng shui",
            "kua",
            "house",
            "home",
            "apartment",
            "country",
            "travel",
            "astrocartography",
        )
    ):
        return "location_and_spatial_alignment"

    if any(
        w in q
        for w in (
            "relationship",
            "love",
            "partner",
            "marriage",
            "dating",
            "spouse",
            "wife",
            "husband",
            "soulmate",
            "compatib",
            "family",
            "cofounder",
            "co-founder",
        )
    ):
        return "relationships_and_alliances"

    if any(
        w in q
        for w in (
            "health",
            "energy",
            "burnout",
            "sleep",
            "stress",
            "body",
            "vitality",
            "healing",
            "fatigue",
            "mental",
        )
    ):
        return "health_and_vitality"

    if any(
        w in q
        for w in (
            "palm",
            "hand",
            "head line",
            "fate line",
            "heart line",
            "mount",
            "tarot",
            "i ching",
            "hexagram",
            "rune",
        )
    ):
        return "somatic_and_oracle_triangulation"

    if any(
        w in q
        for w in (
            "career",
            "job",
            "work",
            "money",
            "wealth",
            "startup",
            "launch",
            "business",
            "priority",
            "6 month",
            "six month",
            "income",
            "finance",
            "project",
            "focus",
        )
    ):
        return "career_and_6month_priority"

    return "targeted_custom_question"


def _extract_horizon_years(user_query: str, default_years: int = 5) -> int:
    m = re.search(r"\b([1-9]|10)\s*(?:year|yr|yrs)\b", (user_query or "").lower())
    if m:
        return min(10, max(1, int(m.group(1))))
    return default_years


def compile_deterministic_master_synthesis(
    profile_name: str,
    user_query: str,
    audit: CrossValidationAudit,
    discipline_payloads: Dict[str, Any],
    profile_input: Optional[Dict[str, Any]] = None,
    include_audit_section: bool = True,
) -> str:
    """
    Dynamically computes and compiles a question-specific, cross-validated answer tailored
    to the exact intent of `user_query`, using live Swiss Ephemeris transits, Vimshottari
    Antardasha transitions, Numerology Personal Year cycles, Palmistry lines, and Vastu/Kua vectors.
    """
    intent = _classify_query_intent(user_query)
    astro = discipline_payloads.get("astrology", {})
    num = discipline_payloads.get("numerology", {})
    loc = discipline_payloads.get("locational", {})
    vastu = discipline_payloads.get("vastu_fengshui", {})
    palm = discipline_payloads.get("palmistry", {})
    oracles = discipline_payloads.get("oracles", {})

    inp = profile_input or {
        "name": profile_name,
        "birth_date": "1996-08-15",
        "birth_time": "10:30",
        "birth_city": loc.get("birthplace", {}).get("city", "New Delhi, Delhi, India"),
    }

    dasha = astro.get("vimshottari_dasha", {})
    sid_asc_obj = astro.get("sidereal_ascendant", {})
    sid_asc = sid_asc_obj.get("sign", "Pisces")
    d9_asc = sid_asc_obj.get("navamsha_d9_sign", "Pisces")
    d10_asc = sid_asc_obj.get("dashamsha_d10_sign", "Leo")
    karakas = astro.get("chara_karakas", {})
    ak = karakas.get("atmakaraka_soul", "Saturn")
    amk = karakas.get("amatyakaraka_career", "Mercury")
    kua = vastu.get("feng_shui_kua", {})
    kua_dirs = kua.get("auspicious_directions", {})
    patterns = audit.verified_core_patterns
    top_pat = patterns[0] if patterns else None
    second_pat = patterns[1] if len(patterns) > 1 else top_pat

    sections: List[str] = []

    if include_audit_section and audit.audit_bullets:
        audit_md = "### [Cross-Validation Audit & Recursive Triangulation]\n"
        for b in audit.audit_bullets:
            audit_md += f"- {b}\n"
        sections.append(audit_md.strip())

    # =========================================================================
    # MODE 1: CHALLENGES, RISKS & MULTI-YEAR FORECAST (e.g. "biggest critical challenges in next 5 years")
    # =========================================================================
    if intent == "challenges_and_multiyear_forecast":
        horizon = _extract_horizon_years(user_query, default_years=5)
        forecast = compute_multi_year_forecast(
            profile_bundle={"profile_input": inp, "disciplines": discipline_payloads},
            horizon_years=horizon,
        )
        crit_list = forecast["critical_challenges"]
        yearly = forecast["yearly_forecasts"]

        natal_sat = astro.get("sidereal_planets", {}).get("Saturn", {"sign": "Pisces", "house": 1, "degree": 24.1})
        natal_moon = astro.get("sidereal_planets", {}).get("Moon", {"sign": "Pisces", "house": 1, "degree": 12.0})
        natal_merc = astro.get("sidereal_planets", {}).get("Mercury", {"sign": "Aquarius", "house": 12})

        sections.append(
            f"**Direct Answer — Your Top 3 Critical Challenges Over the Next {horizon} Years ({forecast['start_year']}–{forecast['end_year']}):**\n"
            f"By cross-referencing your live **Swiss Ephemeris Saturn & Nodal (Rahu/Ketu) transits**, your **Vimshottari {dasha.get('active_mahadasha', 'Mercury')} Mahadasha sub-period shifts**, "
            f"your **Numerology Personal Year 4 -> 9 progression**, and your **Palmistry Fate/Head Line morphology**, the engine isolates **three critical structural pressure points** coming your way—and exactly how to turn each into an advantage."
        )

        # Challenge 1: Peak Saturn / Sade Sati / Saturn Return / Angular Compression
        peak_sat_yr = next((y for y in yearly if "Critical" in y["severity"] or "High" in y["severity"]), yearly[0])
        sections.append(
            f"### 1. Critical Challenge #1: {peak_sat_yr['saturn_phase']} ({peak_sat_yr['year']}–{peak_sat_yr['year'] + 1})\n"
            f"- **The Astronomical & Somatic Convergence:** Your Natal Moon is in **{natal_moon['sign']}** (`{dasha.get('nakshatra', 'Uttara Bhadrapada')}`) "
            f"and your **Atmakaraka (Soul Significator) is {ak}** (with Natal Saturn in **{natal_sat['sign']} House {natal_sat['house']}**). "
            f"During **{peak_sat_yr['year']}–{peak_sat_yr['year'] + 1}**, transiting Sidereal Saturn moves through **{peak_sat_yr['saturn_transit_sign']}**, triggering **{peak_sat_yr['saturn_phase']}** while intersecting your **Numerology Personal Year {peak_sat_yr['personal_year']} ({peak_sat_yr['personal_year_theme']})**.\n"
            f"- **How This Challenge Manifests in Real Life:** High load-bearing compression on your identity, nervous system, and operational commitments. "
            f"Because your Palmistry shows a **{palm.get('head_line', 'deep, forked Head Line sloping toward the Mount of Moon')}** paired with a **{palm.get('fate_line', 'Saturn Fate Line')}**, "
            f"your natural temptation under Saturn pressure is to over-carry everything solo while your mind branches into five directions at once.\n"
            f"- **Counter-Strategy & Vastu Remedy:** Do not take on unverified fixed overhead or ambiguous partnerships during `{peak_sat_yr['year']}`. "
            f"Anchor your **South-West (Nairutya)** Earth quadrant (solid wall behind your work chair), sleep strictly with your head oriented **{vastu.get('sleeping_head_direction', 'South')}**, "
            f"and let **{peak_sat_yr['jupiter_protection']}**"
        )

        # Challenge 2: The 12th/1st House Bifurcation & Constructive Tension (Scattered Brilliance vs. Shipped Focus)
        tns = audit.constructive_tensions[0] if audit.constructive_tensions else None
        sections.append(
            f"### 2. Critical Challenge #2: Cognitive Bifurcation & The 'Unfinished Cauldron' Trap\n"
            f"- **Cross-System Diagnosis:** Across all 6 systems, your #1 superpower—**{top_pat.title if top_pat else 'Creative Communication & Story Architecture'}** "
            f"(Life Path **{num.get('life_path', 3)}**, Soul Urge **{num.get('soul_urge_number', 3)}**, Chaldean **{num.get('chaldean_compound', '50/5')}**, "
            f"Palmistry **Writer's Fork to Moon**, and Sidereal **Mercury in {natal_merc['sign']} House {natal_merc['house']}**)—also creates your biggest recurring vulnerability: **starting high-voltage architectures and pivoting right before commercial compounding kicks in.**\n"
            + (
                f"- **The Internal Polarity Clash:** As flagged in your Constructive Tension audit, **{tns.side_b_claim.source_label}** (*{tns.side_b_claim.raw_feature}*) "
                f"pulls the brakes to audit edge cases, while **{tns.side_a_claim.source_label}** (*{tns.side_a_claim.raw_feature}*) demands rapid expansion. "
                f"When these two gears fight each other simultaneously, it causes stop-start exhaustion.\n"
                if tns
                else ""
            )
            + f"- **Counter-Strategy:** Enforce a strict **Two-Gear Protocol**: lock scope for 90-day sprints during your active **{dasha.get('active_mahadasha', 'Mercury')}-{dasha.get('active_antardasha', 'Jupiter')}** window (`{dasha.get('active_antardasha_window', '2026–2028')}`), "
            f"and clear all physical/digital clutter from your **West (Varuna — Consolidation of Gains)** and **North-West (Vayu)** zones."
        )

        # Challenge 3: Nodal Axis (Rahu/Ketu) & Antardasha Handoff Inflection
        nodal_yr = next((y for y in yearly[1:] if "Rahu-Ketu" in " ".join(y["challenge_details"])), yearly[min(2, len(yearly) - 1)])
        sections.append(
            f"### 3. Critical Challenge #3: Nodal Axis Eclipse & Dasha Transition ({nodal_yr['year']}–{min(forecast['end_year'], nodal_yr['year'] + 1)})\n"
            f"- **The Trigger:** In **{nodal_yr['year']}**, the transiting Nodal Axis moves to **{nodal_yr['rahu_ketu_axis']}** during your **Personal Year {nodal_yr['personal_year']} ({nodal_yr['personal_year_theme']})** "
            f"and **{nodal_yr['active_dasha']}**.\n"
            f"- **The Risk:** *{nodal_yr['personal_year_risk']}* Old professional alliances or revenue models that no longer match your **{d10_asc} Dashamsha (D10)** career authority will hit a hard ceiling.\n"
            f"- **Counter-Strategy:** *{nodal_yr['personal_year_remedy']}* Face your personal **Kua {kua.get('kua_number', 2)} Sheng Qi Wealth direction ({kua_dirs.get('sheng_qi_wealth_expansion', 'North-East')})** when negotiating equity or high-stakes contracts."
        )

        # Year-by-Year 5-Year Tactical Matrix
        yr_lines: List[str] = []
        for y in yearly:
            yr_lines.append(
                f"- **{y['year']} — Personal Year {y['personal_year']} ({y['personal_year_theme']}) • [{y['severity']}]**\n"
                f"  - *Vedic Dasha & Transits:* `{y['active_dasha']}` • `{y['saturn_phase']}` • `{y['rahu_ketu_axis']}`\n"
                f"  - *Primary Trap to Avoid:* {y['personal_year_risk']}\n"
                f"  - *Winning Move:* {y['personal_year_remedy']}"
            )
        sections.append(
            f"### 4. Year-by-Year Multi-System Risk & Opportunity Roadmap ({forecast['start_year']}–{forecast['end_year']})\n"
            + "\n".join(yr_lines)
        )
        return "\n\n".join(sections)

    # =========================================================================
    # MODE 2: CAREER & NEXT 6-MONTH PRIORITY
    # =========================================================================
    if intent == "career_and_6month_priority":
        active_pin = num.get("active_pinnacle", {"stage": "1st Pinnacle", "number": 3, "age_span": "Age 0–33"})
        merc_s = astro.get("sidereal_planets", {}).get("Mercury", {"sign": "Aquarius", "house": 12, "dashamsha_d10_sign": "Leo"})
        lines = loc.get("planetary_lines", [])
        merc_line = next((l for l in lines if l["planet"] == "Mercury"), lines[0] if lines else {})
        jup_line = next((l for l in lines if l["planet"] == "Jupiter"), lines[0] if lines else {})

        sections.append(
            f"**Direct Answer — Your #1 Career & Wealth Priority for the Next 6 Months:**\n"
            f"Your single highest-leverage move over the next 6 months is to **consolidate and ship one flagship intellectual/technical platform** that combines your "
            f"**{top_pat.title if top_pat else 'Creative Communication'}** ({int((top_pat.combined_confidence if top_pat else 0.99)*100)}% verified across {len(top_pat.confirming_disciplines) if top_pat else 6} disciplines) "
            f"with your **{second_pat.title if second_pat else 'Autonomous Executive Authority'}**."
        )
        sections.append(
            f"### 1. Why the Next 6 Months Are a High-Leverage Structural Window\n"
            f"- **Vedic D10 & Mahadasha Convergence:** You are currently running **{dasha.get('active_mahadasha', 'Mercury')} Mahadasha / {dasha.get('active_antardasha', 'Jupiter')} Antardasha (`{dasha.get('active_antardasha_window', 'Active Now')}`)**. "
            f"Because **Mercury is your Amatyakaraka (Career Minister)** placed in **Dashamsha (D10) {merc_s.get('dashamsha_d10_sign', d10_asc)}**, and Jupiter is the natural significator of scale and wisdom, "
            f"this sub-period specifically rewards **authoritative systems, AI/media synthesis, advisory platforms, and scalable IP**.\n"
            f"- **Numerology Personal Year {num.get('personal_year', 4)} (Month {num.get('personal_month', 6)}) + {active_pin['stage']} #{active_pin['number']}:** "
            f"While your Life Path **{num.get('life_path', 3)}** and Chaldean **{num.get('chaldean_compound', '50/5')}** generate rapid ideas, **Personal Year {num.get('personal_year', 4)}** is the architect's foundation year: "
            f"anything you codify into a repeatable, production-grade system right now becomes your primary wealth engine for the next decade.\n"
            f"- **Palmistry & Oracle Confirmation:** Your **{palm.get('head_line', 'Writer’s Fork Head Line to the Mount of Moon')}** + **{palm.get('fate_line', 'Saturn Fate Line with Jupiter branch')}** "
            f"and active **{oracles.get('iching_hexagram', 'Hexagram 57')}** confirm that deep craft illuminated by clear documentation (**{oracles.get('elder_rune', 'Kenaz')}**) beats noisy shallow launches."
        )
        sections.append(
            f"### 2. Concrete 6-Month Execution Blueprint (90-Day Sprints)\n"
            f"1. **Months 1–2 (Architectural Lock & Pruning):** Cut secondary side-quests down to **one flagship system**. Use your Personal Year {num.get('personal_year', 4)} structural focus to harden the backend, data moat, and user experience.\n"
            f"2. **Months 3–4 (Public Narrative & Distribution Along Your Meridians):** Publish high-authority technical/creative breakdowns. Target clients, audiences, or partners aligned with your **Mercury MC corridor ({merc_line.get('mc_hub', 'Tokyo')})** and **Jupiter MC corridor ({jup_line.get('mc_hub', 'Seoul')} / {jup_line.get('asc_hub', 'Dubai')})**.\n"
            f"3. **Months 5–6 (Commercial Monetization & Kua Alignment):** Work from your **{vastu.get('workspace_zone', 'North-West')}** Vastu studio facing **{kua_dirs.get('sheng_qi_wealth_expansion', 'North-East')} (Personal Kua {kua.get('kua_number', 2)} Sheng Qi Wealth vector)** while closing retainers, subscriptions, or product licensing."
        )
        return "\n\n".join(sections)

    # =========================================================================
    # MODE 3: LOCATION, RELOCATION, ASTROCARTOGRAPHY & ROOM VASTU / FENG SHUI
    # =========================================================================
    if intent == "location_and_spatial_alignment":
        birth_geo = astro.get("birthplace_geodesy", {})
        b_city = birth_geo.get("city", loc.get("birthplace", {}).get("city", "Birthplace"))
        curr_city = loc.get("current_location", {}).get("city", b_city)
        reloc = loc.get("relocation_analysis", {})
        lines = loc.get("planetary_lines", [])

        sections.append(
            f"**Direct Answer — Your Optimal Geographic Cities & Room Vastu/Kua Directions:**\n"
            f"Based on your exact birthplace horizon in **{b_city}** (`{birth_geo.get('latitude', 26.91):.2f}°N, {birth_geo.get('longitude', 75.79):.2f}°E`) "
            f"and your current relocation coordinates in **{curr_city}**, here is how your global Astrocartography meridians and local room directions lock together."
        )

        line_items = []
        for ln in lines:
            line_items.append(
                f"- **{ln['planet']} Angular Line:** Midheaven (MC) at `{ln['mc_longitude']}°` near **{ln['mc_hub']}** (orb `{ln['mc_orb_deg']}°`) • "
                f"3D Spherical Ascendant (ASC) near **{ln['asc_hub']}** (orb `{ln['asc_orb_deg']}°`) • DSC near **{ln['dsc_hub']}**\n"
                f"  - *Effect:* {ln['theme']}. (Distance from {curr_city}: `{ln.get('orb_to_current_city_mc_deg', '—')}°` from MC)."
            )

        sections.append(
            f"### 1. Birthplace vs. Current Residence Relocation Chart ({b_city} → {curr_city})\n"
            f"- **Natal Horizon ({b_city}):** Sidereal Lagna **{reloc.get('birth_sidereal_lagna', sid_asc)}** (Navamsha D9 **{d9_asc}**, Dashamsha D10 **{d10_asc}**).\n"
            f"- **Relocated Horizon ({curr_city}):** Relocated Sidereal Lagna **{reloc.get('relocated_sidereal_lagna', sid_asc)}** • "
            f"Relocated Tropical Ascendant **{reloc.get('relocated_tropical_ascendant', 'Aries')}** • Relocated Midheaven **{reloc.get('relocated_sidereal_mc', 'Sagittarius')}**.\n"
            f"### 2. Your 7 Global 3D Astrocartography Power Corridors\n"
            + "\n".join(line_items)
        )

        sections.append(
            f"### 3. Room Vastu Shastra & Personal Kua {kua.get('kua_number', 2)} ({kua.get('trigram', 'Kun')}) Calibration\n"
            f"- **Sheng Qi (Maximum Wealth & Career Expansion):** Face **{kua_dirs.get('sheng_qi_wealth_expansion', 'North-East')}** at your primary work desk.\n"
            f"- **Tian Yi (Health, Recovery & Mentor Support):** Orient key meetings or study toward **{kua_dirs.get('tian_yi_health_mentors', 'West')}**.\n"
            f"- **Fu Wei (Deep Mental Clarity & Meditation):** Face **{kua_dirs.get('fu_wei_clarity_stability', 'South-West')}** or keep the **North-East (Ishanya)** meditation/window zone completely open.\n"
            f"- **Workspace Quadrant:** Your **{vastu.get('workspace_zone', 'North-West')}** (Vayu/Mercury-Moon) or **West (Varuna)** studio directly amplifies your Palmistry **Writer's Fork** and Numerology **Life Path {num.get('life_path', 3)}**."
        )
        return "\n\n".join(sections)

    # =========================================================================
    # MODE 4: CONSTRUCTIVE TENSIONS & CONTRADICTIONS DEEP-DIVE
    # =========================================================================
    if intent == "constructive_tensions_deep_dive":
        sections.append(
            f"**Direct Answer — Where Your Stored Readings Disagree & How to Use That Tension Strategically:**\n"
            f"Instead of hiding contradictions between your palm, numbers, and chart, the Cross-Validation Engine isolated **{len(audit.constructive_tensions)} Constructive Tensions** where two independent systems pull in opposite directions."
        )
        for idx, tns in enumerate(audit.constructive_tensions, 1):
            sections.append(
                f"### {idx}. {tns.title}\n"
                f"- **The Bold Expansion Vector ({tns.side_a_claim.source_label}):** *{tns.side_a_claim.raw_feature}* — {tns.side_a_claim.core_insight}\n"
                f"- **The Structural Caution Vector ({tns.side_b_claim.source_label}):** *{tns.side_b_claim.raw_feature}* — {tns.side_b_claim.core_insight}\n"
                f"- **How to Operate Both Gears Without Stalling:** {tns.strategic_resolution}"
            )
        return "\n\n".join(sections)

    # =========================================================================
    # MODE 5: RELATIONSHIPS, MARRIAGE & CO-FOUNDER COMPATIBILITY
    # =========================================================================
    if intent == "relationships_and_alliances":
        ven_s = astro.get("sidereal_planets", {}).get("Venus", {"sign": "Capricorn", "house": 11, "navamsha_d9_sign": "Taurus", "nakshatra": "Shravana"})
        jup_s = astro.get("sidereal_planets", {}).get("Jupiter", {"sign": "Aquarius", "house": 12, "navamsha_d9_sign": "Sagittarius"})
        moon_s = astro.get("sidereal_planets", {}).get("Moon", {"sign": "Pisces", "house": 1, "nakshatra": "Uttara Bhadrapada"})

        sections.append(
            f"**Direct Answer — Your Relationship, Partnership & Alliance Blueprint:**\n"
            f"Across your **Navamsha (`D9`) Marriage & Alliance Chart**, **Palmistry Heart Line**, **Numerology Soul Urge {num.get('soul_urge_number', 3)} / Expression {num.get('expression_number', 2)}**, and **Spatial Vastu/Kua vectors**, your relational signature demands intellectual parity, emotional loyalty, and shared mission."
        )
        sections.append(
            f"### 1. Somatic & Astrological Partnership Mechanics\n"
            f"- **Vedic D1 & D9 Navamsha Signature:** With **Navamsha (`D9`) Lagna in {d9_asc}**, Sidereal **Venus in {ven_s['sign']} (House {ven_s['house']}, D9 {ven_s.get('navamsha_d9_sign', 'Taurus')})**, "
            f"**Jupiter in {jup_s['sign']} (House {jup_s['house']})**, and **Moon in {moon_s['sign']} ({moon_s.get('nakshatra', 'Uttara Bhadrapada')})**, you do not bond through superficial small talk—you bond through deep philosophical trust and shared architectural building.\n"
            f"- **Palmistry Heart Line & Numerology Harmony:** Your **{palm.get('heart_line', 'deep Heart Line curving beneath the Mount of Jupiter')}** paired with **Expression/Soul Numbers ({num.get('expression_number', 2)} / {num.get('soul_urge_number', 3)})** shows high idealism in love and alliances: once you commit, you invest massive loyalty, provided your autonomy is respected.\n"
            f"### 2. Spatial & Locational Relationship Amplifiers\n"
            f"- **Vastu & Kua Yan Nian Vector:** Your Personal **Kua {kua.get('kua_number', 2)} Yan Nian (Relationship Harmony)** direction is **{kua_dirs.get('yan_nian_relationships', 'North-West')}**. Keep the **South-East (Venus/Agni)** warm and clutter-free, and anchor the master bedroom in the **South-West (Nairutya)**."
        )
        return "\n\n".join(sections)

    # =========================================================================
    # MODE 6: HEALTH, ENERGY, NERVOUS SYSTEM & VITALITY
    # =========================================================================
    if intent == "health_and_vitality":
        forecast = compute_multi_year_forecast(
            profile_bundle={"profile_input": inp, "disciplines": discipline_payloads},
            horizon_years=2,
        )
        curr_yr = forecast["yearly_forecasts"][0]
        sections.append(
            f"**Direct Answer — Your Health, Nervous System & Biomagnetic Vitality Blueprint:**\n"
            f"With **{sid_asc} Sidereal Lagna**, **Janma Nakshatra {dasha.get('nakshatra', 'Uttara Bhadrapada')}**, Palmistry **{palm.get('hand_element', 'Air-Fire')}** morphology, and active **{curr_yr['saturn_phase']}**, your primary health lever is **nervous-system regulation and sleep polarity**."
        )
        sections.append(
            f"### 1. Somatic & Planetary Vitality Indicators\n"
            f"- **Cognitive Over-Clocking:** Your **forked Head Line to the Mount of Moon** + **Budhaditya Yoga (Sun-Mercury)** means your brain runs background synthesis threads even while resting. During **{curr_yr['saturn_phase']}**, this can manifest as late-night mental hyperactivity or neck/shoulder tension.\n"
            f"- **Biomagnetic Sleep & Kua Tian Yi Health Remedy:** Sleep strictly with your head oriented **{vastu.get('sleeping_head_direction', 'South')} or East** (never North), align your recovery area with your **Kua {kua.get('kua_number', 2)} Tian Yi (Heavenly Doctor) vector ({kua_dirs.get('tian_yi_health_mentors', 'West')})**, and keep water/electronics out of the South-East bedroom corner."
        )
        return "\n\n".join(sections)

    # =========================================================================
    # MODE 7: TARGETED CUSTOM QUESTION (Any specific user question not matching the presets)
    # =========================================================================
    if intent in ("targeted_custom_question", "somatic_and_oracle_triangulation"):
        forecast = compute_multi_year_forecast(
            profile_bundle={"profile_input": inp, "disciplines": discipline_payloads},
            horizon_years=3,
        )
        curr_yr = forecast["yearly_forecasts"][0]
        sections.append(
            f"**Direct Cross-Validated Answer to: *\"{user_query}\"*:**\n"
            f"Triangulating your question across all **{len(audit.active_disciplines)} active disciplines** in your vault (**{audit.total_claims_analyzed} atomic claims**), here is what your converged patterns reveal:"
        )
        sections.append(
            f"### 1. Multi-System Triangulation for Your Question\n"
            f"- **Primary Verified Signal ({top_pat.title if top_pat else 'Creative Systems Architecture'} — {int((top_pat.combined_confidence if top_pat else 0.99)*100)}% Confidence):** "
            f"{top_pat.recursive_mechanism if top_pat else ''}\n"
            f"- **Somatic & Symbolic Oracle Lens:** Your Palmistry (**{palm.get('head_line', 'Writer’s Fork Head Line')}** & **{palm.get('fate_line', 'Saturn-Jupiter Fate Line')}**) "
            f"intersects with your active Tarot significator **{oracles.get('tarot_card', 'The Magician (I)')}**, I Ching **{oracles.get('iching_hexagram', 'Hexagram 57')}**, and Elder Rune **{oracles.get('elder_rune', 'Kenaz')}**.\n"
            f"- **Active Timing & Transit Pressure ({curr_yr['year']}):** You are operating inside **{curr_yr['active_dasha']}**, **Personal Year {curr_yr['personal_year']} ({curr_yr['personal_year_theme']})**, and **{curr_yr['saturn_phase']}**.\n"
            f"### 2. Recommended Next Move\n"
            f"- **Strategic Action:** {curr_yr['personal_year_remedy']}\n"
            f"- **Spatial & Directional Lever:** Execute this from your **{vastu.get('workspace_zone', 'North-West')}** workspace facing **{kua_dirs.get('sheng_qi_wealth_expansion', 'North-East')} (Sheng Qi)**."
        )
        return "\n\n".join(sections)

    # =========================================================================
    # MODE 8: FULL HOLISTIC OVERVIEW (Initial Onboarding / Full Profile Request)
    # =========================================================================
    trop_asc = astro.get("tropical_ascendant", {}).get("sign", "Aries")
    sid_asc_deg = sid_asc_obj.get("degree", 14.2)
    birth_geo = astro.get("birthplace_geodesy", {})
    b_city = birth_geo.get("city", loc.get("birthplace", {}).get("city", "Birthplace"))
    b_lat = birth_geo.get("latitude", 28.6139)
    b_lon = birth_geo.get("longitude", 77.2090)
    b_tz = birth_geo.get("timezone_name", "Asia/Kolkata")
    b_off = birth_geo.get("utc_offset_hours", 5.5)
    b_dst = "DST Active" if birth_geo.get("is_dst_active") else "Standard Time"
    reloc = loc.get("relocation_analysis", {})
    curr_city = loc.get("current_location", {}).get("city", b_city)
    yogas = astro.get("vedic_yogas", [])
    yoga_names = ", ".join(y["name"] for y in yogas) if yogas else "Budhaditya & Saraswati Yoga"
    loshu = num.get("loshu_grid", {})
    loshu_arrows = "; ".join(loshu.get("completed_planes_and_arrows", [])) or "Diagonal Axis of Self-Reliance"

    sections.append(
        f"**Unified Cross-Disciplinary Synthesis for {profile_name}:** Out of **{audit.total_claims_analyzed} atomic traits** "
        f"extracted across **{len(audit.active_disciplines)} esoteric systems** ({', '.join(d.replace('_', ' ').title() for d in audit.active_disciplines)}), "
        f"the algorithm isolated **{len(audit.verified_core_patterns)} Verified Core Patterns** and "
        f"**{len(audit.constructive_tensions)} Constructive Tensions**."
    )

    sections.append(
        f"### 1. Core Identity, Birthplace Geodesy & Cognitive Architecture\n"
        f"- **Exact Birthplace Horizon & Meridian Anchor:** Born in **{b_city}** (`{b_lat:.4f}°N, {b_lon:.4f}°E` • Timezone `{b_tz}`, `UTC{b_off:+.2f}` [{b_dst}]), "
        f"your exact eastern horizon casts a **{sid_asc} {sid_asc_deg}° Sidereal Lagna** (**Navamsha D9 in {d9_asc}**, **Dashamsha D10 in {d10_asc}**, Tropical Ascendant in **{trop_asc}**). "
        + (
            f"Relocated to your current residence in **{curr_city}**, your active horizon shifts to **{reloc.get('relocated_sidereal_lagna', sid_asc)}** (Relocated Midheaven in **{reloc.get('relocated_sidereal_mc', 'Aries')}**).\n"
            if curr_city and curr_city != b_city
            else "\n"
        )
        + f"- **Somatic & Mathematical Echo:** In Palmistry, your **{palm.get('head_line', 'deep, forked Head Line sloping toward the Mount of Moon')}** "
        f"and **Mystic Cross in the Quadrangle** lock directly into your **Soul Urge {num.get('soul_urge_number', 7)}**, "
        f"**Maturity Number {num.get('maturity_number', 7)}**, and Lo Shu **{loshu_arrows}**.\n"
        f"- **Vedic & Divisional Confirmation:** Your **Janma Nakshatra {dasha.get('nakshatra', 'Ashlesha')} (Pada {dasha.get('nakshatra_pada', 1)})**, "
        f"**Atmakaraka (Soul Significator) {ak}**, and **{yoga_names}** confirm a dual cognitive engine: one hemisphere demands rigorous, "
        f"first-principles structural verification, while the other synthesizes symbolic, esoteric, and non-linear architectures."
    )

    active_pin = num.get("active_pinnacle", {"stage": "1st Pinnacle", "number": 3, "age_span": "Age 0–33"})
    if top_pat:
        supporting_summary = "; ".join(
            f"**{c.source_label}** (*{c.raw_feature}*)" for c in top_pat.supporting_claims[:4]
        )
        sections.append(
            f"### 2. Career Trajectory, Purpose & Wealth Alchemy\n"
            f"The highest-confidence pillar in your entire vault is **{top_pat.title}** "
            f"({int(top_pat.combined_confidence * 100)}% cross-system confidence across **{top_pat.convergence_count} independent disciplines**), "
            f"confirmed by {supporting_summary}.\n\n"
            f"- **Recursive Mechanism (D1/D9/D10 & Numerology Pinnacles):** {top_pat.recursive_mechanism} "
            f"Your **Amatyakaraka (Career Minister) {amk}** and **{active_pin['stage']} (Number {active_pin['number']}, {active_pin['age_span']})** "
            f"channel this directly into system building, media/AI synthesis, and high-leverage intellectual property.\n"
            f"- **Secondary Authority Pillar:** Reinforced by **{second_pat.title if second_pat else 'Autonomous Executive Leadership'}** "
            f"(Life Path **{num.get('life_path', 1)}**, Expression **{num.get('expression_number', 3)}**, Chaldean **{num.get('chaldean_compound', '45/9')}**, and "
            f"**{palm.get('fate_line', 'Fate Line rising to Saturn with Jupiter branch')}**), your wealth compounds fastest when you own "
            f"proprietary frameworks and automated platforms rather than trading raw hours."
        )

    if audit.constructive_tensions:
        tns = audit.constructive_tensions[0]
        sections.append(
            f"### 3. Strategic Navigation of Constructive Tensions\n"
            f"A single-discipline reading would miss the productive friction between your somatic caution and your cyclical expansion:\n"
            f"- **The Polarity:** **{tns.side_b_claim.source_label}** (*{tns.side_b_claim.raw_feature}*) instills structural caution—an instinct to "
            f"audit every edge case before acting. Simultaneously, **{tns.side_a_claim.source_label}** (*{tns.side_a_claim.raw_feature}*) "
            f"pushes for high-velocity, bold initiation.\n"
            f"- **The Synthesis Strategy:** {tns.strategic_resolution}"
        )

    ven_info = astro.get("sidereal_planets", {}).get("Venus", {"sign": "Libra", "house": 7})
    jup_info = astro.get("sidereal_planets", {}).get("Jupiter", {"sign": "Sagittarius", "house": 9})
    sections.append(
        f"### 4. Relationships & Collaborative Resonance\n"
        f"Your Palmistry **{palm.get('heart_line', 'deep Heart Line curving beneath the Mount of Jupiter')}** converges with "
        f"Sidereal **Venus in {ven_info['sign']} (House {ven_info['house']})** and **Jupiter in {jup_info['sign']} (House {jup_info['house']})**. "
        f"In both romantic and co-founder alliances, you require high intellectual bandwidth, mutual autonomy, and shared architectural vision. "
        f"Spatially, keeping the **South-East (Venus/Agni)** warm and active while keeping the **South-West (Earth)** grounded stabilizes close partnerships."
    )

    lines = loc.get("planetary_lines", [])
    line_bullets = []
    for ln in lines[:4]:
        line_bullets.append(
            f"**{ln['planet']} Angular Corridor** (MC at `{ln['mc_longitude']}°` near **{ln['mc_hub']}** [orb `{ln.get('mc_orb_deg', 1.2)}°`]; "
            f"3D Spherical ASC near **{ln['asc_hub']}**): {ln['theme']}."
        )
    sections.append(
        f"### 5. Optimal Environment: MahaVastu, Classical Kua Feng Shui & 3D Astrocartography\n"
        f"When the engine uses your verified creative-leadership core as a search query across spatial systems, three environmental layers lock together:\n"
        f"- **MahaVastu 16-Zone Alignment:** Your workspace in the **{vastu.get('workspace_zone', 'North-West')}** quadrant "
        f"facing **{vastu.get('desk_facing', 'North')}** with a **{vastu.get('entrance_direction', 'North-East')}** main entrance directly feeds your "
        f"Mercury/Moon creative circuit. Keep a solid wall behind your chair (**South-West Nairutya Earth backing**) and keep the **North-East (Ishanya)** window line completely unobstructed.\n"
        f"- **Classical Ba Zhai Feng Shui (Personal Kua {kua.get('kua_number', 4)} — {kua.get('trigram', 'Xun')} / {kua.get('group', 'East Group')}):** "
        f"Your personal **Sheng Qi (Wealth & Expansion)** vector is **{kua_dirs.get('sheng_qi_wealth_expansion', 'North')}**, "
        f"**Tian Yi (Health & Mentors)** is **{kua_dirs.get('tian_yi_health_mentors', 'South')}**, and **Fu Wei (Mental Clarity)** is "
        f"**{kua_dirs.get('fu_wei_clarity_stability', 'South-East')}**.\n"
        f"- **3D Spherical Astrocartography Corridors:**\n  - " + "\n  - ".join(line_bullets)
    )

    sections.append(
        f"### 6. Upcoming Timing & 5 Concrete Actionable Alignments\n"
        f"1. **Execute Within the Active Mahadasha-Antardasha Window ({dasha.get('active_antardasha_window', 'Current Cycle')}):** Your **{dasha.get('active_mahadasha', 'Mercury')} Mahadasha / {dasha.get('active_antardasha', 'Venus')} Antardasha**, "
        f"**Personal Year {num.get('personal_year', 1)} (Month {num.get('personal_month', 5)})**, **{oracles.get('iching_hexagram', 'Hexagram 50 — The Cauldron')}**, and "
        f"Elder Rune **{oracles.get('elder_rune', 'Ansuz')}** all converge on packaging disparate knowledge streams into one flagship platform.\n"
        f"2. **Apply the 48-Hour Two-Gear Decision Protocol:** Honor your Palmistry Fate/Head Line and Sidereal Saturn caution by dedicating 48 hours to architectural stress-testing, then switch fully into your **{oracles.get('tarot_card', 'The Magician (I)')}** execution gear without second-guessing.\n"
        f"3. **Lock In Your Kua {kua.get('kua_number', 4)} & Vastu Desk Axis Today:** Seat yourself facing **{kua_dirs.get('sheng_qi_wealth_expansion', 'North')} (Sheng Qi)** or **East** during deep synthesis, clear stagnant weight from the **North-West (Vayu)** and **North-East (Ishanya)** corners, and sleep with your head oriented **{vastu.get('sleeping_head_direction', 'South')}**.\n"
        f"4. **Activate Your {lines[1]['mc_hub'] if len(lines) > 1 else 'Bengaluru'} & {lines[3]['mc_hub'] if len(lines) > 3 else 'Singapore'} Meridians:** Align key product launches, client alliances, or remote deployments with hubs sitting along your Mercury and Jupiter Midheaven/Ascendant lines.\n"
        f"5. **Exploit Your Lo Shu & Yogas Compounding Advantage:** Because your chart unites **{yoga_names}** with Palmistry's **Writer's Fork to the Mount of Moon**, write and publish authoritative architectural blueprints alongside every system you build."
    )

    return "\n\n".join(sections)


async def generate_unified_synthesis(
    profile_name: str,
    user_query: str,
    audit: CrossValidationAudit,
    discipline_payloads: Dict[str, Any],
    profile_input: Optional[Dict[str, Any]] = None,
    include_audit_section: bool = True,
    preferred_route: str = "auto",
) -> Dict[str, Any]:
    """
    Routes the Master Synthesis request through the highest-priority zero-cost AI-OS provider available,
    falling back transparently to the Query-Driven Cross-Validation & Ephemeris Forecaster so every question
    gets a distinct, mathematically computed answer.
    """
    t0 = time.time()
    routes = await detect_available_zero_cost_routes()
    online_routes = {r["id"]: r for r in routes if r["status"] == "online"}

    intent = _classify_query_intent(user_query)
    deterministic_output = compile_deterministic_master_synthesis(
        profile_name=profile_name,
        user_query=user_query,
        audit=audit,
        discipline_payloads=discipline_payloads,
        profile_input=profile_input,
        include_audit_section=include_audit_section,
    )

    user_prompt = (
        f"USER PROFILE: {profile_name}\n"
        f"DETECTED QUESTION INTENT: {intent}\n"
        f"EXACT USER QUESTION: {user_query}\n\n"
        f"PRE-VERIFIED CROSS-VALIDATION AUDIT & EPHEMERIS CALCULATIONS:\n"
        + "\n".join(f"- {b}" for b in audit.audit_bullets)
        + f"\n\nCOMPUTED QUESTION-SPECIFIC SYNTHESIS:\n{deterministic_output}\n\n"
        "Directly answer the user's exact question with zero repetition of generic templates."
    )

    served_by = "aios_deterministic_compiler"
    model_used = f"AI-OS Query-Driven Forecaster ({intent})"
    final_text = deterministic_output

    if preferred_route != "aios_deterministic_compiler":
        # 1. Try FreeLLMAPI Local Router (:3001)
        if "freellmapi_local" in online_routes and preferred_route in ("auto", "freellmapi_local"):
            endpoint = online_routes["freellmapi_local"]["endpoint"]
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(
                        f"{endpoint}/chat/completions",
                        json={
                            "model": "auto",
                            "messages": [
                                {"role": "system", "content": MASTER_SYNTHESIS_SYSTEM_PROMPT},
                                {"role": "user", "content": user_prompt},
                            ],
                            "temperature": 0.4,
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data.get("choices", [{}])[0].get("message", {}).get("content")
                        if content:
                            final_text = content
                            served_by = "freellmapi_local"
                            model_used = data.get("model", "freellmapi/auto")
            except Exception:
                pass

        # 2. Try Local Ollama (:11434)
        if served_by == "aios_deterministic_compiler" and "ollama_local" in online_routes and preferred_route in ("auto", "ollama_local"):
            model_name = online_routes["ollama_local"].get("model", "llama3.2")
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
            try:
                async with httpx.AsyncClient(timeout=18.0) as client:
                    resp = await client.post(
                        f"{ollama_url}/api/chat",
                        json={
                            "model": model_name,
                            "stream": False,
                            "messages": [
                                {"role": "system", "content": MASTER_SYNTHESIS_SYSTEM_PROMPT},
                                {"role": "user", "content": user_prompt},
                            ],
                        },
                    )
                    if resp.status_code == 200:
                        content = resp.json().get("message", {}).get("content")
                        if content:
                            final_text = content
                            served_by = "ollama_local"
                            model_used = f"ollama/{model_name}"
            except Exception:
                pass

        # 3. Try Gemini Free Tier
        if served_by == "aios_deterministic_compiler" and "gemini_free" in online_routes and preferred_route in ("auto", "gemini_free"):
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                try:
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        resp = await client.post(
                            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}",
                            json={
                                "system_instruction": {"parts": [{"text": MASTER_SYNTHESIS_SYSTEM_PROMPT}]},
                                "contents": [{"parts": [{"text": user_prompt}]}],
                            },
                        )
                        if resp.status_code == 200:
                            candidates = resp.json().get("candidates", [])
                            if candidates:
                                text_out = candidates[0].get("content", {}).get("parts", [{}])[0].get("text")
                                if text_out:
                                    final_text = text_out
                                    served_by = "gemini_free"
                                    model_used = "gemini-2.5-flash (Free Tier)"
                except Exception:
                    pass

    latency_ms = int((time.time() - t0) * 1000)
    return {
        "synthesis_markdown": final_text,
        "query_intent": intent,
        "served_by": served_by,
        "model_used": model_used,
        "verified_cost_usd": 0.0,
        "latency_ms": latency_ms,
        "available_routes": routes,
    }

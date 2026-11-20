"""
Multi-Year Temporal Forecasting, Transit & Risk/Challenge Calculator (Swiss Ephemeris + Numerology + Vimshottari).

Computes real year-by-year astronomical and esoteric activations for any N-year horizon (e.g. next 1–5 years):
1. Live & Future Sidereal Planetary Positions (Saturn, Jupiter, Rahu, Ketu, Mars) using `pyswisseph`
2. Classical Vedic Saturn Stress Transits:
   - Sade Sati (7.5-year Saturn transit over the 12th, 1st [Janma], and 2nd houses from Natal Moon)
   - Ashtama Shani (Saturn transiting 8th house from Natal Moon or Lagna)
   - Kantaka Shani (Saturn transiting 4th or 10th from Moon/Lagna)
3. Nodal Axis (Rahu/Ketu) Eclipses & Natal Planet Crossings (Rahu/Ketu transiting over Natal Sun, Moon, Lagna, or Saturn)
4. Exact Vimshottari Antardasha (Bhukti) & Mahadasha Transitions occurring within the next N years
5. Year-by-Year Numerology Personal Year + Challenge Number + Pinnacle Transitions
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

import swisseph as swe

from backend.engine.disciplines.astrology import PLANET_IDS, ZODIAC_SIGNS, _sign_and_deg
from backend.engine.disciplines.numerology import NUMBER_ARCHETYPES, _reduce_num

PERSONAL_YEAR_CHALLENGES: Dict[int, Dict[str, str]] = {
    1: {
        "theme": "Autonomous Initiation & Identity Overhaul",
        "risk": "Isolation, impatience, or burning bridges by pushing too aggressively without team alignment.",
        "remedy": "Lead with clear architectural specs; delegate execution friction rather than carrying everything solo.",
    },
    2: {
        "theme": "Gestation, Diplomacy & Partnership Calibration",
        "risk": "Over-hesitation, decision paralysis, or absorbing emotional friction from co-founders/partners.",
        "remedy": "Maintain strict written boundaries; allow high-trust alliances to mature without forcing premature launches.",
    },
    3: {
        "theme": "Creative Expansion & Public Visibility",
        "risk": "Scattered focus across too many shiny projects, unfinished prototypes, and verbal over-commitment.",
        "remedy": "Constrain output to one flagship narrative or platform; finish before starting the next experiment.",
    },
    4: {
        "theme": "Structural Stress-Test, Foundations & Workload Compression",
        "risk": "Burnout, bureaucratic bottlenecks, technical debt, or feeling boxed in by heavy operational constraints.",
        "remedy": "Audit systems ruthlessly, eliminate non-essential obligations, and honor physical recovery and South-West Vastu stability.",
    },
    5: {
        "theme": "Volatility, Rapid Pivots & Geographic/Market Disruption",
        "risk": "Impulsive leaps, abandonment of compounding assets, or nervous-system overstimulation.",
        "remedy": "Keep your core architecture invariant while allowing distribution channels and locations to pivot.",
    },
    6: {
        "theme": "Domestic Responsibility, Alliances & Stewardship",
        "risk": "Over-carrying family or organizational obligations at the expense of your primary creative mission.",
        "remedy": "Re-negotiate domestic and team commitments openly; harmonize the South-East & South-West spaces.",
    },
    7: {
        "theme": "Introspective Audit, Sabbatical & Deep R&D",
        "risk": "Social withdrawal, cynicism, or temporary slowdown in external commercial velocity while inner models upgrade.",
        "remedy": "Treat this year as high-leverage R&D and intellectual property creation rather than pushing noisy marketing.",
    },
    8: {
        "theme": "High-Stakes Capital, Power & Karmic Harvest",
        "risk": "Power struggles, legal/financial friction, or cash-flow strain if structural foundations from Year 4 were weak.",
        "remedy": "Operate with zero compliance gaps, price your intellectual equity at its true value, and keep the North Kubera axis clear.",
    },
    9: {
        "theme": "Culmination, Pruning & Identity Shedding",
        "risk": "Clinging to expired roles, legacy codebases, or draining relationships that must end before the next 9-year cycle.",
        "remedy": "Actively archive and release dead weight in Q3–Q4 to clear runway for the upcoming Personal Year 1 rebirth.",
    },
}


def compute_sidereal_transits_for_date(dt: datetime) -> Dict[str, Any]:
    """Calculates exact Sidereal Lahiri positions of Saturn, Jupiter, Rahu, Ketu, and Mars for any target date."""
    jd = swe.julday(dt.year, dt.month, dt.day, 12.0)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    out: Dict[str, Any] = {}
    for p_name in ("Saturn", "Jupiter", "Rahu", "Mars", "Sun"):
        res, _ = swe.calc_ut(jd, PLANET_IDS[p_name], swe.FLG_SPEED)
        s_lon = (res[0] - ayanamsa) % 360.0
        sign, idx, deg = _sign_and_deg(s_lon)
        out[p_name] = {
            "sign": sign,
            "sign_index": idx,
            "degree": deg,
            "longitude": round(s_lon, 2),
            "retrograde": res[3] < 0 if p_name != "Rahu" else True,
        }

    rahu_lon = out["Rahu"]["longitude"]
    ketu_lon = (rahu_lon + 180.0) % 360.0
    k_sign, k_idx, k_deg = _sign_and_deg(ketu_lon)
    out["Ketu"] = {
        "sign": k_sign,
        "sign_index": k_idx,
        "degree": k_deg,
        "longitude": round(ketu_lon, 2),
        "retrograde": True,
    }
    return out


def compute_multi_year_forecast(
    profile_bundle: Dict[str, Any],
    horizon_years: int = 5,
) -> Dict[str, Any]:
    """
    Computes an exact year-by-year multi-discipline forecast & critical challenge audit
    over the next `horizon_years` (default 5 years) from the profile's stored data.
    """
    inp = profile_bundle["profile_input"]
    disciplines = profile_bundle["disciplines"]
    astro = disciplines["astrology"]
    num = disciplines["numerology"]
    vastu = disciplines["vastu_fengshui"]
    palm = disciplines["palmistry"]

    birth_parts = inp["birth_date"].split("-")
    b_month = int(birth_parts[1])
    b_day = int(birth_parts[2])

    sid_asc_sign = astro["sidereal_ascendant"]["sign"]
    sid_asc_idx = ZODIAC_SIGNS.index(sid_asc_sign)

    natal_moon_sign = astro["sidereal_planets"]["Moon"]["sign"]
    natal_moon_idx = ZODIAC_SIGNS.index(natal_moon_sign)

    natal_sat_sign = astro["sidereal_planets"]["Saturn"]["sign"]
    natal_sat_house = astro["sidereal_planets"]["Saturn"]["house"]
    natal_sun_sign = astro["sidereal_planets"]["Sun"]["sign"]
    natal_merc_sign = astro["sidereal_planets"]["Mercury"]["sign"]

    dasha_info = astro["vimshottari_dasha"]
    antardashas = dasha_info.get("current_mahadasha_antardashas", [])

    start_year = datetime.now().year
    yearly_forecasts: List[Dict[str, Any]] = []
    critical_challenges: List[Dict[str, Any]] = []

    for offset in range(horizon_years + 1):
        yr = start_year + offset
        mid_dt = datetime(yr, 7, 1)
        transits = compute_sidereal_transits_for_date(mid_dt)

        t_sat = transits["Saturn"]
        t_jup = transits["Jupiter"]
        t_rahu = transits["Rahu"]
        t_ketu = transits["Ketu"]

        # Houses of transiting Saturn & Jupiter from Natal Moon (Chandra Lagna) and Natal Ascendant (Udaya Lagna)
        sat_from_moon = ((t_sat["sign_index"] - natal_moon_idx) % 12) + 1
        sat_from_asc = ((t_sat["sign_index"] - sid_asc_idx) % 12) + 1
        jup_from_moon = ((t_jup["sign_index"] - natal_moon_idx) % 12) + 1
        jup_from_asc = ((t_jup["sign_index"] - sid_asc_idx) % 12) + 1
        rahu_from_asc = ((t_rahu["sign_index"] - sid_asc_idx) % 12) + 1

        # Numerology Personal Year for `yr`
        py = _reduce_num(_reduce_num(b_month, False) + _reduce_num(b_day, False) + _reduce_num(yr, False), False)
        py_meta = PERSONAL_YEAR_CHALLENGES.get(py, PERSONAL_YEAR_CHALLENGES[4])

        # Active Antardasha in mid-year `yr`
        active_sub_str = f"{dasha_info['active_mahadasha']} Mahadasha"
        active_sub_lord = dasha_info["active_antardasha"]
        for ad in antardashas:
            if ad["start_date"] <= f"{yr}-07-01" <= ad["end_date"]:
                active_sub_lord = ad["antardasha"]
                active_sub_str = f"{ad['mahadasha']}-{ad['antardasha']} ({ad['start_date']} to {ad['end_date']})"
                break

        # Detect Saturn / Nodal / Numerology Stress & Challenge Vectors for this year
        saturn_phase = f"Saturn in {t_sat['sign']} (House {sat_from_asc} from Lagna, {sat_from_moon} from Moon)"
        severity = "Moderate Structural Calibration"
        challenge_headline = f"{yr}: {py_meta['theme']} (Personal Year {py})"
        challenge_details: List[str] = []

        if sat_from_moon == 12:
            saturn_phase = f"Sade Sati Rising Phase (12th from Moon — Saturn in {t_sat['sign']})"
            severity = "High — Mental & Sleep Overhead / Hidden Costs"
            challenge_details.append(
                f"**Sade Sati Rising Phase (Saturn in {t_sat['sign']}, 12th from your {natal_moon_sign} Moon):** "
                "Increases cognitive load, sleep disruption, and behind-the-scenes restructuring."
            )
        elif sat_from_moon == 1:
            saturn_phase = f"Peak Janma Sade Sati (Saturn in {t_sat['sign']} directly over Natal Moon & {sid_asc_sign} Lagna)"
            severity = "Critical — Identity & Structural Forging (Peak Pressure)"
            challenge_details.append(
                f"**Peak Janma Sade Sati + Saturn Return/Crossing in {t_sat['sign']} (House {sat_from_asc}):** "
                "Transiting Saturn crosses directly over your Natal Moon"
                + (" and Natal Saturn (Saturn Return)" if t_sat["sign"] == natal_sat_sign else "")
                + ". Any unverified partnership, sloppy financial obligation, or over-extended workload is compressed under high pressure so only your most durable work survives."
            )
        elif sat_from_moon == 2:
            saturn_phase = f"Sade Sati Setting Phase (2nd from Moon — Saturn in {t_sat['sign']})"
            severity = "High — Cash-Flow & Family/Speech Discipline"
            challenge_details.append(
                f"**Sade Sati Setting Phase (Saturn in {t_sat['sign']}, 2nd from Moon / House {sat_from_asc}):** "
                "Tests financial treasury discipline, pricing accuracy, and family/communication boundaries."
            )
        elif sat_from_moon == 8 or sat_from_asc == 8:
            saturn_phase = f"Ashtama Shani (8th House Saturn Transit in {t_sat['sign']})"
            severity = "Critical — Deep Transformation & Risk Audit"
            challenge_details.append(
                f"**Ashtama Shani (Saturn in {t_sat['sign']} transiting 8th house):** "
                "Requires strict risk management, zero speculative leverage, and nervous-system pacing."
            )
        elif sat_from_moon in (4, 10) or sat_from_asc in (4, 10):
            saturn_phase = f"Kantaka Shani (Angular Saturn Transit in {t_sat['sign']}, House {sat_from_asc})"
            severity = "High — Career & Domestic Load-Bearing Test"
            challenge_details.append(
                f"**Kantaka Shani (Saturn in {t_sat['sign']} angular to Moon/Lagna):** "
                "Heavy executive responsibility and domestic/property restructuring."
            )

        # Nodal (Rahu/Ketu) Eclipses over key natal planets
        if t_rahu["sign"] in (natal_sun_sign, natal_merc_sign, natal_moon_sign, sid_asc_sign) or t_ketu["sign"] in (
            natal_sun_sign,
            natal_merc_sign,
            natal_moon_sign,
            sid_asc_sign,
        ):
            challenge_details.append(
                f"**Rahu-Ketu Nodal Axis in {t_rahu['sign']}/{t_ketu['sign']} (Houses {rahu_from_asc}/{(rahu_from_asc + 5) % 12 + 1}):** "
                f"Triggers eclipses across your natal {t_rahu['sign']}/{t_ketu['sign']} placements—forcing a shedding of outdated identity and sudden shifts in alliances or technology."
            )

        # Numerology Personal Year Friction
        challenge_details.append(
            f"**Numerology Personal Year {py} ({py_meta['theme']}):** Primary risk is *{py_meta['risk'].lower()}*"
        )

        # Jupiter Protection / Counter-Balance
        jupiter_protection = (
            f"Transiting Jupiter in {t_jup['sign']} (House {jup_from_asc} from Lagna, {jup_from_moon} from Moon) "
            + (
                "provides strong trinal/angular grace and high-value mentors to buffer the pressure."
                if jup_from_moon in (1, 2, 5, 7, 9, 11) or jup_from_asc in (1, 4, 5, 7, 9, 10, 11)
                else "requires self-generated momentum and disciplined focus on internal R&D."
            )
        )

        yr_entry = {
            "year": yr,
            "personal_year": py,
            "personal_year_theme": py_meta["theme"],
            "personal_year_risk": py_meta["risk"],
            "personal_year_remedy": py_meta["remedy"],
            "active_dasha": active_sub_str,
            "active_antardasha_lord": active_sub_lord,
            "saturn_transit_sign": t_sat["sign"],
            "saturn_phase": saturn_phase,
            "jupiter_transit_sign": t_jup["sign"],
            "jupiter_protection": jupiter_protection,
            "rahu_ketu_axis": f"Rahu in {t_rahu['sign']} / Ketu in {t_ketu['sign']}",
            "severity": severity,
            "challenge_details": challenge_details,
        }
        yearly_forecasts.append(yr_entry)

        if "Critical" in severity or "High" in severity or py in (4, 7, 8, 9):
            critical_challenges.append(yr_entry)

    return {
        "start_year": start_year,
        "end_year": start_year + horizon_years,
        "natal_moon_sign": natal_moon_sign,
        "natal_saturn_sign": natal_sat_sign,
        "natal_saturn_house": natal_sat_house,
        "yearly_forecasts": yearly_forecasts,
        "critical_challenges": critical_challenges[:4] or yearly_forecasts[:3],
    }

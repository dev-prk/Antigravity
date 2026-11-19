"""Vedic (Sidereal Lahiri) & Western (Tropical) Astrology Calculation Engine using Swiss Ephemeris."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Tuple

import swisseph as swe

from backend.engine.ontology import AtomicClaim

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

NAKSHATRAS = [
    ("Ashwini", "Ketu"), ("Bharani", "Venus"), ("Krittika", "Sun"),
    ("Rohini", "Moon"), ("Mrigashira", "Mars"), ("Ardra", "Rahu"),
    ("Punarvasu", "Jupiter"), ("Pushya", "Saturn"), ("Ashlesha", "Mercury"),
    ("Magha", "Ketu"), ("Purva Phalguni", "Venus"), ("Uttara Phalguni", "Sun"),
    ("Hasta", "Moon"), ("Chitra", "Mars"), ("Swati", "Rahu"),
    ("Vishakha", "Jupiter"), ("Anuradha", "Saturn"), ("Jyeshtha", "Mercury"),
    ("Mula", "Ketu"), ("Purva Ashadha", "Venus"), ("Uttara Ashadha", "Sun"),
    ("Shravana", "Moon"), ("Dhanishta", "Mars"), ("Shatabhisha", "Rahu"),
    ("Purva Bhadrapada", "Jupiter"), ("Uttara Bhadrapada", "Saturn"), ("Revati", "Mercury"),
]

DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}

DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
}


def _to_julian_day(birth_date: str, birth_time: str, tz_offset: float) -> float:
    dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    decimal_hour = dt.hour + (dt.minute / 60.0) - tz_offset
    return swe.julday(dt.year, dt.month, dt.day, decimal_hour)


def _sign_and_deg(lon: float) -> Tuple[str, int, float]:
    norm = lon % 360.0
    idx = int(norm // 30)
    deg = round(norm % 30, 2)
    return ZODIAC_SIGNS[idx], idx, deg


def _compute_vimshottari_dasha(sidereal_moon_lon: float, birth_date: str) -> Dict[str, Any]:
    norm = sidereal_moon_lon % 360.0
    nak_span = 360.0 / 27.0  # 13.3333 deg
    nak_idx = int(norm // nak_span)
    fraction_elapsed = (norm % nak_span) / nak_span
    fraction_remaining = 1.0 - fraction_elapsed

    nak_name, start_lord = NAKSHATRAS[nak_idx]
    birth_year = int(birth_date.split("-")[0])
    current_year = datetime.now().year
    age = max(0.0, float(current_year - birth_year))

    order_idx = DASHA_ORDER.index(start_lord)
    first_balance = DASHA_YEARS[start_lord] * fraction_remaining

    timeline = []
    cursor_age = 0.0
    active_mahadasha = start_lord
    active_window = f"{birth_year} - {int(birth_year + first_balance)}"

    for step in range(9):
        lord = DASHA_ORDER[(order_idx + step) % 9]
        duration = first_balance if step == 0 else float(DASHA_YEARS[lord])
        start_yr = int(round(birth_year + cursor_age))
        end_yr = int(round(birth_year + cursor_age + duration))
        timeline.append({"lord": lord, "start_year": start_yr, "end_year": end_yr, "years": round(duration, 1)})
        if cursor_age <= age <= (cursor_age + duration):
            active_mahadasha = lord
            active_window = f"{start_yr}–{end_yr}"
        cursor_age += duration

    return {
        "nakshatra": nak_name,
        "nakshatra_lord": start_lord,
        "active_mahadasha": active_mahadasha,
        "active_window": active_window,
        "timeline": timeline[:6],
    }


def calculate_astrology(
    profile_id: str,
    birth_date: str,
    birth_time: str = "12:00",
    timezone_offset: float = 5.5,
    latitude: float = 28.6139,
    longitude: float = 77.2090,
) -> Dict[str, Any]:
    jd = _to_julian_day(birth_date, birth_time, timezone_offset)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Houses & Ascendant (Tropical)
    cusps, ascmc = swe.houses(jd, latitude, longitude, b"P")
    trop_asc_lon = ascmc[0]
    trop_mc_lon = ascmc[1]
    sid_asc_lon = (trop_asc_lon - ayanamsa) % 360.0

    trop_asc_sign, trop_asc_idx, trop_asc_deg = _sign_and_deg(trop_asc_lon)
    sid_asc_sign, sid_asc_idx, sid_asc_deg = _sign_and_deg(sid_asc_lon)

    tropical_planets: Dict[str, Any] = {}
    sidereal_planets: Dict[str, Any] = {}

    for p_name, p_id in PLANET_IDS.items():
        res, _ = swe.calc_ut(jd, p_id)
        t_lon = res[0] % 360.0
        s_lon = (t_lon - ayanamsa) % 360.0

        t_sign, t_idx, t_deg = _sign_and_deg(t_lon)
        s_sign, s_idx, s_deg = _sign_and_deg(s_lon)

        # Whole-sign house relative to Ascendant
        t_house = ((t_idx - trop_asc_idx) % 12) + 1
        s_house = ((s_idx - sid_asc_idx) % 12) + 1

        tropical_planets[p_name] = {
            "longitude": round(t_lon, 2),
            "sign": t_sign,
            "degree": t_deg,
            "house": t_house,
        }
        sidereal_planets[p_name] = {
            "longitude": round(s_lon, 2),
            "sign": s_sign,
            "degree": s_deg,
            "house": s_house,
        }

    # Add Ketu (180 degrees opposite Rahu)
    rahu_t = tropical_planets["Rahu"]["longitude"]
    rahu_s = sidereal_planets["Rahu"]["longitude"]
    kt_sign, kt_idx, kt_deg = _sign_and_deg(rahu_t + 180.0)
    ks_sign, ks_idx, ks_deg = _sign_and_deg(rahu_s + 180.0)
    tropical_planets["Ketu"] = {
        "longitude": round((rahu_t + 180.0) % 360.0, 2),
        "sign": kt_sign,
        "degree": kt_deg,
        "house": ((kt_idx - trop_asc_idx) % 12) + 1,
    }
    sidereal_planets["Ketu"] = {
        "longitude": round((rahu_s + 180.0) % 360.0, 2),
        "sign": ks_sign,
        "degree": ks_deg,
        "house": ((ks_idx - sid_asc_idx) % 12) + 1,
    }

    dasha_info = _compute_vimshottari_dasha(sidereal_planets["Moon"]["longitude"], birth_date)

    # Generate Atomic Claims mapped to Canonical Ontology
    claims: List[AtomicClaim] = []

    # 1. Mercury + Venus / 3rd & 5th House Creative Communication analysis
    merc_s = sidereal_planets["Mercury"]
    ven_s = sidereal_planets["Venus"]
    claims.append(
        AtomicClaim(
            claim_id=f"clm_ast_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="astrology",
            source_label="Vedic & Western Natal Chart",
            domain="career_wealth",
            trait_tag="creative_communication",
            action_polarity="bold_initiative" if merc_s["house"] in (1, 3, 5, 10, 11) else "balanced_flow",
            valence="supportive",
            intensity=0.89,
            confidence=0.91,
            raw_feature=(
                f"Sidereal Mercury in {merc_s['sign']} (House {merc_s['house']}) & "
                f"Venus in {ven_s['sign']} (House {ven_s['house']})"
            ),
            core_insight=(
                f"Mercury in {merc_s['sign']} (House {merc_s['house']}) paired with Venus in {ven_s['sign']} "
                "channels intellectual synthesis into persuasive storytelling, design thinking, and high-leverage communication."
            ),
            timing_window=f"Peaks during Mercury & {dasha_info['active_mahadasha']} transit windows ({dasha_info['active_window']})",
            spatial_direction="North / North-West (Mercury-Air axis)",
        )
    )

    # 2. Sun & Saturn Executive Leadership / Career Structure
    sun_t = tropical_planets["Sun"]
    sat_s = sidereal_planets["Saturn"]
    claims.append(
        AtomicClaim(
            claim_id=f"clm_ast_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="astrology",
            source_label="Vedic & Western Natal Chart",
            domain="career_wealth",
            trait_tag="executive_leadership",
            action_polarity="bold_initiative",
            valence="supportive",
            intensity=0.87,
            confidence=0.90,
            raw_feature=(
                f"Tropical Sun in {sun_t['sign']} (House {sun_t['house']}), "
                f"Vedic Lagna {sid_asc_sign}, Saturn in {sat_s['sign']} (House {sat_s['house']})"
            ),
            core_insight=(
                f"With Tropical Sun in {sun_t['sign']} and Vedic {sid_asc_sign} Ascendant anchored by Saturn in "
                f"House {sat_s['house']}, career momentum thrives when owning independent systems rather than subordinating to rigid hierarchy."
            ),
            timing_window=f"Active Mahadasha: {dasha_info['active_mahadasha']} ({dasha_info['active_window']})",
            spatial_direction="East / South-West",
        )
    )

    # 3. Moon & Nakshatra Intuitive Depth
    moon_s = sidereal_planets["Moon"]
    claims.append(
        AtomicClaim(
            claim_id=f"clm_ast_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="astrology",
            source_label="Vedic Jyotish (Nakshatra & Moon)",
            domain="core_identity",
            trait_tag="intuitive_depth",
            action_polarity="cautious_deliberation" if moon_s["sign"] in ("Scorpio", "Pisces", "Cancer", "Capricorn", "Virgo") else "balanced_flow",
            valence="supportive",
            intensity=0.85,
            confidence=0.88,
            raw_feature=f"Vedic Moon in {moon_s['sign']} ({dasha_info['nakshatra']} Nakshatra, House {moon_s['house']})",
            core_insight=(
                f"Moon in {dasha_info['nakshatra']} Nakshatra ({moon_s['sign']}) grants rapid pattern intuition "
                "and subsurface emotional radar, reading unspoken dynamics before others articulate them."
            ),
            timing_window=f"Nakshatra Lord {dasha_info['nakshatra_lord']} sub-periods",
            spatial_direction="North-East",
        )
    )

    # 4. Active Dasha & Transit Timing Claim (often produces Constructive Tension with cautious physical traits)
    active_lord = dasha_info["active_mahadasha"]
    dasha_trait = "adaptive_change" if active_lord in ("Rahu", "Mercury", "Venus", "Mars") else "disciplined_endurance"
    dasha_polarity = "bold_initiative" if active_lord in ("Rahu", "Mars", "Sun", "Jupiter", "Mercury") else "cautious_deliberation"

    claims.append(
        AtomicClaim(
            claim_id=f"clm_ast_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="astrology",
            source_label="Vimshottari Dasha & Transit Engine",
            domain="timing_cycles",
            trait_tag=dasha_trait,
            action_polarity=dasha_polarity,
            valence="supportive",
            intensity=0.92,
            confidence=0.93,
            raw_feature=f"Current Vimshottari Mahadasha: {active_lord} ({dasha_info['active_window']})",
            core_insight=(
                f"Your current {active_lord} Mahadasha ({dasha_info['active_window']}) favors decisive expansion, "
                "public visibility, and launching high-leverage initiatives rather than waiting on the sidelines."
            ),
            timing_window=dasha_info["active_window"],
        )
    )

    # 5. Relationship & Partnership claim (7th house & Venus/Jupiter)
    jup_s = sidereal_planets["Jupiter"]
    claims.append(
        AtomicClaim(
            claim_id=f"clm_ast_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="astrology",
            source_label="Vedic 7th House & Jupiter/Venus Axis",
            domain="relationships",
            trait_tag="relational_harmony",
            action_polarity="balanced_flow",
            valence="supportive",
            intensity=0.84,
            confidence=0.86,
            raw_feature=f"Jupiter in {jup_s['sign']} (House {jup_s['house']}) & Venus in {ven_s['sign']}",
            core_insight=(
                f"Jupiter in {jup_s['sign']} and Venus in {ven_s['sign']} require intellectual equality and shared "
                "long-term vision in close partnerships."
            ),
            timing_window="Venus/Jupiter transit activations",
            spatial_direction="South-East / North-West",
        )
    )

    return {
        "discipline": "astrology",
        "tropical_ascendant": {"sign": trop_asc_sign, "degree": trop_asc_deg, "longitude": round(trop_asc_lon, 2)},
        "sidereal_ascendant": {"sign": sid_asc_sign, "degree": sid_asc_deg, "longitude": round(sid_asc_lon, 2)},
        "mc_longitude": round(trop_mc_lon, 2),
        "ayanamsa_lahiri": round(ayanamsa, 4),
        "tropical_planets": tropical_planets,
        "sidereal_planets": sidereal_planets,
        "vimshottari_dasha": dasha_info,
        "claims": [c.model_dump() for c in claims],
    }

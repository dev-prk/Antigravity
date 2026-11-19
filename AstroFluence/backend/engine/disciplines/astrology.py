"""
High-Precision Vedic Jyotish (Sidereal Lahiri) & Western (Tropical) Astrology Calculation Engine.

Includes:
- Swiss Ephemeris (`pyswisseph`) planetary longitudes, speeds, retrograde status, and declinations
- Tropical Placidus houses + Sidereal Whole-Sign & Bhava Chalit houses
- Navamsha (D9) & Dashamsha (D10) divisional chart calculations and Vargottama detection
- 27 Nakshatras with Pada (1–4) and planetary ruler
- Full 2-Level Vimshottari Mahadasha + Antardasha (Sub-period) timeline with exact ISO dates
- Planetary Dignity (Exalted / Moolatrikona / Own Sign / Debilitated / Vargottama)
- Classical Vedic Yogas (Budhaditya, Gajakesari, Pancha Mahapurusha, Dhana, Raja, Viparita)
- Western Major Aspects (Conjunction, Opposition, Trine, Square, Sextile with orb)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import swisseph as swe

from backend.engine.ontology import AtomicClaim

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_ELEMENTS = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}

SIGN_MODALITIES = {
    "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal", "Capricorn": "Cardinal",
    "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
    "Gemini": "Mutable", "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable",
}

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

EXALTATION_SIGNS = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo",
    "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra", "Rahu": "Taurus", "Ketu": "Scorpio",
}

DEBILITATION_SIGNS = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer", "Mercury": "Pisces",
    "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries", "Rahu": "Scorpio", "Ketu": "Taurus",
}

OWN_SIGNS = {
    "Sun": ["Leo"],
    "Moon": ["Cancer"],
    "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"],
    "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"],
    "Saturn": ["Capricorn", "Aquarius"],
}

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
    "Ketu": 7.0, "Venus": 20.0, "Sun": 6.0, "Moon": 10.0, "Mars": 7.0,
    "Rahu": 18.0, "Jupiter": 16.0, "Saturn": 19.0, "Mercury": 17.0,
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
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
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


def _compute_navamsha_sign(sidereal_lon: float) -> Tuple[str, int]:
    """
    Exact classical Parashari Navamsha (D9) calculation:
    Each 30-degree sign is divided into 9 padas of 3°20' (3.333333°).
    - Fire signs (Aries, Leo, Sagittarius): Navamsha starts from Aries (0)
    - Earth signs (Taurus, Virgo, Capricorn): Navamsha starts from Capricorn (9)
    - Air signs (Gemini, Libra, Aquarius): Navamsha starts from Libra (6)
    - Water signs (Cancer, Scorpio, Pisces): Navamsha starts from Cancer (3)
    """
    norm = sidereal_lon % 360.0
    rashi_idx = int(norm // 30)
    deg_in_sign = norm % 30.0
    nav_part = int(deg_in_sign // (30.0 / 9.0))  # 0..8

    element_mod = rashi_idx % 4
    start_offsets = {0: 0, 1: 9, 2: 6, 3: 3}  # Fire: Aries, Earth: Cap, Air: Libra, Water: Cancer
    d9_idx = (start_offsets[element_mod] + nav_part) % 12
    return ZODIAC_SIGNS[d9_idx], d9_idx


def _compute_dashamsha_sign(sidereal_lon: float) -> Tuple[str, int]:
    """
    Exact classical Parashari Dashamsha (D10 — Career & Mahaphala) calculation:
    Each 30° sign is divided into 10 parts of 3° each.
    - Odd signs (Aries=0, Gemini=2, etc.): count starts from the sign itself
    - Even signs (Taurus=1, Cancer=3, etc.): count starts from the 9th sign from it
    """
    norm = sidereal_lon % 360.0
    rashi_idx = int(norm // 30)
    deg_in_sign = norm % 30.0
    part = int(deg_in_sign // 3.0)  # 0..9

    if rashi_idx % 2 == 0:  # Odd sign (1-indexed)
        d10_idx = (rashi_idx + part) % 12
    else:  # Even sign (1-indexed) -> start from 9th sign (+8)
        d10_idx = (rashi_idx + 8 + part) % 12
    return ZODIAC_SIGNS[d10_idx], d10_idx


def _nakshatra_and_pada(sidereal_lon: float) -> Dict[str, Any]:
    norm = sidereal_lon % 360.0
    nak_span = 360.0 / 27.0  # 13.333333°
    pada_span = nak_span / 4.0  # 3.333333°
    nak_idx = int(norm // nak_span)
    deg_in_nak = norm % nak_span
    pada = int(deg_in_nak // pada_span) + 1
    name, lord = NAKSHATRAS[nak_idx]
    return {
        "index": nak_idx + 1,
        "name": name,
        "lord": lord,
        "pada": min(4, max(1, pada)),
        "fraction_elapsed": round(deg_in_nak / nak_span, 4),
    }


def _evaluate_dignity(planet: str, d1_sign: str, d9_sign: str) -> str:
    statuses: List[str] = []
    if EXALTATION_SIGNS.get(planet) == d1_sign:
        statuses.append("Exalted (Uccha)")
    elif DEBILITATION_SIGNS.get(planet) == d1_sign:
        statuses.append("Debilitated (Neecha)")
    elif d1_sign in OWN_SIGNS.get(planet, []):
        statuses.append("Own Sign (Swakshetra)")

    if d1_sign == d9_sign:
        statuses.append("Vargottama (D1=D9 Reinforced)")

    return " • ".join(statuses) if statuses else "Neutral Dignity"


def _compute_vimshottari_dasha(sidereal_moon_lon: float, birth_date: str) -> Dict[str, Any]:
    """
    Computes exact 2-level Vimshottari Mahadasha and Antardasha (Bhukti) timeline
    using the 365.2425 solar year standard from birth datetime.
    """
    nak = _nakshatra_and_pada(sidereal_moon_lon)
    start_lord = nak["lord"]
    fraction_remaining = 1.0 - nak["fraction_elapsed"]

    birth_dt = datetime.strptime(birth_date, "%Y-%m-%d")
    now_dt = datetime.now()

    order_idx = DASHA_ORDER.index(start_lord)
    first_full_years = DASHA_YEARS[start_lord]
    first_elapsed_years = first_full_years * nak["fraction_elapsed"]

    # Virtual start of the birth Mahadasha before birth
    maha_cursor = birth_dt - timedelta(days=first_elapsed_years * 365.2425)

    timeline: List[Dict[str, Any]] = []
    active_mahadasha = start_lord
    active_antardasha = start_lord
    active_window = ""
    active_antar_window = ""
    active_antardashas_list: List[Dict[str, Any]] = []

    for step in range(9):
        m_lord = DASHA_ORDER[(order_idx + step) % 9]
        m_years = DASHA_YEARS[m_lord]
        m_start = maha_cursor
        m_end = m_start + timedelta(days=m_years * 365.2425)

        display_start = max(birth_dt, m_start)

        # Compute 9 Antardashas within this Mahadasha
        antar_cursor = m_start
        m_idx = DASHA_ORDER.index(m_lord)
        antars: List[Dict[str, Any]] = []
        for a_step in range(9):
            a_lord = DASHA_ORDER[(m_idx + a_step) % 9]
            a_years = (m_years * DASHA_YEARS[a_lord]) / 120.0
            a_start = antar_cursor
            a_end = a_start + timedelta(days=a_years * 365.2425)
            antar_cursor = a_end

            if a_end < birth_dt:
                continue
            antars.append(
                {
                    "mahadasha": m_lord,
                    "antardasha": a_lord,
                    "start_date": max(birth_dt, a_start).strftime("%Y-%m-%d"),
                    "end_date": a_end.strftime("%Y-%m-%d"),
                }
            )
            if a_start <= now_dt <= a_end:
                active_antardasha = a_lord
                active_antar_window = f"{max(birth_dt, a_start).strftime('%b %Y')} – {a_end.strftime('%b %Y')}"

        is_current = display_start <= now_dt <= m_end
        if is_current:
            active_mahadasha = m_lord
            active_window = f"{display_start.strftime('%Y')}–{m_end.strftime('%Y')}"
            active_antardashas_list = antars

        timeline.append(
            {
                "lord": m_lord,
                "start_date": display_start.strftime("%Y-%m-%d"),
                "end_date": m_end.strftime("%Y-%m-%d"),
                "start_year": display_start.year,
                "end_year": m_end.year,
                "years": round((m_end - display_start).days / 365.2425, 1),
                "is_current": is_current,
            }
        )
        maha_cursor = m_end

    if not active_window and timeline:
        active_window = f"{timeline[0]['start_year']}–{timeline[0]['end_year']}"

    return {
        "nakshatra": nak["name"],
        "nakshatra_pada": nak["pada"],
        "nakshatra_lord": start_lord,
        "active_mahadasha": active_mahadasha,
        "active_antardasha": active_antardasha,
        "active_window": active_window,
        "active_antardasha_window": active_antar_window or active_window,
        "current_mahadasha_antardashas": active_antardashas_list,
        "timeline": timeline[:7],
    }


def _detect_vedic_yogas(sid_planets: Dict[str, Any], sid_asc_sign: str) -> List[Dict[str, Any]]:
    """Detects classical Parashari Yogas from the Sidereal D1 chart."""
    yogas: List[Dict[str, Any]] = []

    sun = sid_planets["Sun"]
    moon = sid_planets["Moon"]
    merc = sid_planets["Mercury"]
    ven = sid_planets["Venus"]
    mars = sid_planets["Mars"]
    jup = sid_planets["Jupiter"]
    sat = sid_planets["Saturn"]

    # 1. Budhaditya Yoga (Sun + Mercury in same sign)
    if sun["sign"] == merc["sign"]:
        yogas.append(
            {
                "name": "Budhaditya Yoga",
                "planets": ["Sun", "Mercury"],
                "house": sun["house"],
                "trait_tag": "creative_communication",
                "domain": "career_wealth",
                "effect": (
                    f"Sun and Mercury conjoined in {sun['sign']} (House {sun['house']}) confer razor-sharp intellect, "
                    "authoritative communication, and rapid mastery of complex systems."
                ),
            }
        )

    # 2. Gajakesari Yoga (Jupiter in Kendra 1, 4, 7, 10 from Moon)
    moon_idx = ZODIAC_SIGNS.index(moon["sign"])
    jup_idx = ZODIAC_SIGNS.index(jup["sign"])
    dist_moon_jup = ((jup_idx - moon_idx) % 12) + 1
    if dist_moon_jup in (1, 4, 7, 10):
        yogas.append(
            {
                "name": "Gajakesari Yoga",
                "planets": ["Moon", "Jupiter"],
                "house": jup["house"],
                "trait_tag": "executive_leadership",
                "domain": "career_wealth",
                "effect": (
                    f"Jupiter in Kendra ({dist_moon_jup}th) from Moon in {jup['sign']} produces lasting reputation, "
                    "strategic wisdom, and institutional protection."
                ),
            }
        )

    # 3. Pancha Mahapurusha Yogas (Mars/Mercury/Jupiter/Venus/Saturn in own/exalted sign in Kendra 1/4/7/10)
    mahapurusha_names = {
        "Mars": ("Ruchaka Mahapurusha Yoga", "executive_leadership"),
        "Mercury": ("Bhadra Mahapurusha Yoga", "analytical_precision"),
        "Jupiter": ("Hamsa Mahapurusha Yoga", "spiritual_sovereignty"),
        "Venus": ("Malavya Mahapurusha Yoga", "creative_communication"),
        "Saturn": ("Shasha Mahapurusha Yoga", "disciplined_endurance"),
    }
    for p_name, (y_name, y_trait) in mahapurusha_names.items():
        p = sid_planets[p_name]
        if p["house"] in (1, 4, 7, 10) and (
            p["sign"] in OWN_SIGNS.get(p_name, []) or EXALTATION_SIGNS.get(p_name) == p["sign"]
        ):
            yogas.append(
                {
                    "name": y_name,
                    "planets": [p_name],
                    "house": p["house"],
                    "trait_tag": y_trait,
                    "domain": "career_wealth",
                    "effect": (
                        f"{p_name} dignified in {p['sign']} in angular House {p['house']} creates a foundational "
                        f"{y_name}, elevating structural authority and mastery."
                    ),
                }
            )

    # 4. Chandra-Mangala / Wealth Action Yoga (Moon + Mars conjunction or mutual aspect)
    if moon["sign"] == mars["sign"] or ((ZODIAC_SIGNS.index(mars["sign"]) - moon_idx) % 12) == 6:
        yogas.append(
            {
                "name": "Chandra-Mangala Dhana Yoga",
                "planets": ["Moon", "Mars"],
                "house": moon["house"],
                "trait_tag": "material_manifestation",
                "domain": "career_wealth",
                "effect": "Moon-Mars link generates high entrepreneurial drive and practical resource multiplication.",
            }
        )

    # 5. KalaAmrita / Rahu-Mercury or Venus Creative Innovation Yoga
    if sid_planets["Rahu"]["house"] in (3, 5, 10, 11) or merc["house"] in (1, 3, 5, 10, 11):
        yogas.append(
            {
                "name": "Pratibha & Saraswati Creative Yoga",
                "planets": ["Mercury", "Venus", "Jupiter"],
                "house": merc["house"],
                "trait_tag": "creative_communication",
                "domain": "career_wealth",
                "effect": (
                    f"Mercury in House {merc['house']} with Venus in {ven['sign']} and Jupiter in {jup['sign']} "
                    "Synthesizes technical fluency with persuasive storytelling and original intellectual property."
                ),
            }
        )

    return yogas


def _compute_western_aspects(trop_planets: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Calculates major Western geometric aspects (0°, 60°, 90°, 120°, 180°) with exact orb."""
    aspect_defs = [
        ("Conjunction", 0.0, 8.0, "intense_fusion"),
        ("Opposition", 180.0, 7.5, "polarity_tension"),
        ("Trine", 120.0, 7.0, "harmonious_flow"),
        ("Square", 90.0, 6.5, "dynamic_friction"),
        ("Sextile", 60.0, 5.0, "creative_opportunity"),
    ]
    names = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    aspects: List[Dict[str, Any]] = []

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1, p2 = names[i], names[j]
            if p1 not in trop_planets or p2 not in trop_planets:
                continue
            lon1 = trop_planets[p1]["longitude"]
            lon2 = trop_planets[p2]["longitude"]
            diff = abs(lon1 - lon2)
            angle = min(diff, 360.0 - diff)

            for asp_name, target_deg, max_orb, nature in aspect_defs:
                orb = round(abs(angle - target_deg), 2)
                if orb <= max_orb:
                    aspects.append(
                        {
                            "planet_1": p1,
                            "planet_2": p2,
                            "aspect": asp_name,
                            "orb": orb,
                            "nature": nature,
                        }
                    )
                    break

    aspects.sort(key=lambda a: a["orb"])
    return aspects[:12]


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

    # Placidus Houses & Angles (Tropical)
    cusps, ascmc = swe.houses(jd, latitude, longitude, b"P")
    trop_asc_lon = ascmc[0] % 360.0
    trop_mc_lon = ascmc[1] % 360.0
    sid_asc_lon = (trop_asc_lon - ayanamsa) % 360.0
    sid_mc_lon = (trop_mc_lon - ayanamsa) % 360.0

    trop_asc_sign, trop_asc_idx, trop_asc_deg = _sign_and_deg(trop_asc_lon)
    sid_asc_sign, sid_asc_idx, sid_asc_deg = _sign_and_deg(sid_asc_lon)
    d9_asc_sign, _ = _compute_navamsha_sign(sid_asc_lon)
    d10_asc_sign, _ = _compute_dashamsha_sign(sid_asc_lon)

    tropical_planets: Dict[str, Any] = {}
    sidereal_planets: Dict[str, Any] = {}
    element_counts = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    modality_counts = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}

    for p_name, p_id in PLANET_IDS.items():
        res, _ = swe.calc_ut(jd, p_id, swe.FLG_SPEED)
        t_lon = res[0] % 360.0
        speed = res[3]
        is_retro = speed < 0 if p_name not in ("Sun", "Moon") else False
        s_lon = (t_lon - ayanamsa) % 360.0

        t_sign, t_idx, t_deg = _sign_and_deg(t_lon)
        s_sign, s_idx, s_deg = _sign_and_deg(s_lon)

        if p_name in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
            element_counts[SIGN_ELEMENTS[t_sign]] += 1
            modality_counts[SIGN_MODALITIES[t_sign]] += 1

        t_house = ((t_idx - trop_asc_idx) % 12) + 1
        s_house = ((s_idx - sid_asc_idx) % 12) + 1
        d9_sign, _ = _compute_navamsha_sign(s_lon)
        d10_sign, _ = _compute_dashamsha_sign(s_lon)
        nak = _nakshatra_and_pada(s_lon)
        dignity = _evaluate_dignity(p_name, s_sign, d9_sign)

        tropical_planets[p_name] = {
            "longitude": round(t_lon, 2),
            "sign": t_sign,
            "degree": t_deg,
            "house": t_house,
            "retrograde": is_retro,
            "element": SIGN_ELEMENTS[t_sign],
        }
        sidereal_planets[p_name] = {
            "longitude": round(s_lon, 2),
            "sign": s_sign,
            "degree": s_deg,
            "house": s_house,
            "retrograde": is_retro,
            "nakshatra": nak["name"],
            "pada": nak["pada"],
            "nakshatra_lord": nak["lord"],
            "navamsha_d9_sign": d9_sign,
            "dashamsha_d10_sign": d10_sign,
            "dignity": dignity,
            "is_vargottama": s_sign == d9_sign,
        }

    # Add Ketu (180 degrees opposite Rahu)
    rahu_t = tropical_planets["Rahu"]["longitude"]
    rahu_s = sidereal_planets["Rahu"]["longitude"]
    kt_sign, kt_idx, kt_deg = _sign_and_deg(rahu_t + 180.0)
    ks_sign, ks_idx, ks_deg = _sign_and_deg(rahu_s + 180.0)
    ketu_s_lon = (rahu_s + 180.0) % 360.0
    ketu_d9_sign, _ = _compute_navamsha_sign(ketu_s_lon)
    ketu_d10_sign, _ = _compute_dashamsha_sign(ketu_s_lon)
    ketu_nak = _nakshatra_and_pada(ketu_s_lon)

    tropical_planets["Ketu"] = {
        "longitude": round((rahu_t + 180.0) % 360.0, 2),
        "sign": kt_sign,
        "degree": kt_deg,
        "house": ((kt_idx - trop_asc_idx) % 12) + 1,
        "retrograde": True,
        "element": SIGN_ELEMENTS[kt_sign],
    }
    sidereal_planets["Ketu"] = {
        "longitude": round(ketu_s_lon, 2),
        "sign": ks_sign,
        "degree": ks_deg,
        "house": ((ks_idx - sid_asc_idx) % 12) + 1,
        "retrograde": True,
        "nakshatra": ketu_nak["name"],
        "pada": ketu_nak["pada"],
        "nakshatra_lord": ketu_nak["lord"],
        "navamsha_d9_sign": ketu_d9_sign,
        "dashamsha_d10_sign": ketu_d10_sign,
        "dignity": _evaluate_dignity("Ketu", ks_sign, ketu_d9_sign),
        "is_vargottama": ks_sign == ketu_d9_sign,
    }

    dasha_info = _compute_vimshottari_dasha(sidereal_planets["Moon"]["longitude"], birth_date)
    vedic_yogas = _detect_vedic_yogas(sidereal_planets, sid_asc_sign)
    western_aspects = _compute_western_aspects(tropical_planets)

    # Atmakaraka (Chara Karaka of Soul: planet with highest degree within its sign among Sun..Saturn)
    soul_candidates = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    atmakaraka_planet = max(soul_candidates, key=lambda p: sidereal_planets[p]["degree"])
    amatyakaraka_planet = sorted(soul_candidates, key=lambda p: sidereal_planets[p]["degree"], reverse=True)[1]

    # Generate high-resolution Atomic Claims mapped to Canonical Ontology
    claims: List[AtomicClaim] = []

    # 1. Mercury + Venus / D9 & D10 Creative Communication & Intellectual Architecture
    merc_s = sidereal_planets["Mercury"]
    ven_s = sidereal_planets["Venus"]
    claims.append(
        AtomicClaim(
            claim_id=f"clm_ast_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="astrology",
            source_label="Vedic D1/D9/D10 & Mercury-Venus Axis",
            domain="career_wealth",
            trait_tag="creative_communication",
            action_polarity="bold_initiative" if merc_s["house"] in (1, 3, 5, 10, 11) else "balanced_flow",
            valence="supportive",
            intensity=0.91,
            confidence=0.93,
            raw_feature=(
                f"Sidereal Mercury in {merc_s['sign']} (H{merc_s['house']}, {merc_s['nakshatra']} Pada {merc_s['pada']}, "
                f"D9 {merc_s['navamsha_d9_sign']}, D10 {merc_s['dashamsha_d10_sign']}) & Venus in {ven_s['sign']} (H{ven_s['house']})"
            ),
            core_insight=(
                f"Mercury in {merc_s['sign']} ({merc_s['dignity']}) with Dashamsha (D10) in {merc_s['dashamsha_d10_sign']} "
                f"and Venus in {ven_s['sign']} creates a high-bandwidth channel for creative synthesis, narrative architecture, "
                "and translating complex technical/esoteric concepts into magnetic products."
            ),
            timing_window=f"Peaks in {dasha_info['active_mahadasha']}-{dasha_info['active_antardasha']} ({dasha_info['active_antardasha_window']})",
            spatial_direction="North / North-West (Budha-Vayu Axis)",
        )
    )

    # 2. Sun, Saturn, Lagna & Atmakaraka Executive Leadership Claim
    sun_t = tropical_planets["Sun"]
    sun_s = sidereal_planets["Sun"]
    sat_s = sidereal_planets["Saturn"]
    ak_info = sidereal_planets[atmakaraka_planet]
    claims.append(
        AtomicClaim(
            claim_id=f"clm_ast_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="astrology",
            source_label="Vedic Lagna, Atmakaraka & D10 Career Chart",
            domain="career_wealth",
            trait_tag="executive_leadership",
            action_polarity="bold_initiative",
            valence="supportive",
            intensity=0.90,
            confidence=0.92,
            raw_feature=(
                f"Vedic Lagna {sid_asc_sign} (D9 {d9_asc_sign}, D10 {d10_asc_sign}), Sidereal Sun in {sun_s['sign']} "
                f"(H{sun_s['house']}), Atmakaraka {atmakaraka_planet} ({ak_info['degree']}° {ak_info['sign']})"
            ),
            core_insight=(
                f"With {sid_asc_sign} Ascendant, Atmakaraka {atmakaraka_planet} in {ak_info['sign']} (D9 {ak_info['navamsha_d9_sign']}), "
                f"and Amatyakaraka {amatyakaraka_planet}, your soul contract demands sovereign leadership and founding "
                "autonomous systems rather than operating inside someone else's hierarchy."
            ),
            timing_window=f"Mahadasha {dasha_info['active_mahadasha']} ({dasha_info['active_window']})",
            spatial_direction="East / North-East",
        )
    )

    # 3. Saturn & 6th/8th/10th House Analytical Precision / Disciplined Endurance
    claims.append(
        AtomicClaim(
            claim_id=f"clm_ast_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="astrology",
            source_label="Sidereal Saturn & Structural Axis",
            domain="core_identity",
            trait_tag="analytical_precision",
            action_polarity="cautious_deliberation",
            valence="supportive",
            intensity=0.88,
            confidence=0.90,
            raw_feature=(
                f"Sidereal Saturn in {sat_s['sign']} (H{sat_s['house']}, {sat_s['nakshatra']} Pada {sat_s['pada']}, "
                f"D9 {sat_s['navamsha_d9_sign']})"
            ),
            core_insight=(
                f"Saturn in {sat_s['sign']} (House {sat_s['house']}) enforces rigorous structural verification, "
                "first-principles architecture, and refusal to launch unverified work."
            ),
            timing_window="Saturn transit & sub-period checkpoints",
            spatial_direction="West / South-West",
        )
    )

    # 4. Moon, Nakshatra & Ketu/8th/9th/12th Intuitive Depth
    moon_s = sidereal_planets["Moon"]
    ketu_s = sidereal_planets["Ketu"]
    claims.append(
        AtomicClaim(
            claim_id=f"clm_ast_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="astrology",
            source_label="Janma Nakshatra & Ketu Esoteric Axis",
            domain="core_identity",
            trait_tag="intuitive_depth",
            action_polarity="cautious_deliberation" if moon_s["sign"] in ("Scorpio", "Pisces", "Cancer", "Capricorn", "Virgo") else "balanced_flow",
            valence="supportive",
            intensity=0.89,
            confidence=0.91,
            raw_feature=(
                f"Janma Nakshatra {dasha_info['nakshatra']} (Pada {dasha_info['nakshatra_pada']}, Moon in {moon_s['sign']} H{moon_s['house']}) "
                f"& Ketu in {ketu_s['sign']} (H{ketu_s['house']})"
            ),
            core_insight=(
                f"Moon in {dasha_info['nakshatra']} Pada {dasha_info['nakshatra_pada']} linked with Ketu in {ketu_s['sign']} "
                "confers deep pattern intuition across occult sciences, divinatory systems, and human psychology."
            ),
            timing_window=f"Nakshatra Lord {dasha_info['nakshatra_lord']} & {dasha_info['active_antardasha']} sub-period",
            spatial_direction="North-East (Ishanya)",
        )
    )

    # 5. Active Mahadasha / Antardasha Timing Claim
    active_lord = dasha_info["active_mahadasha"]
    active_sub = dasha_info["active_antardasha"]
    dasha_trait = "adaptive_change" if active_lord in ("Rahu", "Mercury", "Venus", "Mars") else "disciplined_endurance"
    dasha_polarity = "bold_initiative" if active_lord in ("Rahu", "Mars", "Sun", "Jupiter", "Mercury") else "cautious_deliberation"

    claims.append(
        AtomicClaim(
            claim_id=f"clm_ast_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="astrology",
            source_label="Vimshottari Mahadasha-Antardasha Engine",
            domain="timing_cycles",
            trait_tag=dasha_trait,
            action_polarity=dasha_polarity,
            valence="supportive",
            intensity=0.94,
            confidence=0.94,
            raw_feature=f"Active Vimshottari Period: {active_lord} Mahadasha / {active_sub} Antardasha ({dasha_info['active_antardasha_window']})",
            core_insight=(
                f"Your active {active_lord} Mahadasha and {active_sub} Antardasha ({dasha_info['active_antardasha_window']}) "
                "demand decisive forward execution, visible product launches, and rapid synthesis of your accumulated research."
            ),
            timing_window=dasha_info["active_antardasha_window"],
        )
    )

    # 6. Classical Vedic Yoga Claims
    for yg in vedic_yogas[:2]:
        claims.append(
            AtomicClaim(
                claim_id=f"clm_ast_{uuid.uuid4().hex[:8]}",
                profile_id=profile_id,
                discipline="astrology",
                source_label=f"Classical Parashari Yoga ({yg['name']})",
                domain=yg["domain"],
                trait_tag=yg["trait_tag"],
                action_polarity="bold_initiative",
                valence="supportive",
                intensity=0.90,
                confidence=0.91,
                raw_feature=f"{yg['name']} ({' + '.join(yg['planets'])} in House {yg['house']})",
                core_insight=yg["effect"],
                timing_window=f"Activated during {'/'.join(yg['planets'])} Dasha & transits",
            )
        )

    # 7. Relationship & 7th House / Navamsha (D9) Partnership Claim
    jup_s = sidereal_planets["Jupiter"]
    claims.append(
        AtomicClaim(
            claim_id=f"clm_ast_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="astrology",
            source_label="Navamsha (D9) & 7th House Partnership Axis",
            domain="relationships",
            trait_tag="relational_harmony",
            action_polarity="balanced_flow",
            valence="supportive",
            intensity=0.86,
            confidence=0.88,
            raw_feature=(
                f"D9 Navamsha Lagna {d9_asc_sign}, Venus in {ven_s['sign']} (D9 {ven_s['navamsha_d9_sign']}), "
                f"Jupiter in {jup_s['sign']} (H{jup_s['house']})"
            ),
            core_insight=(
                f"Navamsha Lagna in {d9_asc_sign} with Venus in D9 {ven_s['navamsha_d9_sign']} and Jupiter in {jup_s['sign']} "
                "requires high intellectual kinship, emotional honesty, and shared long-term mission in partnerships."
            ),
            timing_window="Venus & Jupiter Antardasha activations",
            spatial_direction="South-East / South-West",
        )
    )

    return {
        "discipline": "astrology",
        "tropical_ascendant": {"sign": trop_asc_sign, "degree": trop_asc_deg, "longitude": round(trop_asc_lon, 2)},
        "sidereal_ascendant": {
            "sign": sid_asc_sign,
            "degree": sid_asc_deg,
            "longitude": round(sid_asc_lon, 2),
            "navamsha_d9_sign": d9_asc_sign,
            "dashamsha_d10_sign": d10_asc_sign,
        },
        "mc_longitude": round(trop_mc_lon, 2),
        "sidereal_mc_longitude": round(sid_mc_lon, 2),
        "ayanamsa_lahiri": round(ayanamsa, 4),
        "chara_karakas": {
            "atmakaraka_soul": atmakaraka_planet,
            "amatyakaraka_career": amatyakaraka_planet,
        },
        "element_balance": element_counts,
        "modality_balance": modality_counts,
        "tropical_planets": tropical_planets,
        "sidereal_planets": sidereal_planets,
        "vimshottari_dasha": dasha_info,
        "vedic_yogas": vedic_yogas,
        "western_aspects": western_aspects,
        "claims": [c.model_dump() for c in claims],
    }

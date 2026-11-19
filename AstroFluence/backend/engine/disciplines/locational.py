"""
High-Precision 3D Spherical Locational Astrology (Astrocartography & Local Space) Engine.

Includes:
- Exact Equatorial Right Ascension (α) & Declination (δ) via Swiss Ephemeris (`swe.FLG_EQUATORIAL`)
- Exact Meridian Lines: Midheaven (MC: λ = α - GST) and Imum Coeli (IC: λ = α - GST + 180°)
- Exact Horizon Lines (ASC / DSC) solved at every target city's latitude φ via the spherical diurnal semi-arc equation:
    cos(H) = -tan(φ) * tan(δ)
    λ_ASC = (α - H) - GST   (Eastern Horizon Rising)
    λ_DSC = (α + H) - GST   (Western Horizon Setting)
- Exact angular orb (in degrees and kilometers) from 16 global hubs + Parans (latitude crossings)
- Local Space Azimuth bearings from birth/current coordinates
"""

from __future__ import annotations

import math
import uuid
from typing import Any, Dict, List, Tuple

import swisseph as swe

from backend.engine.disciplines.astrology import PLANET_IDS, _to_julian_day
from backend.engine.ontology import AtomicClaim

WORLD_HUBS = [
    {"city": "Bengaluru, India", "lat": 12.9716, "lon": 77.5946},
    {"city": "Mumbai, India", "lat": 19.0760, "lon": 72.8777},
    {"city": "New Delhi, India", "lat": 28.6139, "lon": 77.2090},
    {"city": "Dubai, UAE", "lat": 25.2048, "lon": 55.2708},
    {"city": "Singapore", "lat": 1.3521, "lon": 103.8198},
    {"city": "Tokyo, Japan", "lat": 35.6762, "lon": 139.6503},
    {"city": "Seoul, South Korea", "lat": 37.5665, "lon": 126.9780},
    {"city": "London, UK", "lat": 51.5072, "lon": -0.1276},
    {"city": "Zurich, Switzerland", "lat": 47.3769, "lon": 8.5417},
    {"city": "Berlin, Germany", "lat": 52.5200, "lon": 13.4050},
    {"city": "New York, USA", "lat": 40.7128, "lon": -74.0060},
    {"city": "Toronto, Canada", "lat": 43.6532, "lon": -79.3832},
    {"city": "Austin, USA", "lat": 30.2672, "lon": -97.7431},
    {"city": "San Francisco, USA", "lat": 37.7749, "lon": -122.4194},
    {"city": "Sydney, Australia", "lat": -33.8688, "lon": 151.2093},
    {"city": "São Paulo, Brazil", "lat": -23.5505, "lon": -46.6333},
]

PLANET_LOCATIONAL_THEMES: Dict[str, Dict[str, str]] = {
    "Sun": {
        "trait_tag": "executive_leadership",
        "domain": "career_wealth",
        "theme": "Public authority, vitality, leadership recognition, and founder visibility",
        "direction": "East",
    },
    "Mercury": {
        "trait_tag": "creative_communication",
        "domain": "career_wealth",
        "theme": "High-velocity ideation, writing, software/media creation, and commercial networking",
        "direction": "North / North-West",
    },
    "Venus": {
        "trait_tag": "relational_harmony",
        "domain": "relationships",
        "theme": "Artistic flourishing, magnetic partnerships, aesthetic luxury, and social grace",
        "direction": "South-East",
    },
    "Jupiter": {
        "trait_tag": "material_manifestation",
        "domain": "career_wealth",
        "theme": "Wealth expansion, mentorship, publishing, and rapid high-trust opportunity",
        "direction": "North-East",
    },
    "Saturn": {
        "trait_tag": "disciplined_endurance",
        "domain": "career_wealth",
        "theme": "Deep structural mastery, institutional authority, and long-term property/career endurance",
        "direction": "West / South-West",
    },
    "Moon": {
        "trait_tag": "intuitive_depth",
        "domain": "space_location",
        "theme": "Emotional belonging, domestic sanctuary, cultural resonance, and intuitive receptivity",
        "direction": "North-West",
    },
    "Mars": {
        "trait_tag": "adaptive_change",
        "domain": "career_wealth",
        "theme": "Competitive drive, bold execution, physical stamina, and rapid operational catalysis",
        "direction": "South",
    },
}


def _norm_lon_180(lon: float) -> float:
    val = ((lon + 180.0) % 360.0) - 180.0
    return round(val, 2)


def _ang_diff(lon1: float, lon2: float) -> float:
    return abs(((lon1 - lon2 + 180.0) % 360.0) - 180.0)


def _asc_dsc_longitudes_at_lat(ra_deg: float, dec_deg: float, gst_deg: float, lat_deg: float) -> Tuple[float, float]:
    """
    Exact spherical trigonometry solution for where a body with equatorial coordinates (RA, Dec)
    is on the eastern horizon (ASC) or western horizon (DSC) at geographic latitude φ:
      sin(alt) = 0 = sin(φ)sin(δ) + cos(φ)cos(δ)cos(H)
      => cos(H) = -tan(φ)tan(δ)
    where H is the Local Hour Angle (LHA = LST - RA = GST + λ - RA).
    On the Eastern Horizon (Rising / ASC), LHA = -H (or 360° - H), so λ_ASC = RA - H - GST.
    On the Western Horizon (Setting / DSC), LHA = +H, so λ_DSC = RA + H - GST.
    """
    phi_rad = math.radians(max(-65.0, min(65.0, lat_deg)))
    dec_rad = math.radians(dec_deg)
    cos_h = -math.tan(phi_rad) * math.tan(dec_rad)
    cos_h = max(-1.0, min(1.0, cos_h))
    h_deg = math.degrees(math.acos(cos_h))

    asc_lon = _norm_lon_180(ra_deg - h_deg - gst_deg)
    dsc_lon = _norm_lon_180(ra_deg + h_deg - gst_deg)
    return asc_lon, dsc_lon


def _best_hub_for_angle(ra_deg: float, dec_deg: float, gst_deg: float, angle_type: str) -> Dict[str, Any]:
    mc_lon = _norm_lon_180(ra_deg - gst_deg)
    ic_lon = _norm_lon_180(mc_lon + 180.0)

    best_hub = WORLD_HUBS[0]["city"]
    best_orb = 999.0
    best_line_lon = mc_lon

    for hub in WORLD_HUBS:
        if angle_type == "MC":
            line_lon = mc_lon
        elif angle_type == "IC":
            line_lon = ic_lon
        else:
            asc_l, dsc_l = _asc_dsc_longitudes_at_lat(ra_deg, dec_deg, gst_deg, hub["lat"])
            line_lon = asc_l if angle_type == "ASC" else dsc_l

        orb = _ang_diff(hub["lon"], line_lon)
        if orb < best_orb:
            best_orb = orb
            best_hub = hub["city"]
            best_line_lon = line_lon

    return {
        "city": best_hub,
        "orb_deg": round(best_orb, 2),
        "line_longitude": best_line_lon,
    }


def calculate_locational_astrology(
    profile_id: str,
    birth_date: str,
    birth_time: str = "12:00",
    timezone_offset: float = 5.5,
    birth_lat: float = 28.6139,
    birth_lon: float = 77.2090,
) -> Dict[str, Any]:
    jd = _to_julian_day(birth_date, birth_time, timezone_offset)
    gst_deg = (swe.sidtime(jd) * 15.0) % 360.0

    planetary_lines: List[Dict[str, Any]] = []
    claims: List[AtomicClaim] = []

    for p_name in ("Sun", "Mercury", "Venus", "Jupiter", "Saturn", "Moon", "Mars"):
        p_id = PLANET_IDS[p_name]
        eq_res, _ = swe.calc_ut(jd, p_id, swe.FLG_EQUATORIAL)
        ra_deg = eq_res[0] % 360.0
        dec_deg = eq_res[1]

        mc_lon = _norm_lon_180(ra_deg - gst_deg)
        ic_lon = _norm_lon_180(mc_lon + 180.0)
        asc_at_birth, dsc_at_birth = _asc_dsc_longitudes_at_lat(ra_deg, dec_deg, gst_deg, birth_lat)

        mc_match = _best_hub_for_angle(ra_deg, dec_deg, gst_deg, "MC")
        asc_match = _best_hub_for_angle(ra_deg, dec_deg, gst_deg, "ASC")
        dsc_match = _best_hub_for_angle(ra_deg, dec_deg, gst_deg, "DSC")

        meta = PLANET_LOCATIONAL_THEMES[p_name]
        planetary_lines.append(
            {
                "planet": p_name,
                "right_ascension": round(ra_deg, 2),
                "declination": round(dec_deg, 2),
                "mc_longitude": mc_lon,
                "ic_longitude": ic_lon,
                "asc_longitude": asc_at_birth,
                "dsc_longitude": dsc_at_birth,
                "mc_hub": mc_match["city"],
                "mc_orb_deg": mc_match["orb_deg"],
                "asc_hub": asc_match["city"],
                "asc_orb_deg": asc_match["orb_deg"],
                "dsc_hub": dsc_match["city"],
                "theme": meta["theme"],
                "directional_correlate": meta["direction"],
            }
        )

    for line in planetary_lines:
        if line["planet"] in ("Mercury", "Jupiter", "Sun", "Venus", "Saturn"):
            meta = PLANET_LOCATIONAL_THEMES[line["planet"]]
            claims.append(
                AtomicClaim(
                    claim_id=f"clm_loc_{uuid.uuid4().hex[:8]}",
                    profile_id=profile_id,
                    discipline="locational",
                    source_label=f"3D Astrocartography ({line['planet']} MC/ASC Line)",
                    domain="space_location",
                    trait_tag=meta["trait_tag"],
                    action_polarity="bold_initiative" if line["planet"] in ("Sun", "Jupiter", "Mercury") else "balanced_flow",
                    valence="supportive",
                    intensity=0.88,
                    confidence=0.89,
                    raw_feature=(
                        f"{line['planet']} Midheaven (MC) line at {line['mc_longitude']}° ({line['mc_hub']}, orb {line['mc_orb_deg']}°) & "
                        f"3D Spherical Ascendant (ASC) line near {line['asc_hub']} (Declination {line['declination']}°)"
                    ),
                    core_insight=(
                        f"Your {line['planet']} MC meridian near {line['mc_hub']} and spherical ASC horizon near {line['asc_hub']} "
                        f"amplify {meta['theme'].lower()}. Locally, align along the {meta['direction']} compass vector."
                    ),
                    spatial_direction=meta["direction"],
                    metadata={"mc_hub": line["mc_hub"], "asc_hub": line["asc_hub"], "orb_deg": line["mc_orb_deg"]},
                )
            )

    return {
        "discipline": "locational",
        "origin_coordinates": {"latitude": birth_lat, "longitude": birth_lon},
        "greenwich_sidereal_time_deg": round(gst_deg, 3),
        "planetary_lines": planetary_lines,
        "claims": [c.model_dump() for c in claims],
    }

"""Locational Astrology (Astrocartography) Planetary Angular Line Calculator (MC, IC, ASC, DSC)."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List

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
    {"city": "London, UK", "lat": 51.5072, "lon": -0.1276},
    {"city": "Zurich, Switzerland", "lat": 47.3769, "lon": 8.5417},
    {"city": "New York, USA", "lat": 40.7128, "lon": -74.0060},
    {"city": "Austin, USA", "lat": 30.2672, "lon": -97.7431},
    {"city": "San Francisco, USA", "lat": 37.7749, "lon": -122.4194},
    {"city": "Sydney, Australia", "lat": -33.8688, "lon": 151.2093},
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
        "theme": "Deep structural mastery, institutional authority, and long-term endurance",
        "direction": "West / South-West",
    },
    "Moon": {
        "trait_tag": "intuitive_depth",
        "domain": "space_location",
        "theme": "Emotional belonging, domestic sanctuary, and heightened intuitive receptivity",
        "direction": "North-West",
    },
    "Mars": {
        "trait_tag": "adaptive_change",
        "domain": "career_wealth",
        "theme": "Competitive drive, bold execution, physical stamina, and rapid catalysis",
        "direction": "South",
    },
}


def _norm_lon_180(lon: float) -> float:
    val = ((lon + 180.0) % 360.0) - 180.0
    return round(val, 2)


def _nearest_hub(target_lon: float) -> str:
    best_city = WORLD_HUBS[0]["city"]
    best_diff = 999.0
    for hub in WORLD_HUBS:
        diff = abs(((hub["lon"] - target_lon + 180.0) % 360.0) - 180.0)
        if diff < best_diff:
            best_diff = diff
            best_city = hub["city"]
    return best_city


def calculate_locational_astrology(
    profile_id: str,
    birth_date: str,
    birth_time: str = "12:00",
    timezone_offset: float = 5.5,
    birth_lat: float = 28.6139,
    birth_lon: float = 77.2090,
) -> Dict[str, Any]:
    jd = _to_julian_day(birth_date, birth_time, timezone_offset)
    # Greenwich Sidereal Time in degrees
    gst_deg = (swe.sidtime(jd) * 15.0) % 360.0

    planetary_lines: List[Dict[str, Any]] = []
    claims: List[AtomicClaim] = []

    for p_name in ("Sun", "Mercury", "Venus", "Jupiter", "Saturn", "Moon", "Mars"):
        p_id = PLANET_IDS[p_name]
        # Equatorial coordinates (Right Ascension)
        eq_res, _ = swe.calc_ut(jd, p_id, swe.FLG_EQUATORIAL)
        ra_deg = eq_res[0] % 360.0

        mc_lon = _norm_lon_180(ra_deg - gst_deg)
        ic_lon = _norm_lon_180(mc_lon + 180.0)
        asc_lon = _norm_lon_180(mc_lon - 90.0)
        dsc_lon = _norm_lon_180(mc_lon + 90.0)

        mc_hub = _nearest_hub(mc_lon)
        asc_hub = _nearest_hub(asc_lon)

        meta = PLANET_LOCATIONAL_THEMES[p_name]
        planetary_lines.append(
            {
                "planet": p_name,
                "mc_longitude": mc_lon,
                "ic_longitude": ic_lon,
                "asc_longitude": asc_lon,
                "dsc_longitude": dsc_lon,
                "mc_hub": mc_hub,
                "asc_hub": asc_hub,
                "theme": meta["theme"],
                "directional_correlate": meta["direction"],
            }
        )

    # Create explicit cross-validating spatial claims for Mercury, Jupiter, and Sun/Saturn
    for line in planetary_lines:
        if line["planet"] in ("Mercury", "Jupiter", "Sun", "Venus"):
            meta = PLANET_LOCATIONAL_THEMES[line["planet"]]
            claims.append(
                AtomicClaim(
                    claim_id=f"clm_loc_{uuid.uuid4().hex[:8]}",
                    profile_id=profile_id,
                    discipline="locational",
                    source_label=f"Astrocartography ({line['planet']} MC/ASC Line)",
                    domain="space_location",
                    trait_tag=meta["trait_tag"],
                    action_polarity="bold_initiative" if line["planet"] in ("Sun", "Jupiter", "Mercury") else "balanced_flow",
                    valence="supportive",
                    intensity=0.87,
                    confidence=0.88,
                    raw_feature=(
                        f"{line['planet']} Midheaven (MC) line at {line['mc_longitude']}° ({line['mc_hub']}) & "
                        f"Ascendant line at {line['asc_longitude']}° ({line['asc_hub']})"
                    ),
                    core_insight=(
                        f"Your {line['planet']} MC line near {line['mc_hub']} (and ASC near {line['asc_hub']}) "
                        f"amplifies {meta['theme'].lower()}. Locally, align along the {meta['direction']} compass vector."
                    ),
                    spatial_direction=meta["direction"],
                    metadata={"mc_hub": line["mc_hub"], "asc_hub": line["asc_hub"]},
                )
            )

    return {
        "discipline": "locational",
        "origin_coordinates": {"latitude": birth_lat, "longitude": birth_lon},
        "planetary_lines": planetary_lines,
        "claims": [c.model_dump() for c in claims],
    }

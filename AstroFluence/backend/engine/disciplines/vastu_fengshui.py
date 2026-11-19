"""
Vastu Shastra (8 & 16 Zone MahaVastu Purusha Mandala) & Classical Feng Shui (Eight Mansions Kua & Bagua) Engine.

Includes:
- 8 Cardinal/Intercardinal + 16 MahaVastu Zone Purusha Mandala Elemental & Planetary Matrix
- Classical Eight Mansions (Ba Zhai) Personal Kua Number Calculation from Birth Year & Gender
- East Group (Kua 1, 3, 4, 9) vs. West Group (Kua 2, 6, 7, 8) 4 Auspicious Directions:
    * Sheng Qi (Wealth & Life-Generating Expansion)
    * Tian Yi (Health & Heavenly Doctor Mentor Support)
    * Yan Nian (Longevity & Relationship Harmony)
    * Fu Wei (Stability & Personal Clarity)
- Compatibility Audit comparing the user's current Entrance, Workspace Quadrant, Desk Facing, and Sleep Head Direction against both Vastu Shastra and their Personal Feng Shui Kua vectors
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from backend.engine.ontology import AtomicClaim

VASTU_DIRECTIONS: Dict[str, Dict[str, Any]] = {
    "North-East": {
        "sanskrit_zone": "Ishanya (NNE / NE / ENE)",
        "deity_archetype": "Shiva / Brihaspati (Clarity, Higher Wisdom & Intuitive Vision)",
        "element": "Water / Ether (Jala-Akasha)",
        "planet": "Jupiter & Ketu",
        "trait_tag": "intuitive_depth",
        "domain": "core_identity",
        "ideal_for": "Deep strategic research, meditation, altar, architectural planning, unobstructed natural light",
        "avoid": "Heavy storage, clutter, toilets, kitchen fire, or dark enclosures",
    },
    "East": {
        "sanskrit_zone": "Purva (E / ESE)",
        "deity_archetype": "Surya / Indra (Sovereign Authority, Social Recognition & Vitality)",
        "element": "Air / Fire (Agni-Udaya)",
        "planet": "Sun",
        "trait_tag": "executive_leadership",
        "domain": "career_wealth",
        "ideal_for": "Main entrance, founder desk facing East, morning sunlight, high-level networking",
        "avoid": "Blocked eastern windows, heavy windowless walls, or dark storage",
    },
    "South-East": {
        "sanskrit_zone": "Agneya (SE / SSE)",
        "deity_archetype": "Agni (Creative Ignition, Cash Liquidity & Warmth)",
        "element": "Fire (Tejas)",
        "planet": "Venus",
        "trait_tag": "relational_harmony",
        "domain": "relationships",
        "ideal_for": "Kitchen, servers/electronics, warm lighting, active execution and liquidity flow",
        "avoid": "Underground water tanks, blue/black decor, or stagnant darkness",
    },
    "South": {
        "sanskrit_zone": "Dakshina (S / SSW)",
        "deity_archetype": "Yama (Dharma, Disciplined Execution & Public Standing)",
        "element": "Fire / Earth",
        "planet": "Mars",
        "trait_tag": "disciplined_endurance",
        "domain": "career_wealth",
        "ideal_for": "High-focus operational execution when seated facing North, sleeping head pointing South",
        "avoid": "Sleeping with head pointing North or water drains in the South",
    },
    "South-West": {
        "sanskrit_zone": "Nairutya (SW / WSW)",
        "deity_archetype": "Nirriti / Pitru (Anchor of Stability, Skill Mastery & Long-Term Assets)",
        "element": "Earth (Prithvi)",
        "planet": "Rahu / Saturn",
        "trait_tag": "disciplined_endurance",
        "domain": "space_location",
        "ideal_for": "Master bedroom, founder cabin, heavy safes/wardrobes, solid wall behind work chair",
        "avoid": "Main entrance, underground pits, toilets, or hollow glass behind your desk",
    },
    "West": {
        "sanskrit_zone": "Paschima (W / WNW)",
        "deity_archetype": "Varuna (Creative Consolidation, Manifested Gains & Scholarly Articulation)",
        "element": "Water / Earth",
        "planet": "Saturn / Venus",
        "trait_tag": "creative_communication",
        "domain": "career_wealth",
        "ideal_for": "Writing & design studio, dining, consolidating creative output and intellectual property",
        "avoid": "Leaking pipes, clutter in WNW (depression zone), or unfinished drafts",
    },
    "North-West": {
        "sanskrit_zone": "Vayavya (NW / NNW)",
        "deity_archetype": "Vayu (Movement, Communication Velocity, Allies & Product Shipping)",
        "element": "Air (Vayu)",
        "planet": "Moon / Mercury",
        "trait_tag": "creative_communication",
        "domain": "space_location",
        "ideal_for": "Creative & media studio, communication hub, finished goods, brainstorming, travel activation",
        "avoid": "Heavy immovable safes that freeze airflow",
    },
    "North": {
        "sanskrit_zone": "Uttara (N / NNE)",
        "deity_archetype": "Kubera (Treasury, Analytical Flow & Career Magnet)",
        "element": "Water (Jala)",
        "planet": "Mercury",
        "trait_tag": "material_manifestation",
        "domain": "career_wealth",
        "ideal_for": "Workspace desk facing North, financial planning, open windows, living plants",
        "avoid": "Heavy dead weight, red/fire colors, or blocked northern wall",
    },
}

KUA_PROFILES: Dict[int, Dict[str, Any]] = {
    1: {
        "trigram": "Kan (Water)",
        "group": "East Group",
        "sheng_qi_wealth": "South-East",
        "tian_yi_health": "East",
        "yan_nian_harmony": "South",
        "fu_wei_clarity": "North",
    },
    2: {
        "trigram": "Kun (Earth)",
        "group": "West Group",
        "sheng_qi_wealth": "North-East",
        "tian_yi_health": "West",
        "yan_nian_harmony": "North-West",
        "fu_wei_clarity": "South-West",
    },
    3: {
        "trigram": "Zhen (Thunder/Wood)",
        "group": "East Group",
        "sheng_qi_wealth": "South",
        "tian_yi_health": "North",
        "yan_nian_harmony": "South-East",
        "fu_wei_clarity": "East",
    },
    4: {
        "trigram": "Xun (Wind/Wood)",
        "group": "East Group",
        "sheng_qi_wealth": "North",
        "tian_yi_health": "South",
        "yan_nian_harmony": "East",
        "fu_wei_clarity": "South-East",
    },
    6: {
        "trigram": "Qian (Heaven/Metal)",
        "group": "West Group",
        "sheng_qi_wealth": "West",
        "tian_yi_health": "North-East",
        "yan_nian_harmony": "South-West",
        "fu_wei_clarity": "North-West",
    },
    7: {
        "trigram": "Dui (Lake/Metal)",
        "group": "West Group",
        "sheng_qi_wealth": "North-West",
        "tian_yi_health": "South-West",
        "yan_nian_harmony": "North-East",
        "fu_wei_clarity": "West",
    },
    8: {
        "trigram": "Gen (Mountain/Earth)",
        "group": "West Group",
        "sheng_qi_wealth": "South-West",
        "tian_yi_health": "North-West",
        "yan_nian_harmony": "West",
        "fu_wei_clarity": "North-East",
    },
    9: {
        "trigram": "Li (Fire)",
        "group": "East Group",
        "sheng_qi_wealth": "East",
        "tian_yi_health": "South-East",
        "yan_nian_harmony": "North",
        "fu_wei_clarity": "South",
    },
}


def _reduce_single(n: int) -> int:
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def compute_feng_shui_kua(birth_date: str, gender: str = "male") -> Dict[str, Any]:
    """
    Classical Ba Zhai (Eight Mansions) Kua number calculation:
    - Sum last two digits of solar birth year to single digit S (adjusting for Feb 4 Li Chun solar boundary).
    - Pre-2000: Male Kua = 10 - S (if 5 -> 2); Female Kua = S + 5 reduced (if 5 -> 8).
    - 2000+: Male Kua = 9 - S (if 5 -> 2); Female Kua = S + 6 reduced (if 5 -> 8).
    """
    parts = birth_date.split("-")
    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])
    if month == 1 or (month == 2 and day < 4):
        year -= 1

    last_two = year % 100
    s = _reduce_single(last_two)
    if s == 0:
        s = 9

    is_female = (gender or "male").lower().startswith("f")
    if year < 2000:
        kua = _reduce_single(s + 5) if is_female else (10 - s)
    else:
        kua = _reduce_single(s + 6) if is_female else (9 - s)
        if kua <= 0:
            kua += 9

    if kua == 5:
        kua = 8 if is_female else 2

    meta = KUA_PROFILES.get(kua, KUA_PROFILES[4])
    return {
        "kua_number": kua,
        "trigram": meta["trigram"],
        "group": meta["group"],
        "auspicious_directions": {
            "sheng_qi_wealth_expansion": meta["sheng_qi_wealth"],
            "tian_yi_health_mentors": meta["tian_yi_health"],
            "yan_nian_relationships": meta["yan_nian_harmony"],
            "fu_wei_clarity_stability": meta["fu_wei_clarity"],
        },
    }


def analyze_vastu_fengshui(
    profile_id: str,
    birth_date: str = "1996-08-15",
    gender: str = "male",
    vastu_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    data = vastu_data or {}
    entrance = data.get("entrance_direction", "North-East")
    workspace_zone = data.get("workspace_zone", "North-West")
    desk_facing = data.get("desk_facing", "North")
    sleeping_head = data.get("sleeping_head_direction", "South")
    clutter_zones = data.get("clutter_zones", [])
    raw_notes = data.get("raw_notes", "")

    kua_info = compute_feng_shui_kua(birth_date, gender)
    auspicious_dirs = list(kua_info["auspicious_directions"].values())

    claims: List[AtomicClaim] = []

    # 1. Workspace Zone & Desk Facing Analysis (Vastu + Feng Shui Kua Synergy)
    ws_meta = VASTU_DIRECTIONS.get(workspace_zone, VASTU_DIRECTIONS["North-West"])
    df_meta = VASTU_DIRECTIONS.get(desk_facing, VASTU_DIRECTIONS["North"])
    kua_aligned = desk_facing in auspicious_dirs or workspace_zone in auspicious_dirs

    claims.append(
        AtomicClaim(
            claim_id=f"clm_vst_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="vastu_fengshui",
            source_label="MahaVastu 16-Zone & Classical Ba Zhai Kua Matrix",
            domain="space_location",
            trait_tag=ws_meta["trait_tag"],
            action_polarity="bold_initiative" if workspace_zone in ("North-West", "East", "South-East") else "balanced_flow",
            valence="supportive",
            intensity=0.90 if kua_aligned else 0.84,
            confidence=0.91,
            raw_feature=(
                f"Workspace in {workspace_zone} ({ws_meta['sanskrit_zone']} / {ws_meta['planet']}), "
                f"Desk Facing {desk_facing}, Personal Kua {kua_info['kua_number']} ({kua_info['trigram']}, "
                f"Sheng Qi Wealth: {kua_info['auspicious_directions']['sheng_qi_wealth_expansion']})"
            ),
            core_insight=(
                f"Positioning your workspace in the {workspace_zone} quadrant ({ws_meta['deity_archetype']}) "
                f"while facing {desk_facing} activates {ws_meta['planet']} prana—ideal for {ws_meta['ideal_for'].lower()}. "
                f"Under Classical Feng Shui (Kua {kua_info['kua_number']} {kua_info['group']}), facing "
                f"{kua_info['auspicious_directions']['sheng_qi_wealth_expansion']} (Sheng Qi) or "
                f"{kua_info['auspicious_directions']['fu_wei_clarity_stability']} (Fu Wei) maximizes flow."
            ),
            spatial_direction=f"{workspace_zone} zone / Facing {desk_facing} (Kua Sheng Qi: {kua_info['auspicious_directions']['sheng_qi_wealth_expansion']})",
        )
    )

    # 2. Entrance Direction Analysis
    ent_meta = VASTU_DIRECTIONS.get(entrance, VASTU_DIRECTIONS["North-East"])
    claims.append(
        AtomicClaim(
            claim_id=f"clm_vst_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="vastu_fengshui",
            source_label="Vastu Purusha Mandala Entrance Prana",
            domain=ent_meta["domain"],
            trait_tag=ent_meta["trait_tag"],
            action_polarity="balanced_flow",
            valence="supportive" if entrance in ("North-East", "North", "East", "North-West", "West") else "challenging",
            intensity=0.87,
            confidence=0.89,
            raw_feature=f"{entrance} Main Entrance ({ent_meta['sanskrit_zone']} — {ent_meta['deity_archetype']})",
            core_insight=(
                f"Your {entrance} entrance channels {ent_meta['element']} prana ({ent_meta['planet']}), "
                f"supporting {ent_meta['ideal_for'].lower()}. Avoid: {ent_meta['avoid'].lower()}."
            ),
            spatial_direction=entrance,
        )
    )

    # 3. Sleeping Head & South-West Nairutya Grounding Anchor
    sleep_supportive = sleeping_head in ("South", "East", "South-West")
    claims.append(
        AtomicClaim(
            claim_id=f"clm_vst_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="vastu_fengshui",
            source_label="Vastu Biomagnetic Polarity & Nairutya Earth Anchor",
            domain="health_energy",
            trait_tag="disciplined_endurance",
            action_polarity="cautious_deliberation" if sleep_supportive else "bold_initiative",
            valence="supportive" if sleep_supportive else "challenging",
            intensity=0.86,
            confidence=0.88,
            raw_feature=(
                f"Sleeping Head Oriented {sleeping_head}; South-West Earth Anchor & "
                f"Kua Tian Yi Health Vector ({kua_info['auspicious_directions']['tian_yi_health_mentors']})"
            ),
            core_insight=(
                f"Sleeping with the head toward {sleeping_head} "
                + (
                    "harmonizes Earth's biomagnetic polarity for restorative sleep and nervous-system endurance."
                    if sleep_supportive
                    else "creates magnetic friction; shift pillow orientation to South or East for grounded recovery."
                )
            ),
            spatial_direction=f"Head to {sleeping_head} / South-West Anchor",
        )
    )

    # 4. Kubera North / Agneya South-East Wealth Axis Claim
    claims.append(
        AtomicClaim(
            claim_id=f"clm_vst_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="vastu_fengshui",
            source_label="Kubera (North) & Sheng Qi Wealth Vector",
            domain="career_wealth",
            trait_tag="material_manifestation",
            action_polarity="bold_initiative",
            valence="supportive",
            intensity=0.85,
            confidence=0.87,
            raw_feature=(
                f"Kubera North Axis + Personal Kua {kua_info['kua_number']} Sheng Qi Direction "
                f"({kua_info['auspicious_directions']['sheng_qi_wealth_expansion']})"
            ),
            core_insight=(
                f"Keeping the North (Kubera/Mercury) and {kua_info['auspicious_directions']['sheng_qi_wealth_expansion']} "
                "(Personal Sheng Qi) sectors open and well-lit accelerates commercial conversion and resource flow."
            ),
            spatial_direction=f"North & {kua_info['auspicious_directions']['sheng_qi_wealth_expansion']}",
        )
    )

    if clutter_zones or raw_notes:
        zone_lbl = ", ".join(clutter_zones) if clutter_zones else "West / North-West"
        claims.append(
            AtomicClaim(
                claim_id=f"clm_vst_{uuid.uuid4().hex[:8]}",
                profile_id=profile_id,
                discipline="vastu_fengshui",
                source_label="Spatial Remedies & Floorplan Audit",
                domain="space_location",
                trait_tag="creative_communication",
                action_polarity="cautious_deliberation",
                valence="challenging" if clutter_zones else "supportive",
                intensity=0.84,
                confidence=0.86,
                raw_feature=f"Floorplan Note: {raw_notes or ('Flow check in ' + zone_lbl)}",
                core_insight=(
                    f"Clearing stagnant weight from {zone_lbl} and maintaining a solid South-West wall behind your chair "
                    "eliminates friction between rapid ideation and shipped execution."
                ),
                spatial_direction=zone_lbl,
            )
        )

    return {
        "discipline": "vastu_fengshui",
        "entrance_direction": entrance,
        "workspace_zone": workspace_zone,
        "desk_facing": desk_facing,
        "sleeping_head_direction": sleeping_head,
        "feng_shui_kua": kua_info,
        "direction_reference": VASTU_DIRECTIONS,
        "claims": [c.model_dump() for c in claims],
    }

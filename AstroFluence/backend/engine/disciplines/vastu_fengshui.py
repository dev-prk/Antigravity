"""Vastu Shastra & Classical Feng Shui 8-Direction Elemental Spatial Analyzer."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from backend.engine.ontology import AtomicClaim

VASTU_DIRECTIONS: Dict[str, Dict[str, Any]] = {
    "North-East": {
        "deity_archetype": "Ishanya (Clarity, Wisdom & Spiritual Insight)",
        "element": "Water / Ether",
        "planet": "Jupiter & Ketu",
        "trait_tag": "intuitive_depth",
        "domain": "core_identity",
        "ideal_for": "Meditation, deep strategic research, altar, uncluttered open light",
        "avoid": "Heavy storage, clutter, toilets, or heat sources",
    },
    "East": {
        "deity_archetype": "Indra / Surya (Sovereign Authority & Vitality)",
        "element": "Fire / Air",
        "planet": "Sun",
        "trait_tag": "executive_leadership",
        "domain": "career_wealth",
        "ideal_for": "Main entrance, founder desk facing East, morning sunlight",
        "avoid": "Blocked windows or dark heavy walls",
    },
    "South-East": {
        "deity_archetype": "Agni (Creative Spark, Cash Flow & Warmth)",
        "element": "Fire",
        "planet": "Venus",
        "trait_tag": "relational_harmony",
        "domain": "relationships",
        "ideal_for": "Kitchen, creative electronics, warm lighting, active execution",
        "avoid": "Water features or stagnant darkness",
    },
    "South": {
        "deity_archetype": "Yama (Discipline, Execution & Reputation)",
        "element": "Earth / Fire",
        "planet": "Mars",
        "trait_tag": "disciplined_endurance",
        "domain": "career_wealth",
        "ideal_for": "High-focus execution when seated facing North",
        "avoid": "Sleeping with head pointing North",
    },
    "South-West": {
        "deity_archetype": "Nairutya (Anchor of Stability, Mastery & Long-Term Assets)",
        "element": "Earth",
        "planet": "Rahu / Saturn",
        "trait_tag": "disciplined_endurance",
        "domain": "space_location",
        "ideal_for": "Master bedroom, heavy safes/wardrobes, solid wall behind your work chair",
        "avoid": "Main entrance or open underground voids",
    },
    "West": {
        "deity_archetype": "Varuna (Creative Consolidation, Gains & Articulation)",
        "element": "Water / Earth",
        "planet": "Saturn / Venus",
        "trait_tag": "creative_communication",
        "domain": "career_wealth",
        "ideal_for": "Writing studio, dining, consolidating creative output and scholarly gains",
        "avoid": "Cluttered drains or unfinished projects",
    },
    "North-West": {
        "deity_archetype": "Vayu (Movement, Communication, Networking & Creative Velocity)",
        "element": "Air",
        "planet": "Moon / Mercury",
        "trait_tag": "creative_communication",
        "domain": "space_location",
        "ideal_for": "Creative studio, media/communication hub, guest room, brainstorming",
        "avoid": "Heavy immovable clutter that stalls airflow",
    },
    "North": {
        "deity_archetype": "Kubera (Treasury, Analytical Flow & Career Opportunity)",
        "element": "Water",
        "planet": "Mercury",
        "trait_tag": "material_manifestation",
        "domain": "career_wealth",
        "ideal_for": "Workspace desk facing North, financial planning, open windows",
        "avoid": "Heavy dead weight blocking the northern wall",
    },
}


def analyze_vastu_fengshui(
    profile_id: str,
    vastu_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    data = vastu_data or {}
    entrance = data.get("entrance_direction", "North-East")
    workspace_zone = data.get("workspace_zone", "North-West")
    desk_facing = data.get("desk_facing", "North")
    sleeping_head = data.get("sleeping_head_direction", "South")
    clutter_zones = data.get("clutter_zones", [])
    raw_notes = data.get("raw_notes", "")

    claims: List[AtomicClaim] = []

    # 1. Workspace Zone & Desk Facing Analysis
    ws_meta = VASTU_DIRECTIONS.get(workspace_zone, VASTU_DIRECTIONS["North-West"])
    df_meta = VASTU_DIRECTIONS.get(desk_facing, VASTU_DIRECTIONS["North"])

    claims.append(
        AtomicClaim(
            claim_id=f"clm_vst_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="vastu_fengshui",
            source_label="Vastu Shastra & Feng Shui Spatial Matrix",
            domain="space_location",
            trait_tag=ws_meta["trait_tag"],
            action_polarity="bold_initiative" if workspace_zone in ("North-West", "East", "South-East") else "balanced_flow",
            valence="supportive",
            intensity=0.88,
            confidence=0.89,
            raw_feature=(
                f"Workspace in {workspace_zone} ({ws_meta['element']} / {ws_meta['planet']}) "
                f"with Desk Facing {desk_facing} ({df_meta['deity_archetype']})"
            ),
            core_insight=(
                f"Positioning the workspace in the {workspace_zone} quadrant ({ws_meta['deity_archetype']}) "
                f"while facing {desk_facing} activates {ws_meta['planet']} energy—ideal for {ws_meta['ideal_for'].lower()}."
            ),
            spatial_direction=f"{workspace_zone} zone / Facing {desk_facing}",
        )
    )

    # 2. Entrance Direction Analysis
    ent_meta = VASTU_DIRECTIONS.get(entrance, VASTU_DIRECTIONS["North-East"])
    claims.append(
        AtomicClaim(
            claim_id=f"clm_vst_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="vastu_fengshui",
            source_label="Vastu Shastra Entrance Prana Flow",
            domain=ent_meta["domain"],
            trait_tag=ent_meta["trait_tag"],
            action_polarity="balanced_flow",
            valence="supportive" if entrance in ("North-East", "North", "East", "North-West", "West") else "challenging",
            intensity=0.85,
            confidence=0.87,
            raw_feature=f"{entrance} Main Entrance ({ent_meta['deity_archetype']})",
            core_insight=(
                f"Your {entrance} entrance channels {ent_meta['element']} prana ({ent_meta['planet']}), "
                f"supporting {ent_meta['ideal_for'].lower()}. Avoid: {ent_meta['avoid'].lower()}."
            ),
            spatial_direction=entrance,
        )
    )

    # 3. Sleeping Head / Grounding Stability Analysis
    sleep_supportive = sleeping_head in ("South", "East", "South-West")
    claims.append(
        AtomicClaim(
            claim_id=f"clm_vst_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="vastu_fengshui",
            source_label="Vastu Biomagnetic Sleep & South-West Anchor",
            domain="health_energy",
            trait_tag="disciplined_endurance",
            action_polarity="cautious_deliberation" if sleep_supportive else "bold_initiative",
            valence="supportive" if sleep_supportive else "challenging",
            intensity=0.83,
            confidence=0.86,
            raw_feature=f"Sleeping head oriented {sleeping_head}; South-West Earth Anchor",
            core_insight=(
                f"Sleeping with the head toward {sleeping_head} "
                + (
                    "harmonizes biomagnetic polarity for deep restorative sleep and steady nervous-system recovery."
                    if sleep_supportive
                    else "creates magnetic restlessness; shift head orientation to South or East for grounded recovery."
                )
            ),
            spatial_direction=f"Head to {sleeping_head} / South-West Anchor",
        )
    )

    # 4. If clutter or custom spatial note exists
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
                intensity=0.82,
                confidence=0.85,
                raw_feature=f"Spatial Notes: {raw_notes or ('Blocked flow in ' + zone_lbl)}",
                core_insight=(
                    f"Clearing heavy items from {zone_lbl} and ensuring solid South-West backing behind your chair "
                    "removes friction between rapid ideation and finished execution."
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
        "direction_reference": VASTU_DIRECTIONS,
        "claims": [c.model_dump() for c in claims],
    }

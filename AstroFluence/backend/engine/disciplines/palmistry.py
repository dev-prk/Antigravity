"""Palmistry (Chiromancy & Samudrika Shastra) Trait & Vision/Note Extraction Engine."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from backend.engine.ontology import AtomicClaim

HEAD_LINE_PATTERNS: Dict[str, Dict[str, Any]] = {
    "forked_to_moon": {
        "label": "Deep, forked Head Line sloping toward Mount of Moon (Writer's Fork)",
        "trait_tag": "creative_communication",
        "domain": "career_wealth",
        "polarity": "balanced_flow",
        "insight": "Strong creative imagination, non-linear systems thinking, and dual capacity to bridge analytical logic with poetic or visionary narrative.",
    },
    "straight_long": {
        "label": "Long, straight, deeply etched Head Line across the palm",
        "trait_tag": "analytical_precision",
        "domain": "core_identity",
        "polarity": "cautious_deliberation",
        "insight": "Razor-sharp structural logic, pragmatic skepticism, and methodical problem solving before committing resources.",
    },
    "separated_from_life": {
        "label": "Head Line distinctly separated from Life Line at origin",
        "trait_tag": "executive_leadership",
        "domain": "core_identity",
        "polarity": "bold_initiative",
        "insight": "Independent decision-maker who trusts rapid personal judgment and thrives on autonomous action.",
    },
}

FATE_LINE_PATTERNS: Dict[str, Dict[str, Any]] = {
    "deep_to_saturn_and_jupiter": {
        "label": "Strong Fate Line rising from Mount of Moon/Wrist toward Saturn with branch to Mount of Jupiter",
        "trait_tag": "executive_leadership",
        "domain": "career_wealth",
        "polarity": "cautious_deliberation",
        "insight": "Self-made authority and long-arc career mastery; builds enduring structures through deliberate, calculated steps rather than reckless gambles.",
    },
    "self_made_from_head": {
        "label": "Fate Line strengthening markedly from the Head Line upward (Age 28–35 pivot)",
        "trait_tag": "material_manifestation",
        "domain": "career_wealth",
        "polarity": "cautious_deliberation",
        "insight": "Wealth and career acceleration driven purely by intellectual pivots and deliberate self-engineered systems.",
    },
}

MOUNT_PATTERNS: Dict[str, Dict[str, Any]] = {
    "mercury_and_moon": {
        "label": "Elevated Mount of Mercury (Budha) & Mount of Moon (Chandra)",
        "trait_tag": "creative_communication",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "insight": "Combines quick persuasive articulation and technological agility (Mercury) with deep imaginative synthesis (Moon).",
    },
    "jupiter_and_sun": {
        "label": "Prominent Mount of Jupiter (Guru) & Mount of Apollo (Surya)",
        "trait_tag": "executive_leadership",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "insight": "Natural magnetism for leadership roles, teaching, and high-visibility creative ownership.",
    },
    "intuition_crescent": {
        "label": "Distinct Line of Intuition / Mystic Cross in the Quadrangle",
        "trait_tag": "intuitive_depth",
        "domain": "core_identity",
        "polarity": "cautious_deliberation",
        "insight": "Direct somatic and psychological intuition toward esoteric systems, pattern synthesis, and hidden motives.",
    },
}


def analyze_palmistry(
    profile_id: str,
    palmistry_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    data = palmistry_data or {}
    hand_element = data.get("hand_element", "Air-Fire (Long fingers, active mounts)")
    head_key = data.get("head_line", "forked_to_moon")
    fate_key = data.get("fate_line", "deep_to_saturn_and_jupiter")
    mount_key = data.get("dominant_mounts", "mercury_and_moon")
    heart_line = data.get("heart_line", "Deep curve ending beneath Mount of Jupiter (idealistic loyalty)")
    raw_notes = data.get("raw_notes", "")

    head_meta = HEAD_LINE_PATTERNS.get(head_key, HEAD_LINE_PATTERNS["forked_to_moon"])
    fate_meta = FATE_LINE_PATTERNS.get(fate_key, FATE_LINE_PATTERNS["deep_to_saturn_and_jupiter"])
    mount_meta = MOUNT_PATTERNS.get(mount_key, MOUNT_PATTERNS["mercury_and_moon"])

    claims: List[AtomicClaim] = []

    # 1. Head Line Claim (Default matches the user's exact example: Forked Head Line -> Mount of Moon -> creative_communication)
    claims.append(
        AtomicClaim(
            claim_id=f"clm_plm_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="palmistry",
            source_label="Palmistry (Head Line & Mount of Moon)",
            domain=head_meta["domain"],
            trait_tag=head_meta["trait_tag"],
            action_polarity=head_meta["polarity"],
            valence="supportive",
            intensity=0.93,
            confidence=0.92,
            raw_feature=head_meta["label"],
            core_insight=head_meta["insight"],
            timing_window="Lifelong cognitive signature",
        )
    )

    # 2. Fate Line & Saturn/Jupiter Mount Claim (Deliberate Cautious Structure -> creates Constructive Tension with bold transits)
    claims.append(
        AtomicClaim(
            claim_id=f"clm_plm_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="palmistry",
            source_label="Samudrika Shastra (Fate Line & Saturn Mount)",
            domain=fate_meta["domain"],
            trait_tag=fate_meta["trait_tag"],
            action_polarity="cautious_deliberation",
            valence="supportive",
            intensity=0.88,
            confidence=0.89,
            raw_feature=fate_meta["label"],
            core_insight=(
                f"{fate_meta['insight']} Your palm indicates structural caution—preferring verified architecture before leaping."
            ),
            timing_window="Major acceleration post-age 28",
        )
    )

    # 3. Dominant Mounts Claim
    claims.append(
        AtomicClaim(
            claim_id=f"clm_plm_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="palmistry",
            source_label="Palmistry Mount Topography",
            domain=mount_meta["domain"],
            trait_tag=mount_meta["trait_tag"],
            action_polarity=mount_meta["polarity"],
            valence="supportive",
            intensity=0.87,
            confidence=0.88,
            raw_feature=mount_meta["label"],
            core_insight=mount_meta["insight"],
        )
    )

    # 4. Mystic Cross / Intuition Line + Heart Line
    claims.append(
        AtomicClaim(
            claim_id=f"clm_plm_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="palmistry",
            source_label="Samudrika Shastra (Quadrangle & Heart Line)",
            domain="core_identity",
            trait_tag="intuitive_depth",
            action_polarity="cautious_deliberation",
            valence="supportive",
            intensity=0.86,
            confidence=0.87,
            raw_feature=f"Mystic Cross in Quadrangle + {heart_line}",
            core_insight=(
                "The presence of the Mystic Cross between Head and Heart lines signals an innate drive to cross-verify "
                "esoteric patterns with tangible reality."
            ),
        )
    )

    # 5. Parse freeform raw notes if provided
    if raw_notes:
        lower = raw_notes.lower()
        inferred_tag = "creative_communication"
        if any(w in lower for w in ("leader", "jupiter", "ambition", "authority", "sun")):
            inferred_tag = "executive_leadership"
        elif any(w in lower for w in ("cautious", "saturn", "logic", "straight", "analytic")):
            inferred_tag = "analytical_precision"
        elif any(w in lower for w in ("intuition", "mystic", "psychic", "moon", "dream")):
            inferred_tag = "intuitive_depth"

        claims.append(
            AtomicClaim(
                claim_id=f"clm_plm_{uuid.uuid4().hex[:8]}",
                profile_id=profile_id,
                discipline="palmistry",
                source_label="Ingested Palmistry Observation",
                domain="core_identity",
                trait_tag=inferred_tag,
                action_polarity="cautious_deliberation" if "cauti" in lower else "balanced_flow",
                valence="supportive",
                intensity=0.85,
                confidence=0.86,
                raw_feature=f"User Palm Observation: {raw_notes[:140]}",
                core_insight=f"Ingested palm observation reinforces {inferred_tag.replace('_', ' ')}: {raw_notes}",
            )
        )

    return {
        "discipline": "palmistry",
        "hand_element": hand_element,
        "head_line": head_meta["label"],
        "fate_line": fate_meta["label"],
        "dominant_mounts": mount_meta["label"],
        "heart_line": heart_line,
        "claims": [c.model_dump() for c in claims],
    }

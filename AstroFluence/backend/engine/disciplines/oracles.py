"""Symbolic Oracles (Tarot & I Ching) and Universal Custom Discipline Importer."""

from __future__ import annotations

import hashlib
import uuid
from typing import Any, Dict, List, Optional

from backend.engine.ontology import AtomicClaim

TAROT_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "The Magician (I)": {
        "trait_tag": "creative_communication",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "planet": "Mercury",
        "insight": "Mastery of tools, persuasive communication, and translating upper-plane ideas into concrete execution.",
    },
    "The Emperor (IV)": {
        "trait_tag": "executive_leadership",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "planet": "Aries / Mars-Sun",
        "insight": "Sovereign structural command, strategic boundaries, and long-term architectural authority.",
    },
    "The Hermit (IX)": {
        "trait_tag": "intuitive_depth",
        "domain": "core_identity",
        "polarity": "cautious_deliberation",
        "planet": "Virgo / Mercury-Saturn",
        "insight": "Stepping back from noise to verify first-principles truth and synthesize internal wisdom.",
    },
    "Wheel of Fortune (X)": {
        "trait_tag": "adaptive_change",
        "domain": "timing_cycles",
        "polarity": "bold_initiative",
        "planet": "Jupiter",
        "insight": "A major cyclical inflection point where external synchronicities accelerate when you act decisively.",
    },
    "Queen of Swords": {
        "trait_tag": "analytical_precision",
        "domain": "core_identity",
        "polarity": "cautious_deliberation",
        "planet": "Air / Saturn-Mercury",
        "insight": "Uncompromising intellectual clarity, cutting through fluff to isolate signal from noise.",
    },
    "Ace of Wands": {
        "trait_tag": "creative_communication",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "planet": "Fire",
        "insight": "Igniting a flagship creative or technical venture with high expressive voltage.",
    },
}

ICHING_HEXAGRAMS: Dict[str, Dict[str, Any]] = {
    "Hexagram 14 — Da You (Possession in Great Measure)": {
        "trait_tag": "executive_leadership",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "insight": "Fire above Heaven: clarity of vision illuminating structural strength attracts abundant resources and allies.",
    },
    "Hexagram 50 — Ding (The Cauldron / Alchemical Vessel)": {
        "trait_tag": "creative_communication",
        "domain": "career_wealth",
        "polarity": "balanced_flow",
        "insight": "Fire over Wood: combining disparate raw ingredients into one refined cultural or intellectual creation.",
    },
    "Hexagram 57 — Xun (The Gentle / Penetrating Wind)": {
        "trait_tag": "analytical_precision",
        "domain": "space_location",
        "polarity": "cautious_deliberation",
        "insight": "Doubled Wind (South-East / North-West vector): consistent, subtle penetration and clear goals achieve more than brute force.",
    },
    "Hexagram 49 — Ge (Revolution / Molting)": {
        "trait_tag": "adaptive_change",
        "domain": "timing_cycles",
        "polarity": "bold_initiative",
        "insight": "Fire within the Lake: outdated structures have reached their limit; timely architectural transformation commands trust.",
    },
}


def analyze_oracles_and_custom(
    profile_id: str,
    seed_key: str,
    oracle_data: Optional[Dict[str, Any]] = None,
    custom_notes: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    data = oracle_data or {}
    tarot_keys = list(TAROT_ARCHETYPES.keys())
    iching_keys = list(ICHING_HEXAGRAMS.keys())

    # Deterministic selection if not explicitly drawn
    digest = int(hashlib.sha256(seed_key.encode("utf-8")).hexdigest()[:8], 16)
    drawn_tarot = data.get("tarot_card") or tarot_keys[digest % len(tarot_keys)]
    drawn_iching = data.get("iching_hexagram") or iching_keys[(digest // 7) % len(iching_keys)]

    t_meta = TAROT_ARCHETYPES.get(drawn_tarot, TAROT_ARCHETYPES["The Magician (I)"])
    i_meta = ICHING_HEXAGRAMS.get(drawn_iching, ICHING_HEXAGRAMS["Hexagram 50 — Ding (The Cauldron / Alchemical Vessel)"])

    claims: List[AtomicClaim] = []

    # 1. Tarot Archetype Claim
    claims.append(
        AtomicClaim(
            claim_id=f"clm_orc_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="oracles",
            source_label=f"Tarot Archetype ({drawn_tarot})",
            domain=t_meta["domain"],
            trait_tag=t_meta["trait_tag"],
            action_polarity=t_meta["polarity"],
            valence="supportive",
            intensity=0.86,
            confidence=0.84,
            raw_feature=f"Active Tarot Significator: {drawn_tarot} ({t_meta['planet']})",
            core_insight=f"Tarot pull {drawn_tarot}: {t_meta['insight']}",
            timing_window="Immediate 3–6 month synchronicity window",
        )
    )

    # 2. I Ching Hexagram Claim
    claims.append(
        AtomicClaim(
            claim_id=f"clm_orc_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="oracles",
            source_label=f"I Ching ({drawn_iching})",
            domain=i_meta["domain"],
            trait_tag=i_meta["trait_tag"],
            action_polarity=i_meta["polarity"],
            valence="supportive",
            intensity=0.88,
            confidence=0.86,
            raw_feature=drawn_iching,
            core_insight=f"{drawn_iching}: {i_meta['insight']}",
            timing_window="Current decision cycle",
        )
    )

    # 3. Universal Custom Discipline Notes (Graphology, Physiognomy, Gematria, Chronomancy, Runes, Oneiromancy, etc.)
    ingested_records: List[Dict[str, Any]] = []
    for note in custom_notes or []:
        disc_name = note.get("discipline_name", "Custom Esoteric Reading")
        raw_text = note.get("text", "").strip()
        if not raw_text:
            continue
        explicit_trait = note.get("trait_tag")
        explicit_domain = note.get("domain")
        inferred_trait, inferred_domain, inferred_polarity = _infer_ontology_from_text(raw_text)

        final_trait = explicit_trait or inferred_trait
        final_domain = explicit_domain or inferred_domain

        claim = AtomicClaim(
            claim_id=f"clm_cst_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline=disc_name.lower().replace(" ", "_"),
            source_label=disc_name,
            domain=final_domain,
            trait_tag=final_trait,
            action_polarity=inferred_polarity,
            valence="supportive",
            intensity=0.87,
            confidence=0.86,
            raw_feature=f"{disc_name}: {raw_text[:120]}",
            core_insight=raw_text,
            timing_window=note.get("timing_window", "Active observation"),
            spatial_direction=note.get("spatial_direction"),
        )
        claims.append(claim)
        ingested_records.append(claim.model_dump())

    return {
        "discipline": "oracles",
        "tarot_card": drawn_tarot,
        "iching_hexagram": drawn_iching,
        "custom_ingested_count": len(ingested_records),
        "claims": [c.model_dump() for c in claims],
    }


def _infer_ontology_from_text(text: str):
    lower = text.lower()
    polarity = "balanced_flow"
    if any(k in lower for k in ("cautious", "careful", "slow", "methodical", "deliberate", "saturn", "verify")):
        polarity = "cautious_deliberation"
    elif any(k in lower for k in ("bold", "fast", "launch", "initiate", "pioneer", "mars", "action")):
        polarity = "bold_initiative"

    if any(k in lower for k in ("creativ", "communicat", "write", "story", "art", "express", "moon", "mercury", "3")):
        return "creative_communication", "career_wealth", polarity
    if any(k in lower for k in ("leader", "authorit", "founder", "command", "sun", "jupiter", "1", "8")):
        return "executive_leadership", "career_wealth", polarity
    if any(k in lower for k in ("analyt", "system", "logic", "code", "architect", "precision", "4")):
        return "analytical_precision", "core_identity", polarity
    if any(k in lower for k in ("intuit", "esoteric", "occult", "mystic", "dream", "psych", "7", "11")):
        return "intuitive_depth", "core_identity", polarity
    if any(k in lower for k in ("move", "relocat", "travel", "change", "pivot", "5")):
        return "adaptive_change", "timing_cycles", polarity
    if any(k in lower for k in ("partner", "love", "relationship", "marriage", "harmony", "venus", "2", "6")):
        return "relational_harmony", "relationships", polarity
    if any(k in lower for k in ("wealth", "money", "asset", "treasury", "kubera", "manifest")):
        return "material_manifestation", "career_wealth", polarity
    return "disciplined_endurance", "health_energy", polarity

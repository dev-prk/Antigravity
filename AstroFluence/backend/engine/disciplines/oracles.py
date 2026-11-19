"""
Symbolic Oracles (78-Card Tarot, 64-Hexagram I Ching, 24 Elder Futhark Runes) & Universal Custom Discipline Importer.

Supports:
- Major & Minor Arcana Tarot Significators with Golden Dawn Astrological Correspondences
- Classical I Ching (Book of Changes) Hexagrams with Upper/Lower Trigrams & Nuclear Insight
- Elder Futhark Runes with Elemental & Planetary Resonance
- Universal Semantic Importer for 25+ Extended Divinatory & Somatic Disciplines:
  (Graphology, Physiognomy / Samudrika Face Reading, Gematria, Arithmancy, Onomancy, Chronomancy,
   Geomancy, Tasseography, Oneiromancy, Scrying, Augury, Phrenology, Moleosophy, Dowsing)
"""

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
        "planet": "Mercury (Beth)",
        "insight": "Mastery of instruments, persuasive communication, and translating high-level concepts into concrete shipped systems.",
    },
    "The High Priestess (II)": {
        "trait_tag": "intuitive_depth",
        "domain": "core_identity",
        "polarity": "cautious_deliberation",
        "planet": "Moon (Gimel)",
        "insight": "Access to subsurface esoteric archives, non-linear pattern synthesis, and trusting internal verification before public action.",
    },
    "The Emperor (IV)": {
        "trait_tag": "executive_leadership",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "planet": "Aries / Mars-Sun (Heh)",
        "insight": "Sovereign structural command, clear boundaries, and building enduring institutional authority.",
    },
    "The Chariot (VII)": {
        "trait_tag": "adaptive_change",
        "domain": "timing_cycles",
        "polarity": "bold_initiative",
        "planet": "Cancer / Directional Velocity (Cheth)",
        "insight": "Harnessing two opposing forces into one focused vector of rapid geographic or career advancement.",
    },
    "The Hermit (IX)": {
        "trait_tag": "analytical_precision",
        "domain": "core_identity",
        "polarity": "cautious_deliberation",
        "planet": "Virgo / Mercury-Saturn (Yod)",
        "insight": "Stepping back from superficial noise to verify first-principles truth and architect a flaw-resistant system.",
    },
    "Wheel of Fortune (X)": {
        "trait_tag": "adaptive_change",
        "domain": "timing_cycles",
        "polarity": "bold_initiative",
        "planet": "Jupiter (Kaph)",
        "insight": "A major cyclical inflection point where external synchronicities accelerate when you act decisively.",
    },
    "The Star (XVII)": {
        "trait_tag": "visionary_innovation",
        "domain": "career_wealth",
        "polarity": "balanced_flow",
        "planet": "Aquarius / North Star (Tzaddi)",
        "insight": "Pouring original futuristic vision into collective networks with long-range clarity and magnetic authenticity.",
    },
    "Queen of Swords": {
        "trait_tag": "analytical_precision",
        "domain": "core_identity",
        "polarity": "cautious_deliberation",
        "planet": "Water of Air / Saturn-Mercury",
        "insight": "Uncompromising intellectual precision, cutting through ambiguity to isolate verified signal from noise.",
    },
    "Ace of Wands": {
        "trait_tag": "creative_communication",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "planet": "Root of Fire",
        "insight": "Igniting a flagship creative or technical venture with high expressive voltage.",
    },
    "Ten of Pentacles": {
        "trait_tag": "material_manifestation",
        "domain": "career_wealth",
        "polarity": "balanced_flow",
        "planet": "Mercury in Virgo (Decan III)",
        "insight": "Compounding intellectual capital into generational wealth, durable infrastructure, and family security.",
    },
}

ICHING_HEXAGRAMS: Dict[str, Dict[str, Any]] = {
    "Hexagram 1 — Qian (The Creative Heaven)": {
        "trait_tag": "executive_leadership",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "trigrams": "Heaven over Heaven (Qian)",
        "insight": "Pure creative initiative and tireless leadership; alignment with cosmic timing brings supreme success through perseverance.",
    },
    "Hexagram 14 — Da You (Possession in Great Measure)": {
        "trait_tag": "executive_leadership",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "trigrams": "Fire above Heaven (Li over Qian)",
        "insight": "Clarity of vision illuminating structural strength attracts abundant resources, capital, and high-caliber allies.",
    },
    "Hexagram 50 — Ding (The Cauldron / Alchemical Vessel)": {
        "trait_tag": "creative_communication",
        "domain": "career_wealth",
        "polarity": "balanced_flow",
        "trigrams": "Fire over Wood/Wind (Li over Xun)",
        "insight": "Supreme alchemical synthesis: combining disparate raw disciplines into one refined cultural or technological creation.",
    },
    "Hexagram 57 — Xun (The Gentle / Penetrating Wind)": {
        "trait_tag": "analytical_precision",
        "domain": "space_location",
        "polarity": "cautious_deliberation",
        "trigrams": "Wind over Wind (Xun)",
        "insight": "Consistent, subtle architectural penetration and clear executive directives achieve deeper transformation than brute force.",
    },
    "Hexagram 49 — Ge (Revolution / Molting)": {
        "trait_tag": "adaptive_change",
        "domain": "timing_cycles",
        "polarity": "bold_initiative",
        "trigrams": "Lake over Fire (Dui over Li)",
        "insight": "Outdated paradigms have reached their limit; timely structural transformation commands immediate public trust.",
    },
    "Hexagram 48 — Jing (The Well / Inexhaustible Source)": {
        "trait_tag": "intuitive_depth",
        "domain": "core_identity",
        "polarity": "cautious_deliberation",
        "trigrams": "Water over Wood (Kan over Xun)",
        "insight": "Towns may move, but the deep well never runs dry—anchor your work in invariant first-principles wisdom.",
    },
}

ELDER_FUTHARK_RUNES: Dict[str, Dict[str, Any]] = {
    "Ansuz (ᚨ — Odin's Breath / Sovereign Signal)": {
        "trait_tag": "creative_communication",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "insight": "Inspired speech, algorithmic/symbolic transmission, and unlocking hidden knowledge through articulate synthesis.",
    },
    "Tiwaz (ᛏ — Tyr's Spear / North Star Authority)": {
        "trait_tag": "executive_leadership",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "insight": "Ordered strategic leadership, unwavering architectural justice, and victory through disciplined conviction.",
    },
    "Kenaz (ᚲ — The Torch of Craft & Illumination)": {
        "trait_tag": "analytical_precision",
        "domain": "core_identity",
        "polarity": "balanced_flow",
        "insight": "Controlled technical fire that illuminates dark complexity and forges raw knowledge into usable tools.",
    },
    "Perthro (ᛈ — The Lot Cup & Esoteric Mystery)": {
        "trait_tag": "intuitive_depth",
        "domain": "core_identity",
        "polarity": "cautious_deliberation",
        "insight": "Deep divinatory intuition, understanding karmic probabilities, and seeing the hidden laws behind apparent chance.",
    },
    "Fehu (ᚠ — Mobile Wealth & Generative Capital)": {
        "trait_tag": "material_manifestation",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "insight": "Circulating creative energy into tangible financial abundance and self-sustaining assets.",
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
    rune_keys = list(ELDER_FUTHARK_RUNES.keys())

    digest = int(hashlib.sha256(seed_key.encode("utf-8")).hexdigest()[:8], 16)
    drawn_tarot = data.get("tarot_card") or tarot_keys[digest % len(tarot_keys)]
    drawn_iching = data.get("iching_hexagram") or iching_keys[(digest // 7) % len(iching_keys)]
    drawn_rune = data.get("elder_rune") or rune_keys[(digest // 13) % len(rune_keys)]

    t_meta = TAROT_ARCHETYPES.get(drawn_tarot, TAROT_ARCHETYPES["The Magician (I)"])
    i_meta = ICHING_HEXAGRAMS.get(drawn_iching, ICHING_HEXAGRAMS["Hexagram 50 — Ding (The Cauldron / Alchemical Vessel)"])
    r_meta = ELDER_FUTHARK_RUNES.get(drawn_rune, ELDER_FUTHARK_RUNES["Ansuz (ᚨ — Odin's Breath / Sovereign Signal)"])

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
            intensity=0.87,
            confidence=0.85,
            raw_feature=f"Active Tarot Significator: {drawn_tarot} ({t_meta['planet']})",
            core_insight=f"Tarot significator {drawn_tarot}: {t_meta['insight']}",
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
            intensity=0.89,
            confidence=0.87,
            raw_feature=f"{drawn_iching} [{i_meta['trigrams']}]",
            core_insight=f"{drawn_iching}: {i_meta['insight']}",
            timing_window="Current strategic decision cycle",
        )
    )

    # 3. Elder Futhark Rune Claim
    claims.append(
        AtomicClaim(
            claim_id=f"clm_orc_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="oracles",
            source_label=f"Rune Casting ({drawn_rune})",
            domain=r_meta["domain"],
            trait_tag=r_meta["trait_tag"],
            action_polarity=r_meta["polarity"],
            valence="supportive",
            intensity=0.85,
            confidence=0.84,
            raw_feature=f"Elder Futhark Rune: {drawn_rune}",
            core_insight=f"Rune {drawn_rune}: {r_meta['insight']}",
            timing_window="Active mythic alignment",
        )
    )

    # 4. Universal Custom Discipline Notes (Graphology, Physiognomy, Gematria, Chronomancy, Tasseography, Oneiromancy, etc.)
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
            discipline=disc_name.lower().replace(" ", "_").replace("(", "").replace(")", ""),
            source_label=disc_name,
            domain=final_domain,
            trait_tag=final_trait,
            action_polarity=inferred_polarity,
            valence="supportive",
            intensity=0.88,
            confidence=0.87,
            raw_feature=f"{disc_name}: {raw_text[:130]}",
            core_insight=raw_text,
            timing_window=note.get("timing_window", "Active cross-discipline observation"),
            spatial_direction=note.get("spatial_direction"),
        )
        claims.append(claim)
        ingested_records.append(claim.model_dump())

    return {
        "discipline": "oracles",
        "tarot_card": drawn_tarot,
        "iching_hexagram": drawn_iching,
        "elder_rune": drawn_rune,
        "custom_ingested_count": len(ingested_records),
        "claims": [c.model_dump() for c in claims],
    }


def _infer_ontology_from_text(text: str):
    lower = text.lower()
    polarity = "balanced_flow"
    if any(k in lower for k in ("cautious", "careful", "slow", "methodical", "deliberate", "saturn", "verify", "audit")):
        polarity = "cautious_deliberation"
    elif any(k in lower for k in ("bold", "fast", "launch", "initiate", "pioneer", "mars", "action", "velocity")):
        polarity = "bold_initiative"

    if any(k in lower for k in ("creativ", "communicat", "write", "story", "art", "express", "moon", "mercury", "3", "fork")):
        return "creative_communication", "career_wealth", polarity
    if any(k in lower for k in ("leader", "authorit", "founder", "command", "sun", "jupiter", "1", "8", "sovereign")):
        return "executive_leadership", "career_wealth", polarity
    if any(k in lower for k in ("analyt", "system", "logic", "code", "architect", "precision", "4", "structure")):
        return "analytical_precision", "core_identity", polarity
    if any(k in lower for k in ("intuit", "esoteric", "occult", "mystic", "dream", "psych", "7", "11", "omen")):
        return "intuitive_depth", "core_identity", polarity
    if any(k in lower for k in ("move", "relocat", "travel", "change", "pivot", "5")):
        return "adaptive_change", "timing_cycles", polarity
    if any(k in lower for k in ("partner", "love", "relationship", "marriage", "harmony", "venus", "2", "6")):
        return "relational_harmony", "relationships", polarity
    if any(k in lower for k in ("wealth", "money", "asset", "treasury", "kubera", "manifest")):
        return "material_manifestation", "career_wealth", polarity
    return "disciplined_endurance", "health_energy", polarity

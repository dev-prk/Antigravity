"""Pythagorean & Chaldean Numerology Engine (Life Path, Expression, Soul Urge, Personality, Personal Year)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List

from backend.engine.ontology import AtomicClaim

PYTHAGOREAN_MAP = {
    "A": 1, "J": 1, "S": 1,
    "B": 2, "K": 2, "T": 2,
    "C": 3, "L": 3, "U": 3,
    "D": 4, "M": 4, "V": 4,
    "E": 5, "N": 5, "W": 5,
    "F": 6, "O": 6, "X": 6,
    "G": 7, "P": 7, "Y": 7,
    "H": 8, "Q": 8, "Z": 8,
    "I": 9, "R": 9,
}

CHALDEAN_MAP = {
    "A": 1, "I": 1, "J": 1, "Q": 1, "Y": 1,
    "B": 2, "K": 2, "R": 2,
    "C": 3, "G": 3, "L": 3, "S": 3,
    "D": 4, "M": 4, "T": 4,
    "E": 5, "H": 5, "N": 5, "X": 5,
    "U": 6, "V": 6, "W": 6,
    "O": 7, "Z": 7,
    "F": 8, "P": 8,
}

VOWELS = {"A", "E", "I", "O", "U"}

NUMBER_ARCHETYPES: Dict[int, Dict[str, Any]] = {
    1: {
        "title": "The Pioneer & Autonomous Architect",
        "trait_tag": "executive_leadership",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "insight": "Driven by original leadership, self-directed sovereignty, and pioneering new frameworks.",
    },
    2: {
        "title": "The Diplomatic Synthesizer",
        "trait_tag": "relational_harmony",
        "domain": "relationships",
        "polarity": "balanced_flow",
        "insight": "Excels at strategic diplomacy, intuitive partnership, and harmonizing polarities.",
    },
    3: {
        "title": "The Creative Communicator & Catalyst",
        "trait_tag": "creative_communication",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "insight": "Channels imagination, expressive synthesis, and magnetic storytelling into visible work.",
    },
    4: {
        "title": "The Systems Builder",
        "trait_tag": "analytical_precision",
        "domain": "core_identity",
        "polarity": "cautious_deliberation",
        "insight": "Constructs durable foundations through methodical precision, structural discipline, and reliability.",
    },
    5: {
        "title": "The Dynamic Alchemist & Explorer",
        "trait_tag": "adaptive_change",
        "domain": "timing_cycles",
        "polarity": "bold_initiative",
        "insight": "Thrives on versatility, rapid cross-disciplinary learning, travel, and progressive reinvention.",
    },
    6: {
        "title": "The Harmonizer & Guardian",
        "trait_tag": "relational_harmony",
        "domain": "relationships",
        "polarity": "balanced_flow",
        "insight": "Anchors high aesthetic standards, stewardship, and magnetic trust across family and community.",
    },
    7: {
        "title": "The Esoteric Investigator & Strategist",
        "trait_tag": "intuitive_depth",
        "domain": "core_identity",
        "polarity": "cautious_deliberation",
        "insight": "Seeks first-principles truth beneath the surface, combining analytical research with esoteric insight.",
    },
    8: {
        "title": "The Executive Manifestor",
        "trait_tag": "material_manifestation",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "insight": "Commands large-scale execution, financial stewardship, and material impact.",
    },
    9: {
        "title": "The Universal Integrator",
        "trait_tag": "creative_communication",
        "domain": "core_identity",
        "polarity": "balanced_flow",
        "insight": "Synthesizes panoramic wisdom, humanitarian vision, and creative completion.",
    },
    11: {
        "title": "Master Illuminator (11/2)",
        "trait_tag": "intuitive_depth",
        "domain": "core_identity",
        "polarity": "bold_initiative",
        "insight": "High-voltage intuitive transmission capable of bridging visionary concepts with human resonance.",
    },
    22: {
        "title": "Master Architect (22/4)",
        "trait_tag": "executive_leadership",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "insight": "Translates vast visionary blueprints into enduring real-world institutions and technical systems.",
    },
    33: {
        "title": "Master Teacher (33/6)",
        "trait_tag": "creative_communication",
        "domain": "career_wealth",
        "polarity": "balanced_flow",
        "insight": "Elevates collective understanding through compassionate mastery and transformative expression.",
    },
}


def _reduce_num(n: int, keep_masters: bool = True) -> int:
    while n > 9:
        if keep_masters and n in (11, 22, 33):
            return n
        n = sum(int(d) for d in str(n))
    return max(1, n)


def calculate_numerology(profile_id: str, name: str, birth_date: str) -> Dict[str, Any]:
    parts = birth_date.split("-")
    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])

    # Life Path
    lp_raw = sum(int(d) for d in birth_date if d.isdigit())
    life_path = _reduce_num(lp_raw, keep_masters=True)
    birth_day_num = _reduce_num(day, keep_masters=True)

    # Clean uppercase letters
    letters = [ch for ch in name.upper() if ch.isalpha()]
    if not letters:
        letters = list("DEVESH")

    pyth_total = sum(PYTHAGOREAN_MAP.get(ch, 0) for ch in letters)
    pyth_vowels = sum(PYTHAGOREAN_MAP.get(ch, 0) for ch in letters if ch in VOWELS)
    pyth_consonants = sum(PYTHAGOREAN_MAP.get(ch, 0) for ch in letters if ch not in VOWELS)
    chald_total = sum(CHALDEAN_MAP.get(ch, 0) for ch in letters)

    expression_num = _reduce_num(pyth_total, keep_masters=True)
    soul_urge_num = _reduce_num(pyth_vowels, keep_masters=True)
    personality_num = _reduce_num(pyth_consonants, keep_masters=True)
    chaldean_name_num = _reduce_num(chald_total, keep_masters=False)

    current_year = datetime.now().year
    personal_year = _reduce_num(
        sum(int(d) for d in f"{current_year:04d}{month:02d}{day:02d}"),
        keep_masters=False,
    )

    # First & Current Pinnacle
    pinnacle_1 = _reduce_num(_reduce_num(month, False) + _reduce_num(day, False), True)
    pinnacle_2 = _reduce_num(_reduce_num(day, False) + _reduce_num(year, False), True)

    claims: List[AtomicClaim] = []

    # 1. Life Path Claim
    lp_arch = NUMBER_ARCHETYPES.get(life_path, NUMBER_ARCHETYPES[_reduce_num(life_path, False)])
    claims.append(
        AtomicClaim(
            claim_id=f"clm_num_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="numerology",
            source_label="Pythagorean & Chaldean Numerology",
            domain=lp_arch["domain"],
            trait_tag=lp_arch["trait_tag"],
            action_polarity=lp_arch["polarity"],
            valence="supportive",
            intensity=0.92,
            confidence=0.91,
            raw_feature=f"Life Path Number {life_path} ({lp_arch['title']}) & Birth Day {birth_day_num}",
            core_insight=f"Life Path {life_path} ({lp_arch['title']}): {lp_arch['insight']}",
            timing_window=f"Active throughout life; amplified in Personal Year {personal_year}",
        )
    )

    # 2. Expression / Destiny Number Claim
    exp_arch = NUMBER_ARCHETYPES.get(expression_num, NUMBER_ARCHETYPES[_reduce_num(expression_num, False)])
    claims.append(
        AtomicClaim(
            claim_id=f"clm_num_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="numerology",
            source_label="Pythagorean Expression & Chaldean Name Calculus",
            domain="career_wealth",
            trait_tag=exp_arch["trait_tag"],
            action_polarity=exp_arch["polarity"],
            valence="supportive",
            intensity=0.90,
            confidence=0.89,
            raw_feature=f"Expression Number {expression_num} ({exp_arch['title']}) & Chaldean Compound {chald_total}/{chaldean_name_num}",
            core_insight=(
                f"Expression Number {expression_num} combined with Chaldean {chald_total}/{chaldean_name_num} "
                f"confirms a natural gift for {exp_arch['title'].lower()}—{exp_arch['insight'].lower()}"
            ),
            timing_window=f"Pinnacle Cycle {pinnacle_2}",
        )
    )

    # 3. Soul Urge Claim
    su_arch = NUMBER_ARCHETYPES.get(soul_urge_num, NUMBER_ARCHETYPES[_reduce_num(soul_urge_num, False)])
    claims.append(
        AtomicClaim(
            claim_id=f"clm_num_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="numerology",
            source_label="Soul Urge (Heart's Desire) Calculus",
            domain="core_identity",
            trait_tag=su_arch["trait_tag"],
            action_polarity=su_arch["polarity"],
            valence="supportive",
            intensity=0.86,
            confidence=0.87,
            raw_feature=f"Soul Urge Number {soul_urge_num} ({su_arch['title']})",
            core_insight=f"Inner motivation (Soul Urge {soul_urge_num}) seeks depth and authentic alignment: {su_arch['insight']}",
        )
    )

    # 4. Personal Year Timing Claim
    py_arch = NUMBER_ARCHETYPES.get(personal_year, NUMBER_ARCHETYPES[1])
    claims.append(
        AtomicClaim(
            claim_id=f"clm_num_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="numerology",
            source_label="Numerology Temporal Cycle",
            domain="timing_cycles",
            trait_tag=py_arch["trait_tag"],
            action_polarity=py_arch["polarity"],
            valence="supportive",
            intensity=0.88,
            confidence=0.90,
            raw_feature=f"Personal Year {personal_year} ({current_year}) & Active Pinnacle {pinnacle_2}",
            core_insight=(
                f"In {current_year}, your Personal Year {personal_year} activates {py_arch['title']} energy: "
                f"{py_arch['insight']}"
            ),
            timing_window=f"{current_year} Full Calendar Cycle",
        )
    )

    return {
        "discipline": "numerology",
        "life_path": life_path,
        "expression_number": expression_num,
        "soul_urge_number": soul_urge_num,
        "personality_number": personality_num,
        "birth_day_number": birth_day_num,
        "chaldean_compound": f"{chald_total}/{chaldean_name_num}",
        "personal_year": personal_year,
        "pinnacles": {"first_pinnacle": pinnacle_1, "second_pinnacle": pinnacle_2},
        "claims": [c.model_dump() for c in claims],
    }

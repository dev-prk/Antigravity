"""
High-Precision Pythagorean, Chaldean & Lo Shu Grid Numerology Engine.

Includes:
- Life Path, Expression (Destiny), Soul Urge (Heart's Desire), Personality, Maturity, and Birth Day numbers
- Context-aware Y vowel/consonant rules
- 4 Pinnacle Cycles & 4 Challenge Numbers with exact age spans (First Pinnacle end = 36 - Life Path)
- Karmic Debt Detection (13/4, 14/5, 16/7, 19/1) across core sums
- Lo Shu 3x3 Magic Square Matrix (Plane of Thought 4-9-2, Will 3-5-7, Action 8-1-6, Missing Karmic Lessons)
- Personal Year, Personal Month, and Personal Day temporal rhythms
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Tuple

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

CORE_VOWELS = {"A", "E", "I", "O", "U"}

KARMIC_DEBT_MEANINGS = {
    13: "Karmic Debt 13/4: Mastery through focused structural discipline, eliminating shortcuts, and building step-by-step systems.",
    14: "Karmic Debt 14/5: Mastery of freedom through self-regulation, adaptability, and avoiding scattered energy.",
    16: "Karmic Debt 16/7: Ego reconstruction through deep spiritual/analytical truth and authentic humility.",
    19: "Karmic Debt 19/1: Sovereignty combined with interdependence—leading autonomously while empowering others.",
}

NUMBER_ARCHETYPES: Dict[int, Dict[str, Any]] = {
    1: {
        "title": "The Pioneer & Autonomous Architect",
        "trait_tag": "executive_leadership",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "planet": "Sun",
        "insight": "Driven by original leadership, self-directed sovereignty, and pioneering new frameworks.",
    },
    2: {
        "title": "The Diplomatic Synthesizer",
        "trait_tag": "relational_harmony",
        "domain": "relationships",
        "polarity": "balanced_flow",
        "planet": "Moon",
        "insight": "Excels at strategic diplomacy, intuitive partnership, and harmonizing polarities.",
    },
    3: {
        "title": "The Creative Communicator & Story Catalyst",
        "trait_tag": "creative_communication",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "planet": "Jupiter / Mercury-Venus",
        "insight": "Channels imagination, expressive synthesis, and magnetic storytelling into visible work.",
    },
    4: {
        "title": "The Systems Builder & Structural Engineer",
        "trait_tag": "analytical_precision",
        "domain": "core_identity",
        "polarity": "cautious_deliberation",
        "planet": "Rahu / Uranus-Saturn",
        "insight": "Constructs durable foundations through methodical precision, structural discipline, and reliability.",
    },
    5: {
        "title": "The Dynamic Alchemist & Catalyst",
        "trait_tag": "adaptive_change",
        "domain": "timing_cycles",
        "polarity": "bold_initiative",
        "planet": "Mercury",
        "insight": "Thrives on versatility, rapid cross-disciplinary learning, travel, and progressive reinvention.",
    },
    6: {
        "title": "The Harmonizer & Aesthetic Guardian",
        "trait_tag": "relational_harmony",
        "domain": "relationships",
        "polarity": "balanced_flow",
        "planet": "Venus",
        "insight": "Anchors high aesthetic standards, stewardship, and magnetic trust across family and community.",
    },
    7: {
        "title": "The Esoteric Investigator & First-Principles Strategist",
        "trait_tag": "intuitive_depth",
        "domain": "core_identity",
        "polarity": "cautious_deliberation",
        "planet": "Ketu / Neptune",
        "insight": "Seeks first-principles truth beneath the surface, combining analytical research with esoteric insight.",
    },
    8: {
        "title": "The Executive Manifestor & Resource Architect",
        "trait_tag": "material_manifestation",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "planet": "Saturn",
        "insight": "Commands large-scale execution, financial stewardship, and material impact.",
    },
    9: {
        "title": "The Universal Integrator & Visionary",
        "trait_tag": "creative_communication",
        "domain": "core_identity",
        "polarity": "balanced_flow",
        "planet": "Mars",
        "insight": "Synthesizes panoramic wisdom, humanitarian vision, and creative completion.",
    },
    11: {
        "title": "Master Illuminator (11/2)",
        "trait_tag": "intuitive_depth",
        "domain": "core_identity",
        "polarity": "bold_initiative",
        "planet": "Moon / High-Voltage Uranus",
        "insight": "High-voltage intuitive transmission capable of bridging visionary concepts with human resonance.",
    },
    22: {
        "title": "Master Systems Architect (22/4)",
        "trait_tag": "executive_leadership",
        "domain": "career_wealth",
        "polarity": "bold_initiative",
        "planet": "Saturn / Pluto",
        "insight": "Translates vast visionary blueprints into enduring real-world institutions and technical systems.",
    },
    33: {
        "title": "Master Creative Teacher (33/6)",
        "trait_tag": "creative_communication",
        "domain": "career_wealth",
        "polarity": "balanced_flow",
        "planet": "Venus / Jupiter",
        "insight": "Elevates collective understanding through compassionate mastery and transformative expression.",
    },
}


def _reduce_num(n: int, keep_masters: bool = True) -> int:
    while n > 9:
        if keep_masters and n in (11, 22, 33):
            return n
        n = sum(int(d) for d in str(n))
    return max(0, n)


def _is_vowel(word: str, idx: int) -> bool:
    ch = word[idx]
    if ch in CORE_VOWELS:
        return True
    if ch == "Y":
        # Y is a vowel if there are no adjacent vowels in the syllable
        prev_is_v = (idx > 0) and (word[idx - 1] in CORE_VOWELS)
        next_is_v = (idx < len(word) - 1) and (word[idx + 1] in CORE_VOWELS)
        return not (prev_is_v or next_is_v)
    return False


def _compute_loshu_grid(birth_date: str, life_path: int, birth_day_num: int) -> Dict[str, Any]:
    """
    Computes the classical Lo Shu 3x3 Magic Square:
      4 | 9 | 2   (Mental / Thought Plane)
      3 | 5 | 7   (Emotional / Will Plane)
      8 | 1 | 6   (Practical / Action Plane)
    """
    digits = [int(d) for d in birth_date if d.isdigit() and d != "0"]
    digits.append(_reduce_num(life_path, False))
    digits.append(_reduce_num(birth_day_num, False))

    counts = {i: 0 for i in range(1, 10)}
    for d in digits:
        if 1 <= d <= 9:
            counts[d] += 1

    arrows: List[str] = []
    if counts[4] and counts[9] and counts[2]:
        arrows.append("Arrow of the Intellect / Thought Plane (4-9-2): Strong architectural memory & mental synthesis")
    if counts[3] and counts[5] and counts[7]:
        arrows.append("Arrow of Spiritual & Emotional Will (3-5-7): Deep intuitive conviction & creative resilience")
    if counts[8] and counts[1] and counts[6]:
        arrows.append("Arrow of Practical Execution (8-1-6): Grounded material manifestation & commercial follow-through")
    if counts[4] and counts[5] and counts[6]:
        arrows.append("Golden Arrow of Willpower & Organisation (4-5-6): Unshakable executive persistence")
    if counts[2] and counts[5] and counts[8]:
        arrows.append("Silver Arrow of Earth Balance & Property (2-5-8): Strong real-estate & spatial sensitivity")
    if counts[1] and counts[5] and counts[9]:
        arrows.append("Arrow of Determination & Enterprise (1-5-9): Relentless pioneering momentum")
    if counts[3] and counts[5] and counts[7] or (counts[1] and counts[5]):
        if not arrows:
            arrows.append("Diagonal Axis of Self-Reliance (1-5 / 3-9): Independent problem-solving vector")

    missing = [k for k, v in counts.items() if v == 0]
    return {
        "digit_frequencies": counts,
        "completed_planes_and_arrows": arrows,
        "missing_numbers": missing,
    }


def calculate_numerology(profile_id: str, name: str, birth_date: str) -> Dict[str, Any]:
    parts = birth_date.split("-")
    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])

    # 3-Cycle Reduction for Life Path (Month + Day + Year reduced separately, then summed)
    m_red = _reduce_num(month, keep_masters=True)
    d_red = _reduce_num(day, keep_masters=True)
    y_red = _reduce_num(sum(int(d) for d in str(year)), keep_masters=True)
    lp_compound = m_red + d_red + y_red
    life_path = _reduce_num(lp_compound, keep_masters=True)
    birth_day_num = _reduce_num(day, keep_masters=True)

    # Word-by-word reduction for Pythagorean Expression, Soul Urge & Personality
    words = ["".join(ch for ch in w.upper() if ch.isalpha()) for w in name.split()]
    words = [w for w in words if w] or ["DEVESH"]

    exp_word_sums: List[int] = []
    su_word_sums: List[int] = []
    per_word_sums: List[int] = []
    chald_total = 0

    for w in words:
        w_all = 0
        w_vow = 0
        w_con = 0
        for idx, ch in enumerate(w):
            p_val = PYTHAGOREAN_MAP.get(ch, 0)
            c_val = CHALDEAN_MAP.get(ch, 0)
            w_all += p_val
            chald_total += c_val
            if _is_vowel(w, idx):
                w_vow += p_val
            else:
                w_con += p_val
        exp_word_sums.append(_reduce_num(w_all, keep_masters=True))
        su_word_sums.append(_reduce_num(w_vow, keep_masters=True))
        per_word_sums.append(_reduce_num(w_con, keep_masters=True))

    exp_compound = sum(exp_word_sums)
    expression_num = _reduce_num(exp_compound, keep_masters=True)
    soul_urge_num = _reduce_num(sum(su_word_sums), keep_masters=True)
    personality_num = _reduce_num(sum(per_word_sums), keep_masters=True)
    maturity_num = _reduce_num(_reduce_num(life_path, False) + _reduce_num(expression_num, False), keep_masters=True)
    chaldean_single = _reduce_num(chald_total, keep_masters=False)

    # Karmic Debts (13, 14, 16, 19)
    karmic_debts: List[str] = []
    for raw_val in (day, lp_compound, exp_compound, chald_total):
        if raw_val in KARMIC_DEBT_MEANINGS and KARMIC_DEBT_MEANINGS[raw_val] not in karmic_debts:
            karmic_debts.append(KARMIC_DEBT_MEANINGS[raw_val])

    # 4 Pinnacles & 4 Challenges with Exact Age Windows
    m_base = _reduce_num(month, False)
    d_base = _reduce_num(day, False)
    y_base = _reduce_num(year, False)
    lp_base = _reduce_num(life_path, False)

    p1 = _reduce_num(m_base + d_base, True)
    p2 = _reduce_num(d_base + y_base, True)
    p3 = _reduce_num(p1 + p2, True)
    p4 = _reduce_num(m_base + y_base, True)

    c1 = abs(m_base - d_base)
    c2 = abs(d_base - y_base)
    c3 = abs(c1 - c2)
    c4 = abs(m_base - y_base)

    p1_end_age = 36 - lp_base
    p2_end_age = p1_end_age + 9
    p3_end_age = p2_end_age + 9

    now = datetime.now()
    current_age = max(0, now.year - year)
    if current_age <= p1_end_age:
        active_pinnacle = {"number": p1, "stage": "1st Pinnacle", "age_span": f"Age 0–{p1_end_age}"}
    elif current_age <= p2_end_age:
        active_pinnacle = {"number": p2, "stage": "2nd Pinnacle", "age_span": f"Age {p1_end_age + 1}–{p2_end_age}"}
    elif current_age <= p3_end_age:
        active_pinnacle = {"number": p3, "stage": "3rd Pinnacle (Peak Synthesis)", "age_span": f"Age {p2_end_age + 1}–{p3_end_age}"}
    else:
        active_pinnacle = {"number": p4, "stage": "4th Pinnacle (Legacy)", "age_span": f"Age {p3_end_age + 1}+"}

    personal_year = _reduce_num(m_base + d_base + _reduce_num(now.year, False), keep_masters=False)
    personal_month = _reduce_num(personal_year + _reduce_num(now.month, False), keep_masters=False)

    loshu = _compute_loshu_grid(birth_date, life_path, birth_day_num)

    claims: List[AtomicClaim] = []

    # 1. Life Path Claim
    lp_arch = NUMBER_ARCHETYPES.get(life_path, NUMBER_ARCHETYPES[lp_base])
    claims.append(
        AtomicClaim(
            claim_id=f"clm_num_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="numerology",
            source_label="Pythagorean Life Path & Maturity Calculus",
            domain=lp_arch["domain"],
            trait_tag=lp_arch["trait_tag"],
            action_polarity=lp_arch["polarity"],
            valence="supportive",
            intensity=0.93,
            confidence=0.92,
            raw_feature=f"Life Path {life_path} ({lp_arch['title']}), Birth Day {birth_day_num}, Maturity Number {maturity_num}",
            core_insight=f"Life Path {life_path} ({lp_arch['title']}) converging into Maturity {maturity_num}: {lp_arch['insight']}",
            timing_window=f"Active throughout life; amplified in Personal Year {personal_year}",
        )
    )

    # 2. Expression / Destiny & Chaldean Compound Claim
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
            intensity=0.91,
            confidence=0.90,
            raw_feature=(
                f"Expression Number {expression_num} ({exp_arch['title']}) & "
                f"Chaldean Compound Name {chald_total}/{chaldean_single}"
            ),
            core_insight=(
                f"Expression Number {expression_num} paired with Chaldean Compound {chald_total}/{chaldean_single} "
                f"confirms a natural gift for {exp_arch['title'].lower()}—{exp_arch['insight'].lower()}"
            ),
            timing_window=f"{active_pinnacle['stage']} (Number {active_pinnacle['number']}, {active_pinnacle['age_span']})",
        )
    )

    # 3. Soul Urge (Heart's Desire) Claim
    su_arch = NUMBER_ARCHETYPES.get(soul_urge_num, NUMBER_ARCHETYPES[_reduce_num(soul_urge_num, False)])
    claims.append(
        AtomicClaim(
            claim_id=f"clm_num_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="numerology",
            source_label="Soul Urge (Heart's Desire) & Lo Shu Grid",
            domain="core_identity",
            trait_tag=su_arch["trait_tag"],
            action_polarity=su_arch["polarity"],
            valence="supportive",
            intensity=0.88,
            confidence=0.89,
            raw_feature=(
                f"Soul Urge {soul_urge_num} ({su_arch['title']}) & "
                f"Lo Shu Arrow: {loshu['completed_planes_and_arrows'][0] if loshu['completed_planes_and_arrows'] else 'Self-Reliant Axis'}"
            ),
            core_insight=(
                f"Inner motivation (Soul Urge {soul_urge_num}) demands authentic depth and first-principles mastery: "
                f"{su_arch['insight']}"
            ),
        )
    )

    # 4. Personal Year & Active Pinnacle Timing Claim
    py_arch = NUMBER_ARCHETYPES.get(personal_year, NUMBER_ARCHETYPES[1])
    claims.append(
        AtomicClaim(
            claim_id=f"clm_num_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            discipline="numerology",
            source_label="Numerology Temporal & Pinnacle Engine",
            domain="timing_cycles",
            trait_tag=py_arch["trait_tag"],
            action_polarity=py_arch["polarity"],
            valence="supportive",
            intensity=0.90,
            confidence=0.91,
            raw_feature=(
                f"Personal Year {personal_year} (Personal Month {personal_month}) & "
                f"{active_pinnacle['stage']} {active_pinnacle['number']} ({active_pinnacle['age_span']})"
            ),
            core_insight=(
                f"In {now.year}, Personal Year {personal_year} intersects with {active_pinnacle['stage']} "
                f"{active_pinnacle['number']} ({active_pinnacle['age_span']}), activating {py_arch['title']} momentum: "
                f"{py_arch['insight']}"
            ),
            timing_window=f"{now.year} Personal Year {personal_year} / Month {personal_month}",
        )
    )

    return {
        "discipline": "numerology",
        "life_path": life_path,
        "expression_number": expression_num,
        "soul_urge_number": soul_urge_num,
        "personality_number": personality_num,
        "maturity_number": maturity_num,
        "birth_day_number": birth_day_num,
        "chaldean_compound": f"{chald_total}/{chaldean_single}",
        "karmic_debts": karmic_debts,
        "personal_year": personal_year,
        "personal_month": personal_month,
        "active_pinnacle": active_pinnacle,
        "pinnacles": [
            {"stage": "1st Pinnacle", "number": p1, "challenge": c1, "age_span": f"0–{p1_end_age}"},
            {"stage": "2nd Pinnacle", "number": p2, "challenge": c2, "age_span": f"{p1_end_age + 1}–{p2_end_age}"},
            {"stage": "3rd Pinnacle", "number": p3, "challenge": c3, "age_span": f"{p2_end_age + 1}–{p3_end_age}"},
            {"stage": "4th Pinnacle", "number": p4, "challenge": c4, "age_span": f"{p3_end_age + 1}+"},
        ],
        "loshu_grid": loshu,
        "claims": [c.model_dump() for c in claims],
    }

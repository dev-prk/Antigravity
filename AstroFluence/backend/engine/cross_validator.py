"""Deterministic Cross-Validation & Recursive Deepening (Triangulation) Engine."""

from __future__ import annotations

import uuid
from collections import defaultdict
from typing import Any, Dict, List

from backend.engine.ontology import (
    CANONICAL_TRAITS,
    AtomicClaim,
    ConstructiveTension,
    CrossValidationAudit,
    VerifiedPattern,
)


def _compute_combined_confidence(claims: List[AtomicClaim]) -> float:
    """Probabilistic evidence aggregation across independent disciplines."""
    prod = 1.0
    for c in claims:
        # Weight each claim by 0.75 * confidence so 2 systems yield ~0.90+, 3+ yield ~0.97+
        prod *= 1.0 - (0.75 * c.confidence)
    return round(min(0.995, 1.0 - prod), 3)


def _build_recursive_triangulation(
    trait_tag: str,
    supporting_claims: List[AtomicClaim],
    all_claims: List[AtomicClaim],
    discipline_payloads: Dict[str, Any],
) -> Dict[str, str]:
    """
    Stage 3: Recursive Deep-Dive (Triangulation).
    Once a trait is verified by 2+ independent systems, query the remaining systems
    specifically for:
      1. Mechanism (Astrology houses/planets + Numerology structure)
      2. Timing (Vimshottari Dasha + Numerology Personal Year + Oracles)
      3. Environment (Astrocartography lines + Vastu Shastra / Feng Shui directions)
    """
    trait_meta = CANONICAL_TRAITS.get(trait_tag, CANONICAL_TRAITS["creative_communication"])
    astro = discipline_payloads.get("astrology", {})
    num = discipline_payloads.get("numerology", {})
    loc = discipline_payloads.get("locational", {})
    vastu = discipline_payloads.get("vastu_fengshui", {})
    oracles = discipline_payloads.get("oracles", {})

    # 1. Mechanism Probe (Astrology + Numerology)
    sid_planets = astro.get("sidereal_planets", {})
    ruling_planets = trait_meta.get("ruling_planets", ["Mercury", "Venus"])
    planet_snippets = []
    for p in ruling_planets:
        if p in sid_planets:
            p_info = sid_planets[p]
            planet_snippets.append(f"Sidereal {p} in {p_info['sign']} (House {p_info['house']})")
    if not planet_snippets:
        planet_snippets.append("Natal Ascendant & Midheaven axis")

    lp = num.get("life_path", "—")
    exp = num.get("expression_number", "—")
    mechanism = (
        f"Astrological & Numerical Mechanism: Channeled structurally through {', '.join(planet_snippets)} "
        f"(Houses {'/'.join(str(h) for h in trait_meta.get('ruling_houses', [3, 5]))}) and reinforced by "
        f"Life Path {lp} + Expression {exp}."
    )

    # 2. Timing Probe (Vimshottari Dasha + Personal Year + Symbolic Oracles)
    dasha = astro.get("vimshottari_dasha", {})
    maha = dasha.get("active_mahadasha", "Mercury")
    window = dasha.get("active_window", "Current Cycle")
    py = num.get("personal_year", "—")
    tarot = oracles.get("tarot_card", "The Magician (I)")
    timing = (
        f"Temporal Trigger: Peaks during {maha} Mahadasha ({window}) and Numerology Personal Year {py}, "
        f"with immediate 3–6 month synchronicity highlighted by {tarot}."
    )

    # 3. Environment Probe (Vastu Shastra + Astrocartography)
    target_dirs = trait_meta.get("vastu_directions", ["West", "North-West"])
    ws_zone = vastu.get("workspace_zone", "North-West")
    desk_facing = vastu.get("desk_facing", "North")
    lines = loc.get("planetary_lines", [])
    matching_line = next((ln for ln in lines if ln["planet"] in ruling_planets), None)
    loc_str = (
        f"{matching_line['planet']} MC line near {matching_line['mc_hub']} (ASC near {matching_line['asc_hub']})"
        if matching_line
        else "Mercury/Jupiter angular corridors"
    )
    environment = (
        f"Spatial & Geographic Amplification: Activated locally in the {' / '.join(target_dirs)} Vastu zones "
        f"(current workspace: {ws_zone}, facing {desk_facing}) and globally along your {loc_str}."
    )

    return {
        "mechanism": mechanism,
        "timing": timing,
        "environment": environment,
    }


def run_cross_validation_and_deepening(
    profile_id: str,
    claims: List[AtomicClaim],
    discipline_payloads: Dict[str, Any],
) -> CrossValidationAudit:
    """
    Executes the 3-step deterministic reasoning loop before prose generation:
      Step 1: Pattern Detection across independent disciplines
      Step 2: Cross-Validation (Verified Core Patterns vs. Constructive Tensions vs. Isolated Nuances)
      Step 3: Recursive Deepening (Triangulating Mechanism, Timing, and Environment for every Verified Pattern)
    """
    by_trait: Dict[str, List[AtomicClaim]] = defaultdict(list)
    active_disciplines = sorted({c.discipline for c in claims})

    for c in claims:
        by_trait[c.trait_tag].append(c)

    verified_patterns: List[VerifiedPattern] = []
    isolated_nuances: List[AtomicClaim] = []

    for trait_tag, trait_claims in by_trait.items():
        distinct_disciplines = sorted({c.discipline for c in trait_claims})
        trait_meta = CANONICAL_TRAITS.get(
            trait_tag,
            {
                "title": trait_tag.replace("_", " ").title(),
                "default_domain": trait_claims[0].domain,
            },
        )

        if len(distinct_disciplines) >= 2:
            combined_conf = _compute_combined_confidence(trait_claims)
            triangulation = _build_recursive_triangulation(
                trait_tag=trait_tag,
                supporting_claims=trait_claims,
                all_claims=claims,
                discipline_payloads=discipline_payloads,
            )
            disc_labels = ", ".join(d.replace("_", " ").title() for d in distinct_disciplines)
            headline = (
                f"Confirmed independently across {len(distinct_disciplines)} systems ({disc_labels}) "
                f"with {int(combined_conf * 100)}% cross-validated confidence."
            )
            verified_patterns.append(
                VerifiedPattern(
                    pattern_id=f"pat_{uuid.uuid4().hex[:8]}",
                    trait_tag=trait_tag,
                    title=trait_meta["title"],
                    primary_domain=trait_meta["default_domain"],
                    confirming_disciplines=distinct_disciplines,
                    convergence_count=len(distinct_disciplines),
                    combined_confidence=combined_conf,
                    supporting_claims=trait_claims,
                    recursive_mechanism=triangulation["mechanism"],
                    recursive_timing=triangulation["timing"],
                    recursive_environment=triangulation["environment"],
                    synthesis_headline=headline,
                )
            )
        else:
            isolated_nuances.extend(trait_claims)

    # Sort verified patterns by convergence count then confidence
    verified_patterns.sort(key=lambda p: (p.convergence_count, p.combined_confidence), reverse=True)

    # Detect Constructive Tensions (Divergence between Bold Initiative vs. Cautious Deliberation across different systems)
    bold_claims = [c for c in claims if c.action_polarity == "bold_initiative"]
    cautious_claims = [c for c in claims if c.action_polarity == "cautious_deliberation"]

    constructive_tensions: List[ConstructiveTension] = []
    seen_pairs = set()

    for b_claim in bold_claims:
        for c_claim in cautious_claims:
            if b_claim.discipline == c_claim.discipline:
                continue
            pair_key = tuple(sorted([b_claim.discipline, c_claim.discipline]))
            if pair_key in seen_pairs:
                continue
            # Prefer tensions touching career, core identity, or timing
            seen_pairs.add(pair_key)
            constructive_tensions.append(
                ConstructiveTension(
                    tension_id=f"tns_{uuid.uuid4().hex[:8]}",
                    domain=b_claim.domain,
                    title=f"Expansion Velocity ({b_claim.source_label}) vs. Structural Caution ({c_claim.source_label})",
                    side_a_discipline=b_claim.discipline,
                    side_a_polarity="bold_initiative",
                    side_a_claim=b_claim,
                    side_b_discipline=c_claim.discipline,
                    side_b_polarity="cautious_deliberation",
                    side_b_claim=c_claim,
                    strategic_resolution=(
                        f"While {c_claim.source_label} ({c_claim.raw_feature}) enforces structural caution and "
                        f"architectural verification, {b_claim.source_label} ({b_claim.raw_feature}) signals high-velocity "
                        "initiative. Strategy: Use your somatic/analytical caution for a 48-hour stress-test blueprint, "
                        "then commit with full boldness during the active timing window."
                    ),
                )
            )
            if len(constructive_tensions) >= 3:
                break
        if len(constructive_tensions) >= 3:
            break

    # Build concise Cross-Validation Audit Bullets (as required by the Master Prompt)
    audit_bullets: List[str] = []
    for pat in verified_patterns[:4]:
        sources = " + ".join(
            f"{c.discipline.replace('_', ' ').title()} ({c.raw_feature})"
            for c in pat.supporting_claims[:3]
        )
        audit_bullets.append(
            f"[VERIFIED CORE PATTERN • {int(pat.combined_confidence * 100)}% Confidence] {pat.title}: "
            f"Echoed across {sources}. Recursive Trigger -> {pat.recursive_environment}"
        )
    for tns in constructive_tensions[:2]:
        audit_bullets.append(
            f"[CONSTRUCTIVE TENSION] {tns.title}: {tns.strategic_resolution}"
        )

    return CrossValidationAudit(
        profile_id=profile_id,
        total_claims_analyzed=len(claims),
        active_disciplines=active_disciplines,
        verified_core_patterns=verified_patterns,
        constructive_tensions=constructive_tensions,
        isolated_nuances=isolated_nuances,
        audit_bullets=audit_bullets,
    )

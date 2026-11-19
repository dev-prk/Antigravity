"""Master Orchestrator coordinating all 6 Core Discipline Pillars, Claim Ledger, and Cross-Validation."""

from __future__ import annotations

from typing import Any, Dict, List

from backend.engine.ai_router import generate_unified_synthesis
from backend.engine.cross_validator import run_cross_validation_and_deepening
from backend.engine.disciplines.astrology import calculate_astrology
from backend.engine.disciplines.locational import calculate_locational_astrology
from backend.engine.disciplines.numerology import calculate_numerology
from backend.engine.disciplines.oracles import analyze_oracles_and_custom
from backend.engine.disciplines.palmistry import analyze_palmistry
from backend.engine.disciplines.vastu_fengshui import analyze_vastu_fengshui
from backend.engine.ontology import AtomicClaim, ProfileInput


def compute_full_profile_readings(profile_id: str, inp: ProfileInput) -> Dict[str, Any]:
    """
    Runs all 6 Core Discipline Engines + Custom Discipline Note Importer for a profile,
    collects all AtomicClaims, and executes the deterministic Cross-Validation & Recursive
    Deepening loop.
    """
    astro_res = calculate_astrology(
        profile_id=profile_id,
        birth_date=inp.birth_date,
        birth_time=inp.birth_time,
        timezone_offset=inp.timezone_offset,
        latitude=inp.latitude,
        longitude=inp.longitude,
    )
    num_res = calculate_numerology(
        profile_id=profile_id,
        name=inp.name,
        birth_date=inp.birth_date,
    )
    loc_res = calculate_locational_astrology(
        profile_id=profile_id,
        birth_date=inp.birth_date,
        birth_time=inp.birth_time,
        timezone_offset=inp.timezone_offset,
        birth_lat=inp.latitude,
        birth_lon=inp.longitude,
    )
    vastu_res = analyze_vastu_fengshui(
        profile_id=profile_id,
        vastu_data=inp.vastu_data,
    )
    palm_res = analyze_palmistry(
        profile_id=profile_id,
        palmistry_data=inp.palmistry_data,
    )
    oracle_res = analyze_oracles_and_custom(
        profile_id=profile_id,
        seed_key=f"{inp.name}:{inp.birth_date}:{inp.birth_time}",
        oracle_data=inp.oracle_data,
        custom_notes=inp.custom_notes,
    )

    discipline_payloads = {
        "astrology": astro_res,
        "numerology": num_res,
        "locational": loc_res,
        "vastu_fengshui": vastu_res,
        "palmistry": palm_res,
        "oracles": oracle_res,
    }

    all_claims: List[AtomicClaim] = []
    for payload in discipline_payloads.values():
        for raw_c in payload.get("claims", []):
            all_claims.append(AtomicClaim(**raw_c))

    audit = run_cross_validation_and_deepening(
        profile_id=profile_id,
        claims=all_claims,
        discipline_payloads=discipline_payloads,
    )

    return {
        "profile_id": profile_id,
        "profile_input": inp.model_dump(),
        "disciplines": discipline_payloads,
        "claims": [c.model_dump() for c in all_claims],
        "cross_validation_audit": audit.model_dump(),
    }


async def run_chat_synthesis(
    profile_bundle: Dict[str, Any],
    user_query: str,
    include_audit_section: bool = True,
    preferred_route: str = "auto",
) -> Dict[str, Any]:
    from backend.engine.ontology import CrossValidationAudit

    inp = profile_bundle["profile_input"]
    audit = CrossValidationAudit(**profile_bundle["cross_validation_audit"])
    disciplines = profile_bundle["disciplines"]

    res = await generate_unified_synthesis(
        profile_name=inp["name"],
        user_query=user_query,
        audit=audit,
        discipline_payloads=disciplines,
        include_audit_section=include_audit_section,
        preferred_route=preferred_route,
    )
    return res

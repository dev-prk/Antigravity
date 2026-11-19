"""End-to-End Verification Suite for AstroFluence: 6 Core Pillars, Cross-Validation, Recursive Triangulation & API."""

from fastapi.testclient import TestClient

from backend.engine.ontology import ProfileInput
from backend.engine.synthesizer import compute_full_profile_readings
from backend.main import app


def test_cross_validation_and_recursive_triangulation():
    """
    Verifies the exact 3-step reasoning loop from the user's specification:
    1. Palmistry (Deep forked Head Line sloping toward Mount of Moon) + Numerology (Expression 3)
       -> Detected as a Verified Core Pattern ('creative_communication') across 2+ independent systems.
    2. Confidence Score elevated (> 0.90).
    3. Recursive Deepening queries Astrology (Mercury/Venus/Houses) and Vastu/Astrocartography (North-West/West).
    """
    inp = ProfileInput(
        name="Devesh Prakash",
        birth_date="1996-08-15",
        birth_time="10:30",
        timezone_offset=5.5,
        birth_city="New Delhi, India",
        latitude=28.6139,
        longitude=77.2090,
        palmistry_data={
            "head_line": "forked_to_moon",
            "fate_line": "deep_to_saturn_and_jupiter",
            "dominant_mounts": "mercury_and_moon",
        },
        vastu_data={
            "entrance_direction": "North-East",
            "workspace_zone": "North-West",
            "desk_facing": "North",
        },
    )

    bundle = compute_full_profile_readings("prf_test_triangulation", inp)
    audit = bundle["cross_validation_audit"]

    assert audit["total_claims_analyzed"] >= 15
    assert len(audit["active_disciplines"]) >= 6

    verified_tags = {p["trait_tag"]: p for p in audit["verified_core_patterns"]}
    assert "creative_communication" in verified_tags
    cc_pat = verified_tags["creative_communication"]

    # Confirm both Palmistry and Numerology (plus Astrology/Vastu) independently confirmed it
    assert "palmistry" in cc_pat["confirming_disciplines"]
    assert "numerology" in cc_pat["confirming_disciplines"]
    assert cc_pat["combined_confidence"] >= 0.90

    # Confirm Recursive Deepening populated Mechanism, Timing, and Environment
    assert "Mercury" in cc_pat["recursive_mechanism"]
    assert "Mahadasha" in cc_pat["recursive_timing"]
    assert "North-West" in cc_pat["recursive_environment"]

    # Confirm Constructive Tensions are detected between cautious palm lines and bold astrological/numerological cycles
    assert len(audit["constructive_tensions"]) >= 1


def test_api_endpoints_and_dual_frontends():
    with TestClient(app) as client:
        # 1. Health & AI-OS Zero-Cost Router check
        r_health = client.get("/api/health")
        assert r_health.status_code == 200
        h_data = r_health.json()
        assert h_data["zero_cost_enforced"] is True
        assert any(rt["id"] == "aios_deterministic_compiler" for rt in h_data["routes"])

        # 2. Seeded Profiles check
        r_profs = client.get("/api/profiles")
        assert r_profs.status_code == 200
        profiles = r_profs.json()["profiles"]
        assert len(profiles) >= 2

        # 3. Single Profile Bundle inspection
        r_bundle = client.get("/api/profiles/prf_devesh_prime")
        assert r_bundle.status_code == 200
        b_data = r_bundle.json()
        assert "astrology" in b_data["disciplines"]
        assert "numerology" in b_data["disciplines"]
        assert "palmistry" in b_data["disciplines"]
        assert "vastu_fengshui" in b_data["disciplines"]
        assert "locational" in b_data["disciplines"]
        assert "oracles" in b_data["disciplines"]

        # 4. Unified Synthesis Chat check (organized by Life Theme, $0.00 cost)
        r_chat = client.post(
            "/api/chat/synthesize",
            json={
                "profile_id": "prf_devesh_prime",
                "query": "Based on this synthesis, what should my top priority be over the next 6 months?",
                "surface": "workbench",
                "include_audit_section": True,
            },
        )
        assert r_chat.status_code == 200
        c_data = r_chat.json()
        assert c_data["telemetry"]["verified_cost_usd"] == 0.0
        assert "Core Identity" in c_data["synthesis_markdown"]
        assert "Career Trajectory" in c_data["synthesis_markdown"]
        assert "Optimal Environment" in c_data["synthesis_markdown"]

        # 5. Progressive Enrichment endpoint check
        r_enrich = client.post(
            "/api/profiles/prf_devesh_prime/enrich",
            json={
                "custom_note": {
                    "discipline_name": "Chronomancy & Muhurat",
                    "text": "Auspicious waxing moon mercury window favors creative communication and product launch.",
                    "trait_tag": "creative_communication",
                }
            },
        )
        assert r_enrich.status_code == 200
        assert r_enrich.json()["cross_validation_audit"]["total_claims_analyzed"] > b_data["cross_validation_audit"]["total_claims_analyzed"]

        # 6. Dual Frontend HTML routes check
        r_wb = client.get("/workbench")
        assert r_wb.status_code == 200
        assert "AstroFluence Workbench" in r_wb.text

        r_cb = client.get("/chat")
        assert r_cb.status_code == 200
        assert "6-Discipline Unified Oracle" in r_cb.text

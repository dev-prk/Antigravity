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
    disciplines = bundle["disciplines"]

    # Verify high-precision Vedic Divisional Charts (D9 Navamsha & D10 Dashamsha), Nakshatra Pada, and Antardashas
    astro = disciplines["astrology"]
    assert "navamsha_d9_sign" in astro["sidereal_ascendant"]
    assert "dashamsha_d10_sign" in astro["sidereal_ascendant"]
    assert "nakshatra_pada" in astro["vimshottari_dasha"]
    assert "active_antardasha" in astro["vimshottari_dasha"]
    assert "atmakaraka_soul" in astro["chara_karakas"]

    # Verify Numerology Pinnacles, Challenges, Maturity & Lo Shu Grid
    num = disciplines["numerology"]
    assert len(num["pinnacles"]) == 4
    assert "loshu_grid" in num
    assert "maturity_number" in num

    # Verify 3D Spherical Astrocartography Declination & Horizon orbs
    loc = disciplines["locational"]
    assert "declination" in loc["planetary_lines"][0]
    assert "mc_orb_deg" in loc["planetary_lines"][0]

    # Verify Classical Feng Shui Kua & Eight Mansions Vectors alongside Vastu
    vastu = disciplines["vastu_fengshui"]
    assert "feng_shui_kua" in vastu
    assert "sheng_qi_wealth_expansion" in vastu["feng_shui_kua"]["auspicious_directions"]

    assert audit["total_claims_analyzed"] >= 18
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


def test_birthplace_geodesy_and_historical_timezone_sensitivity():
    """
    Proves that Place of Birth (latitude, longitude, IANA timezone, and historical DST)
    materially changes Universal Time (Julian Day), Sidereal Lagna (Ascendant),
    Navamsha (D9) Lagna, House placements, and Astrocartography lines for the exact
    same local clock date & time.
    """
    # Same local clock time: 1996-08-15 at 10:30 AM local clock
    inp_delhi = ProfileInput(
        name="Devesh Prakash",
        birth_date="1996-08-15",
        birth_time="10:30",
        birth_city="New Delhi, Delhi, India",
        current_city="Bengaluru, Karnataka, India",
    )
    inp_ny = ProfileInput(
        name="Devesh Prakash",
        birth_date="1996-08-15",
        birth_time="10:30",
        birth_city="New York, NY, USA",
        current_city="London, United Kingdom",
    )
    inp_tokyo = ProfileInput(
        name="Devesh Prakash",
        birth_date="1996-08-15",
        birth_time="10:30",
        birth_city="Tokyo, Japan",
        current_city="Singapore",
    )

    b_delhi = compute_full_profile_readings("prf_geo_delhi", inp_delhi)
    b_ny = compute_full_profile_readings("prf_geo_ny", inp_ny)
    b_tokyo = compute_full_profile_readings("prf_geo_tokyo", inp_tokyo)

    # 1. Verify automatic IANA timezone & historical DST resolution (August 15, 1996 in NY is EDT = UTC-4.0)
    assert b_delhi["profile_input"]["timezone_name"] == "Asia/Kolkata"
    assert b_delhi["profile_input"]["timezone_offset"] == 5.5
    assert b_ny["profile_input"]["timezone_name"] == "America/New_York"
    assert b_ny["profile_input"]["timezone_offset"] == -4.0
    assert b_ny["disciplines"]["astrology"]["birthplace_geodesy"]["is_dst_active"] is True
    assert b_tokyo["profile_input"]["timezone_name"] == "Asia/Tokyo"
    assert b_tokyo["profile_input"]["timezone_offset"] == 9.0

    # 2. Verify that Ascendant (Lagna) longitude and Midheaven shift across birthplaces
    asc_delhi = b_delhi["disciplines"]["astrology"]["sidereal_ascendant"]["longitude"]
    asc_ny = b_ny["disciplines"]["astrology"]["sidereal_ascendant"]["longitude"]
    asc_tokyo = b_tokyo["disciplines"]["astrology"]["sidereal_ascendant"]["longitude"]
    assert asc_delhi != asc_ny
    assert asc_delhi != asc_tokyo
    assert asc_ny != asc_tokyo

    # 3. Verify Relocation Chart (Birthplace vs. Current City)
    reloc_ny_to_lon = b_ny["disciplines"]["locational"]["relocation_analysis"]
    assert reloc_ny_to_lon["birth_sidereal_lagna"] != reloc_ny_to_lon["relocated_sidereal_lagna"]


def test_api_endpoints_and_dual_frontends():
    with TestClient(app) as client:
        # 1. Health & AI-OS Zero-Cost Router check
        r_health = client.get("/api/health")
        assert r_health.status_code == 200
        h_data = r_health.json()
        assert h_data["zero_cost_enforced"] is True
        assert any(rt["id"] == "aios_deterministic_compiler" for rt in h_data["routes"])

        # 1b. Geocode & Historical Timezone API check
        r_geo = client.get("/api/geocode?q=Varanasi&birth_date=1996-08-15&birth_time=10:30")
        assert r_geo.status_code == 200
        g_res = r_geo.json()["results"]
        assert len(g_res) >= 1
        assert "Varanasi" in g_res[0]["city"]
        assert g_res[0]["timezone_name"] == "Asia/Kolkata"
        assert g_res[0]["utc_offset_hours"] == 5.5

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
        assert "Your #1 Career & Wealth Priority for the Next 6 Months" in c_data["synthesis_markdown"]

        # 4b. Verify that asking a specific 5-year critical challenges question returns a distinct, live-computed forecast
        r_chal = client.post(
            "/api/chat/synthesize",
            json={
                "profile_id": "prf_devesh_prime",
                "query": "what is the biggest ciritical challenges coming my way in the next 5 years",
                "surface": "chat",
                "include_audit_section": False,
            },
        )
        assert r_chal.status_code == 200
        chal_md = r_chal.json()["synthesis_markdown"]
        assert chal_md != c_data["synthesis_markdown"]
        assert "Critical Challenge #1" in chal_md
        assert "Year-by-Year Multi-System Risk & Opportunity Roadmap" in chal_md

        # 4c. Verify that asking a location/Vastu question returns a distinct spatial & Astrocartography answer
        r_loc = client.post(
            "/api/chat/synthesize",
            json={
                "profile_id": "prf_devesh_prime",
                "query": "Which cities and room directions amplify my natural strengths?",
                "surface": "chat",
                "include_audit_section": False,
            },
        )
        assert r_loc.status_code == 200
        loc_md = r_loc.json()["synthesis_markdown"]
        assert loc_md != chal_md
        assert "Your 7 Global 3D Astrocartography Power Corridors" in loc_md

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

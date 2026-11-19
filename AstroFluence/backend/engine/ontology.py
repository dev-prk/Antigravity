"""Canonical Ontology, Data Contracts, and Atomic Claim Schemas for AstroFluence."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

LifeDomain = Literal[
    "core_identity",
    "career_wealth",
    "relationships",
    "health_energy",
    "space_location",
    "timing_cycles",
]

ActionPolarity = Literal[
    "bold_initiative",
    "cautious_deliberation",
    "balanced_flow",
]

ValenceType = Literal[
    "supportive",
    "challenging",
    "neutral_directive",
]

# Standardized Cross-Disciplinary Semantic Trait Ontology (16 High-Resolution Archetypal Vectors)
CANONICAL_TRAITS: Dict[str, Dict[str, Any]] = {
    "creative_communication": {
        "title": "Creative Communication & Story Architecture",
        "default_domain": "career_wealth",
        "ruling_planets": ["Mercury", "Venus", "Moon"],
        "ruling_houses": [3, 5],
        "vastu_directions": ["North-West", "West", "North"],
        "feng_shui_bagua": ["Dui (West / Children & Creativity)", "Qian (North-West / Helpful People & Travel)"],
        "element": "Air / Water",
        "description": "Ability to synthesize imagination, non-linear ideation, and persuasive storytelling or media/system design.",
    },
    "executive_leadership": {
        "title": "Autonomous Leadership & Strategic Authority",
        "default_domain": "career_wealth",
        "ruling_planets": ["Sun", "Saturn", "Mars", "Jupiter"],
        "ruling_houses": [1, 10, 11],
        "vastu_directions": ["East", "North-East", "South"],
        "feng_shui_bagua": ["Li (South / Fame & Recognition)", "Qian (North-West / Heaven & Leadership)"],
        "element": "Fire / Earth",
        "description": "Drive to build independent systems, command responsibility, and lead high-impact ventures without micromanagement.",
    },
    "analytical_precision": {
        "title": "Systems Architecture & Analytical Precision",
        "default_domain": "core_identity",
        "ruling_planets": ["Mercury", "Saturn"],
        "ruling_houses": [3, 6, 11],
        "vastu_directions": ["North", "North-East"],
        "feng_shui_bagua": ["Gen (North-East / Knowledge & Self-Cultivation)", "Kan (North / Career Flow)"],
        "element": "Earth / Air",
        "description": "Methodical problem solving, structural logic, mathematical verification, and investigative rigor.",
    },
    "intuitive_depth": {
        "title": "Esoteric & Psychological Pattern Intuition",
        "default_domain": "core_identity",
        "ruling_planets": ["Moon", "Ketu", "Jupiter"],
        "ruling_houses": [8, 9, 12],
        "vastu_directions": ["North-East", "South-West"],
        "feng_shui_bagua": ["Gen (North-East / Inner Wisdom)"],
        "element": "Water / Ether",
        "description": "Capacity to perceive hidden motives, symbolic structures, occult sciences, and subsurface psychological truths.",
    },
    "adaptive_change": {
        "title": "Catalytic Mobility & Reinvention",
        "default_domain": "timing_cycles",
        "ruling_planets": ["Rahu", "Mercury", "Mars"],
        "ruling_houses": [3, 9, 11],
        "vastu_directions": ["North-West"],
        "feng_shui_bagua": ["Qian (North-West / Movement)", "Zhen (East / New Beginnings)"],
        "element": "Air",
        "description": "High responsiveness to cross-border opportunities, technological shifts, relocation, and rapid strategic pivots.",
    },
    "relational_harmony": {
        "title": "Magnetic Partnership & Emotional Resonance",
        "default_domain": "relationships",
        "ruling_planets": ["Venus", "Jupiter", "Moon"],
        "ruling_houses": [2, 4, 7],
        "vastu_directions": ["South-East", "South-West", "North-West"],
        "feng_shui_bagua": ["Kun (South-West / Love & Partnerships)"],
        "element": "Water / Fire",
        "description": "Deep loyalty, diplomatic magnetism, and high sensitivity to harmony in close alliances and domestic sanctuaries.",
    },
    "disciplined_endurance": {
        "title": "Long-Arc Mastery & Structural Endurance",
        "default_domain": "health_energy",
        "ruling_planets": ["Saturn", "Mars"],
        "ruling_houses": [6, 8, 10],
        "vastu_directions": ["South-West", "South"],
        "feng_shui_bagua": ["Kun (South-West / Earth Stability)", "Zhen (East / Vitality)"],
        "element": "Earth",
        "description": "Resilience under pressure, compounding focus over multi-year cycles, and disciplined physical/mental stamina.",
    },
    "material_manifestation": {
        "title": "Resource Alchemy & Wealth Accumulation",
        "default_domain": "career_wealth",
        "ruling_planets": ["Jupiter", "Venus", "Saturn", "Mercury"],
        "ruling_houses": [2, 8, 11],
        "vastu_directions": ["North", "North-East", "South-East"],
        "feng_shui_bagua": ["Xun (South-East / Wealth & Prosperity)", "Kan (North / Treasury)"],
        "element": "Earth / Water",
        "description": "Pragmatic conversion of intellectual or creative capital into tangible assets, equity, and multi-stream financial flow.",
    },
    "visionary_innovation": {
        "title": "Frontier Innovation & Paradigm Disruption",
        "default_domain": "career_wealth",
        "ruling_planets": ["Rahu", "Mercury", "Sun"],
        "ruling_houses": [5, 9, 11],
        "vastu_directions": ["North-East", "North-West", "East"],
        "feng_shui_bagua": ["Zhen (East / Thunder & Breakthrough)"],
        "element": "Ether / Air",
        "description": "Originality that challenges convention, synthesizing emerging technology, esoteric philosophy, and future systems.",
    },
    "spiritual_sovereignty": {
        "title": "Philosophical Sovereignty & Inner Sanctuary",
        "default_domain": "core_identity",
        "ruling_planets": ["Ketu", "Jupiter", "Saturn"],
        "ruling_houses": [4, 9, 12],
        "vastu_directions": ["North-East", "Center (Brahmasthana)"],
        "feng_shui_bagua": ["Tai Qi (Center / Balance)", "Gen (North-East / Contemplation)"],
        "element": "Ether",
        "description": "Detachment from superficial status games, anchored in self-knowledge, dharma, and contemplative clarity.",
    },
}

DISCIPLINE_CATALOG: Dict[str, Dict[str, str]] = {
    "astrology": {
        "name": "Vedic Jyotish (D1/D9/Ashtakavarga/Yogas/Dashas) & Western Tropical Astrology",
        "category": "Celestial & Time-Based Systems",
        "badge": "Celestial",
    },
    "numerology": {
        "name": "Pythagorean, Chaldean & Lo Shu Grid Numerology",
        "category": "Number, Letter & Symbol Systems",
        "badge": "Mathematical",
    },
    "locational": {
        "name": "Locational Astrology (3D Spherical Astrocartography & Relocation Chart)",
        "category": "Location, Space & Earth Systems",
        "badge": "Geographic",
    },
    "vastu_fengshui": {
        "name": "Vastu Shastra (16-Zone MahaVastu) & Classical Kua/Flying Star Feng Shui",
        "category": "Location, Space & Earth Systems",
        "badge": "Spatial",
    },
    "palmistry": {
        "name": "Palmistry (Chiromancy & Classical Samudrika Shastra)",
        "category": "Body & Physical Trait Reading",
        "badge": "Somatic",
    },
    "oracles": {
        "name": "Symbolic Oracles (78-Card Tarot, 64-Hexagram I Ching, Elder Futhark Runes & Custom Arts)",
        "category": "Card, Tile & Lot Casting",
        "badge": "Synchronistic",
    },
}


class AtomicClaim(BaseModel):
    claim_id: str
    profile_id: str
    discipline: str
    source_label: str
    domain: LifeDomain
    trait_tag: str
    action_polarity: ActionPolarity = "balanced_flow"
    valence: ValenceType = "supportive"
    intensity: float = Field(default=0.82, ge=0.0, le=1.0)
    confidence: float = Field(default=0.86, ge=0.0, le=1.0)
    raw_feature: str
    core_insight: str
    timing_window: Optional[str] = None
    spatial_direction: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VerifiedPattern(BaseModel):
    pattern_id: str
    trait_tag: str
    title: str
    primary_domain: LifeDomain
    confirming_disciplines: List[str]
    convergence_count: int
    combined_confidence: float
    supporting_claims: List[AtomicClaim]
    recursive_mechanism: str
    recursive_timing: str
    recursive_environment: str
    synthesis_headline: str


class ConstructiveTension(BaseModel):
    tension_id: str
    domain: LifeDomain
    title: str
    side_a_discipline: str
    side_a_polarity: str
    side_a_claim: AtomicClaim
    side_b_discipline: str
    side_b_polarity: str
    side_b_claim: AtomicClaim
    strategic_resolution: str


class CrossValidationAudit(BaseModel):
    profile_id: str
    total_claims_analyzed: int
    active_disciplines: List[str]
    verified_core_patterns: List[VerifiedPattern]
    constructive_tensions: List[ConstructiveTension]
    isolated_nuances: List[AtomicClaim]
    domain_consensus_scores: Dict[str, float] = Field(default_factory=dict)
    audit_bullets: List[str]


class ProfileInput(BaseModel):
    name: str
    gender: str = Field(default="male", description="male | female | neutral (used for classical Feng Shui Kua calculation)")
    birth_date: str = Field(description="YYYY-MM-DD")
    birth_time: str = Field(default="12:00", description="HH:MM (24h)")
    timezone_name: Optional[str] = Field(default=None, description="IANA timezone e.g. Asia/Kolkata, America/New_York")
    timezone_offset: Optional[float] = Field(default=None, description="Auto-computed historical UTC offset in hours from birthplace & birth date")
    birth_city: str = Field(default="New Delhi, Delhi, India")
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    current_city: Optional[str] = Field(default="Bengaluru, Karnataka, India")
    current_latitude: Optional[float] = Field(default=None)
    current_longitude: Optional[float] = Field(default=None)
    palmistry_data: Optional[Dict[str, Any]] = None
    vastu_data: Optional[Dict[str, Any]] = None
    oracle_data: Optional[Dict[str, Any]] = None
    custom_notes: Optional[List[Dict[str, Any]]] = None

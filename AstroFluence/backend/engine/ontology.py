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

# Standardized Cross-Disciplinary Semantic Trait Ontology
CANONICAL_TRAITS: Dict[str, Dict[str, Any]] = {
    "creative_communication": {
        "title": "Creative Communication & Story Architecture",
        "default_domain": "career_wealth",
        "ruling_planets": ["Mercury", "Venus", "Moon"],
        "ruling_houses": [3, 5],
        "vastu_directions": ["West", "North-West", "North"],
        "element": "Air / Water",
        "description": "Ability to synthesize imagination, non-linear ideation, and expressive storytelling or design.",
    },
    "executive_leadership": {
        "title": "Autonomous Leadership & Strategic Authority",
        "default_domain": "career_wealth",
        "ruling_planets": ["Sun", "Saturn", "Mars", "Jupiter"],
        "ruling_houses": [1, 10, 11],
        "vastu_directions": ["East", "North-East", "South"],
        "element": "Fire / Earth",
        "description": "Drive to build independent systems, command responsibility, and lead high-impact ventures.",
    },
    "analytical_precision": {
        "title": "Systems Architecture & Analytical Precision",
        "default_domain": "core_identity",
        "ruling_planets": ["Mercury", "Saturn", "Uranus"],
        "ruling_houses": [3, 6, 11],
        "vastu_directions": ["North", "North-East"],
        "element": "Earth / Air",
        "description": "Methodical problem solving, structural logic, pattern recognition, and investigative rigor.",
    },
    "intuitive_depth": {
        "title": "Esoteric & Psychological Pattern Intuition",
        "default_domain": "core_identity",
        "ruling_planets": ["Moon", "Ketu", "Neptune", "Pluto"],
        "ruling_houses": [8, 9, 12],
        "vastu_directions": ["North-East", "South-West"],
        "element": "Water / Ether",
        "description": "Capacity to perceive hidden motives, symbolic structures, and subsurface emotional or spiritual truths.",
    },
    "adaptive_change": {
        "title": "Catalytic Mobility & Reinvention",
        "default_domain": "timing_cycles",
        "ruling_planets": ["Rahu", "Mercury", "Uranus"],
        "ruling_houses": [3, 9, 11],
        "vastu_directions": ["North-West"],
        "element": "Air",
        "description": "High responsiveness to travel, cross-border opportunities, technological shifts, and rapid pivots.",
    },
    "relational_harmony": {
        "title": "Magnetic Partnership & Emotional Resonance",
        "default_domain": "relationships",
        "ruling_planets": ["Venus", "Jupiter", "Moon"],
        "ruling_houses": [2, 4, 7],
        "vastu_directions": ["South-East", "South-West", "North-West"],
        "element": "Water / Fire",
        "description": "Deep loyalty, diplomatic magnetism, and high sensitivity to harmony in close alliances and home spaces.",
    },
    "disciplined_endurance": {
        "title": "Long-Arc Mastery & Structural Endurance",
        "default_domain": "health_energy",
        "ruling_planets": ["Saturn", "Mars"],
        "ruling_houses": [6, 8, 10],
        "vastu_directions": ["South-West", "South"],
        "element": "Earth",
        "description": "Resilience under pressure, compounding focus over multi-year cycles, and physical/mental stamina.",
    },
    "material_manifestation": {
        "title": "Resource Alchemy & Wealth Accumulation",
        "default_domain": "career_wealth",
        "ruling_planets": ["Jupiter", "Venus", "Saturn"],
        "ruling_houses": [2, 8, 11],
        "vastu_directions": ["North", "North-East", "South-East"],
        "element": "Earth / Water",
        "description": "Pragmatic conversion of intellectual or creative capital into tangible assets and financial stability.",
    },
}

DISCIPLINE_CATALOG: Dict[str, Dict[str, str]] = {
    "astrology": {
        "name": "Vedic & Western Astrology",
        "category": "Celestial & Time-Based Systems",
        "badge": "Celestial",
    },
    "numerology": {
        "name": "Pythagorean & Chaldean Numerology",
        "category": "Number, Letter & Symbol Systems",
        "badge": "Mathematical",
    },
    "locational": {
        "name": "Locational Astrology (Astrocartography)",
        "category": "Location, Space & Earth Systems",
        "badge": "Geographic",
    },
    "vastu_fengshui": {
        "name": "Vastu Shastra & Feng Shui",
        "category": "Location, Space & Earth Systems",
        "badge": "Spatial",
    },
    "palmistry": {
        "name": "Palmistry (Chiromancy & Samudrika Shastra)",
        "category": "Body & Physical Trait Reading",
        "badge": "Somatic",
    },
    "oracles": {
        "name": "Symbolic Oracles (Tarot & I Ching)",
        "category": "Card, Tile & Lot Casting",
        "badge": "Synchronistic",
    },
    "custom": {
        "name": "Custom Esoteric Discipline (Graphology / Physiognomy / Runes / Omens)",
        "category": "Extended Divinatory Arts",
        "badge": "Extended",
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
    intensity: float = Field(default=0.8, ge=0.0, le=1.0)
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
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
    audit_bullets: List[str]


class ProfileInput(BaseModel):
    name: str
    birth_date: str = Field(description="YYYY-MM-DD")
    birth_time: str = Field(default="12:00", description="HH:MM (24h)")
    timezone_offset: float = Field(default=5.5, description="UTC offset in hours, e.g. 5.5 for IST")
    birth_city: str = Field(default="New Delhi, India")
    latitude: float = Field(default=28.6139)
    longitude: float = Field(default=77.2090)
    current_city: Optional[str] = Field(default="Bengaluru, India")
    palmistry_data: Optional[Dict[str, Any]] = None
    vastu_data: Optional[Dict[str, Any]] = None
    oracle_data: Optional[Dict[str, Any]] = None
    custom_notes: Optional[List[Dict[str, Any]]] = None

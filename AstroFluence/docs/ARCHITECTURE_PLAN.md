# AstroFluence: Architecture & Cross-Disciplinary Esoteric Synthesis Blueprint

AstroFluence is a dual-interface **Cross-Disciplinary Esoteric Synthesis Platform** engineered under `/ai-os` principles. Instead of treating divinatory and spatial traditions as isolated silos or dumping raw text into a single giant prompt, AstroFluence models every discipline as a structured producer of **Atomic Claims** mapped to a **Canonical Ontology**, executes deterministic **Cross-Validation & Recursive Deepening (Triangulation)**, and synthesizes one cohesive, theme-organized response.

---

## 1. Taxonomy of Supported Esoteric & Spatial Disciplines

AstroFluence organizes the esoteric and divinatory arts into **6 Core First-Class Pillars** plus an extensible **Universal Custom Discipline Importer** covering 25+ classical traditions:

| Pillar ID | Pillar Name | Sub-Systems Calculated / Ingested | Primary Input Modalities | Primary Life Domains |
| :--- | :--- | :--- | :--- | :--- |
| **`astrology`** | **Celestial & Time-Based Systems** | Western Tropical Natal, Vedic Jyotish (Sidereal Lahiri), Nakshatras, Vimshottari Dasha, Planetary Transits, Horary/Prashna, Electional/Muhurat | Birth Date, Exact Time, Birth Latitude/Longitude | All Domains (`core_identity`, `career_wealth`, `relationships`, `timing_cycles`) |
| **`numerology`** | **Number, Letter & Symbol Systems** | Pythagorean & Chaldean Numerology (Life Path, Expression/Destiny, Soul Urge, Personality, Personal Year, Pinnacles), Gematria/Arithmancy/Onomancy | Full Birth Name, Common Name, Birth Date | `core_identity`, `career_wealth`, `timing_cycles` |
| **`locational`** | **Locational Astrology** | Astrocartography (Planetary Angular Lines: MC, IC, ASC, DSC), Relocation Charting | Birth Date/Time/Coordinates + Target Cities | `space_location`, `career_wealth`, `relationships` |
| **`vastu_fengshui`** | **Spatial & Architectural Systems** | Vastu Shastra (8 Cardinal/Intercardinal Directions + Pancha Bhoota 5 Elements), Classical Feng Shui (Bagua & Desk/Entrance Command) | Entrance Direction, Workspace/Desk Facing, Bedroom Quadrant, Floor Plan Image/Notes | `space_location`, `career_wealth`, `health_energy`, `relationships` |
| **`palmistry`** | **Body & Physical Trait Reading** | Palmistry / Chiromancy & Samudrika Shastra (Head Line, Heart Line, Life Line, Fate Line, Mounts of Jupiter/Saturn/Apollo/Mercury/Moon/Venus, Hand Element) | Structured Trait Checklist, Raw Palm Reading Notes, or Palm Photo Vision Analysis | `core_identity`, `career_wealth`, `relationships`, `health_energy` |
| **`oracles`** | **Card, Tile, Lot & Omen Casting** | 78-Card Tarot Archetypes, 64-Hexagram I Ching (Book of Changes), plus Custom Importer for Runes, Graphology, Physiognomy, Tasseography, Oneiromancy | Interactive In-App Draw/Cast or Raw Reading Paste | `timing_cycles`, `core_identity`, `career_wealth`, `relationships` |

---

## 2. The 4-Stage Cross-Validation & Recursive Deepening Protocol

### Stage 1: Atomic Claim Extraction & Canonical Ontology Tagging
Every discipline module translates its mathematical calculations or parsed observations into normalized `AtomicClaim` objects:
- `discipline`: Source pillar (`astrology`, `numerology`, `locational`, `vastu_fengshui`, `palmistry`, `oracles`, or custom slug)
- `domain`: One of `core_identity`, `career_wealth`, `relationships`, `health_energy`, `space_location`, `timing_cycles`
- `trait_tag`: Canonical semantic key (e.g., `creative_communication`, `executive_leadership`, `analytical_precision`, `intuitive_depth`, `adaptive_change`, `relational_harmony`, `disciplined_endurance`, `material_manifestation`)
- `action_polarity`: `bold_initiative` | `cautious_deliberation` | `balanced_flow`
- `valence`: `supportive` | `challenging` | `neutral_directive`
- `confidence`: Base reliability score ($0.0 - 1.0$)
- `raw_feature`: Exact technical proof (e.g., *"Deep, forked Head Line sloping toward Mount of Moon"* or *"Expression Number 3 + Life Path 1"*)
- `core_insight`: 1–2 sentence domain-specific interpretation
- `timing_window` & `spatial_direction`: Optional temporal or directional anchors

### Stage 2: Cross-Validation (Signal vs. Noise)
The deterministic graph matcher (`backend/engine/cross_validator.py`) scans all claims for a profile:
1. **Verified Core Patterns (Convergence)**:
   - Triggered when **2 or more independent disciplines** emit claims sharing the same `trait_tag`.
   - Combined Confidence is calculated via independent probabilistic reinforcement:
     $$C_{\text{combined}} = 1 - \prod_{i=1}^{k} (1 - 0.85 \cdot c_i)$$
2. **Constructive Tensions (Divergence)**:
   - Triggered when claims in the same `domain` or `trait_tag` exhibit opposing `action_polarity` (e.g., `bold_initiative` in an active Astrological Transit / Personal Year 1 vs. `cautious_deliberation` in Palmistry Head Line or Saturn placement) or opposing `valence` (`supportive` natal potential vs. `challenging` Vastu room direction).
   - Framed as a **Strategic Tension** with an explicit resolution rule (e.g., *"Use your palm's analytical caution to vet the blueprint, then execute boldly during the astrological transit window"*).
3. **Isolated Nuances**:
   - Single-discipline claims ($k = 1$) preserved as secondary texture without cluttering the headline synthesis.

### Stage 3: Recursive Deepening (Triangulation)
For every **Verified Core Pattern**, the engine automatically executes three recursive sub-queries across the *other* stored systems in the user's vault:
- **Mechanism Probe (`Astrology` + `Numerology`)**: *"How does this verified trait operate structurally?"* (Inspects specific Houses 1/2/3/5/7/9/10, ruling planets Mercury/Venus/Sun/Saturn/Jupiter, and Numerology Pinnacles).
- **Timing Probe (`Vedic Dasha` + `Transits` + `Personal Year` + `Oracles`)**: *"When is this verified pattern actively triggered?"* (Checks current Vimshottari Mahadasha/Antardasha, Personal Year number, and active oracle symbolism).
- **Environment Probe (`Astrocartography` + `Vastu Shastra` + `Feng Shui`)**: *"Which physical directions and geographic lines amplify or obstruct this pattern?"* (Maps the trait's ruling planet/element to Vastu directions like West/North-West/North-East and Astrocartography MC/ASC lines).

### Stage 4: Unified Narrative Synthesis
The Master Synthesizer formats the final response strictly by **Life Theme** (`Core Nature & Verified Pillars`, `Career, Purpose & Wealth`, `Relationships & Emotional Dynamics`, `Space, Location & Vastu Alignment`, `Active Timing & Cycles`, and `3–5 Actionable Alignments`), optionally preceded by the concise **[Cross-Validation Audit]**.

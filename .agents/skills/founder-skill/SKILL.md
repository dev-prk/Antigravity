---
name: founder-skill
description: >-
  ONLY invoke when explicitly called by the user (e.g., /founder-skill); never activate by default. Master orchestrator for the 11 Founder skills that stress-test a business idea end-to-end before launch (board, competitors, consumer panel, pricing, offer, CFO unit economics, marketing, brand, ops, launch, and business plan).
disable-model-invocation: true
disable-slash-command: false
license: MIT
---

# The Founder Skill Suite

Eleven specialized skills that test a business before you launch it, reading and writing shared artifacts in your project's `founder/` directory.

## Execution Order

Run the full sequence in order, or invoke any individual skill directly:

```text
board -> competitors -> consumer -> pricing -> offer -> cfo -> marketing -> brand -> ops -> launch -> plan
```

| Skill | Role | What It Produces in `founder/` |
| :--- | :--- | :--- |
| [`/founder-board`](../founder-board/SKILL.md) | Board of Directors | `founder/idea.md` & `founder/board.md` — Three board members (Offers, Monopoly, Product lenses) score the idea, list what would kill it, and vote. |
| [`/founder-competitors`](../founder-competitors/SKILL.md) | Competitor Scout | `founder/competitors.md` — Direct competitors, indirect ones, and substitutes from public sources with linked prices and customer complaints. |
| [`/founder-consumer`](../founder-consumer/SKILL.md) | Consumer Panel | `founder/panel/` — Spins up 100 simulated buyer personas (`panel.py`) across income, habits, and objections; tallies who buys and why. |
| [`/founder-pricing`](../founder-pricing/SKILL.md) | Pricing Strategist | `founder/pricing.md` — Runs Van Westendorp price sensitivity (`van_westendorp.py`) against panel answers, competitors, and margins. |
| [`/founder-offer`](../founder-offer/SKILL.md) | Offer Architect | `founder/offer.md` — Builds the offer stack (bonuses, guarantee, urgency, naming) to answer top buyer objections and re-tests on the panel. |
| [`/founder-cfo`](../founder-cfo/SKILL.md) | CFO | `founder/cfo.md` — Computes unit economics (`unit_economics.py`): contribution margin, daily break-even, 12-month ramp, cash needed, payback, and what-ifs. |
| [`/founder-marketing`](../founder-marketing/SKILL.md) | Marketing Director | `founder/marketing.md` — Positioning, buyer channels, max CAC, 10 hooks, and a dated 30-day launch campaign. |
| [`/founder-brand`](../founder-brand/SKILL.md) | Brand Designer | `founder/brand.md` — Name candidates with trademark/domain/handle checks, voice, promise, and visual brief. |
| [`/founder-ops`](../founder-ops/SKILL.md) | Operations Manager | `founder/ops.md` — Suppliers, staffing, day-one routines, permits, and risk register feeding real costs back to the CFO. |
| [`/founder-launch`](../founder-launch/SKILL.md) | Launch Lead | `founder/launch.md` — Cheap real-world validation test first, dated countdown, launch-day run sheet, and first 30 days. |
| [`/founder-plan`](../founder-plan/SKILL.md) | Business Planner | `founder/business-plan.md` — Compiles all artifacts (`compile.py`) with a computed verdict: *Profitable*, *Not yet*, or *Incomplete*. |

## How to Run When `/founder-skill` Is Invoked

1. Ask the user whether they want to run the **full 11-step pipeline** on their business idea or start with a **specific skill** (e.g., `/founder-board` or `/founder-consumer --quick`).
2. Read the corresponding `SKILL.md` from `../founder-<step>/SKILL.md` and follow its workflow and standard-library Python tools strictly.

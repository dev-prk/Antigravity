# BRIEFING — 2026-11-10T17:35:00Z

## Mission
Design the authentication and session management architecture for ZenClass (`https://v2.zenclass.in/login`) covering form selectors, MFA detection, HITL delegation, session persistence, token extraction, cookie sync, and multi-tier session recovery.

## 🔒 My Identity
- Archetype: teamwork_explorer
- Roles: ZenClass Auth & Session Explorer
- Working directory: /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m4_1
- Original parent: cbd0649b-f648-4724-a244-a22a5102ccc4
- Milestone: Milestone 4 — ZenClass Tasks Driver

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Zero mock evaluate shims in production code
- Explicit selectors with fallbacks (trailing space in password input: `.password-input input[placeholder="Enter your password "]`)
- Safe MFA / OTP detection halting and delegating to HITL handler without bypassing
- Session persistence via Playwright storage_state + localStorage authToken extraction and cookie sync

## Current Parent
- Conversation ID: cbd0649b-f648-4724-a244-a22a5102ccc4
- Updated: 2026-11-10T17:35:00Z

## Investigation State
- **Explored paths**:
  - `zenclass_guvi/drivers/base_driver.py` & `guvi_driver.py`
  - `zenclass_guvi/core/browser.py` & `core/hitl_handler.py`
  - `zenclass_guvi/tests/e2e/harness/dom_fixtures.py`, `mock_server.py`, `test_f12_zenclass_auth.py`
  - `.agents/teamwork/spec_miner_survey_3/raw_js/2586.a6a9de77739f3e953367.js` (Login bundle chunk)
  - `.agents/teamwork/spec_miner_survey_3/raw_js/main.js` (Webpack runtime, Axios interceptors, route navigation)
- **Key findings**:
  - Form selectors verified with exact trailing space in password placeholder: `.password-input input[placeholder="Enter your password "]`
  - MFA challenge dynamic classes verified: `.login-mfa-active` and `.login-mfa-wrapper` trigger challenge component `g.A` and hide `<form>`
  - Session stored as JSON in `localStorage.authToken`: `{"authToken": "...", "expiry": Date.now() + 172800000}` (48 hours)
  - Cookies synchronized via `document.cookie = "authToken=" + s.authtoken + "; path=/"`
  - Progressive 4-tier recovery architecture designed: Tier 1 (Fast-Path DOM Anchor) -> Tier 2 (Storage/Expiry) -> Tier 3 (Platform Probe) -> Tier 4 (Credential Login)
  - Zero mock evaluate shims policy strictly enforced for production code
- **Unexplored areas**: None for this assignment scope.

## Key Decisions Made
- Architecture blueprint completed and fully detailed in `handoff.md`.
- Recommended implementing `ZenClassDriver` inheriting from `BaseDriver` with exact canonical selectors and fallback lists.
- Recommended handling both JSON-serialized dictionary tokens and raw string tokens in `get_auth_token()` for seamless production and test mock compatibility.

## Artifact Index
- DISPATCH.md — Dispatch assignment and instructions
- BRIEFING.md — Persistent working memory
- progress.md — Liveness heartbeat
- handoff.md — Complete ZenClass authentication & session architecture blueprint report

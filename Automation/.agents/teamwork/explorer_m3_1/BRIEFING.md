# BRIEFING — 2026-11-10T16:09:00Z

## Mission
Blueprint Guvi Authentication & Session Management in `drivers/guvi_driver.py` for Milestone 3 (autonomous Guvi CodeKata driver).

## 🔒 My Identity
- Archetype: explorer
- Roles: investigation, synthesis
- Working directory: /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m3_1
- Original parent: cbd0649b-f648-4724-a244-a22a5102ccc4
- Milestone: Milestone 3 (Guvi CodeKata Driver)

## 🔒 Key Constraints
- Read-only investigation — do NOT implement directly in production codebase
- Output self-contained handoff.md in working directory
- Provide concrete, production-ready blueprint with exact selectors, flows, HITL integration, session persistence, and error handling
- Zero automated bypass of CAPTCHA/Turnstile/OTP — mandatory HITL integration

## Current Parent
- Conversation ID: cbd0649b-f648-4724-a244-a22a5102ccc4
- Updated: 2026-11-10T16:09:00Z

## Investigation State
- **Explored paths**:
  - `zenclass_guvi/config.py`: URL constants, default credentials (`devsh.pareek@gmail.com` / `Dev@99#$%esh`), headless=False.
  - `zenclass_guvi/core/browser.py`: `BrowserManager`, persistent context in `.browser_profile/`, `save_storage_state()` / `_restore_storage_state()`.
  - `zenclass_guvi/core/hitl_handler.py`: `check_and_handle_guardrails()`, `detect_guardrail()`, `GUARDRAIL_RULES` (Turnstile, reCAPTCHA, Guvi activation modal `#myModal #sendmail`, OTP).
  - `zenclass_guvi/core/state_manager.py`: `StateManager` task record tracking and state persistence.
  - `tests/e2e/tier1_features/test_f09_guvi_auth.py` and `tests/e2e/harness/mock_server.py`: Verified `usercheck.php` request/response schema and DOM fixture `GUVI_LOGIN_HTML`.
  - `spec_miner_survey_2/handoff.md`: Verbatim DOM probe findings, cookie schemas (`authToken`, `mail`, `cusername`, `userpoints`), edge cases.
- **Key findings**:
  - Direct form submission on `/sign-in/` sends `POST /usercheck.php` with `{emails, password, loggedInType}`.
  - Form inputs support dual selectors: live DOM (`#email`, `#password`, `a#login-btn`, `#logged-in`) and semantic fallbacks (`#login_email`, `input[type="email"]`, `#login_password`, `#login_button`, `button[type="submit"]`).
  - Pre-login session detection: Check cookies for `authToken` and navigate to `/code-kata/` or check if `/sign-in/` 302-redirects to `/`. If authenticated, skip credential entry.
  - HITL integration: Guardrail detection for Cloudflare Turnstile, reCAPTCHA, Guvi `#myModal #sendmail`, OTP. Emit `\a` bell x3 and pause for foreground user resolution.
  - Dual-layer session persistence: Chromium persistent context profile + explicit `storage_state.json` via `save_storage_state()`.
- **Unexplored areas**: None. All dependencies, contracts, and test fixtures are fully analyzed.

## Key Decisions Made
- Architecture follows `BaseDriver` base class in `drivers/base_driver.py` and specialized `GuviDriver` in `drivers/guvi_driver.py`.
- Selector resolution will use cascade list matching to guarantee compatibility with both live production DOM and mock server test fixtures.
- `ensure_authenticated()` provides idempotent session verification before executing full `login()`.

## Artifact Index
- DISPATCH.md — record of dispatch instructions
- BRIEFING.md — working memory and identity
- progress.md — heartbeat progress log
- handoff.md — comprehensive blueprint and architecture report

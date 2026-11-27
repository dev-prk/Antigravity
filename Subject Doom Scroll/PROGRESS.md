# Progress — CBSE Shorts (Class 9 Science Pilot)

## Brief
1. **Ask:** Build a static web app (`./run.sh` on `:8770`) that presents a vertical snap-scroll feed of 10 animated, narrated 45–60s science explainer shorts for CBSE Class 9 Science ("Motion" and "Force and Laws of Motion") with onboarding, Web Speech narration, key-term definitions, and physics-accurate content in `content/class9_science.json`.
2. **Must-haves:**
   - "Static web app (HTML/CSS/JS, no build step, no paid API, $0 cost). Run: `./run.sh` on :8770."
   - "Onboarding: pick class (6–10 selectable; only Class 9 has content, others say 'coming soon' and still save). Choice saved in localStorage. Optional subject filter chips (All / Science)."
   - "Vertical full-screen snap-scroll feed of shorts, random order per session, filtered by class + subject."
   - "Each short = 4–6 animated 'scenes' (big text, CSS/SVG illustration, one key-term chip that defines the jargon in plain words) with spoken narration via the browser Web Speech API (voice on/off toggle, tap to pause, progress bar). Scene changes are driven by narration timing (estimate from word count at ~2.2 words/s if speech is unavailable)."
   - "Content lives in `content/class9_science.json` (data, not code). Schema per short: `id, class, subject, chapter, title, hook, narration (100–130 words), terms[{word, meaning}], scenes[{text, visual}], misconception` (the common wrong belief this short fixes)."
   - "Write **10 shorts** for Class 9 Science, NCERT ch. 8 'Force and Laws of Motion' + ch. 7 'Motion': inertia, 1st law, why friction exists, momentum, 2nd law F=ma (one worked number), 3rd law (rocket/swimmer/gun recoil, why equal forces don't cancel), conservation of momentum, speed vs velocity, acceleration, distance vs displacement. Physics must be correct; explain *why*, not just the formula. Language: simple, an Indian 14-year-old, no unexplained jargon."
   - Expert gaps:
     - "'Equal and opposite' forces act on DIFFERENT bodies, so they don't cancel. Say it."
     - "Friction is not the cause of rest; objects keep moving unless a force (often friction) acts."
     - "45–60 s at ~2.2 words/s means 100–130 words. Out of range = rejected."
     - "Every term used in narration must appear in `terms` or be everyday words."
     - "Don't invent NCERT page numbers or quotes. Cite chapter name only."
   - Acceptance:
     - `python3 ~/Documents/Antigravity/exams/02_cbse_shorts/check.py <app dir>` passes.
     - Bad input must be rejected (both in `check.py` and in client/validator logic if malformed JSON is loaded).
     - `index.html` loads with no console errors, `localStorage` key for class set after onboarding.
3. **Done test:** Start `./run.sh` on `:8770`, open `http://localhost:8770` in the browser, pick Class 8 (see "coming soon" and verify saved in `localStorage`), switch to Class 9, filter by Science/All, scroll through the vertical snap-scroll feed of 10 shorts, toggle voice / tap to pause / watch scenes advance with SVG animations and key-term chips, verify zero console errors, and run `python3 ~/Documents/Antigravity/exams/02_cbse_shorts/check.py .` to confirm `PASS`.
4. **Expert gap:**
   - Newton's 3rd Law: explicitly state that equal and opposite forces act on **two different bodies** (or **different objects**), which is why they never cancel each other out.
   - Newton's 1st Law & Friction: rest is not the "natural state" that requires no explanation; constant velocity (including rest) persists unless an external unbalanced force like friction slows the object down. Friction arises from microscopic bumps and ridges interlocking between surfaces.
   - F=ma worked numerical example: e.g., pushing a `5 kg` cart so it accelerates at `3 m/s²` (written with `3 m/s` or `3 m/s²` so `check.py` regex `\d+\s*(kg)?.*\d+\s*m/s` matches and hand arithmetic `F = 5 kg × 3 m/s² = 15 N` is exact).
   - Strict word-count compliance: every narration must have between 100 and 130 words matching `re.findall(r"\b[\w'-]+\b", narration)`.
   - Every `term.word` must appear verbatim (case-insensitive substring) in `narration`.
5. **Smallest version:** `run.sh`, `index.html`, `styles.css`, `app.js`, and `content/class9_science.json`.
6. **Not building:** User accounts, backend database, quizzes/leaderboards, extra subjects or other classes' content beyond the "coming soon" state, build tools/bundlers.
7. **Unknowns:**
   - *Assume:* App lives in current workspace `/Users/devesh/Documents/Antigravity/Subject Doom Scroll` and we also symlink or copy `content/`, `index.html`, `styles.css`, `app.js`, `run.sh` if needed, or keep everything cleanly in `/Users/devesh/Documents/Antigravity/Subject Doom Scroll`.

## Audit Log (Done)
- [x] Brief & plan written in `PROGRESS.md`.

## Next
- Create `content/class9_science.json` with 10 physics-accurate shorts and verify word counts & schema with `check.py`.

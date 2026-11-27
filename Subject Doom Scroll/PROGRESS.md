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
     - Bad input must be rejected (both in `check.py` and in client validator logic if malformed JSON is loaded).
     - `index.html` loads with no console errors, `localStorage` key for class set after onboarding.
3. **Done test:** Start `./run.sh` on `:8770`, open `http://localhost:8770` in the browser, pick Class 8 (see "coming soon" and verify saved across reload via `localStorage`), switch to Class 9, filter by Science/All, scroll through the vertical snap-scroll feed of 10 shorts, toggle voice / tap to pause / watch scenes advance with SVG animations and key-term chips, verify zero console errors, and run `python3 ~/Documents/Antigravity/exams/02_cbse_shorts/check.py .` to confirm `PASS`.
4. **Expert gap:**
   - Newton's 3rd Law: explicitly states that equal and opposite forces act on **two different bodies** (`different objects`), which is why they never cancel each other out.
   - Newton's 1st Law & Friction: explains that rest is not automatic; constant velocity (or rest) persists unless an external unbalanced force like friction acts, and friction comes from microscopic hills and ridges interlocking between surfaces.
   - F=ma worked numerical example: pushing a `5 kg` shopping cart at an acceleration of `3 m/s` squared (`F = 5 kg × 3 m/s² = 15 newtons`; doubled mass `10 kg × 3 m/s² = 30 newtons`).
   - Strict word-count compliance: all 10 narrations are between 122 and 129 words (`check.py` word regex `\b[\w'-]+\b`).
   - Every `term.word` appears verbatim in `narration`.
5. **Smallest version:** `run.sh`, `index.html`, `styles.css`, `app.js`, and `content/class9_science.json`.
6. **Not building:** User accounts, backend database, quizzes/leaderboards, extra subjects or other classes' content beyond the "coming soon" state, build tools/bundlers.
7. **Unknowns:**
   - *Assume:* App lives in current workspace `/Users/devesh/Documents/Antigravity/Subject Doom Scroll`.

## Audit Log (Done)
- `10 shorts valid schema & 100-130 words` → `python3 /Users/devesh/Documents/Antigravity/exams/02_cbse_shorts/check.py "/Users/devesh/Documents/Antigravity/Subject Doom Scroll"` → `PASS` (exit code 0; word counts: 129, 127, 125, 127, 125, 129, 122, 125, 125, 125; each has 4 scenes and 2–3 terms).
- `F=ma numeric example hand check` → `5 kg × 3 m/s² = 15 newtons` and `10 kg × 3 m/s² = 30 newtons` in `c9-sci-second-law-fma` → exact arithmetic confirmed.
- `3rd law different bodies stated` → `c9-sci-third-law` narration states `"action and reaction always act on two different bodies!"` and `"Because they act on different objects, they never cancel"` → passes `check.py` regex and domain check.
- `Bad input rejected (contrast check)` → tested `check.validate` with a planted 40-word narration and empty `terms: []` → rejected with `['c9-sci-distance-displacement: missing terms', 'c9-sci-distance-displacement: narration 40 words']`; `app.js` `validateShorts()` enforces the same checks and shows `#errorPanel`.
- `Live browser UI & localStorage persistence` → opened `http://localhost:8770`, picked Class 8 ("Coming Soon!" panel appeared and persisted across page reload via `localStorage.setItem('cbse_shorts_selected_class', ...)`), switched to Class 9 Pilot (10 randomized shorts rendered in `#feedContainer`, persisted across reload), tested `Scene ▶` button (updated scene 1 → 2, SVG visual, big text, and key-term chip `inertia` → `mass`), tested tap-to-pause (`⏸ Paused` / `▶ Playing`) and `Science` filter chip, verified rendered screenshot `final_step_16.png` with zero console errors.

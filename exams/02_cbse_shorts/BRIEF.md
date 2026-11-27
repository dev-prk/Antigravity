# Brief: CBSE Shorts (pilot: Class 9 Science, Motion & Newton's Laws)

## Why
Students doom-scroll and feel guilty. Give them a scroll feed where every short is a 45–60 s
explainer that makes one school concept click (the founder never understood biology in class 8
and quit it; this is the app he needed). Visual + spoken, so both visual and oral learners get it.

## v1 scope (MUST-HAVES ONLY. No logins server, no payments, no extras)
1. Static web app (HTML/CSS/JS, no build step, no paid API, $0 cost). Run: `./run.sh` on :8770.
2. Onboarding: pick class (6–10 selectable; only Class 9 has content, others say "coming soon"
   and still save). Choice saved in localStorage. Optional subject filter chips (All / Science).
3. Vertical full-screen snap-scroll feed of shorts, random order per session, filtered by class + subject.
4. Each short = 4–6 animated "scenes" (big text, CSS/SVG illustration, one key-term chip that
   defines the jargon in plain words) with spoken narration via the browser Web Speech API
   (voice on/off toggle, tap to pause, progress bar). Scene changes are driven by narration timing
   (estimate from word count at ~2.2 words/s if speech is unavailable).
5. Content lives in `content/class9_science.json` (data, not code). Schema per short:
   `id, class, subject, chapter, title, hook, narration (100–130 words), terms[{word, meaning}],
   scenes[{text, visual}], misconception` (the common wrong belief this short fixes).
6. Write **10 shorts** for Class 9 Science, NCERT ch. 8 "Force and Laws of Motion" + ch. 7
   "Motion": inertia, 1st law, why friction exists, momentum, 2nd law F=ma (one worked number),
   3rd law (rocket/swimmer/gun recoil, why equal forces don't cancel), conservation of momentum,
   speed vs velocity, acceleration, distance vs displacement. Physics must be correct; explain
   *why*, not just the formula. Language: simple, an Indian 14-year-old, no unexplained jargon.

## Code-driven physics animations (rule: numbers come from equations, never hand-drawn)
- Any short with a calculation or motion (F=ma, speed/velocity, acceleration, momentum,
  recoil, displacement) uses a live canvas/SVG simulation, not a static picture or video.
- Put ALL physics in `js/physics.js`, a pure module with NO DOM access, exported with
  `module.exports` so node can test it: `accel(F,m)`, `velocityAfter(u,a,t)`,
  `distance(u,a,t)` (= ut + 1/2 a t^2), `stickCollision(m1,u1,m2,u2)` (final velocity),
  `recoilVelocity(m_bullet,v_bullet,m_gun)` (negative = opposite direction).
- Sims (`js/sims.js`) call these functions each frame and show the live numbers on screen
  with units (e.g. "a = F/m = 10/2 = 5 m/s^2"). A slider for force or mass is allowed for the
  F=ma short only. No magic constants in the animation: displayed value = function output.
- scene.visual is either an SVG/text illustration or `{"sim":"name","params":{...}}`.
  A scene may also point to a video file path (optional clips added later by the founder).

## Expert gaps (do not skip)
- "Equal and opposite" forces act on DIFFERENT bodies, so they don't cancel. Say it.
- Friction is not the cause of rest; objects keep moving unless a force (often friction) acts.
- 45–60 s at ~2.2 words/s means 100–130 words. Out of range = rejected.
- Every term used in narration must appear in `terms` or be everyday words.
- Don't invent NCERT page numbers or quotes. Cite chapter name only.

## Acceptance (Claude runs `python3 exams/02_cbse_shorts/check.py <app dir>`)
- JSON valid; exactly 10 shorts; unique ids; all fields present; 100–130 words narration.
- Each short has 4–6 scenes and ≥1 term; every term word appears in narration.
- F=ma short contains a numeric example whose arithmetic is right (hand-checked).
- 3rd-law short states the forces act on different bodies.
- `node exams/02_cbse_shorts/physics_test.js <app dir>` passes (hand-worked values below).
- `index.html` loads with no console errors, localStorage key for class set after onboarding.
- **Bad input must be rejected**: a content file with a 40-word narration or missing `terms`
  must fail the check (graded by check.py on a planted bad file).

## Report rules
Report only what you actually ran. State anything untested (e.g. speech voices) as untested.
Do not add features beyond v1. Put evidence in PROGRESS.md.

# Brief: Shorts Engine, pilot = ONE short ("Inertia", Class 9 Science)

## Why
The v1 app (exam 02) plays in-browser slides with the browser's robotic voice. The founder
rejected it: audio robotic, visuals feel like AI slop. Replace it with a **code-driven video
renderer**: a scene file goes in, a real vertical MP4 with a natural voice comes out. $0, runs
on this Mac, no GPU, no paid API, deterministic (same input = same video).

## Deliverable (ONE short only; do not build the other nine)
`Subject Doom Scroll/engine/` with:
1. `scenes/inertia.json`: scene graph for the short (schema below).
2. `engine/render.py` (or .js): `render <scene.json> <out.mp4>`. Draws every frame
   deterministically, then encodes with ffmpeg (`/Users/devesh/.local/bin/ffmpeg`).
   Frame drawing: Playwright Chromium is already installed (`~/Library/Caches/ms-playwright`)
   or use Python Pillow/Skia/cairo. Choose one, justify it in PROGRESS.md in 3 lines.
3. `engine/voice.py`: narration to WAV with a **local neural TTS** (free, CPU): try Kokoro
   first, then Piper. macOS `say` is allowed ONLY as a labelled fallback, never the final.
   Must output word-level timestamps (`inertia.words.json`) so scene changes land on words.
4. `js/physics.js`: pure functions from exam 02 (accel, velocityAfter, distance,
   stickCollision, recoilVelocity). The inertia animation uses them (bus braking:
   deceleration from real numbers; passenger keeps v until a force acts).
5. Output `out/inertia.mp4`: **1080x1920, 30 fps, 45-60 s, H.264 + AAC**.

## Scene schema (keep it small)
`{"size":[1080,1920],"fps":30,"style":"flat|paper","voice":{...},
 "scenes":[{"start_word":N,"duration_hint":s,"layers":[{"type":"text|shape|svg|sim",
 "from":{props},"to":{props},"ease":"outCubic|spring|inOutSine","t":[t0,t1]}]}]}`
Scene starts are tied to narration word indexes, not hard-coded seconds.

## Feel requirements (the point of this exam)
- Motion uses easing curves + at least one spring (settle/overshoot) and one anticipation
  (small back-move before the main move). No linear tweens for movement.
- Style `paper`: soft drop shadows, subtle paper grain, slight offset layers. Style `flat`:
  clean vector. A single `style` switch changes the whole video; both must render.
- Captions burned in, word-highlighted from the word timestamps. Safe margins for phones.
- Content (narration text, terms) reuse `inertia` from content/class9_science.json. Do not
  rewrite the physics explanation; do make the visuals show it (bus, passenger, brake,
  lurch forward, key term "inertia" defined on screen).

## Honest limits (do not hide)
This will not look photorealistic. Do not fake realism with stock footage or AI image calls.
If something is not done (e.g. only one voice tried), say so.

## Acceptance (Claude runs `python3 exams/03_shorts_engine/check.py <app dir>`)
- `out/inertia.mp4` exists: 1080x1920, ~30 fps, 45-60 s, has audio stream, audio not silent.
- Video is not static: frames sampled at 8 timestamps differ from each other.
- Words file exists, monotonic timestamps, word count within 5% of narration.
- Rendering twice gives byte-identical frames (determinism check on frame 100).
- `node exams/02_cbse_shorts/physics_test.js <app dir>` passes.
- **Bad input rejected**: a scene file with a missing `scenes` or a negative duration must
  make `render` exit non-zero with a clear message (no silent output).
- A human (Devesh) will judge look and voice; Argon must save 2 stills + a voice-only WAV.

## Report rules
Report only what you ran. Record voice engine used, render time, anything untested.
No extra features (no UI, no other shorts). Evidence in PROGRESS.md.

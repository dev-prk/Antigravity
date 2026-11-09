---
name: animated-short-film
description: >-
  End-to-end 2D/3D animated short film production pipeline (Pixar/Disney/Anime style): gathers target duration, language, and aspect ratio, generates locked character reference sheets, writes the Story Bible, generates match-cut keyframes K1..K(N+1), crafts per-scene mega-prompts, synthesizes voiceovers (VO), and assembles the final MP4 with FFmpeg. Activate automatically when the user asks to create an animated short film, story animation, Pixar/2D/3D short video, or multi-scene narrative animation from scratch.
disable-model-invocation: false
disable-slash-command: false
---

# Animated Short Film Pipeline (End-to-End 2D / 3D Story Shorts)

Guides the complete production of a narrative 2D or 3D animated short film—from a raw concept to a finished MP4 file with locked character consistency, match-cut continuity, voiceover narration, and FFmpeg assembly.

## Stage 0 — Gather Core Inputs (Mandatory First Step)
Ask or confirm these 3 inputs before generating assets:

1. **Target Duration:**
   - Each generated video scene clip is ~5–10 seconds.
   - `Scene Count = ceil(Target Duration / Clip Duration)` (e.g., 60s at 10s/clip = 6 scenes).
2. **Primary Language:**
   - Determines the language of the Voiceover (`VO_SCRIPT.md`) and script dialogue.
3. **Aspect Ratio (`16:9` landscape or `9:16` vertical shorts):**
   - **STRICT ASPECT RATIO LOCK:** Paste this verbatim into every image/video generation prompt:
     > **STRICT ASPECT RATIO LOCK:** The final output video MUST be **[16:9 landscape | 9:16 vertical]**. All reference images — character sheets, context sheets, keyframes, first-frame and last-frame images — MUST share this exact aspect ratio. Reference images directly condition output framing and composition. Never mix aspect ratios within a single project.

## 7-Stage Production Workflow
Execute in strict order, consulting the corresponding guide in `references/` and sample artifacts in `examples/the-last-lantern/`:

1. **Character Reference Sheets** (`references/01-character-sheets.md`)
   - Generate multi-angle + expression turnaround sheets for every character in the locked aspect ratio. Every subsequent prompt MUST pass this character sheet first.
2. **Story Bible & Script** (`references/02-story-and-script.md`)
   - Write `STORY.md`: logline, verbatim character locks, world/style lock, continuity rules, and scene-by-scene beats (first frame, motion, last frame, VO, music).
3. **Match-Cut Keyframes** (`references/03-keyframes.md`)
   - Generate keyframes `K1 .. K(N+1)` in the locked aspect ratio using the character sheets as reference. The last frame of Scene $N$ equals the first frame of Scene $N+1$ (`K(N+1)`) for seamless match-cuts.
4. **Per-Scene Mega Prompts** (`references/04-mega-prompts.md`)
   - Write `MEGA_PROMPTS.md` with copy-pasteable prompts per scene: Global Locks + Reference Order + `FIRST FRAME / MOTION / CAMERA / LAST FRAME / SOUND / MUSIC / VO`.
5. **Scene Video Generation** (`references/05-video-generation.md`)
   - Generate each scene from its first-frame to last-frame with character sheet references. Verify resolution, aspect ratio, and on-model consistency with `ffprobe`.
6. **Voiceover (VO) Production** (`references/06-vo-production.md`)
   - Write `VO_SCRIPT.md` with timecoded storytelling narration (~60% speaking time, leaving breathing room for visual acting and score) and synthesize via ElevenLabs / TTS.
7. **FFmpeg Final Assembly** (`references/07-assembly.md`)
   - Normalize all clips to the locked resolution and frame rate (24/30 fps), concatenate scenes, duck background audio under VO, and verify the final `.mp4` with `ffprobe`.
   - Consult `references/08-lessons.md` for critical production lessons and physical realism rules.

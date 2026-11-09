# Content Creation Studio — Automatic Skill Routing & Production Rules

This directory (`~/Documents/Antigravity/Content Creation`) is dedicated exclusively to **Content Creation**, with a primary focus on **short-form 2D & 3D animations, voice synthesis/lip-sync, and multi-scene character consistency**.

## 1. Automatic Project-Scoped Skill Activation (Always Active in `Content Creation`)

Unlike global skills in `~/Documents/Antigravity/.agents/skills/` (which require explicit `/<skill>` invocation), all 40 skills inside `/Users/devesh/Documents/Antigravity/Content Creation/.agents/skills/` are **project-scoped** (`disable-model-invocation: false`) and **MUST be automatically activated and read** whenever a user request in this project matches their domain—even when the user does not type a slash command.

Before executing any content creation, animation, character, audio, or video task in this workspace, **automatically read the relevant `SKILL.md`** from `.agents/skills/`:

### A. End-to-End 2D / 3D Animated Short Film Directors
- **2D characters in a 3D painted world (55–70s vertical story shorts, Three.js + Remotion + voice):**
  Read [`.agents/skills/cartoon-3d-short/SKILL.md`](./.agents/skills/cartoon-3d-short/SKILL.md)
- **End-to-end Pixar / Disney / Anime 2D or 3D animated short film (Story Bible $\to$ Character Sheets $\to$ Match-Cut Keyframes $\to$ VO $\to$ FFmpeg):**
  Read [`.agents/skills/animated-short-film/SKILL.md`](./.agents/skills/animated-short-film/SKILL.md)
- **Full multi-stage agentic video production pipeline:**
  Read [`.agents/skills/create-video/SKILL.md`](./.agents/skills/create-video/SKILL.md)

### B. Character Consistency, Turnarounds & 2D/3D Rigging
- **Character Bible, verbatim character passport, turnaround sheets, 6 expressions & voice spec:**
  Read [`.agents/skills/character-passport/SKILL.md`](./.agents/skills/character-passport/SKILL.md)
- **Multi-scene character, outfit & location lock across video shots:**
  Read [`.agents/skills/varg-consistent-characters/SKILL.md`](./.agents/skills/varg-consistent-characters/SKILL.md)
- **Stylized 2D/3D & cartoon character design sheets:**
  Read [`.agents/skills/varg-character-design/SKILL.md`](./.agents/skills/varg-character-design/SKILL.md) and [`.agents/skills/varg-character-cartoon/SKILL.md`](./.agents/skills/varg-character-cartoon/SKILL.md)
- **2D rigged SVG character animation, joint pivots, pose libraries & QA:**
  Read [`.agents/skills/svg-character-animation/SKILL.md`](./.agents/skills/svg-character-animation/SKILL.md), [`.agents/skills/character-rigging/SKILL.md`](./.agents/skills/character-rigging/SKILL.md), [`.agents/skills/pose-library-design/SKILL.md`](./.agents/skills/pose-library-design/SKILL.md), and [`.agents/skills/character-animation-qa/SKILL.md`](./.agents/skills/character-animation-qa/SKILL.md)

### C. Voice Synthesis, Lip-Sync, Sound Effects & Audio Mixing (ElevenLabs)
- **Voiceovers, multi-character dialogue & timestamp alignment:**
  Read [`.agents/skills/elevenlabs-text-to-speech/SKILL.md`](./.agents/skills/elevenlabs-text-to-speech/SKILL.md) and [`.agents/skills/elevenlabs-speech-to-text/SKILL.md`](./.agents/skills/elevenlabs-speech-to-text/SKILL.md)
- **Character voice acting / speech-to-speech transformation:**
  Read [`.agents/skills/elevenlabs-voice-changer/SKILL.md`](./.agents/skills/elevenlabs-voice-changer/SKILL.md)
- **SFX, background music & final audio mixing/ducking:**
  Read [`.agents/skills/elevenlabs-sound-effects/SKILL.md`](./.agents/skills/elevenlabs-sound-effects/SKILL.md), [`.agents/skills/elevenlabs-music/SKILL.md`](./.agents/skills/elevenlabs-music/SKILL.md), and [`.agents/skills/video-sound/SKILL.md`](./.agents/skills/video-sound/SKILL.md)

### D. Programmatic Video & Motion Design (Remotion, Manim, Lottie Principles)
- **Remotion React/Three.js video creation, markup, captions, media & rendering:**
  Read [`.agents/skills/remotion-best-practices/SKILL.md`](./.agents/skills/remotion-best-practices/SKILL.md), [`.agents/skills/remotion-create/SKILL.md`](./.agents/skills/remotion-create/SKILL.md), [`.agents/skills/remotion-markup/SKILL.md`](./.agents/skills/remotion-markup/SKILL.md), [`.agents/skills/remotion-captions/SKILL.md`](./.agents/skills/remotion-captions/SKILL.md), [`.agents/skills/remotion-multimedia/SKILL.md`](./.agents/skills/remotion-multimedia/SKILL.md), and [`.agents/skills/remotion-render/SKILL.md`](./.agents/skills/remotion-render/SKILL.md)
- **Disney's 12 animation principles, timing, easing & choreography:**
  Read [`.agents/skills/motion-design/SKILL.md`](./.agents/skills/motion-design/SKILL.md)
- **Manim 2D mathematical & technical explainer animation:**
  Read [`.agents/skills/manim-composer/SKILL.md`](./.agents/skills/manim-composer/SKILL.md)

### E. 3D Animation Engines (Three.js & Blender)
- **Three.js 3D skeletal/morph animation, camera animatics, worlds, lighting, materials & glTF loaders:**
  Read [`.agents/skills/threejs-animation/SKILL.md`](./.agents/skills/threejs-animation/SKILL.md), [`.agents/skills/threejs-animatic/SKILL.md`](./.agents/skills/threejs-animatic/SKILL.md), [`.agents/skills/threejs-world-generation/SKILL.md`](./.agents/skills/threejs-world-generation/SKILL.md), [`.agents/skills/threejs-lighting/SKILL.md`](./.agents/skills/threejs-lighting/SKILL.md), [`.agents/skills/threejs-materials/SKILL.md`](./.agents/skills/threejs-materials/SKILL.md), and [`.agents/skills/threejs-loaders/SKILL.md`](./.agents/skills/threejs-loaders/SKILL.md)
- **Blender 3D character rigging, ARKit 52 facial shape keys/lip-sync, keyframe/NLA animation, 2D/3D cel-shaded NPR & rendering:**
  Read [`.agents/skills/blender-character-rigging/SKILL.md`](./.agents/skills/blender-character-rigging/SKILL.md), [`.agents/skills/blender-facial-shapekeys/SKILL.md`](./.agents/skills/blender-facial-shapekeys/SKILL.md), [`.agents/skills/blender-animation/SKILL.md`](./.agents/skills/blender-animation/SKILL.md), [`.agents/skills/blender-stylized-npr/SKILL.md`](./.agents/skills/blender-stylized-npr/SKILL.md), and [`.agents/skills/blender-rendering/SKILL.md`](./.agents/skills/blender-rendering/SKILL.md)

### F. Storyboarding, Generative Keyframe Video & FFmpeg Assembly
- **Short-form video scripts, image-to-video animation, Kling keyframe-to-keyframe films & FFmpeg assembly:**
  Read [`.agents/skills/video-script/SKILL.md`](./.agents/skills/video-script/SKILL.md), [`.agents/skills/video-animate/SKILL.md`](./.agents/skills/video-animate/SKILL.md), [`.agents/skills/kling-4-keyframe-film/SKILL.md`](./.agents/skills/kling-4-keyframe-film/SKILL.md), and [`.agents/skills/short-form-ffmpeg-cookbook/SKILL.md`](./.agents/skills/short-form-ffmpeg-cookbook/SKILL.md)

import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import ffmpegPath from "ffmpeg-static";
import { bundle } from "@remotion/bundler";
import { renderMedia, renderStill, selectComposition } from "@remotion/renderer";

const outDir = path.resolve("out");
fs.mkdirSync(outDir, { recursive: true });

const browserExecutable = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser";
const chromiumOptions = { gl: "angle" };

console.log("1. Bundling Remotion + Three.js project...");
const serveUrl = await bundle({
  entryPoint: path.resolve("src/index.ts"),
  publicDir: path.resolve("public"),
});

console.log("2. Selecting BridgeSample composition...");
const composition = await selectComposition({
  serveUrl,
  id: "BridgeSample",
  browserExecutable,
  chromiumOptions,
});

// Render 6 representative stills (1 per beat)
const keyFrames = [
  { f: 20, name: "shot1_hook_marching.jpg" },
  { f: 85, name: "shot2_town_wide.jpg" },
  { f: 145, name: "shot3_whistling_bounce.jpg" },
  { f: 205, name: "shot4_bolt_snap_fall.jpg" },
  { f: 265, name: "shot5_golden_swing.jpg" },
  { f: 325, name: "shot6_break_step_tourists.jpg" },
];

console.log("3. Rendering 6 keyframe stills for look check...");
for (const kf of keyFrames) {
  const outPath = path.join(outDir, kf.name);
  await renderStill({
    composition,
    serveUrl,
    frame: kf.f,
    output: outPath,
    imageFormat: "jpeg",
    jpegQuality: 90,
    scale: 0.5,
    browserExecutable,
    chromiumOptions,
  });
  console.log("  -> Saved", kf.name);
}

console.log("4. Rendering 360-frame (12s @ 30fps) BridgeSample video...");
const silentMp4 = path.join(outDir, "bridge-sample-silent.mp4");
await renderMedia({
  composition,
  serveUrl,
  codec: "h264",
  crf: 18,
  scale: 0.5, // 540x960 fast crisp preview (all post-effects auto-scale to 1080x1920 metrics)
  outputLocation: silentMp4,
  browserExecutable,
  chromiumOptions,
  concurrency: 4,
  onProgress: ({ renderedFrames, encodedFrames }) => {
    if (renderedFrames % 60 === 0) {
      console.log(`  Progress: rendered ${renderedFrames}/360 frames (encoded ${encodedFrames})`);
    }
  },
});

console.log("5. Muxing video + voiceover + marching score + SFX...");
const finalMp4 = path.join(outDir, "cartoon-3d-sample.mp4");
const audioWav = path.join(outDir, "sample-audio.wav");
execFileSync(ffmpegPath, [
  "-y",
  "-i", silentMp4,
  "-i", audioWav,
  "-map", "0:v:0",
  "-map", "1:a:0",
  "-c:v", "copy",
  "-c:a", "aac",
  "-b:a", "192k",
  "-shortest",
  finalMp4,
]);

console.log("Done! Final sample video:", finalMp4);

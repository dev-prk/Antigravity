import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import ffmpegPath from "ffmpeg-static";
import { bundle } from "@remotion/bundler";
import { renderMedia, renderStill, selectComposition } from "@remotion/renderer";

const outDir = path.resolve("out/sleepy-ball");
fs.mkdirSync(outDir, { recursive: true });

const browserExecutable = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser";
const chromiumOptions = { gl: "angle" };

console.log("1. Bundling Remotion + Three.js project...");
const serveUrl = await bundle({
  entryPoint: path.resolve("src/index.ts"),
  publicDir: path.resolve("public"),
});

console.log("2. Selecting SleepyBall composition (1200 frames / 40.0s @ 30fps)...");
const composition = await selectComposition({
  serveUrl,
  id: "SleepyBall",
  browserExecutable,
  chromiumOptions,
});

// 6 keyframe stills across the 6 story beats
const keyFrames = [
  { f: 45, name: "shot1_hello_benny.jpg" },
  { f: 390, name: "shot2_sleepy_ball_wait.jpg" },
  { f: 610, name: "shot3_gentle_kick.jpg" },
  { f: 740, name: "shot4_rolling_meadow.jpg" },
  { f: 995, name: "shot5_fluffy_hill_stop.jpg" },
  { f: 1100, name: "shot6_byebye_friends.jpg" },
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

console.log("4. Rendering 1200-frame (40.0s @ 30fps) SleepyBall video...");
const silentMp4 = path.join(outDir, "sleepy-ball-silent.mp4");
await renderMedia({
  composition,
  serveUrl,
  codec: "h264",
  crf: 18,
  scale: 0.5,
  outputLocation: silentMp4,
  browserExecutable,
  chromiumOptions,
  concurrency: 4,
  onProgress: ({ renderedFrames, encodedFrames }) => {
    if (renderedFrames % 150 === 0) {
      console.log(`  Progress: rendered ${renderedFrames}/1200 frames (encoded ${encodedFrames})`);
    }
  },
});

console.log("5. Muxing video + voiceover + music + SFX...");
const finalMp4 = path.join(outDir, "the-sleepy-ball.mp4");
const audioWav = path.join(outDir, "sleepy-ball-audio.wav");
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

console.log("Done! Final video:", finalMp4);

import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { execFileSync } from "node:child_process";
import ffmpegPath from "ffmpeg-static";
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";

const outDir = path.resolve("out/sleepy-ball");
fs.mkdirSync(outDir, { recursive: true });

const browserExecutable = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser";
const chromiumOptions = { gl: "angle" };
const concurrency = Math.max(4, os.cpus().length - 2);

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

console.log(`3. Rendering 1200-frame (40.0s @ 30fps) SleepyBall video (concurrency=${concurrency}, imageFormat=jpeg)...`);
const silentMp4 = path.join(outDir, "sleepy-ball-silent.mp4");
await renderMedia({
  composition,
  serveUrl,
  codec: "h264",
  crf: 18,
  scale: 0.5,
  imageFormat: "jpeg",
  jpegQuality: 90,
  outputLocation: silentMp4,
  browserExecutable,
  chromiumOptions,
  concurrency,
  onProgress: ({ renderedFrames, encodedFrames }) => {
    if (renderedFrames % 150 === 0) {
      console.log(`  Progress: rendered ${renderedFrames}/1200 frames (encoded ${encodedFrames})`);
    }
  },
});

console.log("4. Muxing video + voiceover + music + SFX...");
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

// 5. Fast FFmpeg still extraction directly from the rendered MP4
const keyFrames = [
  { f: 45, name: "shot1_hello_benny.jpg" },
  { f: 390, name: "shot2_sleepy_ball_wait.jpg" },
  { f: 610, name: "shot3_gentle_kick.jpg" },
  { f: 740, name: "shot4_rolling_meadow.jpg" },
  { f: 995, name: "shot5_fluffy_hill_stop.jpg" },
  { f: 1100, name: "shot6_byebye_friends.jpg" },
];

console.log("5. Extracting 6 keyframe stills via FFmpeg...");
for (const kf of keyFrames) {
  const outPath = path.join(outDir, kf.name);
  const sec = (kf.f / 30).toFixed(2);
  execFileSync(ffmpegPath, ["-y", "-ss", sec, "-i", finalMp4, "-frames:v", "1", "-q:v", "2", outPath], {
    stdio: "ignore",
  });
  console.log("  -> Extracted", kf.name);
}

console.log("Done! Final video:", finalMp4);

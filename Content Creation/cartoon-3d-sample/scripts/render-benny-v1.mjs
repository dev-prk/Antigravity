import path from "node:path";
import fs from "node:fs";
import os from "node:os";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";

const require = createRequire(import.meta.url);
const ffmpegPath = require("ffmpeg-static");

const OUT_DIR = path.resolve("out/benny-v1");
fs.mkdirSync(OUT_DIR, { recursive: true });

const browserExecutable = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser";
const chromiumOptions = { gl: "angle" };
const isDraft = process.argv.includes("--draft");
const preset = isDraft ? "draft" : "final";
const concurrency = Math.max(4, os.cpus().length - 2);

const KEYFRAMES = [
  { name: "v1_shot1_hook_can_you_move", sec: 1.6 },
  { name: "v1_shot2_sleepy_ball_butterfly", sec: 5.5 },
  { name: "v1_shot3_shrug_silent_pause", sec: 8.8 },
  { name: "v1_shot5_kick_and_roll", sec: 14.35 },
  { name: "v1_shot6_baby_bunnies_surprise", sec: 19.5 },
  { name: "v1_shot7_chorus_parade", sec: 24.0 },
  { name: "v1_shot8_fluffy_hill_stop", sec: 30.2 },
  { name: "v1_shot10_byebye_friends", sec: 38.4 },
];

async function main() {
  const t0 = Date.now();
  console.log(
    `[BennySleepyBall3D] Bundling Remotion project (preset=${preset}, concurrency=${concurrency}, imageFormat=jpeg)...`
  );

  const serveUrl = await bundle({
    entryPoint: path.resolve("src/index.ts"),
    publicDir: path.resolve("public"),
  });

  const inputProps = { preset };
  const comp = await selectComposition({
    serveUrl,
    id: "BennySleepyBall3D",
    inputProps,
    browserExecutable,
    chromiumOptions,
  });

  const silentMp4 = path.join(OUT_DIR, "video-silent.mp4");
  const finalMp4 = path.join(OUT_DIR, "benny-sleepy-ball-3d.mp4");
  const audioWav = path.join(OUT_DIR, "audio.wav");

  console.log(
    `[BennySleepyBall3D] Rendering ${comp.durationInFrames} frames (${(
      comp.durationInFrames / comp.fps
    ).toFixed(1)}s @ ${comp.width}x${comp.height}, scale=${isDraft ? 0.5 : 0.75})...`
  );

  await renderMedia({
    composition: comp,
    serveUrl,
    codec: "h264",
    crf: 18,
    scale: isDraft ? 0.5 : 0.75,
    outputLocation: silentMp4,
    inputProps,
    imageFormat: "jpeg",
    jpegQuality: 90,
    concurrency,
    browserExecutable,
    chromiumOptions,
    onProgress: ({ renderedFrames, encodedFrames }) => {
      if (renderedFrames % 150 === 0 || renderedFrames === comp.durationInFrames) {
        console.log(
          `  progress: rendered=${renderedFrames}/${comp.durationInFrames}, encoded=${encodedFrames}`
        );
      }
    },
  });

  console.log("[BennySleepyBall3D] Muxing 3D animation with natural neural voice + ukulele audio...");
  execFileSync(
    ffmpegPath,
    [
      "-y",
      "-i",
      silentMp4,
      "-i",
      audioWav,
      "-map",
      "0:v:0",
      "-map",
      "1:a:0",
      "-c:v",
      "copy",
      "-c:a",
      "aac",
      "-b:a",
      "192k",
      "-ar",
      "48000",
      "-shortest",
      finalMp4,
    ],
    { stdio: "inherit" }
  );

  // Fast FFmpeg still extraction (no extra Chromium launches!)
  console.log("[BennySleepyBall3D] Extracting look-check stills directly from MP4 via FFmpeg...");
  for (const kf of KEYFRAMES) {
    const outJpg = path.join(OUT_DIR, `${kf.name}.jpg`);
    execFileSync(
      ffmpegPath,
      [
        "-y",
        "-ss",
        String(kf.sec),
        "-i",
        finalMp4,
        "-frames:v",
        "1",
        "-q:v",
        "2",
        outJpg,
      ],
      { stdio: "ignore" }
    );
    console.log(`  extracted ${outJpg} (@ ${kf.sec}s)`);
  }

  const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
  console.log(`[BennySleepyBall3D] Done in ${elapsed}s -> ${finalMp4}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

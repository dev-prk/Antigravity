import path from "node:path";
import fs from "node:fs";
import os from "node:os";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";

const require = createRequire(import.meta.url);
const ffmpegPath = require("ffmpeg-static");

const OUT_DIR = path.resolve("out/fun-fact");
fs.mkdirSync(OUT_DIR, { recursive: true });

const browserExecutable = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser";
const chromiumOptions = { gl: "angle" };
const isDraft = process.argv.includes("--draft");
const preset = isDraft ? "draft" : "final";
const concurrency = Math.max(4, os.cpus().length - 2);

const KEYFRAMES = [
  { name: "ff_shot1_hook_cloud_quiz", sec: 2.0 },
  { name: "ff_shot2_100_elephants_reveal", sec: 6.5 },
  { name: "ff_shot3_why_doesnt_it_fall", sec: 12.0 },
  { name: "ff_shot4_microscopic_droplets", sec: 18.2 },
  { name: "ff_shot5_warm_air_updrafts", sec: 24.2 },
  { name: "ff_shot6_rainbow_finale", sec: 33.8 },
];

async function main() {
  const t0 = Date.now();
  console.log(
    `[CloudElephantFunFact3D] Bundling Remotion project (preset=${preset}, concurrency=${concurrency}, imageFormat=jpeg)...`
  );

  const serveUrl = await bundle({
    entryPoint: path.resolve("src/index.ts"),
    publicDir: path.resolve("public"),
  });

  const inputProps = { preset };
  const comp = await selectComposition({
    serveUrl,
    id: "CloudElephantFunFact3D",
    inputProps,
    browserExecutable,
    chromiumOptions,
  });

  const silentMp4 = path.join(OUT_DIR, "video-silent.mp4");
  const finalMp4 = path.join(OUT_DIR, "cloud-100-elephants-fun-fact-3d.mp4");
  const audioWav = path.join(OUT_DIR, "audio.wav");

  console.log(
    `[CloudElephantFunFact3D] Rendering ${comp.durationInFrames} frames (${(
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

  console.log("[CloudElephantFunFact3D] Muxing 3D animation with natural neural voice + ukulele audio...");
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

  console.log("[CloudElephantFunFact3D] Extracting look-check stills directly from MP4 via FFmpeg...");
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
  console.log(`[CloudElephantFunFact3D] Done in ${elapsed}s -> ${finalMp4}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

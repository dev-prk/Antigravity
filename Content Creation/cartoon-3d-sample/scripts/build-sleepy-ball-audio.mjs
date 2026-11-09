import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const SR = 48000;
const FPS = 30;
const outDir = path.resolve("out/sleepy-ball");
const tmpDir = path.resolve("out/sleepy-ball/tmp_vo");
fs.mkdirSync(tmpDir, { recursive: true });

// 5 script segments + exact pauses from user script
const segments = [
  { id: "line1", text: "Hello, little friends! This is Benny the Bunny. And this is his red ball.", pauseAfter: 2.0 },
  { id: "line2", text: "The ball is sleeping. Look! It isn't moving at all. Benny waits... and waits...", pauseAfter: 3.0 },
  { id: "line3", text: "The ball doesn't move by itself. It stays sleepy, until... somebody pushes it!", pauseAfter: 1.3 },
  { id: "line4", text: "Whoosh! Now the ball is rolling. And do you know what? Once it rolls, it wants to keep rolling and rolling... until something stops it, like Benny's paws, or a big, fluffy hill.", pauseAfter: 1.6 },
  { id: "line5", text: "Things that are still stay still. Things that move keep moving. Bye-bye, friends!", pauseAfter: 1.2 },
];

const readWavSamples = (wavPath) => {
  const buf = fs.readFileSync(wavPath);
  let offset = 12;
  while (offset < buf.length - 8) {
    const id = buf.toString("ascii", offset, offset + 4);
    const sz = buf.readUInt32LE(offset + 4);
    if (id === "data") {
      const count = Math.floor(sz / 2);
      const out = new Float32Array(count);
      for (let i = 0; i < count; i++) {
        out[i] = buf.readInt16LE(offset + 8 + i * 2) / 32768;
      }
      // Trim trailing silence
      let end = count;
      while (end > 0 && Math.abs(out[end - 1]) < 0.003) end--;
      return out.subarray(0, Math.min(count, end + Math.floor(0.08 * SR)));
    }
    offset += 8 + sz;
  }
  return new Float32Array(0);
};

let cursorSec = 0.5; // 0.5s intro as Benny hops in
const timeline = [];
const renderedClips = [];

for (const seg of segments) {
  const aiff = path.join(tmpDir, `${seg.id}.aiff`);
  const wav = path.join(tmpDir, `${seg.id}.wav`);
  execFileSync("/usr/bin/say", ["-r", "168", "-o", aiff, seg.text]);
  execFileSync("/usr/bin/afconvert", ["-f", "WAVE", "-d", `LEI16@${SR}`, "-c", "1", aiff, wav]);
  const pcm = readWavSamples(wav);
  const dur = pcm.length / SR;
  const startSec = cursorSec;
  const endSec = startSec + dur;
  const pauseEndSec = endSec + seg.pauseAfter;
  timeline.push({
    id: seg.id,
    text: seg.text,
    startSec: Number(startSec.toFixed(3)),
    endSec: Number(endSec.toFixed(3)),
    pauseEndSec: Number(pauseEndSec.toFixed(3)),
    startFrame: Math.round(startSec * FPS),
    endFrame: Math.round(endSec * FPS),
    pauseEndFrame: Math.round(pauseEndSec * FPS),
  });
  renderedClips.push({ startSample: Math.floor(startSec * SR), pcm });
  cursorSec = pauseEndSec;
}

const totalSec = Math.ceil(cursorSec * FPS) / FPS;
const totalFrames = Math.round(totalSec * FPS);
const N = Math.floor(totalSec * SR);

const voiceTrack = new Float32Array(N);
for (const clip of renderedClips) {
  const maxK = Math.min(clip.pcm.length, N - clip.startSample);
  for (let k = 0; k < maxK; k++) {
    voiceTrack[clip.startSample + k] += clip.pcm[k] * 0.95;
  }
}

// Compute key story event timestamps from actual voice timeline:
const tLine1 = timeline[0];
const tLine2 = timeline[1];
const tLine3 = timeline[2];
const tLine4 = timeline[3];
const tLine5 = timeline[4];

const events = {
  fps: FPS,
  totalSec,
  totalFrames,
  hopInStart: 0.0,
  hopInEnd: 1.6,
  pause1Start: tLine1.endSec,
  pause1End: tLine1.pauseEndSec,
  pause2Start: tLine2.endSec,
  pause2End: tLine2.pauseEndSec,
  kickWindupSec: tLine3.endSec - 0.35,
  kickImpactSec: tLine3.endSec + 0.15,
  rollStartSec: tLine3.endSec + 0.15,
  hillSlowStartSec: tLine4.endSec - 1.5,
  ballStopSec: tLine4.endSec + 0.6,
  waveStartSec: tLine5.startSec,
  timeline,
};

fs.writeFileSync(path.join(outDir, "timeline.json"), JSON.stringify(events, null, 2));
console.log("Timeline events:\n", JSON.stringify(events, null, 2));

// Synthesize playful storybook music + SFX synced to `events`
const left = new Float32Array(N);
const right = new Float32Array(N);

let seed = 4242;
const rand = () => {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return (seed / 0xffffffff) * 2 - 1;
};

const addMono = (t0, dur, pan, fn) => {
  const s0 = Math.max(0, Math.floor(t0 * SR));
  const len = Math.min(N - s0, Math.floor(dur * SR));
  const gl = Math.cos(((pan + 1) * Math.PI) / 4);
  const gr = Math.sin(((pan + 1) * Math.PI) / 4);
  for (let i = 0; i < len; i++) {
    const v = fn(i / SR, i / len);
    left[s0 + i] += v * gl;
    right[s0 + i] += v * gr;
  }
};

// 1. Playful pizzicato / marimba storybook melody across the meadow (quiet during pause1 & pause2!)
const scale = [261.63, 293.66, 329.63, 392.0, 440.0, 523.25, 587.33, 659.25];
for (let t = 0.0; t < totalSec - 0.4; t += 0.45) {
  const inPause1 = t >= events.pause1Start && t < events.pause1End;
  const inPause2 = t >= events.pause2Start && t < events.pause2End;
  if (inPause1 || inPause2) continue; // silent comedy hold during sleepy pauses!
  const idx = Math.floor((t * 3.1) % scale.length);
  const freq = scale[idx];
  const isRolling = t >= events.kickImpactSec && t < events.ballStopSec;
  const gain = isRolling ? 0.095 : 0.065;
  addMono(t, 0.35, Math.sin(t) * 0.3, (dt) => {
    const env = Math.exp(-dt * 9.5) * (1 - Math.exp(-dt * 120));
    return (Math.sin(2 * Math.PI * freq * dt) + 0.3 * Math.sin(4 * Math.PI * freq * dt)) * env * gain;
  });
}

// 2. Gentle sleepy snoring / cricket chirp during Pause 1 (2s) and Pause 2 (3s)
for (const pStart of [events.pause1Start + 0.3, events.pause2Start + 0.3, events.pause2Start + 1.6]) {
  addMono(pStart, 0.85, -0.15, (dt, u) => {
    // soft sleepy whistle breath
    const f = 380 + 60 * Math.sin(Math.PI * u);
    return Math.sin(2 * Math.PI * f * dt) * Math.sin(Math.PI * u) * 0.045;
  });
}

// 3. Benny's bunny hops (0.1s, 0.55s, 1.0s, 1.45s) + kick hop
const hopTimes = [0.12, 0.55, 0.98, 1.42, events.kickWindupSec];
for (const ht of hopTimes) {
  addMono(ht, 0.18, 0.15, (dt, u) => {
    const f = 180 + 260 * u; // cute cartoon boing
    return Math.sin(2 * Math.PI * f * dt) * Math.exp(-dt * 16) * 0.18;
  });
}

// 4. Kick impact BOING + POP + WHOOSH!
addMono(events.kickImpactSec, 0.28, 0.0, (dt, u) => {
  const f = 140 + 380 * Math.exp(-dt * 12);
  const pop = Math.sin(2 * Math.PI * f * dt) * Math.exp(-dt * 12);
  return pop * 0.42;
});
addMono(events.kickImpactSec + 0.12, 0.55, 0.2, (dt, u) => {
  return rand() * Math.sin(Math.PI * u) * Math.exp(-dt * 3.5) * 0.22;
});

// 5. Rolling grass swishes while ball rolls
for (let rt = events.rollStartSec + 0.4; rt < events.ballStopSec - 0.3; rt += 0.38) {
  const prog = (rt - events.rollStartSec) / (events.ballStopSec - events.rollStartSec);
  const vol = 0.12 * (1 - 0.7 * prog);
  addMono(rt, 0.22, -0.2 + 0.4 * prog, (dt, u) => rand() * Math.sin(Math.PI * u) * vol);
}

// 6. Soft thud when ball stops against paws/hill
addMono(events.ballStopSec, 0.18, 0.1, (dt) => Math.sin(2 * Math.PI * 110 * dt) * Math.exp(-dt * 24) * 0.22);

// 7. Warm ending chord on "Bye-bye, friends!"
for (const freq of [261.63, 329.63, 392.0, 523.25]) {
  addMono(totalSec - 1.6, 1.5, 0.0, (dt, u) => Math.sin(2 * Math.PI * freq * dt) * Math.sin(Math.PI * u) * 0.055);
}

// Mix voice + ducked music/SFX and write 48kHz 16-bit stereo WAV
const pcm = Buffer.alloc(44 + N * 4);
pcm.write("RIFF", 0);
pcm.writeUInt32LE(36 + N * 4, 4);
pcm.write("WAVEfmt ", 8);
pcm.writeUInt32LE(16, 16);
pcm.writeUInt16LE(1, 20);
pcm.writeUInt16LE(2, 22);
pcm.writeUInt32LE(SR, 24);
pcm.writeUInt32LE(SR * 4, 28);
pcm.writeUInt16LE(4, 32);
pcm.writeUInt16LE(16, 34);
pcm.write("data", 36);
pcm.writeUInt32LE(N * 4, 40);

for (let i = 0; i < N; i++) {
  const v = voiceTrack[i];
  const duck = Math.abs(v) > 0.015 ? 0.48 : 0.92;
  const l = Math.max(-0.98, Math.min(0.98, v + left[i] * duck));
  const r = Math.max(-0.98, Math.min(0.98, v + right[i] * duck));
  pcm.writeInt16LE(Math.round(l * 32767), 44 + i * 4);
  pcm.writeInt16LE(Math.round(r * 32767), 44 + i * 4 + 2);
}

const outWav = path.join(outDir, "sleepy-ball-audio.wav");
fs.writeFileSync(outWav, pcm);
console.log("Generated audio:", outWav, `(${totalSec}s / ${totalFrames} frames)`);

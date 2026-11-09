import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const SR = 48000;
const DUR = 12.0;
const N = Math.floor(SR * DUR);

const outDir = path.resolve("out");
const tmpDir = path.resolve("out/tmp_vo");
fs.mkdirSync(tmpDir, { recursive: true });

// 6 voiceover beats aligned to the 6 2-second shots (0..12s)
const lines = [
  { t: 0.08, text: "Seventy-four soldiers knocked down an iron bridge." },
  { t: 2.08, text: "In eighteen thirty-one, it was the pride of the town." },
  { t: 4.08, text: "They whistled a tune, and stomped in step." },
  { t: 6.08, text: "Then a bolt snapped, and the bridge dropped!" },
  { t: 8.08, text: "Each step pushed that bridge just like a swing." },
  { t: 10.08, text: "So now, armies break step on every bridge." },
];

const voiceTrack = new Float32Array(N);

for (let i = 0; i < lines.length; i++) {
  const aiff = path.join(tmpDir, `line_${i}.aiff`);
  const wav = path.join(tmpDir, `line_${i}.wav`);
  execFileSync("/usr/bin/say", ["-r", "195", "-o", aiff, lines[i].text]);
  execFileSync("/usr/bin/afconvert", ["-f", "WAVE", "-d", `LEI16@${SR}`, "-c", "1", aiff, wav]);
  const buf = fs.readFileSync(wav);
  // Find 'data' chunk
  let offset = 12;
  while (offset < buf.length - 8) {
    const id = buf.toString("ascii", offset, offset + 4);
    const sz = buf.readUInt32LE(offset + 4);
    if (id === "data") {
      const samples = Math.floor(sz / 2);
      const startIdx = Math.floor(lines[i].t * SR);
      const maxLen = Math.min(samples, Math.floor(1.92 * SR), N - startIdx);
      for (let k = 0; k < maxLen; k++) {
        const s = buf.readInt16LE(offset + 8 + k * 2) / 32768;
        // Soft fade at end of clip
        const fade = k > maxLen - 960 ? (maxLen - k) / 960 : 1.0;
        voiceTrack[startIdx + k] += s * fade * 0.95;
      }
      break;
    }
    offset += 8 + sz;
  }
}

// Synthesize stereo music + SFX
const left = new Float32Array(N);
const right = new Float32Array(N);

// Deterministic PRNG for noise
let seed = 1337;
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

// 1. Marching boots + snare drum (0..6s, 2 steps/sec = every 0.5s)
for (let step = 0; step < 12; step++) {
  const t = step * 0.5 + 0.05;
  const heavy = step >= 8 ? 1.35 : 1.0;
  // Boot thud + gravel crunch
  addMono(t, 0.14, (step % 2 ? -0.25 : 0.25), (dt, u) => {
    const thud = Math.sin(2 * Math.PI * (95 - 55 * u) * dt) * Math.exp(-dt * 28);
    const crunch = rand() * Math.exp(-dt * 42) * 0.45;
    return (thud + crunch) * 0.28 * heavy;
  });
  // Snare tap
  addMono(t, 0.09, 0.15, (dt) => rand() * Math.exp(-dt * 55) * 0.14 * heavy);
}

// 2. Fife march melody (0..6s) & whistling (4..6s)
const marchNotes = [
  [0.0, 523.25], [0.25, 587.33], [0.5, 659.25], [0.75, 783.99],
  [1.0, 659.25], [1.25, 587.33], [1.5, 523.25], [2.0, 587.33],
  [2.5, 659.25], [3.0, 783.99], [3.5, 880.0],  [4.0, 783.99],
  [4.5, 880.0],  [5.0, 987.77], [5.5, 1046.5],
];
for (const [nt, freq] of marchNotes) {
  const isWhistle = nt >= 4.0;
  addMono(nt, 0.42, isWhistle ? -0.2 : 0.2, (dt, u) => {
    const env = Math.sin(Math.PI * u) * Math.exp(-dt * 2.5);
    const vib = isWhistle ? 1 + 0.008 * Math.sin(2 * Math.PI * 6 * dt) : 1;
    return Math.sin(2 * Math.PI * freq * vib * dt) * env * (isWhistle ? 0.14 : 0.09);
  });
}

// 3. White-flash whoosh at f=58 (1.93s)
addMono(1.88, 0.25, 0, (dt, u) => rand() * Math.sin(Math.PI * u) * 0.25);

// 4. Bridge chain groans (4.2..6.5s)
for (const gt of [4.3, 5.1, 6.1]) {
  addMono(gt, 0.45, -0.3, (dt, u) => {
    const f = 180 + 40 * Math.sin(2 * Math.PI * 3 * dt);
    return Math.tanh(Math.sin(2 * Math.PI * f * dt) * 2.5) * Math.sin(Math.PI * u) * 0.12;
  });
}

// 5. Bolt SNAP (6.55s) + Deck Crash (6.85s) + River Splash (7.15s)
addMono(6.55, 0.18, -0.2, (dt) => {
  const ping = Math.sin(2 * Math.PI * 1420 * dt) * Math.exp(-dt * 35);
  const crack = rand() * Math.exp(-dt * 70);
  return (ping * 0.6 + crack * 0.8) * 0.55;
});
addMono(6.85, 0.55, 0.0, (dt) => {
  const boom = Math.sin(2 * Math.PI * (70 - 35 * dt) * dt) * Math.exp(-dt * 8);
  return (boom + rand() * Math.exp(-dt * 12) * 0.5) * 0.42;
});
addMono(7.15, 0.8, 0.1, (dt, u) => rand() * Math.sin(Math.PI * u) * Math.exp(-dt * 3.2) * 0.35);

// 6. Golden hour warm pad + swing creaks (8.0..10.0s)
for (const freq of [261.63, 329.63, 392.0, 493.88]) {
  addMono(8.0, 2.0, 0, (dt, u) => Math.sin(2 * Math.PI * freq * dt) * Math.sin(Math.PI * u) * 0.055);
}
for (const st of [8.35, 9.15]) {
  addMono(st, 0.3, 0.25, (dt, u) => Math.sin(2 * Math.PI * (520 + 90 * u) * dt) * Math.sin(Math.PI * u) * 0.08);
}

// 7. Sign hammer taps + casual tourist footsteps (10.0..12.0s)
for (const ht of [10.05, 10.32]) {
  addMono(ht, 0.1, -0.25, (dt) => Math.sin(2 * Math.PI * 420 * dt) * Math.exp(-dt * 45) * 0.25);
}
for (const ft of [10.2, 10.43, 10.71, 10.95, 11.18, 11.47, 11.73]) {
  addMono(ft, 0.1, (ft % 0.4) - 0.2, (dt) => rand() * Math.exp(-dt * 55) * 0.14);
}

// Mix voice + ducked music/SFX and write 48kHz 16-bit stereo WAV
const pcm = Buffer.alloc(44 + N * 4);
pcm.write("RIFF", 0);
pcm.writeUInt32LE(36 + N * 4, 4);
pcm.write("WAVEfmt ", 8);
pcm.writeUInt32LE(16, 16);
pcm.writeUInt16LE(1, 20); // PCM
pcm.writeUInt16LE(2, 22); // Stereo
pcm.writeUInt32LE(SR, 24);
pcm.writeUInt32LE(SR * 4, 28);
pcm.writeUInt16LE(4, 32);
pcm.writeUInt16LE(16, 34);
pcm.write("data", 36);
pcm.writeUInt32LE(N * 4, 40);

for (let i = 0; i < N; i++) {
  const v = voiceTrack[i];
  const duck = Math.abs(v) > 0.02 ? 0.55 : 0.9;
  const l = Math.max(-0.98, Math.min(0.98, v + left[i] * duck));
  const r = Math.max(-0.98, Math.min(0.98, v + right[i] * duck));
  pcm.writeInt16LE(Math.round(l * 32767), 44 + i * 4);
  pcm.writeInt16LE(Math.round(r * 32767), 44 + i * 4 + 2);
}

const outWav = path.join(outDir, "sample-audio.wav");
fs.writeFileSync(outWav, pcm);
console.log("Generated audio:", outWav, `(${(pcm.length / 1024).toFixed(1)} KB)`);

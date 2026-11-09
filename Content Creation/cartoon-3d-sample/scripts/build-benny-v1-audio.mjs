import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import { MsEdgeTTS, OUTPUT_FORMAT } from "msedge-tts";

const require = createRequire(import.meta.url);
const ffmpegPath = require("ffmpeg-static");

const OUT_DIR = path.resolve("out/benny-v1");
const TMP_DIR = path.resolve("out/benny-v1/tmp_tts");
fs.mkdirSync(OUT_DIR, { recursive: true });
fs.mkdirSync(TMP_DIR, { recursive: true });

const SAMPLE_RATE = 48000;
const DURATION_SEC = 40.0;
const TOTAL_SAMPLES = Math.floor(SAMPLE_RATE * DURATION_SEC);

// Natural Microsoft Neural Voices:
// - en-US-AnaNeural: expressive, natural young child voice (Benny, Baby Bunnies & Kids Chorus)
// - en-US-AriaNeural: warm, smiling storyteller narrator
const VOICES = {
  benny: "en-US-AnaNeural",
  narrator: "en-US-AriaNeural",
};

const LINES = [
  // Shot 1 (0:00 - 0:03)
  {
    id: "shot1_hook",
    start: 0.85,
    maxDur: 2.0,
    voice: VOICES.benny,
    text: "Can YOU make the ball move?",
    rate: 1.05,
    gain: 1.05,
  },
  // Shot 2 (0:03 - 0:07)
  {
    id: "shot2_song12",
    start: 3.0,
    maxDur: 3.9,
    voice: VOICES.benny,
    harmonyVoice: VOICES.narrator,
    text: "Sleepy ball, sleepy ball, sitting on the grass, Not a move, not a move, till a push comes past!",
    rate: 1.25,
    gain: 1.0,
  },
  // Shot 3 (0:07 - 0:10): "The ball is sleeping." + 2-second silent pause (8.10s - 10.10s)
  {
    id: "shot3_whisper",
    start: 7.05,
    maxDur: 1.02,
    voice: VOICES.narrator,
    text: "The ball is sleeping.",
    rate: 1.08,
    gain: 0.95,
  },
  // Shot 4 (0:10 - 0:14): "Let's push!" + pause for child to say "push!"
  {
    id: "shot4_letspush",
    start: 10.15,
    maxDur: 2.4,
    voice: VOICES.benny,
    harmonyVoice: VOICES.narrator,
    text: "Let's push! Ready? Say push!",
    rate: 1.05,
    gain: 1.05,
  },
  // Shot 5 (0:14 - 0:18): Kick! "Whoosh! Now it's rolling!" + Song lines 3-4
  {
    id: "shot5_whoosh",
    start: 14.08,
    maxDur: 1.32,
    voice: VOICES.benny,
    text: "Whoosh! Now it's rolling!",
    rate: 1.22,
    gain: 1.05,
  },
  {
    id: "shot5_song34",
    start: 15.48,
    maxDur: 2.85,
    voice: VOICES.benny,
    harmonyVoice: VOICES.narrator,
    text: "Push it, push it, off it goes! Roll, roll, roll, away it goes!",
    rate: 1.32,
    gain: 1.0,
  },
  // Shot 6 (0:18 - 0:22): Three Baby Bunnies pop out of the grass and cheer with giggles
  {
    id: "shot6_babies",
    start: 18.55,
    maxDur: 3.2,
    voice: VOICES.benny,
    text: "Hehehe! Yay! Look at it roll!",
    rate: 1.08,
    pitchSemitones: 2.2,
    gain: 1.02,
  },
  // Shot 7 (0:22 - 0:28): Ball keeps rolling; Benny & Baby Bunnies hop alongside singing chorus
  {
    id: "shot7_chorus1",
    start: 22.1,
    maxDur: 5.5,
    voice: VOICES.benny,
    harmonyVoice: VOICES.narrator,
    text: "Still stays still, clap clap! Rolling keeps rolling, whoosh!",
    rate: 1.05,
    gain: 1.05,
  },
  // Shot 8 (0:28 - 0:32): Ball slows and stops at the big fluffy hill
  {
    id: "shot8_hillstop",
    start: 28.15,
    maxDur: 3.6,
    voice: VOICES.narrator,
    text: "And the big, fluffy hill slows it down, to a stop!",
    rate: 1.08,
    gain: 1.0,
  },
  // Shot 9 (0:32 - 0:37): Chorus repeat with claps and a "whoosh" gesture
  {
    id: "shot9_chorus2",
    start: 32.15,
    maxDur: 4.5,
    voice: VOICES.benny,
    harmonyVoice: VOICES.narrator,
    text: "Still stays still, clap clap! Rolling keeps rolling, whoosh!",
    rate: 1.05,
    gain: 1.05,
  },
  // Shot 10 (0:37 - 0:40): Wave: "Bye-bye, friends. Hop, hop, hooray!" Calm music
  {
    id: "shot10_byebye",
    start: 37.05,
    maxDur: 2.65,
    voice: VOICES.benny,
    harmonyVoice: VOICES.narrator,
    text: "Bye-bye, friends! Hop, hop, hooray!",
    rate: 1.08,
    gain: 1.05,
  },
];

async function synthesizeNeuralClip(voice, text, outRawPath, rate = 1.0, pitchSemitones = 0, maxDur = 10.0) {
  const tts = new MsEdgeTTS();
  await tts.setMetadata(voice, OUTPUT_FORMAT.AUDIO_24KHZ_96KBITRATE_MONO_MP3);
  const subDir = path.join(TMP_DIR, `job_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`);
  fs.mkdirSync(subDir, { recursive: true });
  const { audioFilePath } = await tts.toFile(subDir, text);

  // Pass 1: Trim both leading and trailing silence and apply base rate/pitch
  const trimFilter =
    "silenceremove=start_periods=1:start_silence=0.01:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_silence=0.01:start_threshold=-45dB,areverse";

  const buildFilter = (effectiveRate) => {
    const f = [trimFilter];
    if (Math.abs(pitchSemitones) > 0.05) {
      const pitchFactor = Math.pow(2, pitchSemitones / 12);
      const tempo = Math.max(0.5, Math.min(2.0, effectiveRate / pitchFactor));
      f.push(`asetrate=24000*${pitchFactor.toFixed(4)},aresample=48000,atempo=${tempo.toFixed(4)}`);
    } else if (Math.abs(effectiveRate - 1.0) > 0.01) {
      const tempo = Math.max(0.5, Math.min(2.0, effectiveRate));
      f.push(`atempo=${tempo.toFixed(4)}`);
    }
    f.push("highpass=f=95,lowpass=f=12000,afade=t=in:st=0:d=0.012");
    return f.join(",");
  };

  execFileSync(ffmpegPath, [
    "-y",
    "-i",
    audioFilePath,
    "-af",
    buildFilter(rate),
    "-f",
    "s16le",
    "-ac",
    "1",
    "-ar",
    String(SAMPLE_RATE),
    outRawPath,
  ], { stdio: "ignore" });

  let buf = fs.readFileSync(outRawPath);
  let dur = buf.length / 2 / SAMPLE_RATE;

  // If the trimmed clip still exceeds maxDur, speed it up slightly so shots never overlap
  if (dur > maxDur) {
    const neededRate = Math.min(1.95, rate * (dur / maxDur) * 1.04);
    execFileSync(ffmpegPath, [
      "-y",
      "-i",
      audioFilePath,
      "-af",
      buildFilter(neededRate),
      "-f",
      "s16le",
      "-ac",
      "1",
      "-ar",
      String(SAMPLE_RATE),
      outRawPath,
    ], { stdio: "ignore" });
    buf = fs.readFileSync(outRawPath);
  }

  const samples = new Float32Array(buf.length / 2);
  let peak = 0.01;
  for (let i = 0; i < samples.length; i++) {
    const v = buf.readInt16LE(i * 2) / 32768;
    samples[i] = v;
    if (Math.abs(v) > peak) peak = Math.abs(v);
  }
  const norm = 0.85 / peak;
  for (let i = 0; i < samples.length; i++) {
    // Gentle 15ms fade-out at end of clip
    const rem = samples.length - i;
    const fadeOut = rem < 720 ? rem / 720 : 1.0;
    samples[i] *= norm * fadeOut;
  }
  return samples;
}

function writeWavStereo(filePath, left, right) {
  const numChannels = 2;
  const bytesPerSample = 2;
  const dataSize = left.length * numChannels * bytesPerSample;
  const buf = Buffer.alloc(44 + dataSize);

  buf.write("RIFF", 0);
  buf.writeUInt32LE(36 + dataSize, 4);
  buf.write("WAVE", 8);
  buf.write("fmt ", 12);
  buf.writeUInt32LE(16, 16);
  buf.writeUInt16LE(1, 20);
  buf.writeUInt16LE(numChannels, 22);
  buf.writeUInt32LE(SAMPLE_RATE, 24);
  buf.writeUInt32LE(SAMPLE_RATE * numChannels * bytesPerSample, 28);
  buf.writeUInt16LE(numChannels * bytesPerSample, 32);
  buf.writeUInt16LE(16, 34);
  buf.write("data", 36);
  buf.writeUInt32LE(dataSize, 40);

  let offset = 44;
  for (let i = 0; i < left.length; i++) {
    const l = Math.max(-0.98, Math.min(0.98, left[i]));
    const r = Math.max(-0.98, Math.min(0.98, right[i]));
    buf.writeInt16LE(Math.round(l * 32767), offset);
    buf.writeInt16LE(Math.round(r * 32767), offset + 2);
    offset += 4;
  }
  fs.writeFileSync(filePath, buf);
}

function addUkuleleNote(L, R, startSec, freq, durSec, amp, pan = 0) {
  const startIdx = Math.floor(startSec * SAMPLE_RATE);
  const len = Math.floor(durSec * SAMPLE_RATE);
  const lGain = amp * Math.cos(((pan + 1) * Math.PI) / 4);
  const rGain = amp * Math.sin(((pan + 1) * Math.PI) / 4);
  for (let i = 0; i < len; i++) {
    const idx = startIdx + i;
    if (idx < 0 || idx >= TOTAL_SAMPLES) continue;
    const t = i / SAMPLE_RATE;
    const attack = Math.min(1, t / 0.006);
    const decay = Math.exp(-t * 5.2);
    const sig =
      (Math.sin(2 * Math.PI * freq * t) * 0.68 +
        Math.sin(4 * Math.PI * freq * t) * 0.22 * Math.exp(-t * 9) +
        Math.sin(6 * Math.PI * freq * t) * 0.1 * Math.exp(-t * 14)) *
      attack *
      decay;
    L[idx] += sig * lGain;
    R[idx] += sig * rGain;
  }
}

function strumUkuleleChord(L, R, startSec, freqs, amp = 0.09) {
  freqs.forEach((f, idx) => {
    addUkuleleNote(L, R, startSec + idx * 0.018, f, 0.55, amp, -0.25 + idx * 0.15);
  });
}

function addXylophoneNote(L, R, startSec, freq, durSec = 0.28, amp = 0.11, pan = 0.2) {
  const startIdx = Math.floor(startSec * SAMPLE_RATE);
  const len = Math.floor(durSec * SAMPLE_RATE);
  const lGain = amp * Math.cos(((pan + 1) * Math.PI) / 4);
  const rGain = amp * Math.sin(((pan + 1) * Math.PI) / 4);
  for (let i = 0; i < len; i++) {
    const idx = startIdx + i;
    if (idx < 0 || idx >= TOTAL_SAMPLES) continue;
    const t = i / SAMPLE_RATE;
    const attack = Math.min(1, t / 0.003);
    const env = attack * Math.exp(-t * 11.5);
    const click = Math.exp(-t * 95) * Math.sin(2 * Math.PI * freq * 4.2 * t) * 0.25;
    const sig =
      (Math.sin(2 * Math.PI * freq * t) * 0.82 +
        Math.sin(2 * Math.PI * freq * 3.0 * t) * 0.18 * Math.exp(-t * 22) +
        click) *
      env;
    L[idx] += sig * lGain;
    R[idx] += sig * rGain;
  }
}

function addHandClap(L, R, startSec, amp = 0.18) {
  const offsets = [0, 0.009, 0.019];
  offsets.forEach((off, k) => {
    const sIdx = Math.floor((startSec + off) * SAMPLE_RATE);
    const len = Math.floor(0.09 * SAMPLE_RATE);
    for (let i = 0; i < len; i++) {
      const idx = sIdx + i;
      if (idx < 0 || idx >= TOTAL_SAMPLES) continue;
      const t = i / SAMPLE_RATE;
      const env = Math.exp(-t * 48) * (k === 1 ? 1.0 : 0.7);
      const n = (Math.random() * 2 - 1) * Math.sin(2 * Math.PI * 1150 * t);
      L[idx] += n * env * amp * 0.95;
      R[idx] += n * env * amp * 1.05;
    }
  });
}

function addWhoosh(L, R, startSec, durSec = 0.55, amp = 0.16) {
  const sIdx = Math.floor(startSec * SAMPLE_RATE);
  const len = Math.floor(durSec * SAMPLE_RATE);
  let lp = 0;
  for (let i = 0; i < len; i++) {
    const idx = sIdx + i;
    if (idx < 0 || idx >= TOTAL_SAMPLES) continue;
    const u = i / len;
    const env = Math.sin(Math.PI * u);
    const noise = Math.random() * 2 - 1;
    const alpha = 0.06 + 0.18 * env;
    lp = lp + alpha * (noise - lp);
    const pan = -0.5 + u * 1.0;
    L[idx] += lp * env * amp * (1 - pan * 0.4);
    R[idx] += lp * env * amp * (1 + pan * 0.4);
  }
}

function addBoing(L, R, startSec, fStart = 240, fEnd = 520, durSec = 0.22, amp = 0.16) {
  const sIdx = Math.floor(startSec * SAMPLE_RATE);
  const len = Math.floor(durSec * SAMPLE_RATE);
  let phase = 0;
  for (let i = 0; i < len; i++) {
    const idx = sIdx + i;
    if (idx < 0 || idx >= TOTAL_SAMPLES) continue;
    const u = i / len;
    const t = i / SAMPLE_RATE;
    const freq = fStart + (fEnd - fStart) * Math.pow(u, 0.55);
    phase += (2 * Math.PI * freq) / SAMPLE_RATE;
    const env = Math.sin(Math.PI * u) * Math.exp(-t * 6.5);
    const s = Math.sin(phase) * env * amp;
    L[idx] += s;
    R[idx] += s;
  }
}

async function main() {
  console.log("Synthesizing trimmed, non-overlapping natural neural voices for Video 1...");
  const voiceL = new Float32Array(TOTAL_SAMPLES);
  const voiceR = new Float32Array(TOTAL_SAMPLES);
  const voiceEnv = new Float32Array(TOTAL_SAMPLES);

  for (const line of LINES) {
    const rawPath = path.join(TMP_DIR, `${line.id}.raw`);
    const samples = await synthesizeNeuralClip(
      line.voice,
      line.text,
      rawPath,
      line.rate || 1.0,
      line.pitchSemitones || 0,
      line.maxDur || 5.0
    );
    const dur = samples.length / SAMPLE_RATE;
    console.log(
      `  [${line.id}] start=${line.start.toFixed(2)}s, dur=${dur.toFixed(2)}s (max=${line.maxDur.toFixed(2)}s), end=${(line.start + dur).toFixed(2)}s`
    );

    const startIdx = Math.floor(line.start * SAMPLE_RATE);
    for (let i = 0; i < samples.length; i++) {
      const idx = startIdx + i;
      if (idx >= 0 && idx < TOTAL_SAMPLES) {
        const v = samples[i] * (line.gain ?? 1.0);
        voiceL[idx] += v;
        voiceR[idx] += v;
        voiceEnv[idx] = Math.max(voiceEnv[idx], Math.abs(v));
      }
    }

    if (line.harmonyVoice) {
      const harmRawPath = path.join(TMP_DIR, `${line.id}_harm.raw`);
      const harmSamples = await synthesizeNeuralClip(
        line.harmonyVoice,
        line.text,
        harmRawPath,
        line.rate || 1.0,
        0,
        line.maxDur || 5.0
      );
      const offsetSamples = Math.floor(0.012 * SAMPLE_RATE);
      const len = Math.min(samples.length, harmSamples.length);
      for (let i = 0; i < len; i++) {
        const idx = startIdx + offsetSamples + i;
        if (idx >= 0 && idx < TOTAL_SAMPLES) {
          const v = harmSamples[i] * 0.26;
          voiceL[idx] += v * 0.9;
          voiceR[idx] += v * 1.1;
        }
      }
    }
  }

  const duckMask = new Float32Array(TOTAL_SAMPLES);
  let envSmooth = 0;
  for (let i = 0; i < TOTAL_SAMPLES; i++) {
    const target = voiceEnv[i] > 0.03 ? 1 : 0;
    envSmooth += (target - envSmooth) * 0.0015;
    duckMask[i] = envSmooth;
  }

  const musicL = new Float32Array(TOTAL_SAMPLES);
  const musicR = new Float32Array(TOTAL_SAMPLES);
  const beatSec = 60 / 95;

  const CHORDS = [
    [261.63, 329.63, 392.0, 523.25], // C
    [349.23, 440.0, 523.25, 698.46], // F
    [392.0, 493.88, 587.33, 698.46], // G7
    [261.63, 329.63, 392.0, 523.25], // C
  ];
  const XYL_NOTES = [523.25, 587.33, 659.25, 698.46, 783.99, 880.0, 783.99, 659.25];

  for (let beat = 0; beat * beatSec < DURATION_SEC - 0.4; beat++) {
    const t = beat * beatSec;
    // Complete 2-second silent pause in Shot 3 (8.00s - 10.10s)
    if (t >= 7.85 && t <= 10.1) continue;

    const isCalmOutro = t >= 37.0;
    const chord = CHORDS[Math.floor(beat / 2) % CHORDS.length];
    const ampScale = isCalmOutro ? 0.65 * Math.max(0.2, 1 - (t - 37.0) / 3.2) : 1.0;

    strumUkuleleChord(musicL, musicR, t, chord, 0.085 * ampScale);
    if (!isCalmOutro && t + beatSec * 0.5 < 7.85 || t > 10.1) {
      strumUkuleleChord(musicL, musicR, t + beatSec * 0.5, chord, 0.048 * ampScale);
    }

    const xylFreq = XYL_NOTES[beat % XYL_NOTES.length];
    addXylophoneNote(musicL, musicR, t, xylFreq, 0.26, 0.075 * ampScale, beat % 2 === 0 ? -0.25 : 0.25);

    if (t >= 14.2 && t <= 36.8 && beat % 2 === 1) {
      addHandClap(musicL, musicR, t, 0.09);
    }
  }

  strumUkuleleChord(musicL, musicR, 39.1, CHORDS[0], 0.1);
  addXylophoneNote(musicL, musicR, 39.15, 1046.5, 0.65, 0.09, 0);

  const sfxL = new Float32Array(TOTAL_SAMPLES);
  const sfxR = new Float32Array(TOTAL_SAMPLES);

  // Shot 1 (0:00-0:03): Ball zooms past camera & freezes + Benny pops in
  addWhoosh(sfxL, sfxR, 0.12, 0.65, 0.22);
  addBoing(sfxL, sfxR, 0.78, 320, 640, 0.24, 0.18);
  addBoing(sfxL, sfxR, 0.95, 250, 520, 0.2, 0.15);

  // Shot 2 (0:03-0:07): Butterfly flutters in & lands on sleeping ball
  addXylophoneNote(sfxL, sfxR, 4.8, 880, 0.35, 0.09, -0.2);
  addXylophoneNote(sfxL, sfxR, 5.05, 1046.5, 0.35, 0.09, 0.2);
  addXylophoneNote(sfxL, sfxR, 5.3, 1318.5, 0.45, 0.09, 0.0);

  // Shot 4 (0:10-0:14): Anticipation xylophone roll as child says "PUSH!"
  [523.25, 587.33, 659.25, 783.99, 1046.5].forEach((f, idx) => {
    addXylophoneNote(sfxL, sfxR, 13.15 + idx * 0.11, f, 0.22, 0.1, -0.3 + idx * 0.15);
  });

  // Shot 5 (0:14-0:18): Kick!
  addBoing(sfxL, sfxR, 14.02, 160, 480, 0.26, 0.24);
  addWhoosh(sfxL, sfxR, 14.12, 0.85, 0.24);
  addWhoosh(sfxL, sfxR, 16.5, 0.7, 0.16);

  // Shot 6 (0:18-0:22): Three Baby Bunnies pop out of the grass!
  addBoing(sfxL, sfxR, 18.12, 300, 660, 0.2, 0.18);
  addBoing(sfxL, sfxR, 18.3, 340, 720, 0.2, 0.18);
  addBoing(sfxL, sfxR, 18.48, 380, 780, 0.2, 0.18);

  // Shot 7 (0:22-0:28): Chorus 1 claps & whoosh
  addHandClap(sfxL, sfxR, 23.65, 0.24);
  addHandClap(sfxL, sfxR, 23.95, 0.24);
  addWhoosh(sfxL, sfxR, 25.55, 0.65, 0.22);

  // Shot 8 (0:28-0:32): Ball slows & stops at big fluffy hill
  addWhoosh(sfxL, sfxR, 28.15, 1.1, 0.14);
  addBoing(sfxL, sfxR, 29.55, 280, 180, 0.32, 0.16);

  // Shot 9 (0:32-0:37): Chorus 2 claps & whoosh
  addHandClap(sfxL, sfxR, 33.7, 0.24);
  addHandClap(sfxL, sfxR, 34.0, 0.24);
  addWhoosh(sfxL, sfxR, 35.6, 0.65, 0.22);

  // Shot 10 (0:37-0:40): Hop, hop, hooray!
  addBoing(sfxL, sfxR, 38.2, 280, 560, 0.18, 0.14);
  addBoing(sfxL, sfxR, 38.5, 320, 640, 0.18, 0.14);

  const outL = new Float32Array(TOTAL_SAMPLES);
  const outR = new Float32Array(TOTAL_SAMPLES);
  for (let i = 0; i < TOTAL_SAMPLES; i++) {
    const tSec = i / SAMPLE_RATE;
    // Enforce absolute silence during the 2-second comedy/learning pause (8.08s - 10.08s)
    if (tSec >= 8.08 && tSec <= 10.08) {
      outL[i] = 0;
      outR[i] = 0;
      continue;
    }
    const mGain = 1.0 - 0.55 * duckMask[i];
    const l = voiceL[i] * 0.92 + musicL[i] * mGain + sfxL[i] * 0.85;
    const r = voiceR[i] * 0.92 + musicR[i] * mGain + sfxR[i] * 0.85;
    outL[i] = Math.tanh(l * 1.05);
    outR[i] = Math.tanh(r * 1.05);
  }

  const outWav = path.join(OUT_DIR, "audio.wav");
  writeWavStereo(outWav, outL, outR);
  console.log(`Saved natural 48kHz stereo master soundtrack to ${outWav}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

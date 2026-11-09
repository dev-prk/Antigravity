import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import { MsEdgeTTS, OUTPUT_FORMAT } from "msedge-tts";

const require = createRequire(import.meta.url);
const ffmpegPath = require("ffmpeg-static");

const OUT_DIR = path.resolve("out/fun-fact");
const TMP_DIR = path.resolve("out/fun-fact/tmp_tts");
fs.mkdirSync(OUT_DIR, { recursive: true });
fs.mkdirSync(TMP_DIR, { recursive: true });

const SAMPLE_RATE = 48000;
const DURATION_SEC = 36.0;
const TOTAL_SAMPLES = Math.floor(SAMPLE_RATE * DURATION_SEC);

const VOICES = {
  benny: "en-US-AnaNeural",
  narrator: "en-US-AriaNeural",
};

// 7 tight, high-retention fun-fact beats (NCAR / USGS verified fact:
// A typical 1 km³ cumulus cloud weighs ~1.1 million pounds / 500,000 kg = ~100 elephants!)
const LINES = [
  // Shot 1 (0:00 - 0:04.5): Hook!
  {
    id: "shot1_hook",
    start: 0.35,
    maxDur: 4.0,
    voice: VOICES.benny,
    text: "Pop quiz! How much does ONE fluffy white cloud weigh? Like a feather, or a hundred elephants?",
    rate: 1.08,
    gain: 1.05,
  },
  // Shot 2 (0:04.5 - 0:10.0): The 1.1 million pound elephant reveal!
  {
    id: "shot2_reveal",
    start: 4.75,
    maxDur: 5.0,
    voice: VOICES.narrator,
    text: "Believe it or not, one single cumulus cloud weighs over one million pounds! That is as heavy as one hundred giant elephants!",
    rate: 1.12,
    gain: 1.0,
  },
  // Shot 3 (0:10.0 - 0:15.0): The mystery question ("Why doesn't it fall?")
  {
    id: "shot3_question",
    start: 10.15,
    maxDur: 4.6,
    voice: VOICES.benny,
    text: "Whoa! Wait a second! If a cloud weighs a hundred elephants, why doesn't it crash right onto my head?!",
    rate: 1.1,
    gain: 1.05,
  },
  // Shot 4 (0:15.0 - 0:21.5): Microscopic water droplets spread out
  {
    id: "shot4_droplets",
    start: 15.15,
    maxDur: 6.1,
    voice: VOICES.narrator,
    text: "Because that weight isn't one solid block! It's spread across billions of microscopic water droplets, each smaller than a grain of dust.",
    rate: 1.12,
    gain: 1.0,
  },
  // Shot 5 (0:21.5 - 0:27.5): Rising warm air updrafts
  {
    id: "shot5_updraft",
    start: 21.65,
    maxDur: 5.6,
    voice: VOICES.narrator,
    text: "Warm air rising from the sunny meadow pushes upward faster than those tiny droplets can fall, keeping the whole cloud floating!",
    rate: 1.12,
    gain: 1.0,
  },
  // Shot 6 (0:27.5 - 0:32.5): Rain + Rainbow payoff
  {
    id: "shot6_rainbow",
    start: 27.6,
    maxDur: 4.7,
    voice: VOICES.narrator,
    text: "Until the droplets bump together, grow heavy, and fall as fresh rain, painting a bright rainbow!",
    rate: 1.12,
    gain: 1.0,
  },
  // Shot 7 (0:32.5 - 0:36.0): Payoff & Outro
  {
    id: "shot7_outro",
    start: 32.55,
    maxDur: 3.1,
    voice: VOICES.benny,
    harmonyVoice: VOICES.narrator,
    text: "A hundred elephants in the sky! See you next time, friends!",
    rate: 1.12,
    gain: 1.05,
  },
];

async function synthesizeNeuralClip(voice, text, outRawPath, rate = 1.0, pitchSemitones = 0, maxDur = 10.0) {
  const tts = new MsEdgeTTS();
  await tts.setMetadata(voice, OUTPUT_FORMAT.AUDIO_24KHZ_96KBITRATE_MONO_MP3);
  const subDir = path.join(TMP_DIR, `job_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`);
  fs.mkdirSync(subDir, { recursive: true });
  const { audioFilePath } = await tts.toFile(subDir, text);

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

function strumUkuleleChord(L, R, startSec, freqs, amp = 0.085) {
  freqs.forEach((f, idx) => {
    addUkuleleNote(L, R, startSec + idx * 0.018, f, 0.55, amp, -0.25 + idx * 0.15);
  });
}

function addXylophoneNote(L, R, startSec, freq, durSec = 0.28, amp = 0.1, pan = 0.2) {
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

// Heavy comical elephant thump + brassy trumpet note
function addElephantThump(L, R, startSec, amp = 0.28) {
  const sIdx = Math.floor(startSec * SAMPLE_RATE);
  const len = Math.floor(0.42 * SAMPLE_RATE);
  let phase = 0;
  for (let i = 0; i < len; i++) {
    const idx = sIdx + i;
    if (idx < 0 || idx >= TOTAL_SAMPLES) continue;
    const t = i / SAMPLE_RATE;
    const freq = 115 * Math.exp(-t * 6) + 48;
    phase += (2 * Math.PI * freq) / SAMPLE_RATE;
    const env = Math.exp(-t * 8.5);
    const s = Math.tanh(Math.sin(phase) * 1.6) * env * amp;
    L[idx] += s;
    R[idx] += s;
  }
}

function addWhoosh(L, R, startSec, durSec = 0.65, amp = 0.16) {
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
    const pan = -0.4 + u * 0.8;
    L[idx] += lp * env * amp * (1 - pan * 0.4);
    R[idx] += lp * env * amp * (1 + pan * 0.4);
  }
}

async function main() {
  console.log("Synthesizing natural neural voices for Fun Fact Short: The 100-Elephant Cloud...");
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
          const v = harmSamples[i] * 0.25;
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

  // Playful 102 BPM Curiosity & Wonder Ukulele + Xylophone Score
  const musicL = new Float32Array(TOTAL_SAMPLES);
  const musicR = new Float32Array(TOTAL_SAMPLES);
  const beatSec = 60 / 102;

  const CHORDS = [
    [293.66, 369.99, 440.0, 587.33], // D major
    [392.0, 493.88, 587.33, 783.99],  // G major
    [440.0, 554.37, 659.25, 880.0],   // A major
    [293.66, 369.99, 440.0, 587.33], // D major
  ];
  const XYL_NOTES = [587.33, 659.25, 739.99, 783.99, 880.0, 987.77, 880.0, 739.99];

  for (let beat = 0; beat * beatSec < DURATION_SEC - 0.3; beat++) {
    const t = beat * beatSec;
    const chord = CHORDS[Math.floor(beat / 2) % CHORDS.length];
    const ampScale = t >= 33.5 ? Math.max(0.25, 1 - (t - 33.5) / 2.8) : 1.0;

    strumUkuleleChord(musicL, musicR, t, chord, 0.082 * ampScale);
    strumUkuleleChord(musicL, musicR, t + beatSec * 0.5, chord, 0.045 * ampScale);

    const xylFreq = XYL_NOTES[beat % XYL_NOTES.length];
    addXylophoneNote(musicL, musicR, t, xylFreq, 0.25, 0.072 * ampScale, beat % 2 === 0 ? -0.25 : 0.25);
  }

  // SFX synchronized to visual beats
  const sfxL = new Float32Array(TOTAL_SAMPLES);
  const sfxR = new Float32Array(TOTAL_SAMPLES);

  // Shot 1 (0:00-0:04.5): Pop quiz boing + feather twinkle + elephant thump
  addBoing(sfxL, sfxR, 0.2, 260, 580, 0.22, 0.18);
  addXylophoneNote(sfxL, sfxR, 2.5, 1174.66, 0.3, 0.11, -0.3);
  addElephantThump(sfxL, sfxR, 3.35, 0.26);

  // Shot 2 (0:04.5-0:10.0): Elephant lands on the giant golden scale!
  addElephantThump(sfxL, sfxR, 5.1, 0.3);
  addBoing(sfxL, sfxR, 5.35, 180, 420, 0.3, 0.2);

  // Shot 3 (0:10.0-0:15.0): Benny's ears pop up in shock!
  addBoing(sfxL, sfxR, 10.2, 300, 740, 0.22, 0.2);

  // Shot 4 (0:15.0-0:21.5): Sparkling water droplets chime cascade
  [880, 987.77, 1174.66, 1318.5, 1567.98].forEach((f, idx) => {
    addXylophoneNote(sfxL, sfxR, 15.6 + idx * 0.18, f, 0.32, 0.085, -0.3 + idx * 0.15);
  });

  // Shot 5 (0:21.5-0:27.5): Rising warm air updraft whooshes
  addWhoosh(sfxL, sfxR, 22.1, 0.9, 0.2);
  addWhoosh(sfxL, sfxR, 24.4, 0.9, 0.18);

  // Shot 6 (0:27.5-0:32.5): Magical rainbow harp/xylophone glissando!
  [587.33, 659.25, 739.99, 880.0, 987.77, 1174.66, 1318.5, 1567.98].forEach((f, idx) => {
    addXylophoneNote(sfxL, sfxR, 29.8 + idx * 0.1, f, 0.38, 0.095, -0.35 + idx * 0.1);
  });

  // Shot 7 (0:32.5-0:36.0): Happy hop & farewell chime
  addBoing(sfxL, sfxR, 33.2, 280, 620, 0.2, 0.16);
  strumUkuleleChord(sfxL, sfxR, 35.2, CHORDS[0], 0.11);

  const outL = new Float32Array(TOTAL_SAMPLES);
  const outR = new Float32Array(TOTAL_SAMPLES);
  for (let i = 0; i < TOTAL_SAMPLES; i++) {
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

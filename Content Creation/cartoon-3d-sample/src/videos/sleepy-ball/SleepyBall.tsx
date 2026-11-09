import React, { useEffect, useMemo } from "react";
import * as THREE from "three";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import { EffectComposer } from "@react-three/postprocessing";
import { BlendFunction, BloomEffect, ToneMappingEffect, ToneMappingMode } from "postprocessing";
import { Pen, INK, blobPts, headBlob, thickAngle } from "../bridge/toon";
import { InkPass, NOINK, noInkFallback } from "../bridge/ink";
import { LensBlur } from "../bridge/lensblur";
import { GradeEffect, GRADES, GRADE_STRENGTH, gradeFor } from "../bridge/grade";
import { LIGHTS, LOOK } from "../bridge/lights";
import { TONE, CHAR, twoTone, untone } from "../bridge/shade";
import { grassHD, cobbleHD, stoneHD, roofHD, facadeHD, cloudHD, ctex, rep } from "../bridge/paint";

export const SLEEPY_BALL_FRAMES = 1200; // 40.0s @ 30fps
const FPS = 30;

// Exact measured timestamps from out/sleepy-ball/timeline.json
const EV = {
  hopInStart: 0.0,
  hopInEnd: 1.6,
  pause1Start: 4.873,
  pause1End: 6.873,
  pause2Start: 12.269,
  pause2End: 15.269,
  kickWindupSec: 19.775,
  kickImpactSec: 20.275,
  rollStartSec: 20.275,
  hillSlowStartSec: 30.911,
  ballStopSec: 33.011,
  waveStartSec: 34.011,
};

const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
const smooth = (x: number) => {
  const u = clamp01(x);
  return u * u * (3 - 2 * u);
};
const glide = (u: number) => {
  const x = clamp01(u);
  return x * x * x * (x * (6 * x - 15) + 10);
};

// Meadow terrain height y(x, z): flat sunny meadow on left/center (x <= 3.5), rising into a big fluffy hill on the right (x > 3.5)
const hillY = (x: number, z = 0): number => {
  const hx = Math.max(0, x - 3.2);
  const mainHill = 2.85 * Math.exp(-((x - 10.5) ** 2) / 22 - ((z - 0.2) ** 2) / 28);
  const ramp = 0.18 * smooth(hx / 5.0);
  const backRoll = z < -5 ? 0.9 * Math.sin((x + 4) * 0.22) ** 2 * smooth((-z - 5) / 12) : 0;
  return mainHill + ramp + backRoll;
};

// Ball X trajectory over time t (seconds)
const ballXAt = (t: number): number => {
  const x0 = -0.15;
  const xStop = 7.45; // halfway up the big fluffy hill!
  if (t <= EV.kickImpactSec) return x0;
  if (t >= EV.ballStopSec) return xStop;
  const u = (t - EV.kickImpactSec) / (EV.ballStopSec - EV.kickImpactSec);
  // Fast initial roll after kick, then smooth deceleration on grass & hill slope
  const eased = 1 - (1 - u) ** 2.35;
  return x0 + (xStop - x0) * eased;
};

// Benny X trajectory over time t (seconds)
const bennyXAt = (t: number): { x: number; hopY: number; phase: number; moving: boolean } => {
  const standX = -1.15;
  if (t < EV.hopInEnd) {
    const u = clamp01(t / EV.hopInEnd);
    const x = -3.8 + (standX - -3.8) * smooth(u);
    const ph = (u * 4) % 1;
    const hopY = Math.sin(ph * Math.PI) * 0.42;
    return { x, hopY, phase: ph, moving: true };
  }
  if (t < EV.kickWindupSec) {
    return { x: standX, hopY: 0, phase: 0, moving: false };
  }
  if (t < EV.kickImpactSec + 0.35) {
    // Windup step back then kick lunge forward
    const u = clamp01((t - EV.kickWindupSec) / (EV.kickImpactSec - EV.kickWindupSec));
    const lunge = u < 0.6 ? -0.22 * smooth(u / 0.6) : -0.22 + 0.52 * smooth((u - 0.6) / 0.4);
    const hopY = u < 0.6 ? 0.12 * Math.sin((u / 0.6) * Math.PI) : 0;
    return { x: standX + lunge, hopY, phase: u, moving: true };
  }
  // Follow the rolling ball across the meadow and up the hill, stopping right behind it
  const followStart = EV.kickImpactSec + 0.55;
  const followEnd = EV.ballStopSec + 0.15;
  const endX = 6.35;
  if (t < followStart) {
    return { x: standX + 0.3, hopY: 0, phase: 0, moving: false };
  }
  if (t < followEnd) {
    const u = (t - followStart) / (followEnd - followStart);
    const eased = smooth(u);
    const x = standX + 0.3 + (endX - (standX + 0.3)) * eased;
    const hops = 14;
    const ph = (u * hops) % 1;
    const hopY = Math.sin(ph * Math.PI) * 0.34 * (1 - 0.35 * u);
    return { x, hopY, phase: ph, moving: true };
  }
  return { x: endX, hopY: 0, phase: 0, moving: false };
};

// ---------------- 2D Cartoon Drawing: Benny the Bunny & FX Cards ----------------
type BennyPose = {
  earTilt: number;
  headTilt: number;
  blink: boolean;
  expr: "happy" | "curious" | "waiting" | "kick" | "excited" | "wave";
  waveAngle: number;
  kickAngle: number;
  footTap: number;
  hopPhase: number;
  moving: boolean;
};

const drawBenny = (g: CanvasRenderingContext2D, pose: BennyPose) => {
  g.clearRect(0, 0, 600, 1000);
  const p = new Pen(g);
  p.ol = 13;
  const FUR = "#fffaf0";
  const FUR_SH = "#ead8c3";
  const PINK = "#f49eb0";
  const OVERALL = "#3d82d8";
  const OVERALL_SH = "#2a5ca0";
  const STRAP = "#5296eb";
  const GOLD = "#f5c84c";
  const light = (-120 * Math.PI) / 180;
  const thick = thickAngle(light);

  const bobY = pose.moving ? -Math.sin(pose.hopPhase * Math.PI) * 18 : 0;
  const cx = 300;
  const hipY = 745 + bobY;
  const torsoY = 605 + bobY;
  const headY = 395 + bobY;

  // Fluffy bunny cotton tail on left hip
  p.ell(cx - 88, hipY - 25, 38, 36, FUR, 12);

  // Legs (stick limbs with dark plum ink & bunny paw pads)
  const lFootX = cx - 46;
  const lFootY = 955;
  const rKick = pose.kickAngle;
  const rFootX = cx + 48 + Math.sin(rKick) * 125;
  const rFootY = 955 - Math.abs(Math.sin(rKick)) * 95 - pose.footTap * 22;

  p.line([[cx - 42, hipY], [lFootX, lFootY]], FUR, 22, true);
  p.line([[cx + 42, hipY], [rFootX, rFootY]], FUR, 22, true);

  // Feet / Paws
  p.ell(lFootX + 8, lFootY, 36, 16, FUR, 12);
  p.ell(rFootX + 12, rFootY, 36, 16, FUR, 12, 0, 360, (-rKick * 180) / Math.PI);

  // Bean Torso in sky-blue overalls
  const torsoPts = blobPts(cx, torsoY, {
    a: 92,
    b: 138,
    nTop: 1.85,
    nBot: 2.2,
    egg: -0.14,
    asym: 0.04,
    rot: 0,
    noise: 0.005,
    seed: 7,
  });
  p.gradFill(torsoPts, OVERALL, OVERALL_SH, light);
  // White chest bib / shirt top
  p.ell(cx + 4, torsoY - 82, 56, 42, FUR, 10);
  // Overall straps + gold buttons
  p.band([[cx - 42, torsoY - 110], [cx - 36, torsoY - 35]], STRAP, 18, 5);
  p.band([[cx + 42, torsoY - 110], [cx + 36, torsoY - 35]], STRAP, 18, 5);
  p.dot(cx - 36, torsoY - 32, 10, GOLD);
  p.dot(cx + 36, torsoY - 32, 10, GOLD);
  p.inkRing(torsoPts, 13, thick);

  // Left Arm
  const lHandX = pose.expr === "waiting" ? cx - 96 : cx - 108;
  const lHandY = pose.expr === "waiting" ? torsoY + 35 : torsoY + 55;
  p.line([[cx - 78, torsoY - 55], [cx - 115, torsoY - 5], [lHandX, lHandY]], FUR, 20, true);
  p.ell(lHandX, lHandY, 20, 18, FUR, 11);

  // Right Arm (waves during intro & outro, points during line 1/2)
  const rArmX = cx + 78;
  const rArmY = torsoY - 55;
  let rHandX = cx + 115;
  let rHandY = torsoY + 45;
  if (pose.expr === "wave" || pose.waveAngle !== 0) {
    const wa = pose.waveAngle;
    rHandX = cx + 145 + Math.sin(wa) * 32;
    rHandY = torsoY - 135 - Math.cos(wa) * 18;
  } else if (pose.expr === "waiting") {
    rHandX = cx + 96;
    rHandY = torsoY + 35;
  } else if (pose.expr === "curious") {
    rHandX = cx + 135;
    rHandY = torsoY - 10;
  }
  p.line([[rArmX, rArmY], [(rArmX + rHandX) / 2 + 18, (rArmY + rHandY) / 2 + 10], [rHandX, rHandY]], FUR, 20, true);
  p.ell(rHandX, rHandY, 20, 18, FUR, 11);

  // Head + Long Bunny Ears (rotated slightly by headTilt)
  p.rot = [pose.headTilt, cx, headY + 40];

  // Long Bunny Ears behind head
  const lEarRot = -14 + pose.earTilt * 18;
  const rEarRot = 14 + pose.earTilt * 24;
  p.ell(cx - 52, headY - 195, 34, 118, FUR, 13, 0, 360, lEarRot);
  p.ell(cx - 52, headY - 190, 17, 86, PINK, 0, 0, 360, lEarRot);
  p.ell(cx + 52, headY - 195, 34, 118, FUR, 13, 0, 360, rEarRot);
  p.ell(cx + 52, headY - 190, 17, 86, PINK, 0, 0, 360, rEarRot);

  // Bean Head (h/w ~0.94)
  const hPts = blobPts(cx, headY, headBlob(19, 124, 1));
  p.shadedFill(hPts, FUR, FUR_SH, light, 124);
  p.inkRing(hPts, 14, thick);

  // Whiskers on cheeks
  p.stroke([[cx - 95, headY + 12], [cx - 142, headY + 4]], 6);
  p.stroke([[cx - 95, headY + 28], [cx - 140, headY + 30]], 6);
  p.stroke([[cx + 95, headY + 12], [cx + 142, headY + 4]], 6);
  p.stroke([[cx + 95, headY + 28], [cx + 140, headY + 30]], 6);

  // Eyes (.26 W apart)
  const exL = cx - 36;
  const exR = cx + 42;
  const ey = headY - 14;
  if (pose.blink) {
    p.stroke([[exL - 16, ey], [exL + 16, ey]], 10);
    p.stroke([[exR - 16, ey], [exR + 16, ey]], 10);
  } else if (pose.expr === "happy" || pose.expr === "wave") {
    p.arc(exL, ey + 4, 16, 14, 195, 345, 10);
    p.arc(exR, ey + 4, 16, 14, 195, 345, 10);
  } else {
    p.dot(exL, ey, 11, INK);
    p.dot(exR, ey, 11, INK);
  }

  // Expressive Brows
  const browLift = pose.expr === "curious" || pose.expr === "waiting" ? -12 : pose.expr === "excited" ? -10 : -4;
  const rBrowTilt = pose.expr === "waiting" ? -10 : 0;
  p.stroke([[exL - 18, ey - 26 + browLift], [exL + 16, ey - 28 + browLift]], 9);
  p.stroke([[exR - 16, ey - 28 + browLift + rBrowTilt], [exR + 18, ey - 24 + browLift - rBrowTilt]], 9);

  // Cute pink oval nose & bunny mouth + buck tooth
  p.ell(cx + 4, headY + 14, 14, 10, PINK, 8);
  if (pose.expr === "waiting" || pose.expr === "curious") {
    p.stroke([[cx - 12, headY + 42], [cx + 18, headY + 38]], 8);
  } else {
    // Happy bunny smile with single white tooth
    p.poly([[cx - 22, headY + 36], [cx + 28, headY + 36], [cx + 20, headY + 62], [cx - 14, headY + 62]], "#5a1e28", 8);
    p.poly([[cx - 6, headY + 36], [cx + 12, headY + 36], [cx + 10, headY + 50], [cx - 4, headY + 50]], "#ffffff", 6);
  }

  p.rot = null;
};

// 2D Face & Sleepy/Awake Overlay for the Red Ball
const drawBallFace = (g: CanvasRenderingContext2D, state: "sleepy" | "shock" | "rolling" | "happy", t: number) => {
  g.clearRect(0, 0, 256, 256);
  const p = new Pen(g);
  p.ol = 8;
  const cx = 128;
  const cy = 128;

  if (state === "sleepy") {
    // Closed sleepy eyes (curved downward arcs) + tiny breathing mouth
    p.arc(cx - 34, cy - 8, 18, 12, 20, 160, 9);
    p.arc(cx + 34, cy - 8, 18, 12, 20, 160, 9);
    const r = 7 + 2.5 * Math.sin(t * 2.6);
    p.ell(cx, cy + 26, r, r * 0.85, "#5a1e28", 7);
  } else if (state === "shock") {
    // Wide awake startled eyes!
    p.ell(cx - 34, cy - 10, 18, 22, "#ffffff", 8);
    p.ell(cx + 34, cy - 10, 18, 22, "#ffffff", 8);
    p.dot(cx - 34, cy - 10, 8, INK);
    p.dot(cx + 34, cy - 10, 8, INK);
    p.ell(cx, cy + 28, 14, 18, "#5a1e28", 8);
  } else if (state === "rolling") {
    // Wheee happy arcs!
    p.arc(cx - 34, cy - 6, 16, 14, 195, 345, 9);
    p.arc(cx + 34, cy - 6, 16, 14, 195, 345, 9);
    p.arc(cx, cy + 18, 22, 16, 15, 165, 9);
  } else {
    // Contented smile at rest on the hill
    p.dot(cx - 34, cy - 8, 10, INK);
    p.dot(cx + 34, cy - 8, 10, INK);
    p.arc(cx, cy + 16, 20, 14, 20, 160, 9);
  }
};

// 2D Floating FX Card (Zzz sleep bubbles, ? question mark, Kick Starburst, or Whoosh lines)
const drawFxCard = (g: CanvasRenderingContext2D, mode: "zzz" | "question" | "kick" | "whoosh" | "none", phase: number) => {
  g.clearRect(0, 0, 256, 256);
  if (mode === "none") return;
  const p = new Pen(g);
  if (mode === "zzz") {
    // Draw 3 floating comic Z's with white fill & plum ink outline
    const drawZ = (cx: number, cy: number, s: number, alpha: number) => {
      g.save();
      g.globalAlpha = alpha;
      const pts: [number, number][] = [
        [cx - s, cy - s],
        [cx + s, cy - s],
        [cx - s * 0.2, cy + s * 0.5],
        [cx + s, cy + s * 0.5],
        [cx + s, cy + s],
        [cx - s, cy + s],
        [cx + s * 0.2, cy - s * 0.5],
        [cx - s, cy - s * 0.5],
      ];
      p.poly(pts, "#ffffff", 8);
      g.restore();
    };
    const u1 = phase % 1;
    const u2 = (phase + 0.33) % 1;
    const u3 = (phase + 0.66) % 1;
    for (const u of [u1, u2, u3]) {
      const x = 90 + u * 85 + Math.sin(u * Math.PI * 2) * 14;
      const y = 205 - u * 155;
      const sc = 12 + u * 14;
      const a = Math.sin(u * Math.PI);
      drawZ(x, y, sc, a);
    }
  } else if (mode === "question") {
    // Puzzled '?' bubble above Benny during the 3-second wait pause
    p.ell(128, 115, 58, 48, "#fffef8", 9);
    p.ell(95, 178, 14, 12, "#fffef8", 8);
    p.arc(128, 98, 18, 16, 180, 45, 10);
    p.stroke([[144, 104], [128, 120], [128, 128]], 10);
    p.dot(128, 144, 7, INK);
  } else if (mode === "kick") {
    // Starburst impact at kick
    const pts: [number, number][] = [];
    const spikes = 10;
    for (let i = 0; i < spikes * 2; i++) {
      const r = i % 2 === 0 ? 96 : 44;
      const a = (i / (spikes * 2)) * Math.PI * 2;
      pts.push([128 + Math.cos(a) * r, 128 + Math.sin(a) * r]);
    }
    p.poly(pts, "#ffe156", 9);
  } else if (mode === "whoosh") {
    // Speed lines behind rolling ball
    for (const [y, len] of [[85, 150], [128, 190], [170, 140]] as const) {
      const shift = ((phase * 180) % 60) - 30;
      p.line([[30 + shift, y], [30 + shift + len, y]], "#ffffff", 10, true);
    }
  }
};

// ---------------- 3D Sunny Meadow + Fluffy Hill World ----------------
class SleepyBallWorld {
  root = new THREE.Group();
  private hemi: THREE.HemisphereLight;
  private sun: THREE.DirectionalLight;
  private sky: THREE.Mesh;
  private skyMat: THREE.ShaderMaterial;
  private fog = new THREE.Fog("#b8d0ec", 28, 320);
  private clouds: THREE.Mesh[] = [];
  private cloudMaps: Record<"day" | "golden", THREE.Texture[]>;

  private ballGroup = new THREE.Group();
  private ballMesh: THREE.Mesh;
  private ballShadow: THREE.Mesh;
  private ballFaceMesh: THREE.Mesh;
  private ballFaceCanvas: HTMLCanvasElement;
  private ballFaceCtx: CanvasRenderingContext2D;
  private ballFaceTex: THREE.CanvasTexture;

  private bennyMesh: THREE.Mesh;
  private bennyShadow: THREE.Mesh;
  private bennyCanvas: HTMLCanvasElement;
  private bennyCtx: CanvasRenderingContext2D;
  private bennyTex: THREE.CanvasTexture;

  private fxMesh: THREE.Mesh;
  private fxCanvas: HTMLCanvasElement;
  private fxCtx: CanvasRenderingContext2D;
  private fxTex: THREE.CanvasTexture;

  constructor() {
    const R = this.root;

    // 1. Sky dome shader
    this.skyMat = new THREE.ShaderMaterial({
      uniforms: {
        c0: { value: new THREE.Color() },
        c1: { value: new THREE.Color() },
        c2: { value: new THREE.Color() },
        c3: { value: new THREE.Color() },
        c4: { value: new THREE.Color() },
        e: { value: new THREE.Vector4() },
      },
      vertexShader:
        "varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
      fragmentShader: `uniform vec3 c0, c1, c2, c3, c4; uniform vec4 e; varying vec3 vP;
        void main(){ float el = asin(clamp(normalize(vP).y, -1.0, 1.0));
          vec3 c = mix(c0, c1, smoothstep(0.0, e.x, el));
          c = mix(c, c2, smoothstep(e.x, e.y, el));
          c = mix(c, c3, smoothstep(e.y, e.z, el));
          c = mix(c, c4, smoothstep(e.z, e.w, el));
          gl_FragColor = vec4(c, 1.0); }`,
      side: THREE.BackSide,
      depthWrite: false,
      fog: false,
    });
    this.sky = new THREE.Mesh(new THREE.SphereGeometry(900, 40, 20), this.skyMat);
    this.sky.renderOrder = -1;
    this.sky.frustumCulled = false;
    this.sky.layers.set(NOINK);
    R.add(this.sky);

    // 2. Lights
    this.hemi = new THREE.HemisphereLight("#cfe6ff", "#6c5c8c", 1.1);
    this.sun = new THREE.DirectionalLight("#fff0d6", 2.6);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(2048, 2048);
    R.add(this.hemi, this.sun, this.sun.target);

    // 3. Painted Clouds
    this.cloudMaps = {
      day: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.day.cloud)),
      golden: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.golden.cloud)),
    };
    for (let i = 0; i < 7; i++) {
      const a = -0.9 + (i / 6) * 1.8;
      const d = 190 + (i % 3) * 35;
      const m = new THREE.Mesh(
        new THREE.PlaneGeometry(1, 1),
        new THREE.MeshBasicMaterial({
          map: this.cloudMaps.day[i % 4],
          color: new THREE.Color(1.08, 1.08, 1.08),
          transparent: true,
          depthWrite: false,
          fog: false,
        })
      );
      const w = 44 + (i % 3) * 14;
      m.position.set(Math.sin(a) * d, 32 + (i % 3) * 9, -Math.cos(a) * d);
      m.scale.set(w, w * 0.5, 1);
      m.layers.set(NOINK);
      this.clouds.push(m);
      R.add(m);
    }

    // 4. Rolling 3D Sunny Meadow + Big Fluffy Hill Mesh
    const segX = 120,
      segZ = 80;
    const groundGeo = new THREE.PlaneGeometry(90, 70, segX, segZ);
    groundGeo.rotateX(-Math.PI / 2);
    const pos = groundGeo.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const z = pos.getZ(i);
      pos.setY(i, hillY(x, z));
    }
    groundGeo.computeVertexNormals();
    const grassTex = rep(grassHD(), 28, 22);
    const grassMat = twoTone(new THREE.MeshLambertMaterial({ map: grassTex }));
    const groundMesh = new THREE.Mesh(groundGeo, grassMat);
    groundMesh.receiveShadow = true;
    R.add(groundMesh);

    // Extra fluffy hill puffs on the right so the hill reads unmistakably as a "big, fluffy hill"
    const hillLeafMat = twoTone(new THREE.MeshLambertMaterial({ color: "#68b84e" }));
    for (const [hx, hz, rx, ry, rz] of [
      [10.2, -0.8, 3.6, 1.6, 3.2],
      [11.8, 0.9, 3.1, 1.45, 2.8],
      [8.8, 1.2, 2.4, 1.1, 2.2],
    ] as const) {
      const puff = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 16), hillLeafMat);
      puff.scale.set(rx, ry, rz);
      puff.position.set(hx, hillY(hx, hz) + ry * 0.35, hz);
      puff.castShadow = true;
      puff.receiveShadow = true;
      R.add(puff);
    }

    // 5. White Wooden Meadow Fence, Storybook Cottage, Trees, Bushes & Wildflowers
    const woodMat = twoTone(new THREE.MeshLambertMaterial({ color: "#f2eadc" }));
    const barkMat = twoTone(new THREE.MeshLambertMaterial({ color: "#8a5a3c" }));
    const treeMat1 = twoTone(new THREE.MeshLambertMaterial({ color: "#58a846" }));
    const treeMat2 = twoTone(new THREE.MeshLambertMaterial({ color: "#48913a" }));

    // Fence along z = -4.2 from x = -14 to x = 4
    for (let fx = -14; fx <= 4; fx += 1.6) {
      const fy = hillY(fx, -4.2);
      const post = new THREE.Mesh(new THREE.BoxGeometry(0.14, 1.15, 0.14), woodMat);
      post.position.set(fx, fy + 0.55, -4.2);
      post.castShadow = true;
      post.receiveShadow = true;
      R.add(post);
      if (fx < 4) {
        const fyNext = hillY(fx + 1.6, -4.2);
        for (const rh of [0.38, 0.78]) {
          const rail = new THREE.Mesh(new THREE.BoxGeometry(1.65, 0.1, 0.07), woodMat);
          rail.position.set(fx + 0.8, (fy + fyNext) * 0.5 + rh, -4.2);
          rail.castShadow = true;
          R.add(rail);
        }
      }
    }

    // Distant storybook cottage in the meadow background
    const wallMat = twoTone(
      new THREE.MeshLambertMaterial({ map: facadeHD("cot", 4.6, 3.2, { wall: "#f5ead6", shutter: "#4a78a8", door: true }) })
    );
    const roofMat = twoTone(new THREE.MeshLambertMaterial({ map: roofHD("#d25a48") }));
    const stoneMat = twoTone(new THREE.MeshLambertMaterial({ map: stoneHD("cot") }));
    const cotX = -7.5,
      cotZ = -13.5,
      cotY = hillY(cotX, cotZ);
    const cotBody = new THREE.Mesh(new THREE.BoxGeometry(4.6, 3.2, 3.6), wallMat);
    cotBody.position.set(cotX, cotY + 1.6, cotZ);
    cotBody.castShadow = true;
    cotBody.receiveShadow = true;
    const cotRoof = new THREE.Mesh(new THREE.ConeGeometry(3.6, 2.2, 4), roofMat);
    cotRoof.rotation.y = Math.PI / 4;
    cotRoof.position.set(cotX, cotY + 4.3, cotZ);
    cotRoof.castShadow = true;
    const chimney = new THREE.Mesh(new THREE.BoxGeometry(0.55, 1.8, 0.55), stoneMat);
    chimney.position.set(cotX + 1.2, cotY + 4.4, cotZ - 0.5);
    R.add(cotBody, cotRoof, chimney);

    // Trees & Bushes framing the meadow and crowning the fluffy hill
    const treeSpots: [number, number, number][] = [
      [-11.5, -8.5, 1.35],
      [-4.2, -9.2, 1.2],
      [1.8, -8.0, 1.15],
      [7.2, -7.5, 1.25],
      [12.4, -3.5, 1.3],
      [14.2, 1.5, 1.15],
      [-8.5, 3.2, 1.1],
    ];
    for (const [tx, tz, sc] of treeSpots) {
      const ty = hillY(tx, tz);
      const tg = new THREE.Group();
      const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.28, 1.6, 8), barkMat);
      trunk.position.y = 0.8;
      const c1 = new THREE.Mesh(new THREE.SphereGeometry(1.15, 14, 12), treeMat1);
      c1.position.set(0, 2.2, 0);
      const c2 = new THREE.Mesh(new THREE.SphereGeometry(0.85, 12, 10), treeMat2);
      c2.position.set(0.45, 2.75, 0.2);
      const c3 = new THREE.Mesh(new THREE.SphereGeometry(0.8, 12, 10), treeMat1);
      c3.position.set(-0.45, 2.55, -0.15);
      tg.add(trunk, c1, c2, c3);
      tg.position.set(tx, ty, tz);
      tg.scale.setScalar(sc);
      tg.traverse((o) => {
        o.castShadow = true;
        o.receiveShadow = true;
      });
      R.add(tg);
    }

    // Wildflowers across the grass and hill
    const flowerCols = ["#ff5c6c", "#ffd84d", "#fff8e7", "#a56eff"].map((c) =>
      twoTone(new THREE.MeshLambertMaterial({ color: c }))
    );
    const stemMat = twoTone(new THREE.MeshLambertMaterial({ color: "#4a9142" }));
    for (let i = 0; i < 42; i++) {
      const fx = -8 + ((i * 37) % 220) * 0.1;
      const fz = -3.4 + ((i * 53) % 70) * 0.1;
      if (Math.abs(fz) < 0.85) continue; // keep rolling lane clean!
      const fy = hillY(fx, fz);
      const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.26, 5), stemMat);
      stem.position.set(fx, fy + 0.13, fz);
      const blossom = new THREE.Mesh(new THREE.SphereGeometry(0.095, 8, 8), flowerCols[i % 4]);
      blossom.position.set(fx, fy + 0.27, fz);
      R.add(stem, blossom);
    }

    // 6. The Red Ball (3D painted striped sphere + contact shadow + 2D face card)
    const ballTex = ctex("redBall", 512, 256, (g) => {
      g.fillStyle = "#e6322e";
      g.fillRect(0, 0, 512, 256);
      // Cream stripe around the middle so rolling rotation is clearly visible!
      g.fillStyle = "#fff5e0";
      g.fillRect(0, 106, 512, 44);
      g.fillStyle = "#241726";
      g.fillRect(0, 100, 512, 6);
      g.fillRect(0, 150, 512, 6);
    });
    const ballMat = twoTone(
      new THREE.MeshPhongMaterial({ map: ballTex, specular: "#ff9e96", shininess: 38 }),
      0.18
    );
    this.ballMesh = new THREE.Mesh(new THREE.SphereGeometry(0.42, 28, 24), ballMat);
    this.ballMesh.castShadow = true;
    this.ballMesh.receiveShadow = true;
    this.ballGroup.add(this.ballMesh);
    R.add(this.ballGroup);

    // Contact shadow blob under the ball and under Benny
    const shadowTex = ctex("shadowBlob", 128, 128, (g) => {
      const gr = g.createRadialGradient(64, 64, 8, 64, 64, 60);
      gr.addColorStop(0, "rgba(25, 20, 35, 0.55)");
      gr.addColorStop(1, "rgba(25, 20, 35, 0.0)");
      g.fillStyle = gr;
      g.fillRect(0, 0, 128, 128);
    });
    const shadowMat = new THREE.MeshBasicMaterial({ map: shadowTex, transparent: true, depthWrite: false });
    const shadowGeo = new THREE.PlaneGeometry(1, 1);
    shadowGeo.rotateX(-Math.PI / 2);
    this.ballShadow = new THREE.Mesh(shadowGeo, shadowMat);
    this.ballShadow.scale.set(0.95, 1, 0.95);
    this.ballShadow.layers.set(NOINK);
    R.add(this.ballShadow);

    this.bennyShadow = new THREE.Mesh(shadowGeo, shadowMat);
    this.bennyShadow.scale.set(1.15, 1, 0.85);
    this.bennyShadow.layers.set(NOINK);
    R.add(this.bennyShadow);

    // Ball 2D face card
    this.ballFaceCanvas = document.createElement("canvas");
    this.ballFaceCanvas.width = 256;
    this.ballFaceCanvas.height = 256;
    this.ballFaceCtx = this.ballFaceCanvas.getContext("2d")!;
    this.ballFaceTex = new THREE.CanvasTexture(this.ballFaceCanvas);
    const faceGeo = new THREE.PlaneGeometry(0.58, 0.58);
    this.ballFaceMesh = new THREE.Mesh(
      faceGeo,
      new THREE.MeshBasicMaterial({ map: this.ballFaceTex, transparent: true, depthWrite: false })
    );
    this.ballFaceMesh.layers.set(NOINK);
    R.add(this.ballFaceMesh);

    // 7. Benny the Bunny 2D Billboard Card (NOINK layer)
    this.bennyCanvas = document.createElement("canvas");
    this.bennyCanvas.width = 600;
    this.bennyCanvas.height = 1000;
    this.bennyCtx = this.bennyCanvas.getContext("2d")!;
    this.bennyTex = new THREE.CanvasTexture(this.bennyCanvas);
    const bennyGeo = new THREE.PlaneGeometry(1.5, 2.5);
    bennyGeo.translate(0, 1.2, 0); // soles at y = 0
    this.bennyMesh = new THREE.Mesh(
      bennyGeo,
      new THREE.MeshBasicMaterial({ map: this.bennyTex, transparent: true, alphaTest: 0.4 })
    );
    this.bennyMesh.layers.set(NOINK);
    R.add(this.bennyMesh);

    // 8. 2D FX Card (Zzz / ? / Kick Star / Whoosh)
    this.fxCanvas = document.createElement("canvas");
    this.fxCanvas.width = 256;
    this.fxCanvas.height = 256;
    this.fxCtx = this.fxCanvas.getContext("2d")!;
    this.fxTex = new THREE.CanvasTexture(this.fxCanvas);
    this.fxMesh = new THREE.Mesh(
      new THREE.PlaneGeometry(0.95, 0.95),
      new THREE.MeshBasicMaterial({ map: this.fxTex, transparent: true, depthWrite: false })
    );
    this.fxMesh.layers.set(NOINK);
    R.add(this.fxMesh);
  }

  update(f: number, cam: THREE.PerspectiveCamera, scene: THREE.Scene): { focus: THREE.Vector3; cInf: number; lightMode: "day" | "golden" } {
    const t = f / FPS;
    const isGolden = t >= EV.waveStartSec;
    const lightMode: "day" | "golden" = isGolden ? "golden" : "day";
    const L = LIGHTS[lightMode];
    const K = LOOK[lightMode];

    // 1. Pose Ball & Benny
    const bx = ballXAt(t);
    const by = hillY(bx, 0);
    const ballRadius = 0.42;
    this.ballGroup.position.set(bx, by + ballRadius, 0);
    const distRolled = Math.max(0, bx - -0.15);
    this.ballMesh.rotation.z = -distRolled / ballRadius;
    this.ballMesh.rotation.y = -0.35;
    this.ballShadow.position.set(bx, by + 0.02, 0);

    const bennyState = bennyXAt(t);
    const bennyGroundY = hillY(bennyState.x, 0);
    this.bennyMesh.position.set(bennyState.x, bennyGroundY + bennyState.hopY, 0.08);
    this.bennyShadow.position.set(bennyState.x, bennyGroundY + 0.02, 0.08);
    const sScale = Math.max(0.5, 1 - bennyState.hopY * 0.7);
    this.bennyShadow.scale.set(1.1 * sScale, 1, 0.8 * sScale);

    // 2. Determine Shot & Camera Choreography (6 shots across 1200 frames)
    let camPos = new THREE.Vector3(0, 1.8, 5.2);
    let camLook = new THREE.Vector3(-0.5, 0.95, 0);
    let fov = 38;
    let roll = 0;
    let cInf = 8;

    if (t < EV.pause1End) {
      // Shot 1 (0..6.873s): Sunny meadow establishing + creeping push-in on Benny & sleepy red ball
      const u = t / EV.pause1End;
      const push = 1 - 0.14 * u;
      camPos.set(-0.65, 1.55, 5.4 * push);
      camLook.set(-0.6, 0.92, 0);
      cInf = 7;
    } else if (t < EV.pause2End) {
      // Shot 2 (6.873..15.269s): Close-up with creamy DOF on the sleeping ball & waiting Benny ("Benny waits... and waits...")
      const u = (t - EV.pause1End) / (EV.pause2End - EV.pause1End);
      const push = 1 - 0.12 * u;
      camPos.set(-0.45, 1.18, 3.45 * push);
      camLook.set(-0.52, 0.78, 0);
      cInf = 14;
    } else if (t < EV.rollStartSec + 1.15) {
      // Shot 3 (15.269..21.425s): Medium action framing for the kick + 6-frame impact shake!
      const u = clamp01((t - EV.pause2End) / 5.0);
      camPos.set(-0.5 + 0.25 * u, 1.38, 4.35 - 0.25 * u);
      camLook.set(-0.45 + 0.35 * u, 0.85, 0);
      cInf = 11;
      // 6-frame flip-sign impact kick at kickImpactSec
      const kf = f - Math.round(EV.kickImpactSec * FPS);
      if (kf >= 0 && kf < 7) {
        const sign = kf % 2 === 0 ? 1 : -1;
        const decay = (7 - kf) / 7;
        camPos.y += sign * 0.06 * decay;
        roll = sign * 0.032 * decay;
      }
    } else if (t < 29.0) {
      // Shot 4 (21.425..29.0s): Smooth tracking glide following the rolling ball & hopping Benny across the meadow
      camPos.set(bx - 0.65, by + 1.45, 4.6);
      camLook.set(bx - 0.25, by + 0.85, 0);
      roll = -0.025;
      cInf = 10;
    } else if (t < EV.waveStartSec) {
      // Shot 5 (29.0..34.011s): Wide hill view as the ball climbs the big fluffy hill, slows down, and stops at Benny's paws
      const u = glide((t - 29.0) / 1.8);
      camPos.set(4.8 + 1.8 * u, 2.35 + 0.45 * u, 5.8 - 0.9 * u);
      camLook.set(6.7, hillY(6.7, 0) + 0.82, 0);
      cInf = 9;
    } else {
      // Shot 6 (34.011..40.0s): Golden-hour close medium finale on the hill as Benny waves goodbye!
      const u = (t - EV.waveStartSec) / (40.0 - EV.waveStartSec);
      const push = 1 - 0.1 * u;
      const topY = hillY(6.8, 0);
      camPos.set(6.85, topY + 1.25, 3.65 * push);
      camLook.set(6.85, topY + 0.88, 0);
      cInf = 13;
    }

    cam.position.copy(camPos);
    cam.up.set(0, 1, 0);
    cam.lookAt(camLook);
    cam.rotateZ(roll);
    cam.fov = fov;
    cam.near = 0.2;
    cam.far = 1200;
    cam.updateProjectionMatrix();
    cam.updateMatrixWorld();
    cam.layers.enable(NOINK);

    // 3. Update Sun, Sky & Two-Tone Uniforms
    const az = THREE.MathUtils.degToRad(isGolden ? 18 : 65);
    const el = THREE.MathUtils.degToRad(isGolden ? 14 : 48);
    const sunDir = new THREE.Vector3(Math.sin(az) * Math.cos(el), Math.sin(el), Math.cos(az) * Math.cos(el)).normalize();
    this.hemi.color.set(L.sky);
    this.hemi.groundColor.set(L.ground);
    this.hemi.intensity = L.hemiI;
    this.sun.color.set(L.sunCol);
    this.sun.intensity = L.sunI;
    this.sun.position.copy(camLook).addScaledVector(sunDir, 120);
    this.sun.target.position.copy(camLook);
    const sc = this.sun.shadow.camera;
    sc.left = -25;
    sc.right = 25;
    sc.top = 25;
    sc.bottom = -25;
    sc.near = 10;
    sc.far = 260;
    sc.updateProjectionMatrix();

    TONE.uLitCol.value.set(...L.lit);
    TONE.uShadeCol.value.set(...L.shade);
    TONE.uShadeLift.value.set(...L.lift);
    TONE.uLambert.value = L.lambert;
    TONE.uSideK.value = L.sideK;
    TONE.uTerm.value = L.term;
    TONE.uBounce.value.set(...K.bounce);
    TONE.uSat.value = K.sat;
    CHAR.uCharTint.value.set(...L.charTint);
    CHAR.uCharShade.value = L.charShade;
    CHAR.uGrad.value = L.charGrad;
    CHAR.uBodyGrad.value = L.bodyGrad;
    CHAR.uSideTint.value.set(...L.sideTint);

    const su = this.skyMat.uniforms;
    K.sky.c.forEach((h, i) => untone(h, su["c" + i].value));
    const e = K.sky.e.map((deg) => THREE.MathUtils.degToRad(deg));
    su.e.value.set(e[1], e[2], e[3], e[4]);
    this.sky.position.copy(cam.position);
    untone(L.fog, this.fog.color);
    scene.fog = this.fog;

    for (let i = 0; i < this.clouds.length; i++) {
      const m = this.clouds[i];
      (m.material as THREE.MeshBasicMaterial).map = this.cloudMaps[lightMode][i % 4];
    }

    // 4. Update Benny's 2D Pose & Expression
    const blink = (f % 46) < 4;
    let expr: BennyPose["expr"] = "happy";
    let headTilt = 0;
    let earTilt = Math.sin(t * 2.2) * 0.15;
    let waveAngle = 0;
    let kickAngle = 0;
    let footTap = 0;

    if (t >= 0.4 && t < 2.2) {
      expr = "wave";
      waveAngle = Math.sin(t * 10) * 0.45;
    } else if (t >= EV.pause1Start && t < EV.pause1End) {
      expr = "curious";
      headTilt = 0.14;
    } else if (t >= EV.pause1End && t < EV.pause2End) {
      expr = "waiting";
      headTilt = 0.22 * Math.sin(t * 1.4);
      footTap = t >= EV.pause2Start ? Math.max(0, Math.sin(t * 9)) : 0;
    } else if (t >= EV.kickWindupSec && t < EV.kickImpactSec + 0.35) {
      expr = "kick";
      const ku = (t - EV.kickWindupSec) / (EV.kickImpactSec - EV.kickWindupSec);
      kickAngle = ku < 0.7 ? -0.45 * smooth(ku / 0.7) : -0.45 + 1.15 * smooth((ku - 0.7) / 0.5);
    } else if (t >= EV.rollStartSec && t < EV.ballStopSec) {
      expr = "excited";
      earTilt = -0.35 + Math.sin(t * 8) * 0.2;
    } else if (t >= EV.waveStartSec) {
      expr = "wave";
      waveAngle = Math.sin(t * 9) * 0.5;
    }

    drawBenny(this.bennyCtx, {
      earTilt,
      headTilt,
      blink,
      expr,
      waveAngle,
      kickAngle,
      footTap,
      hopPhase: bennyState.phase,
      moving: bennyState.moving,
    });
    this.bennyTex.needsUpdate = true;
    this.bennyMesh.lookAt(cam.position.x, this.bennyMesh.position.y + 1.2, cam.position.z);

    // 5. Update Ball 2D Face & Floating FX Card
    const ballState =
      t < EV.kickImpactSec
        ? "sleepy"
        : t < EV.kickImpactSec + 0.65
          ? "shock"
          : t < EV.ballStopSec
            ? "rolling"
            : "happy";
    drawBallFace(this.ballFaceCtx, ballState, t);
    this.ballFaceTex.needsUpdate = true;
    const toCam = cam.position.clone().sub(this.ballGroup.position).normalize();
    this.ballFaceMesh.position.copy(this.ballGroup.position).addScaledVector(toCam, ballRadius + 0.03);
    this.ballFaceMesh.quaternion.copy(cam.quaternion);

    let fxMode: "zzz" | "question" | "kick" | "whoosh" | "none" = "none";
    if (t < EV.kickWindupSec) {
      fxMode = t >= EV.pause2Start && t < EV.pause2End - 0.4 ? "question" : "zzz";
    } else if (t >= EV.kickImpactSec && t < EV.kickImpactSec + 0.35) {
      fxMode = "kick";
    } else if (t >= EV.kickImpactSec + 0.35 && t < EV.ballStopSec - 0.8) {
      fxMode = "whoosh";
    }

    drawFxCard(this.fxCtx, fxMode, t * 0.75);
    this.fxTex.needsUpdate = true;
    this.fxMesh.visible = fxMode !== "none";
    if (fxMode === "zzz") {
      this.fxMesh.position.set(bx + 0.35, by + 1.15, 0.15);
    } else if (fxMode === "question") {
      this.fxMesh.position.set(bennyState.x + 0.55, bennyGroundY + 2.35, 0.15);
    } else if (fxMode === "kick") {
      this.fxMesh.position.set(bx - 0.25, by + 0.52, 0.25);
    } else if (fxMode === "whoosh") {
      this.fxMesh.position.set(bx - 0.75, by + 0.48, 0.1);
    }
    this.fxMesh.quaternion.copy(cam.quaternion);

    return { focus: camLook, cInf, lightMode };
  }
}

const makeBloom = () => {
  const b = new BloomEffect({
    blendFunction: BlendFunction.ADD,
    intensity: 0.45,
    luminanceThreshold: 1.0,
    luminanceSmoothing: 0.2,
    mipmapBlur: true,
    levels: 6,
    radius: 0.6,
  });
  const mip = b.mipmapBlurPass;
  const setSize = mip.setSize.bind(mip);
  mip.setSize = (w: number, h: number) => setSize(Math.round((1920 * w) / Math.max(h, 1)), 1920);
  return b;
};

const fwd = new THREE.Vector3();
const fpt = new THREE.Vector3();

const SleepyBallInner: React.FC = () => {
  const f = useCurrentFrame();
  const { camera, scene } = useThree();
  const world = useMemo(() => new SleepyBallWorld(), []);
  const fx = useMemo(
    () => ({
      ink: new InkPass(scene, camera as THREE.PerspectiveCamera),
      lens: new LensBlur({ maxCoC: 24, nearScale: 1.2 }),
      bloom: makeBloom(),
      tone: new ToneMappingEffect({ mode: ToneMappingMode.NEUTRAL }),
      grade: new GradeEffect(GRADES.day, GRADE_STRENGTH.day),
    }),
    [camera, scene]
  );
  useEffect(() => () => fx.ink.dispose(), [fx]);

  const cam = camera as THREE.PerspectiveCamera;
  const { focus, cInf, lightMode } = world.update(f, cam, scene);
  noInkFallback(world.root);

  cam.getWorldDirection(fwd);
  fpt.copy(focus);
  fx.lens.focus = Math.max(0.3, fpt.sub(cam.position).dot(fwd));
  fx.lens.cInf = cInf;
  gradeFor(fx.grade, lightMode);

  return (
    <>
      <primitive object={world.root} dispose={null} />
      <EffectComposer multisampling={4}>
        <primitive object={fx.ink} dispose={null} />
        <primitive object={fx.lens.pre} dispose={null} />
        <primitive object={fx.lens.main} dispose={null} />
        <primitive object={fx.bloom} dispose={null} />
        <primitive object={fx.tone} dispose={null} />
        <primitive object={fx.grade} dispose={null} />
      </EffectComposer>
    </>
  );
};

export const SleepyBallShort: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: "#cfe3f2" }}>
      <ThreeCanvas
        width={1080}
        height={1920}
        shadows
        gl={{ antialias: false, stencil: false, powerPreference: "high-performance", toneMappingExposure: 1.0 }}
        camera={{ fov: 38, near: 0.2, far: 1200 }}
      >
        <SleepyBallInner />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};

import React, { useMemo } from "react";
import * as THREE from "three";
import { EffectComposer, Bloom, Vignette } from "@react-three/postprocessing";

// ---------------------------------------------------------------------------
// Palette from Scripts/benny_production_pack.md
// ---------------------------------------------------------------------------
export const BENNY_PALETTE = {
  grass: "#7ED957",
  grassDark: "#63B83F",
  grassLight: "#9BE870",
  skyTop: "#6EC4FF",
  skyHorizon: "#C8ECFF",
  fur: "#F7F5F0",
  furCream: "#FFFDF9",
  earPink: "#FFB5C8",
  nosePink: "#FF8FA3",
  scarfYellow: "#FFD166",
  scarfPink: "#FFB5C8",
  scarfMint: "#B8F2E6",
  scarfLilac: "#D7C6FF",
  ballRed: "#E63946",
  ballBlue: "#457B9D",
  starWhite: "#FFFFFF",
  eyeDark: "#231915",
  woodWarm: "#C88A55",
};

export type RenderPreset = "draft" | "final";

export type BunnyPose =
  | "idle"
  | "hop"
  | "hook"
  | "shrug"
  | "encourage"
  | "kick"
  | "clap"
  | "whoosh"
  | "cheer"
  | "wave";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
export const clamp01 = (v: number) => Math.max(0, Math.min(1, v));
export const smoothstep = (a: number, b: number, x: number) => {
  const t = clamp01((x - a) / (b - a));
  return t * t * (3 - 2 * t);
};
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

function createStarShape(outerR = 0.28, innerR = 0.13, points = 5): THREE.Shape {
  const shape = new THREE.Shape();
  for (let i = 0; i < points * 2; i++) {
    const r = i % 2 === 0 ? outerR : innerR;
    const angle = (i * Math.PI) / points - Math.PI / 2;
    const x = Math.cos(angle) * r;
    const y = Math.sin(angle) * r;
    if (i === 0) shape.moveTo(x, y);
    else shape.lineTo(x, y);
  }
  shape.closePath();
  return shape;
}

// ---------------------------------------------------------------------------
// True 3D Volumetric Bunny Component (Benny & Baby Bunnies)
// ---------------------------------------------------------------------------
export interface Bunny3DProps {
  position: [number, number, number];
  rotationY?: number;
  scale?: number;
  scarfColor?: string;
  pose?: BunnyPose;
  phase?: number; // animation phase in seconds or cycles
  talking?: boolean;
  talkEnergy?: number;
  blink?: boolean;
  kickProgress?: number; // 0..1 during kick
}

export const Bunny3D: React.FC<Bunny3DProps> = ({
  position,
  rotationY = 0,
  scale = 1.0,
  scarfColor = BENNY_PALETTE.scarfYellow,
  pose = "idle",
  phase = 0,
  talking = false,
  talkEnergy = 0.5,
  blink = false,
  kickProgress = 0,
}) => {
  // Compute procedural 3D limb & body articulation from pose + phase
  let hopY = 0;
  let squashY = 1.0;
  let squashXZ = 1.0;
  let bodyTiltX = 0;
  let bodyTiltZ = 0;
  let headPitch = 0;
  let headYaw = 0;
  let headRoll = 0;

  let leftArmRot: [number, number, number] = [0.15, 0, 0.45];
  let rightArmRot: [number, number, number] = [0.15, 0, -0.45];
  let leftLegRot: [number, number, number] = [0, 0, 0];
  let rightLegRot: [number, number, number] = [0, 0, 0];
  let earBounce = Math.sin(phase * 3.2) * 0.06;

  if (pose === "hop") {
    const c = phase * Math.PI * 2;
    const s = Math.sin(c);
    hopY = Math.max(0, s) * 0.52;
    if (s > 0) {
      squashY = 1.0 + s * 0.1;
      squashXZ = 1.0 - s * 0.05;
    } else {
      const land = Math.sin(c * 2) * 0.08;
      squashY = 1.0 - Math.abs(land);
      squashXZ = 1.0 + Math.abs(land) * 0.6;
    }
    bodyTiltX = 0.12 * Math.cos(c);
    leftArmRot = [-0.45 - Math.max(0, s) * 0.5, 0, 0.35];
    rightArmRot = [-0.45 - Math.max(0, s) * 0.5, 0, -0.35];
    leftLegRot = [Math.max(0, s) * 0.55, 0, 0];
    rightLegRot = [Math.max(0, s) * 0.55, 0, 0];
    earBounce = -Math.cos(c) * 0.22;
  } else if (pose === "hook" || pose === "encourage") {
    // Leaning in warmly toward the viewer, one paw gesturing to the ball, head tilted curiously
    bodyTiltX = 0.12;
    headRoll = 0.16 * Math.sin(phase * 2.5);
    headPitch = 0.08;
    leftArmRot = [-0.75, 0.35, 0.35];
    rightArmRot = [-0.95 + Math.sin(phase * 6) * 0.18, -0.25, -0.25];
    earBounce = Math.sin(phase * 4) * 0.1;
  } else if (pose === "shrug") {
    // Cute confused/gentle shrug: both arms extended wide outward to the sides, head tilted
    const w = 0.5 + 0.5 * Math.sin(phase * 2.2);
    headRoll = 0.22;
    headPitch = 0.04;
    leftArmRot = [-0.25, 0, 1.25 + w * 0.12];
    rightArmRot = [-0.25, 0, -1.25 - w * 0.12];
  } else if (pose === "kick") {
    // Wind-up (0..0.4) -> Kick impact (0.4..0.7) -> Follow-through (0.7..1.0)
    const p = clamp01(kickProgress);
    const windup = smoothstep(0.0, 0.38, p) * (1 - smoothstep(0.38, 0.52, p));
    const strike = smoothstep(0.35, 0.55, p) * (1 - smoothstep(0.75, 1.0, p));
    bodyTiltX = -0.18 * strike + 0.12 * windup;
    rightLegRot = [0.65 * windup - 1.25 * strike, 0, 0];
    leftArmRot = [-0.7 * strike, 0, 0.55];
    rightArmRot = [0.4 * strike - 0.5 * windup, 0, -0.55];
    hopY = strike * 0.18;
    earBounce = -strike * 0.25;
  } else if (pose === "clap") {
    // Double rhythmic hand-clap in front of tummy
    const clapWave = Math.abs(Math.sin(phase * Math.PI * 3.2));
    const close = smoothstep(0.3, 0.95, clapWave);
    leftArmRot = [-1.15, 0.55 + close * 0.42, 0.2];
    rightArmRot = [-1.15, -0.55 - close * 0.42, -0.2];
    hopY = Math.max(0, Math.sin(phase * Math.PI * 3.2)) * 0.12;
    headRoll = Math.sin(phase * Math.PI * 1.6) * 0.12;
  } else if (pose === "whoosh") {
    // Big sweeping arm motion across the body
    const sweep = Math.sin(phase * 3.5);
    bodyTiltZ = -0.12 * sweep;
    headYaw = 0.25 * sweep;
    leftArmRot = [-0.85, 0.4 * sweep, 0.45];
    rightArmRot = [-1.25, -0.55 * sweep, -0.35];
    hopY = Math.abs(sweep) * 0.15;
  } else if (pose === "cheer") {
    // Both arms raised high, bouncing joyfully!
    const b = Math.abs(Math.sin(phase * 6.5));
    hopY = b * 0.34;
    squashY = 1.0 + b * 0.08;
    leftArmRot = [-2.25 + b * 0.2, 0, 0.35];
    rightArmRot = [-2.25 + b * 0.2, 0, -0.35];
    headPitch = -0.1;
    earBounce = -b * 0.2;
  } else if (pose === "wave") {
    // Warm goodbye wave with right paw + gentle bounce
    const w = Math.sin(phase * 7.5);
    hopY = Math.max(0, Math.sin(phase * 3.5)) * 0.14;
    rightArmRot = [-2.15, 0, -0.35 + w * 0.28];
    leftArmRot = [0.15, 0, 0.4];
    headRoll = 0.12 * Math.sin(phase * 3.5);
  } else {
    // Gentle breathing idle
    const b = Math.sin(phase * 2.6);
    squashY = 1.0 + b * 0.025;
    squashXZ = 1.0 - b * 0.015;
    headRoll = Math.sin(phase * 1.5) * 0.06;
  }

  const mouthOpen = talking ? 0.25 + 0.75 * Math.abs(Math.sin(phase * 11.5)) * talkEnergy : 0.08;
  const eyeScaleY = blink ? 0.12 : 1.0;

  return (
    <group position={[position[0], position[1] + hopY, position[2]]} rotation={[0, rotationY, 0]} scale={scale}>
      <group scale={[squashXZ, squashY, squashXZ]} rotation={[bodyTiltX, 0, bodyTiltZ]}>
        {/* ---------------- FEET & LEGS ---------------- */}
        {/* Left Leg & Plump 3D Foot */}
        <group position={[-0.24, 0.28, 0.02]} rotation={leftLegRot}>
          <mesh castShadow receiveShadow position={[0, -0.06, 0]}>
            <capsuleGeometry args={[0.13, 0.16, 12, 20]} />
            <meshStandardMaterial color={BENNY_PALETTE.fur} roughness={0.75} />
          </mesh>
          <mesh castShadow receiveShadow position={[0, -0.2, 0.1]} scale={[1.05, 0.65, 1.45]}>
            <sphereGeometry args={[0.16, 20, 16]} />
            <meshStandardMaterial color={BENNY_PALETTE.fur} roughness={0.72} />
          </mesh>
          {/* Pink Toe Pads */}
          <mesh position={[0, -0.21, 0.31]} scale={[0.85, 0.55, 0.4]}>
            <sphereGeometry args={[0.09, 12, 12]} />
            <meshStandardMaterial color={BENNY_PALETTE.earPink} roughness={0.65} />
          </mesh>
        </group>

        {/* Right Leg & Plump 3D Foot */}
        <group position={[0.24, 0.28, 0.02]} rotation={rightLegRot}>
          <mesh castShadow receiveShadow position={[0, -0.06, 0]}>
            <capsuleGeometry args={[0.13, 0.16, 12, 20]} />
            <meshStandardMaterial color={BENNY_PALETTE.fur} roughness={0.75} />
          </mesh>
          <mesh castShadow receiveShadow position={[0, -0.2, 0.1]} scale={[1.05, 0.65, 1.45]}>
            <sphereGeometry args={[0.16, 20, 16]} />
            <meshStandardMaterial color={BENNY_PALETTE.fur} roughness={0.72} />
          </mesh>
          <mesh position={[0, -0.21, 0.31]} scale={[0.85, 0.55, 0.4]}>
            <sphereGeometry args={[0.09, 12, 12]} />
            <meshStandardMaterial color={BENNY_PALETTE.earPink} roughness={0.65} />
          </mesh>
        </group>

        {/* ---------------- PLUMP 3D TORSO & COTTON TAIL ---------------- */}
        <mesh castShadow receiveShadow position={[0, 0.72, 0]} scale={[0.96, 1.08, 0.88]}>
          <sphereGeometry args={[0.52, 32, 28]} />
          <meshStandardMaterial
            color={BENNY_PALETTE.fur}
            roughness={0.72}
            emissive="#ffffff"
            emissiveIntensity={0.04}
          />
        </mesh>
        {/* Warm Cream Belly Patch */}
        <mesh receiveShadow position={[0, 0.7, 0.16]} scale={[0.72, 0.85, 0.68]}>
          <sphereGeometry args={[0.48, 28, 24]} />
          <meshStandardMaterial color={BENNY_PALETTE.furCream} roughness={0.7} />
        </mesh>
        {/* Fluffy Round 3D Cotton Tail */}
        <mesh castShadow position={[0, 0.52, -0.48]}>
          <sphereGeometry args={[0.2, 20, 20]} />
          <meshStandardMaterial color={BENNY_PALETTE.furCream} roughness={0.8} />
        </mesh>

        {/* ---------------- COSY 3D SCARF ---------------- */}
        <group position={[0, 1.18, 0.02]}>
          {/* Plump Torus Neck Ring */}
          <mesh castShadow receiveShadow rotation={[Math.PI / 2 + 0.08, 0, 0]} scale={[1.04, 0.96, 1.25]}>
            <torusGeometry args={[0.38, 0.11, 20, 36]} />
            <meshStandardMaterial
              color={scarfColor}
              roughness={0.58}
              emissive={scarfColor}
              emissiveIntensity={0.08}
            />
          </mesh>
          {/* Draped 3D Scarf Knot & Tails on Front-Right */}
          <mesh castShadow position={[0.2, -0.06, 0.35]}>
            <sphereGeometry args={[0.12, 16, 16]} />
            <meshStandardMaterial color={scarfColor} roughness={0.58} />
          </mesh>
          <mesh
            castShadow
            position={[0.24, -0.26, 0.38]}
            rotation={[0.15, 0, -0.18 + Math.sin(phase * 3) * 0.08]}
            scale={[0.85, 1.35, 0.45]}
          >
            <capsuleGeometry args={[0.09, 0.22, 12, 16]} />
            <meshStandardMaterial color={scarfColor} roughness={0.58} />
          </mesh>
          <mesh
            castShadow
            position={[0.11, -0.22, 0.4]}
            rotation={[0.2, 0, 0.08 + Math.cos(phase * 3) * 0.06]}
            scale={[0.75, 1.1, 0.45]}
          >
            <capsuleGeometry args={[0.08, 0.18, 12, 16]} />
            <meshStandardMaterial color={scarfColor} roughness={0.58} />
          </mesh>
        </group>

        {/* ---------------- ARTICULATED 3D ARMS ---------------- */}
        {/* Left Arm */}
        <group position={[-0.44, 1.02, 0.04]} rotation={leftArmRot}>
          <mesh castShadow position={[0, -0.2, 0]}>
            <capsuleGeometry args={[0.11, 0.28, 12, 18]} />
            <meshStandardMaterial color={BENNY_PALETTE.fur} roughness={0.72} />
          </mesh>
          <mesh castShadow position={[0, -0.38, 0.02]}>
            <sphereGeometry args={[0.13, 18, 18]} />
            <meshStandardMaterial color={BENNY_PALETTE.furCream} roughness={0.7} />
          </mesh>
          <mesh position={[0, -0.38, 0.12]} scale={[0.7, 0.7, 0.35]}>
            <sphereGeometry args={[0.08, 12, 12]} />
            <meshStandardMaterial color={BENNY_PALETTE.earPink} roughness={0.65} />
          </mesh>
        </group>

        {/* Right Arm */}
        <group position={[0.44, 1.02, 0.04]} rotation={rightArmRot}>
          <mesh castShadow position={[0, -0.2, 0]}>
            <capsuleGeometry args={[0.11, 0.28, 12, 18]} />
            <meshStandardMaterial color={BENNY_PALETTE.fur} roughness={0.72} />
          </mesh>
          <mesh castShadow position={[0, -0.38, 0.02]}>
            <sphereGeometry args={[0.13, 18, 18]} />
            <meshStandardMaterial color={BENNY_PALETTE.furCream} roughness={0.7} />
          </mesh>
          <mesh position={[0, -0.38, 0.12]} scale={[0.7, 0.7, 0.35]}>
            <sphereGeometry args={[0.08, 12, 12]} />
            <meshStandardMaterial color={BENNY_PALETTE.earPink} roughness={0.65} />
          </mesh>
        </group>

        {/* ---------------- SCULPTED 3D HEAD, CHEEKS, EYES & EARS ---------------- */}
        <group position={[0, 1.62, 0.04]} rotation={[headPitch, headYaw, headRoll]}>
          {/* Main Rounded Head Sphere */}
          <mesh castShadow receiveShadow scale={[1.08, 0.98, 1.0]}>
            <sphereGeometry args={[0.52, 36, 32]} />
            <meshStandardMaterial
              color={BENNY_PALETTE.fur}
              roughness={0.7}
              emissive="#ffffff"
              emissiveIntensity={0.04}
            />
          </mesh>
          {/* Left & Right Plump 3D Chubby Cheeks */}
          <mesh castShadow position={[-0.32, -0.12, 0.22]} scale={[1.1, 0.88, 0.95]}>
            <sphereGeometry args={[0.25, 24, 20]} />
            <meshStandardMaterial color={BENNY_PALETTE.fur} roughness={0.7} />
          </mesh>
          <mesh castShadow position={[0.32, -0.12, 0.22]} scale={[1.1, 0.88, 0.95]}>
            <sphereGeometry args={[0.25, 24, 20]} />
            <meshStandardMaterial color={BENNY_PALETTE.fur} roughness={0.7} />
          </mesh>
          {/* Warm Rosy Blush ovals on cheeks */}
          <mesh position={[-0.36, -0.08, 0.42]} rotation={[0, -0.38, 0]} scale={[1.2, 0.75, 0.3]}>
            <sphereGeometry args={[0.095, 16, 16]} />
            <meshStandardMaterial color={BENNY_PALETTE.earPink} roughness={0.65} />
          </mesh>
          <mesh position={[0.36, -0.08, 0.42]} rotation={[0, 0.38, 0]} scale={[1.2, 0.75, 0.3]}>
            <sphereGeometry args={[0.095, 16, 16]} />
            <meshStandardMaterial color={BENNY_PALETTE.earPink} roughness={0.65} />
          </mesh>

          {/* Rounded 3D Cream Snout / Muzzle */}
          <mesh position={[0, -0.1, 0.44]} scale={[1.15, 0.88, 0.78]}>
            <sphereGeometry args={[0.21, 24, 20]} />
            <meshStandardMaterial color={BENNY_PALETTE.furCream} roughness={0.68} />
          </mesh>
          {/* Cute Pink 3D Nose */}
          <mesh position={[0, -0.02, 0.6]} scale={[1.25, 0.9, 0.85]}>
            <sphereGeometry args={[0.068, 18, 16]} />
            <meshStandardMaterial color={BENNY_PALETTE.nosePink} roughness={0.35} />
          </mesh>
          {/* Nose highlight */}
          <mesh position={[-0.02, 0.0, 0.65]}>
            <sphereGeometry args={[0.018, 10, 10]} />
            <meshBasicMaterial color="#ffffff" />
          </mesh>

          {/* Expressive 3D Mouth & Cute Bunny Tooth */}
          <group position={[0, -0.17, 0.56]}>
            <mesh scale={[1.1, 0.45 + mouthOpen * 0.95, 0.6]}>
              <sphereGeometry args={[0.085, 18, 16]} />
              <meshStandardMaterial color="#8E2B3A" roughness={0.5} />
            </mesh>
            {/* Cute Little White Bunny Front Tooth */}
            <mesh position={[0, 0.035 + mouthOpen * 0.02, 0.035]} scale={[0.9, 0.7, 0.35]}>
              <boxGeometry args={[0.065, 0.045, 0.03]} />
              <meshStandardMaterial color="#ffffff" roughness={0.2} />
            </mesh>
          </group>

          {/* ---------------- BIG SHINY 3D EYES WITH CATCHLIGHTS ---------------- */}
          {/* Left Eye */}
          <group position={[-0.2, 0.09, 0.45]} scale={[1, eyeScaleY, 1]}>
            {/* White Sclera rim */}
            <mesh scale={[1.05, 1.12, 0.65]}>
              <sphereGeometry args={[0.135, 24, 24]} />
              <meshStandardMaterial color="#ffffff" roughness={0.2} />
            </mesh>
            {/* Glossy Deep Espresso Iris/Pupil */}
            <mesh position={[0.01, 0, 0.03]} scale={[0.95, 1.05, 0.65]}>
              <sphereGeometry args={[0.115, 24, 24]} />
              <meshPhysicalMaterial color={BENNY_PALETTE.eyeDark} roughness={0.06} clearcoat={1.0} />
            </mesh>
            {/* Primary Big White Catchlight */}
            <mesh position={[-0.032, 0.042, 0.1]}>
              <sphereGeometry args={[0.034, 14, 14]} />
              <meshBasicMaterial color="#ffffff" />
            </mesh>
            {/* Secondary Sparkle Catchlight */}
            <mesh position={[0.038, -0.035, 0.098]}>
              <sphereGeometry args={[0.016, 12, 12]} />
              <meshBasicMaterial color="#ffffff" />
            </mesh>
          </group>

          {/* Right Eye */}
          <group position={[0.2, 0.09, 0.45]} scale={[1, eyeScaleY, 1]}>
            <mesh scale={[1.05, 1.12, 0.65]}>
              <sphereGeometry args={[0.135, 24, 24]} />
              <meshStandardMaterial color="#ffffff" roughness={0.2} />
            </mesh>
            <mesh position={[-0.01, 0, 0.03]} scale={[0.95, 1.05, 0.65]}>
              <sphereGeometry args={[0.115, 24, 24]} />
              <meshPhysicalMaterial color={BENNY_PALETTE.eyeDark} roughness={0.06} clearcoat={1.0} />
            </mesh>
            <mesh position={[-0.032, 0.042, 0.1]}>
              <sphereGeometry args={[0.034, 14, 14]} />
              <meshBasicMaterial color="#ffffff" />
            </mesh>
            <mesh position={[0.038, -0.035, 0.098]}>
              <sphereGeometry args={[0.016, 12, 12]} />
              <meshBasicMaterial color="#ffffff" />
            </mesh>
          </group>

          {/* Soft 3D Eyebrows */}
          <mesh
            position={[-0.21, 0.27, 0.46]}
            rotation={[0, 0, pose === "shrug" || pose === "hook" ? 0.22 : 0.1]}
            scale={[1.2, 0.45, 0.45]}
          >
            <capsuleGeometry args={[0.028, 0.09, 8, 12]} />
            <meshStandardMaterial color="#B8B2A6" roughness={0.7} />
          </mesh>
          <mesh
            position={[0.21, 0.27, 0.46]}
            rotation={[0, 0, pose === "shrug" || pose === "hook" ? -0.22 : -0.1]}
            scale={[1.2, 0.45, 0.45]}
          >
            <capsuleGeometry args={[0.028, 0.09, 8, 12]} />
            <meshStandardMaterial color="#B8B2A6" roughness={0.7} />
          </mesh>

          {/* ---------------- LONG 3D EARS WITH PINK INNER EARS ---------------- */}
          {/* Left Ear */}
          <group
            position={[-0.22, 0.42, -0.02]}
            rotation={[0.08 + earBounce, 0.08, 0.18 + earBounce * 0.5]}
          >
            <mesh castShadow position={[0, 0.46, 0]} scale={[0.92, 1.25, 0.52]}>
              <capsuleGeometry args={[0.145, 0.48, 16, 24]} />
              <meshStandardMaterial color={BENNY_PALETTE.fur} roughness={0.7} />
            </mesh>
            {/* Pink Inner Ear */}
            <mesh position={[0, 0.45, 0.052]} scale={[0.62, 1.05, 0.32]}>
              <capsuleGeometry args={[0.13, 0.44, 14, 20]} />
              <meshStandardMaterial color={BENNY_PALETTE.earPink} roughness={0.62} />
            </mesh>
          </group>

          {/* Right Ear */}
          <group
            position={[0.22, 0.42, -0.02]}
            rotation={[0.08 - earBounce * 0.8, -0.08, -0.22 - earBounce * 0.5]}
          >
            <mesh castShadow position={[0, 0.46, 0]} scale={[0.92, 1.25, 0.52]}>
              <capsuleGeometry args={[0.145, 0.48, 16, 24]} />
              <meshStandardMaterial color={BENNY_PALETTE.fur} roughness={0.7} />
            </mesh>
            {/* Pink Inner Ear */}
            <mesh position={[0, 0.45, 0.052]} scale={[0.62, 1.05, 0.32]}>
              <capsuleGeometry args={[0.13, 0.44, 14, 20]} />
              <meshStandardMaterial color={BENNY_PALETTE.earPink} roughness={0.62} />
            </mesh>
          </group>
        </group>
      </group>
    </group>
  );
};

// ---------------------------------------------------------------------------
// True 3D Glossy Red Ball with Raised White Star & Sleeping/Awake Eyes
// ---------------------------------------------------------------------------
export interface RedBall3DProps {
  position: [number, number, number];
  rollAngle?: number;
  sleeping?: boolean;
  zzzPhase?: number;
  showZzz?: boolean;
  squash?: number; // 0..1 impact squash
  scale?: number;
  color?: string;
}

export const RedBall3D: React.FC<RedBall3DProps> = ({
  position,
  rollAngle = 0,
  sleeping = false,
  zzzPhase = 0,
  showZzz = false,
  squash = 0,
  scale = 1.0,
  color = BENNY_PALETTE.ballRed,
}) => {
  const starGeo = useMemo(() => {
    const shape = createStarShape(0.24, 0.11, 5);
    return new THREE.ExtrudeGeometry(shape, {
      depth: 0.035,
      bevelEnabled: true,
      bevelThickness: 0.012,
      bevelSize: 0.012,
      bevelSegments: 3,
    });
  }, []);

  const radius = 0.52;
  const sx = 1.0 + squash * 0.22;
  const sy = 1.0 - squash * 0.18;

  return (
    <group position={[position[0], position[1] + radius * sy * scale, position[2]]} scale={[scale * sx, scale * sy, scale * sx]}>
      {/* Rolling 3D Sphere Body + Raised 3D White Star Badges */}
      <group rotation={[0, 0, -rollAngle]}>
        <mesh castShadow receiveShadow>
          <sphereGeometry args={[radius, 36, 36]} />
          <meshPhysicalMaterial
            color={color}
            roughness={0.22}
            clearcoat={0.85}
            clearcoatRoughness={0.15}
          />
        </mesh>
        {/* Front 3D White Star Badge */}
        <mesh geometry={starGeo} position={[0, 0, radius - 0.015]}>
          <meshStandardMaterial color={BENNY_PALETTE.starWhite} roughness={0.3} />
        </mesh>
        {/* Back 3D White Star Badge */}
        <mesh geometry={starGeo} position={[0, 0, -(radius - 0.015)]} rotation={[0, Math.PI, 0]}>
          <meshStandardMaterial color={BENNY_PALETTE.starWhite} roughness={0.3} />
        </mesh>
        {/* Subtle Equatorial White Stripe Ring for clear rolling feedback */}
        <mesh rotation={[0, Math.PI / 2, 0]}>
          <torusGeometry args={[radius * 0.995, 0.018, 12, 48]} />
          <meshStandardMaterial color="#FFD8DC" roughness={0.35} />
        </mesh>
      </group>

      {/* Cute 3D Sleeping / Awake Face Overlay on Front of Ball */}
      <group position={[0, 0.06, radius + 0.02]}>
        {sleeping ? (
          <>
            {/* Sleeping Closed-Eye Arcs */}
            <mesh position={[-0.14, 0.06, 0]} rotation={[0, 0, Math.PI]}>
              <torusGeometry args={[0.065, 0.016, 10, 20, Math.PI]} />
              <meshBasicMaterial color={BENNY_PALETTE.eyeDark} />
            </mesh>
            <mesh position={[0.14, 0.06, 0]} rotation={[0, 0, Math.PI]}>
              <torusGeometry args={[0.065, 0.016, 10, 20, Math.PI]} />
              <meshBasicMaterial color={BENNY_PALETTE.eyeDark} />
            </mesh>
            {/* Peaceful Tiny Sleepy Mouth */}
            <mesh position={[0, -0.06, 0]}>
              <sphereGeometry args={[0.028, 12, 12]} />
              <meshBasicMaterial color={BENNY_PALETTE.eyeDark} />
            </mesh>
          </>
        ) : (
          <>
            {/* Awake Sparkly Eyes */}
            <group position={[-0.14, 0.08, 0]}>
              <mesh>
                <sphereGeometry args={[0.055, 16, 16]} />
                <meshBasicMaterial color={BENNY_PALETTE.eyeDark} />
              </mesh>
              <mesh position={[-0.015, 0.018, 0.045]}>
                <sphereGeometry args={[0.018, 10, 10]} />
                <meshBasicMaterial color="#ffffff" />
              </mesh>
            </group>
            <group position={[0.14, 0.08, 0]}>
              <mesh>
                <sphereGeometry args={[0.055, 16, 16]} />
                <meshBasicMaterial color={BENNY_PALETTE.eyeDark} />
              </mesh>
              <mesh position={[-0.015, 0.018, 0.045]}>
                <sphereGeometry args={[0.018, 10, 10]} />
                <meshBasicMaterial color="#ffffff" />
              </mesh>
            </group>
            {/* Happy Smile Arc */}
            <mesh position={[0, -0.02, 0]} rotation={[0, 0, Math.PI]}>
              <torusGeometry args={[0.075, 0.016, 10, 20, Math.PI]} />
              <meshBasicMaterial color="#ffffff" />
            </mesh>
          </>
        )}
      </group>

      {/* Floating 3D Sleepy "Zzz" Bubbles when sleeping */}
      {showZzz && (
        <group position={[0.25, 0.68, 0]}>
          {[0, 1, 2].map((idx) => {
            const u = (zzzPhase * 0.65 + idx * 0.33) % 1;
            const y = u * 0.95;
            const x = idx * 0.18 + Math.sin((u + idx) * Math.PI * 2) * 0.1;
            const s = (0.55 + u * 0.65) * (1 - Math.pow(u, 3));
            return (
              <group key={idx} position={[x, y, 0]} scale={s} rotation={[0, 0, -0.15 + idx * 0.08]}>
                {/* Top horizontal bar of Z */}
                <mesh position={[0, 0.08, 0]} rotation={[0, 0, Math.PI / 2]}>
                  <capsuleGeometry args={[0.022, 0.12, 8, 12]} />
                  <meshStandardMaterial color="#FFF6B3" emissive="#FFD166" emissiveIntensity={0.35} />
                </mesh>
                {/* Diagonal bar of Z */}
                <mesh position={[0, 0, 0]} rotation={[0, 0, -0.72]}>
                  <capsuleGeometry args={[0.022, 0.15, 8, 12]} />
                  <meshStandardMaterial color="#FFF6B3" emissive="#FFD166" emissiveIntensity={0.35} />
                </mesh>
                {/* Bottom horizontal bar of Z */}
                <mesh position={[0, -0.08, 0]} rotation={[0, 0, Math.PI / 2]}>
                  <capsuleGeometry args={[0.022, 0.12, 8, 12]} />
                  <meshStandardMaterial color="#FFF6B3" emissive="#FFD166" emissiveIntensity={0.35} />
                </mesh>
              </group>
            );
          })}
        </group>
      )}
    </group>
  );
};

// ---------------------------------------------------------------------------
// 3D Animated Butterfly (lands on sleeping ball in Shot 2)
// ---------------------------------------------------------------------------
export interface Butterfly3DProps {
  position: [number, number, number];
  rotationY?: number;
  flapPhase?: number;
  scale?: number;
}

export const Butterfly3D: React.FC<Butterfly3DProps> = ({
  position,
  rotationY = 0,
  flapPhase = 0,
  scale = 1.0,
}) => {
  const wingAngle = 0.25 + 0.65 * Math.abs(Math.sin(flapPhase * 12));
  return (
    <group position={position} rotation={[0.15, rotationY, 0]} scale={scale}>
      {/* Little body */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <capsuleGeometry args={[0.025, 0.14, 8, 12]} />
        <meshStandardMaterial color="#3A2618" roughness={0.6} />
      </mesh>
      {/* Left Wing Pair */}
      <group rotation={[0, 0, wingAngle]}>
        <mesh position={[-0.09, 0.01, 0.02]} scale={[1.2, 0.18, 1.0]}>
          <sphereGeometry args={[0.085, 16, 12]} />
          <meshStandardMaterial color="#FFD166" emissive="#FFD166" emissiveIntensity={0.2} roughness={0.4} />
        </mesh>
        <mesh position={[-0.07, 0.01, -0.07]} scale={[0.95, 0.18, 0.85]}>
          <sphereGeometry args={[0.068, 14, 12]} />
          <meshStandardMaterial color="#FF8FA3" emissive="#FF8FA3" emissiveIntensity={0.15} roughness={0.4} />
        </mesh>
      </group>
      {/* Right Wing Pair */}
      <group rotation={[0, 0, -wingAngle]}>
        <mesh position={[0.09, 0.01, 0.02]} scale={[1.2, 0.18, 1.0]}>
          <sphereGeometry args={[0.085, 16, 12]} />
          <meshStandardMaterial color="#FFD166" emissive="#FFD166" emissiveIntensity={0.2} roughness={0.4} />
        </mesh>
        <mesh position={[0.07, 0.01, -0.07]} scale={[0.95, 0.18, 0.85]}>
          <sphereGeometry args={[0.068, 14, 12]} />
          <meshStandardMaterial color="#FF8FA3" emissive="#FF8FA3" emissiveIntensity={0.15} roughness={0.4} />
        </mesh>
      </group>
    </group>
  );
};

// ---------------------------------------------------------------------------
// 3D Painted Storybook Meadow World + Big Fluffy Hill + Lighting
// ---------------------------------------------------------------------------
export interface MeadowWorld3DProps {
  cloudDrift?: number;
  hillX?: number; // x-center of the big fluffy hill where the ball stops
  preset?: RenderPreset;
}

export const MeadowWorld3D: React.FC<MeadowWorld3DProps> = ({
  cloudDrift = 0,
  hillX = 14.2,
  preset = "final",
}) => {
  const shadowMapSize = preset === "draft" ? 1024 : 2048;

  const flowers = useMemo(
    () => [
      { x: -4.2, z: -2.4, color: "#FFD166", s: 1.0 },
      { x: -2.1, z: 1.7, color: "#FFB5C8", s: 0.9 },
      { x: -0.6, z: -2.8, color: "#FFFFFF", s: 1.05 },
      { x: 1.8, z: 1.85, color: "#FFD166", s: 0.85 },
      { x: 3.4, z: -2.2, color: "#D7C6FF", s: 1.1 },
      { x: 5.5, z: 1.65, color: "#FFB5C8", s: 0.95 },
      { x: 7.4, z: -2.5, color: "#FFFFFF", s: 1.0 },
      { x: 9.6, z: 1.75, color: "#FFD166", s: 0.9 },
      { x: 11.4, z: -2.1, color: "#FFB5C8", s: 1.05 },
    ],
    []
  );

  const grassClusters = useMemo(
    () => [
      [-3.5, 1.35],
      [-1.2, -1.9],
      [0.8, 1.45],
      [2.6, -1.8],
      [4.5, 1.4],
      [6.4, -1.75],
      [8.2, 1.5],
      [10.2, -1.85],
      [12.1, 1.4],
    ],
    []
  );

  return (
    <group>
      {/* Soft Sunny Sky Background & Gentle Atmospheric Fog */}
      <color attach="background" args={["#8FD3FF"]} />
      <fog attach="fog" args={["#B8E6FF", 26, 68]} />

      {/* Warm Storybook Three-Point Lighting + Fur Rim Light */}
      <ambientLight intensity={0.78} color="#FFFBF2" />
      <hemisphereLight args={["#B8E6FF", "#7ED957", 0.62]} />

      {/* Primary Morning Sun with Soft Shadows */}
      <directionalLight
        castShadow
        position={[10, 18, 12]}
        intensity={1.55}
        color="#FFF5D6"
        shadow-mapSize-width={shadowMapSize}
        shadow-mapSize-height={shadowMapSize}
        shadow-camera-near={1}
        shadow-camera-far={55}
        shadow-camera-left={-18}
        shadow-camera-right={22}
        shadow-camera-top={14}
        shadow-camera-bottom={-14}
        shadow-bias={-0.0005}
      />

      {/* Golden Rim Light from Behind for Warm Fur Halo */}
      <directionalLight position={[-8, 9, -12]} intensity={0.85} color="#FFE3A8" />

      {/* Warm Glowing Sun Orb in Upper Left Sky */}
      <group position={[-11, 11.5, -26]}>
        <mesh>
          <sphereGeometry args={[2.3, 28, 28]} />
          <meshBasicMaterial color="#FFF3B0" />
        </mesh>
        <mesh>
          <sphereGeometry args={[3.1, 28, 28]} />
          <meshBasicMaterial color="#FFE169" transparent opacity={0.32} />
        </mesh>
      </group>

      {/* Fluffy 3D Volumetric Clouds */}
      {[
        { x: -8 + cloudDrift * 0.4, y: 9.2, z: -22, s: 1.25 },
        { x: 1.5 + cloudDrift * 0.3, y: 10.4, z: -25, s: 1.45 },
        { x: 11.0 + cloudDrift * 0.35, y: 8.8, z: -21, s: 1.15 },
        { x: 19.5 + cloudDrift * 0.3, y: 9.8, z: -24, s: 1.3 },
      ].map((c, idx) => (
        <group key={idx} position={[c.x, c.y, c.z]} scale={c.s}>
          <mesh position={[0, 0, 0]}>
            <sphereGeometry args={[1.35, 20, 20]} />
            <meshStandardMaterial color="#FFFFFF" roughness={0.9} emissive="#FFFFFF" emissiveIntensity={0.12} />
          </mesh>
          <mesh position={[-1.15, -0.2, 0.1]}>
            <sphereGeometry args={[0.98, 18, 18]} />
            <meshStandardMaterial color="#FFFFFF" roughness={0.9} emissive="#FFFFFF" emissiveIntensity={0.12} />
          </mesh>
          <mesh position={[1.15, -0.18, 0.1]}>
            <sphereGeometry args={[1.05, 18, 18]} />
            <meshStandardMaterial color="#FFFFFF" roughness={0.9} emissive="#FFFFFF" emissiveIntensity={0.12} />
          </mesh>
        </group>
      ))}

      {/* Main Sunny Meadow Ground Plane */}
      <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[6, 0, 0]}>
        <planeGeometry args={[90, 60]} />
        <meshStandardMaterial color={BENNY_PALETTE.grass} roughness={0.88} />
      </mesh>

      {/* Soft Lighter Grass Rolling Path Strip where the Ball Rolls */}
      <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[6, 0.01, 0.1]}>
        <planeGeometry args={[36, 2.2]} />
        <meshStandardMaterial color={BENNY_PALETTE.grassLight} roughness={0.85} />
      </mesh>

      {/* Distant Rolling Pastel Background Hills & Storybook Trees */}
      <mesh receiveShadow position={[-7, -2.6, -15]} scale={[2.6, 1.1, 1.4]}>
        <sphereGeometry args={[5.5, 32, 24]} />
        <meshStandardMaterial color="#8CE268" roughness={0.88} />
      </mesh>
      <mesh receiveShadow position={[7, -3.0, -17]} scale={[3.0, 1.25, 1.5]}>
        <sphereGeometry args={[6.0, 32, 24]} />
        <meshStandardMaterial color="#72CC50" roughness={0.88} />
      </mesh>
      <mesh receiveShadow position={[21, -2.8, -15]} scale={[2.5, 1.15, 1.4]}>
        <sphereGeometry args={[5.5, 32, 24]} />
        <meshStandardMaterial color="#85DC60" roughness={0.88} />
      </mesh>

      {/* Rounded 3D Storybook Puff Trees on Background Hills */}
      {[
        { x: -6.5, y: 1.2, z: -9.5, s: 1.1 },
        { x: -1.8, y: 1.3, z: -10.5, s: 1.25 },
        { x: 4.2, y: 1.1, z: -9.8, s: 1.0 },
        { x: 9.8, y: 1.25, z: -10.2, s: 1.2 },
        { x: 16.5, y: 1.5, z: -9.2, s: 1.15 },
      ].map((t, i) => (
        <group key={i} position={[t.x, t.y, t.z]} scale={t.s}>
          <mesh castShadow receiveShadow position={[0, -0.4, 0]}>
            <cylinderGeometry args={[0.22, 0.3, 1.4, 14]} />
            <meshStandardMaterial color={BENNY_PALETTE.woodWarm} roughness={0.85} />
          </mesh>
          <mesh castShadow receiveShadow position={[0, 0.75, 0]}>
            <sphereGeometry args={[1.05, 24, 20]} />
            <meshStandardMaterial color="#58B847" roughness={0.82} />
          </mesh>
          <mesh castShadow receiveShadow position={[-0.6, 0.45, 0.2]}>
            <sphereGeometry args={[0.72, 20, 18]} />
            <meshStandardMaterial color="#6ED15A" roughness={0.82} />
          </mesh>
          <mesh castShadow receiveShadow position={[0.62, 0.5, 0.15]}>
            <sphereGeometry args={[0.76, 20, 18]} />
            <meshStandardMaterial color="#4DA83C" roughness={0.82} />
          </mesh>
        </group>
      ))}

      {/* ---------------- THE BIG FLUFFY 3D HILL (Right Side Stopper) ---------------- */}
      <group position={[hillX, 0, 0]}>
        {/* Main Plush Rounded Mound */}
        <mesh castShadow receiveShadow position={[1.4, -0.85, 0]} scale={[1.65, 1.15, 1.55]}>
          <sphereGeometry args={[2.2, 36, 28]} />
          <meshStandardMaterial color="#68C747" roughness={0.82} />
        </mesh>
        {/* Secondary Soft Top Pillow Mound */}
        <mesh castShadow receiveShadow position={[2.2, 0.45, -0.3]} scale={[1.35, 0.95, 1.25]}>
          <sphereGeometry args={[1.65, 32, 24]} />
          <meshStandardMaterial color="#82E05E" roughness={0.8} />
        </mesh>
        {/* Cozy Flowers on the Fluffy Hill */}
        {[
          [0.2, 1.15, 0.6, "#FFD166"],
          [0.95, 1.52, 0.35, "#FFB5C8"],
          [1.65, 1.72, 0.5, "#FFFFFF"],
        ].map(([fx, fy, fz, fc], idx) => (
          <group key={idx} position={[Number(fx), Number(fy), Number(fz)]}>
            <mesh>
              <sphereGeometry args={[0.09, 12, 12]} />
              <meshStandardMaterial color={String(fc)} roughness={0.5} />
            </mesh>
            <mesh position={[0, 0.05, 0]}>
              <sphereGeometry args={[0.045, 10, 10]} />
              <meshStandardMaterial color="#FF9F1C" roughness={0.4} />
            </mesh>
          </group>
        ))}
      </group>

      {/* ---------------- 3D WILDFLOWERS & GRASS TUFTS (Where Baby Bunnies Pop Out!) ---------------- */}
      {flowers.map((f, i) => (
        <group key={i} position={[f.x, 0, f.z]} scale={f.s}>
          <mesh position={[0, 0.14, 0]}>
            <cylinderGeometry args={[0.025, 0.03, 0.28, 8]} />
            <meshStandardMaterial color="#4CA634" roughness={0.8} />
          </mesh>
          {[0, 1, 2, 3, 4].map((p) => {
            const a = (p * Math.PI * 2) / 5;
            return (
              <mesh key={p} position={[Math.cos(a) * 0.09, 0.28, Math.sin(a) * 0.09]} scale={[1, 0.55, 1]}>
                <sphereGeometry args={[0.065, 12, 10]} />
                <meshStandardMaterial color={f.color} roughness={0.5} />
              </mesh>
            );
          })}
          <mesh position={[0, 0.3, 0]}>
            <sphereGeometry args={[0.055, 12, 12]} />
            <meshStandardMaterial color="#FF9F1C" roughness={0.4} />
          </mesh>
        </group>
      ))}

      {grassClusters.map(([gx, gz], i) => (
        <group key={i} position={[gx, 0, gz]}>
          <mesh castShadow receiveShadow position={[0, 0.18, 0]} scale={[1.3, 0.9, 0.9]}>
            <sphereGeometry args={[0.28, 16, 14]} />
            <meshStandardMaterial color="#5CC23C" roughness={0.82} />
          </mesh>
          <mesh castShadow receiveShadow position={[-0.22, 0.14, 0.08]} scale={[1.1, 0.8, 0.85]}>
            <sphereGeometry args={[0.22, 14, 12]} />
            <meshStandardMaterial color="#6FD44E" roughness={0.82} />
          </mesh>
          <mesh castShadow receiveShadow position={[0.22, 0.15, -0.05]} scale={[1.1, 0.85, 0.85]}>
            <sphereGeometry args={[0.23, 14, 12]} />
            <meshStandardMaterial color="#4FB032" roughness={0.82} />
          </mesh>
        </group>
      ))}
    </group>
  );
};

// ---------------------------------------------------------------------------
// Post-Processing Rig with Draft vs. Final Preset Support
// ---------------------------------------------------------------------------
export const PostProcessRig: React.FC<{ preset?: RenderPreset }> = ({ preset = "final" }) => {
  const multisampling = preset === "draft" ? 2 : 4;
  return (
    <EffectComposer multisampling={multisampling}>
      <Bloom intensity={0.22} luminanceThreshold={0.85} luminanceSmoothing={0.4} mipmapBlur />
      <Vignette eskil={false} offset={0.18} darkness={0.28} />
    </EffectComposer>
  );
};

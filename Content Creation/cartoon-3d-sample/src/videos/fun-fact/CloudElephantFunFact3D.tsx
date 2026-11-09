import React, { useMemo } from "react";
import * as THREE from "three";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import {
  BENNY_PALETTE,
  Bunny3D,
  BunnyPose,
  MeadowWorld3D,
  PostProcessRig,
  RenderPreset,
  clamp01,
  smoothstep,
  lerp,
} from "../../shared/benny3d";

export const FUN_FACT_FRAMES = 1080; // 36.0s @ 30fps

const VOICE_WINDOWS: Array<[number, number]> = [
  [0.35, 4.3],
  [4.75, 9.55],
  [10.15, 14.56],
  [15.15, 21.02],
  [21.65, 27.03],
  [27.6, 32.12],
  [32.55, 35.5],
];

function isVoiceActive(t: number): boolean {
  return VOICE_WINDOWS.some(([s, e]) => t >= s && t <= e);
}

const CameraRig: React.FC<{
  pos: [number, number, number];
  lookAt: [number, number, number];
  fov?: number;
}> = ({ pos, lookAt, fov = 40 }) => {
  const camera = useThree((s) => s.camera as THREE.PerspectiveCamera);
  camera.position.set(pos[0], pos[1], pos[2]);
  camera.lookAt(lookAt[0], lookAt[1], lookAt[2]);
  if (camera.fov !== fov) {
    camera.fov = fov;
    camera.updateProjectionMatrix();
  }
  return null;
};

// ---------------------------------------------------------------------------
// 1. Adorable Chubby 3D Cartoon Elephant ("100 Elephants!")
// ---------------------------------------------------------------------------
const CartoonElephant3D: React.FC<{
  position: [number, number, number];
  rotationY?: number;
  scale?: number;
  phase?: number;
  trumpet?: boolean;
}> = ({ position, rotationY = 0, scale = 1.0, phase = 0, trumpet = false }) => {
  const earFlap = Math.sin(phase * 4.2) * 0.14;
  const trunkLift = trumpet ? 0.65 + Math.sin(phase * 8) * 0.15 : 0.15 + Math.sin(phase * 3) * 0.12;
  const bounceY = Math.abs(Math.sin(phase * 3.5)) * 0.08;

  const slateBlue = "#7596B8";
  const slateLight = "#A9C6E2";

  return (
    <group position={[position[0], position[1] + bounceY, position[2]]} rotation={[0, rotationY, 0]} scale={scale}>
      {/* 4 Stubby 3D Elephant Legs with White Toenails */}
      {[
        [-0.38, 0.28, 0.28],
        [0.38, 0.28, 0.28],
        [-0.38, 0.28, -0.28],
        [0.38, 0.28, -0.28],
      ].map(([lx, ly, lz], i) => (
        <group key={i} position={[lx, ly, lz]}>
          <mesh castShadow receiveShadow>
            <cylinderGeometry args={[0.19, 0.22, 0.56, 20]} />
            <meshStandardMaterial color={slateBlue} roughness={0.68} />
          </mesh>
          {/* Cute 3D Toenails on front feet */}
          {[-0.08, 0, 0.08].map((nx, k) => (
            <mesh key={k} position={[nx, -0.24, 0.19]} scale={[1, 0.8, 0.6]}>
              <sphereGeometry args={[0.045, 10, 10]} />
              <meshStandardMaterial color="#FFFDF9" roughness={0.4} />
            </mesh>
          ))}
        </group>
      ))}

      {/* Plump Rounded 3D Elephant Torso */}
      <mesh castShadow receiveShadow position={[0, 0.86, 0]} scale={[1.18, 0.98, 1.08]}>
        <sphereGeometry args={[0.68, 32, 28]} />
        <meshStandardMaterial color={slateBlue} roughness={0.65} />
      </mesh>
      {/* Soft Pastel Belly Patch */}
      <mesh position={[0, 0.8, 0.24]} scale={[0.88, 0.78, 0.72]}>
        <sphereGeometry args={[0.58, 24, 20]} />
        <meshStandardMaterial color={slateLight} roughness={0.68} />
      </mesh>

      {/* Sculpted 3D Elephant Head */}
      <group position={[0, 1.56, 0.28]} rotation={[-trunkLift * 0.18, 0, Math.sin(phase * 2) * 0.06]}>
        <mesh castShadow receiveShadow scale={[1.08, 0.98, 0.96]}>
          <sphereGeometry args={[0.54, 32, 28]} />
          <meshStandardMaterial color={slateBlue} roughness={0.64} />
        </mesh>

        {/* Big Floppy 3D Left Ear with Pink Inner Ear */}
        <group position={[-0.48, 0.04, -0.05]} rotation={[0, -0.25 - earFlap, 0.12]}>
          <mesh castShadow position={[-0.22, 0, 0]} scale={[0.95, 1.25, 0.28]}>
            <sphereGeometry args={[0.38, 24, 20]} />
            <meshStandardMaterial color={slateBlue} roughness={0.65} />
          </mesh>
          <mesh position={[-0.2, -0.02, 0.06]} scale={[0.72, 0.98, 0.2]}>
            <sphereGeometry args={[0.34, 20, 16]} />
            <meshStandardMaterial color={BENNY_PALETTE.earPink} roughness={0.62} />
          </mesh>
        </group>

        {/* Big Floppy 3D Right Ear with Pink Inner Ear */}
        <group position={[0.48, 0.04, -0.05]} rotation={[0, 0.25 + earFlap, -0.12]}>
          <mesh castShadow position={[0.22, 0, 0]} scale={[0.95, 1.25, 0.28]}>
            <sphereGeometry args={[0.38, 24, 20]} />
            <meshStandardMaterial color={slateBlue} roughness={0.65} />
          </mesh>
          <mesh position={[0.2, -0.02, 0.06]} scale={[0.72, 0.98, 0.2]}>
            <sphereGeometry args={[0.34, 20, 16]} />
            <meshStandardMaterial color={BENNY_PALETTE.earPink} roughness={0.62} />
          </mesh>
        </group>

        {/* Rosy Cheeks */}
        <mesh position={[-0.34, -0.12, 0.38]} scale={[1.1, 0.75, 0.35]}>
          <sphereGeometry args={[0.1, 14, 14]} />
          <meshStandardMaterial color={BENNY_PALETTE.earPink} roughness={0.6} />
        </mesh>
        <mesh position={[0.34, -0.12, 0.38]} scale={[1.1, 0.75, 0.35]}>
          <sphereGeometry args={[0.1, 14, 14]} />
          <meshStandardMaterial color={BENNY_PALETTE.earPink} roughness={0.6} />
        </mesh>

        {/* Big Shiny 3D Eyes with Dual Catchlights */}
        {[-0.2, 0.2].map((ex, idx) => (
          <group key={idx} position={[ex, 0.1, 0.45]}>
            <mesh scale={[1.05, 1.12, 0.65]}>
              <sphereGeometry args={[0.12, 20, 20]} />
              <meshStandardMaterial color="#ffffff" roughness={0.2} />
            </mesh>
            <mesh position={[0, 0, 0.03]} scale={[0.92, 1.0, 0.65]}>
              <sphereGeometry args={[0.1, 20, 20]} />
              <meshPhysicalMaterial color={BENNY_PALETTE.eyeDark} roughness={0.08} clearcoat={1.0} />
            </mesh>
            <mesh position={[-0.028, 0.035, 0.09]}>
              <sphereGeometry args={[0.03, 12, 12]} />
              <meshBasicMaterial color="#ffffff" />
            </mesh>
          </group>
        ))}

        {/* Cute White 3D Ivory Tusks */}
        <mesh position={[-0.18, -0.18, 0.48]} rotation={[0.55, 0, -0.2]}>
          <coneGeometry args={[0.055, 0.22, 14]} />
          <meshStandardMaterial color="#FFFDF5" roughness={0.3} />
        </mesh>
        <mesh position={[0.18, -0.18, 0.48]} rotation={[0.55, 0, 0.2]}>
          <coneGeometry args={[0.055, 0.22, 14]} />
          <meshStandardMaterial color="#FFFDF5" roughness={0.3} />
        </mesh>

        {/* Articulated 3D Curling Elephant Trunk */}
        <group position={[0, -0.06, 0.48]} rotation={[-trunkLift, 0, 0]}>
          <mesh castShadow position={[0, -0.12, 0.08]} rotation={[0.35, 0, 0]}>
            <capsuleGeometry args={[0.13, 0.22, 12, 16]} />
            <meshStandardMaterial color={slateBlue} roughness={0.65} />
          </mesh>
          <mesh castShadow position={[0, -0.28, 0.22]} rotation={[0.85, 0, 0]}>
            <capsuleGeometry args={[0.11, 0.2, 12, 16]} />
            <meshStandardMaterial color={slateBlue} roughness={0.65} />
          </mesh>
          <mesh castShadow position={[0, -0.32, 0.4]} rotation={[1.55, 0, 0]}>
            <capsuleGeometry args={[0.095, 0.16, 12, 16]} />
            <meshStandardMaterial color={slateBlue} roughness={0.65} />
          </mesh>
        </group>

        {/* Cute Little Yellow Party/Crown Hat on Top */}
        <mesh castShadow position={[0, 0.56, 0.05]}>
          <coneGeometry args={[0.16, 0.28, 16]} />
          <meshStandardMaterial color="#FFD166" roughness={0.45} />
        </mesh>
      </group>
    </group>
  );
};

// ---------------------------------------------------------------------------
// 2. Hero 3D Smiling Fluffy Cloud + Microscopic Water Droplets + Updrafts
// ---------------------------------------------------------------------------
const HeroCloud3D: React.FC<{
  position: [number, number, number];
  scale?: number;
  phase?: number;
  showDropletsInside?: boolean;
  showUpdrafts?: boolean;
  showRain?: boolean;
}> = ({
  position,
  scale = 1.0,
  phase = 0,
  showDropletsInside = false,
  showUpdrafts = false,
  showRain = false,
}) => {
  const cloudOpacity = showDropletsInside ? 0.36 : 1.0;

  const droplets = useMemo(() => {
    const arr: Array<{ x: number; y: number; z: number; s: number; speed: number }> = [];
    for (let i = 0; i < 42; i++) {
      const a = i * 2.39996;
      const r = 0.25 + (i % 7) * 0.24;
      arr.push({
        x: Math.cos(a) * r * 1.35,
        y: ((i % 5) - 2) * 0.24,
        z: Math.sin(a) * r * 0.55,
        s: 0.075 + (i % 3) * 0.022,
        speed: 1.5 + (i % 4) * 0.45,
      });
    }
    return arr;
  }, []);

  return (
    <group position={position} scale={scale}>
      {/* Sculpted Volumetric 3D Cumulus Cloud Puffs */}
      {[
        [0, 0.12, 0, 1.05],
        [-0.95, -0.05, 0.08, 0.82],
        [0.95, -0.04, 0.08, 0.85],
        [-0.48, 0.48, 0.05, 0.78],
        [0.52, 0.45, 0.05, 0.76],
        [-1.52, -0.22, 0.0, 0.58],
        [1.52, -0.2, 0.0, 0.6],
      ].map(([cx, cy, cz, cr], idx) => (
        <mesh key={idx} castShadow receiveShadow position={[cx, cy, cz]}>
          <sphereGeometry args={[cr, 28, 24]} />
          <meshStandardMaterial
            color="#FFFFFF"
            roughness={0.75}
            emissive="#E8F7FF"
            emissiveIntensity={0.22}
            transparent={showDropletsInside}
            opacity={showDropletsInside ? 0.26 : 1.0}
            depthWrite={!showDropletsInside}
          />
        </mesh>
      ))}

      {/* Cute 3D Face on the Front of the Fluffy Cloud */}
      <group position={[0, 0.08, 1.04]}>
        {/* Left & Right Sparkly Eyes */}
        {[-0.32, 0.32].map((ex, i) => (
          <group key={i} position={[ex, 0.08, 0]}>
            <mesh>
              <sphereGeometry args={[0.1, 18, 18]} />
              <meshPhysicalMaterial color={BENNY_PALETTE.eyeDark} roughness={0.08} clearcoat={1.0} />
            </mesh>
            <mesh position={[-0.025, 0.03, 0.085]}>
              <sphereGeometry args={[0.028, 10, 10]} />
              <meshBasicMaterial color="#ffffff" />
            </mesh>
          </group>
        ))}
        {/* Rosy Pink Cloud Cheeks */}
        <mesh position={[-0.5, -0.06, -0.04]} scale={[1.2, 0.75, 0.4]}>
          <sphereGeometry args={[0.11, 14, 14]} />
          <meshStandardMaterial color={BENNY_PALETTE.earPink} roughness={0.6} />
        </mesh>
        <mesh position={[0.5, -0.06, -0.04]} scale={[1.2, 0.75, 0.4]}>
          <sphereGeometry args={[0.11, 14, 14]} />
          <meshStandardMaterial color={BENNY_PALETTE.earPink} roughness={0.6} />
        </mesh>
        {/* Happy Smile Arc */}
        <mesh position={[0, -0.08, 0.02]} rotation={[0, 0, Math.PI]}>
          <torusGeometry args={[0.12, 0.024, 10, 24, Math.PI]} />
          <meshBasicMaterial color={BENNY_PALETTE.eyeDark} />
        </mesh>
      </group>

      {/* Billions of Tiny Glowing 3D Water Droplets Inside the Cloud (Shots 4 & 5) */}
      {showDropletsInside && (
        <group position={[0, 0.05, 0.45]}>
          {droplets.map((d, i) => {
            const bobY = Math.sin(phase * d.speed + i) * 0.14;
            return (
              <mesh key={i} position={[d.x, d.y + bobY, d.z]}>
                <sphereGeometry args={[d.s, 14, 14]} />
                <meshPhysicalMaterial
                  color="#38BDF8"
                  emissive="#0EA5E9"
                  emissiveIntensity={0.55}
                  roughness={0.1}
                  clearcoat={1.0}
                />
              </mesh>
            );
          })}
        </group>
      )}

      {/* Rising Golden Warm-Air Updraft Columns Pushing the Cloud Up (Shot 5) */}
      {showUpdrafts && (
        <group position={[0, -1.65, 0]}>
          {[-1.0, -0.35, 0.35, 1.0].map((ux, idx) => {
            const lift = ((phase * 0.85 + idx * 0.25) % 1) * 1.25;
            const alpha = Math.sin(((phase * 0.85 + idx * 0.25) % 1) * Math.PI);
            return (
              <group key={idx} position={[ux, lift, 0.2]}>
                {/* Upward Warm Air Shaft */}
                <mesh position={[0, -0.25, 0]}>
                  <cylinderGeometry args={[0.045, 0.065, 0.55, 12]} />
                  <meshStandardMaterial
                    color="#FFD166"
                    emissive="#FF9F1C"
                    emissiveIntensity={0.45}
                    transparent
                    opacity={0.75 * alpha}
                  />
                </mesh>
                {/* Upward Arrow Cone Tip */}
                <mesh position={[0, 0.1, 0]}>
                  <coneGeometry args={[0.14, 0.26, 14]} />
                  <meshStandardMaterial
                    color="#FFD166"
                    emissive="#FF9F1C"
                    emissiveIntensity={0.5}
                    transparent
                    opacity={0.85 * alpha}
                  />
                </mesh>
              </group>
            );
          })}
        </group>
      )}

      {/* Gentle Sparkling Raindrops in Shot 6 */}
      {showRain && (
        <group position={[0, -0.7, 0]}>
          {Array.from({ length: 18 }).map((_, i) => {
            const rx = ((i % 6) - 2.5) * 0.48;
            const rz = (Math.floor(i / 6) - 1) * 0.25;
            const fall = ((phase * 1.8 + i * 0.19) % 1) * 1.8;
            return (
              <mesh key={i} position={[rx, -fall, rz]} scale={[0.7, 1.6, 0.7]}>
                <sphereGeometry args={[0.055, 10, 10]} />
                <meshStandardMaterial color="#38BDF8" emissive="#7DD3FC" emissiveIntensity={0.4} />
              </mesh>
            );
          })}
        </group>
      )}
    </group>
  );
};

// ---------------------------------------------------------------------------
// 3. Vibrant 6-Band 3D Rainbow Arch (Shots 6 & 7 Payoff)
// ---------------------------------------------------------------------------
const RainbowArch3D: React.FC<{ progress: number }> = ({ progress }) => {
  if (progress <= 0.01) return null;
  const bands = [
    { color: "#FF595E", r: 6.4 },
    { color: "#FF924C", r: 6.12 },
    { color: "#FFCA3A", r: 5.84 },
    { color: "#8AC926", r: 5.56 },
    { color: "#1982C4", r: 5.28 },
    { color: "#6A4C93", r: 5.0 },
  ];
  const arcAngle = Math.PI * clamp01(progress);

  return (
    <group position={[0, -0.2, -5.5]}>
      {bands.map((b, i) => (
        <mesh key={i}>
          <torusGeometry args={[b.r, 0.15, 16, 64, arcAngle]} />
          <meshStandardMaterial
            color={b.color}
            emissive={b.color}
            emissiveIntensity={0.35}
            roughness={0.35}
          />
        </mesh>
      ))}
    </group>
  );
};

// ---------------------------------------------------------------------------
// Main Composition: CloudElephantFunFact3D (36.0s, 1080 frames @ 30fps)
// ---------------------------------------------------------------------------
export const CloudElephantFunFact3D: React.FC<{ preset?: RenderPreset }> = ({ preset = "final" }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;

  // 1. Hero Fluffy Cloud Position & State
  let cloudPos: [number, number, number] = [0.2, 3.15, -0.5];
  let cloudScale = 1.05;
  const showDropletsInside = t >= 15.0 && t < 27.5;
  const showUpdrafts = t >= 21.4 && t < 27.5;
  const showRain = t >= 27.5 && t < 31.2;

  if (t < 4.5) {
    // Shot 1: Floating happily above Benny in the sunny sky
    cloudPos = [0.4, 3.05 + Math.sin(t * 2.5) * 0.12, -0.4];
  } else if (t < 10.0) {
    // Shot 2: On the left side of the giant balance comparison opposite the 3D Elephant!
    cloudPos = [-1.95, 2.35 + Math.sin(t * 2.2) * 0.1, -0.2];
    cloudScale = 0.92;
  } else if (t < 15.0) {
    // Shot 3: Hovering right over Benny's head as he looks up in shock!
    cloudPos = [0.0, 3.1 + Math.sin(t * 3.0) * 0.1, -0.2];
    cloudScale = 1.1;
  } else if (t < 27.5) {
    // Shots 4 & 5: Center stage for microscopic droplets & rising warm air updrafts (clear above ears)
    cloudPos = [0.25, 3.12 + Math.sin(t * 2.2) * 0.08, 0.0];
    cloudScale = 1.12;
  } else {
    // Shots 6 & 7: Rains gently and frames the glowing rainbow finale
    cloudPos = [-2.2, 3.25 + Math.sin(t * 2.0) * 0.1, -1.2];
    cloudScale = 0.95;
  }

  // 2. Chubby 3D Cartoon Elephant State (Drops in at 3.2s for the 100-Elephant reveal!)
  const showElephant = (t >= 3.15 && t < 14.8) || t >= 27.5;
  let elephantPos: [number, number, number] = [1.85, 0, -0.2];
  let elephantRotY = -0.35;
  let elephantScale = 1.0;

  if (t >= 3.15 && t < 10.0) {
    const dropU = smoothstep(3.15, 3.65, t);
    const dropY = (1 - dropU) * 3.5;
    elephantPos = [1.75, dropY, -0.15];
    elephantRotY = -0.35;
  } else if (t >= 10.0 && t < 14.8) {
    elephantPos = [2.25, 0, -0.4];
    elephantRotY = -0.45;
  } else if (t >= 27.5) {
    elephantPos = [2.15, 0, -0.35];
    elephantRotY = -0.25;
  }

  // 3. Benny the Bunny & Baby Bunnies Blocking
  let bennyPos: [number, number, number] = [-1.45, 0, 0.2];
  let bennyRotY = 0.25;
  let bennyPose: BunnyPose = "hook";

  if (t < 4.5) {
    bennyPos = [-1.35, 0, 0.2];
    bennyPose = "hook";
    bennyRotY = 0.22;
  } else if (t < 10.0) {
    // Watching the Cloud vs. Elephant comparison in amazement
    bennyPos = [-0.15, 0, 0.45];
    bennyPose = "cheer";
    bennyRotY = 0.05;
  } else if (t < 15.0) {
    // Shot 3: "Why doesn't it crash right onto my head?!" -> Shrug / surprised!
    bennyPos = [-0.65, 0, 0.3];
    bennyPose = "shrug";
    bennyRotY = 0.18;
  } else if (t < 21.5) {
    // Shot 4: Looking closely at the glowing microscopic water droplets
    bennyPos = [-2.1, 0, 0.2];
    bennyPose = "encourage";
    bennyRotY = 0.42;
  } else if (t < 27.5) {
    // Shot 5: Sweeping arms upward with the warm rising air updrafts!
    bennyPos = [-2.1, 0, 0.2];
    bennyPose = "whoosh";
    bennyRotY = 0.35;
  } else if (t < 32.5) {
    // Shot 6: Cheering as the rainbow arches across the sky!
    bennyPos = [-1.95, 0, 0.25];
    bennyPose = "cheer";
    bennyRotY = 0.15;
  } else {
    // Shot 7: Waving goodbye with all friends under the rainbow!
    bennyPos = [-1.95, 0, 0.25];
    bennyPose = "wave";
    bennyRotY = 0.08;
  }

  // Baby Bunnies join from Shot 5 onward (21.5s - 36.0s)
  const showBabies = t >= 21.5;
  const babyConfigs = [
    { scarf: BENNY_PALETTE.scarfPink, x: -0.85, z: -0.45 },
    { scarf: BENNY_PALETTE.scarfMint, x: -0.05, z: -0.55 },
    { scarf: BENNY_PALETTE.scarfLilac, x: 0.75, z: -0.45 },
  ];

  // 4. 7-Shot Camera Choreography
  let camPos: [number, number, number] = [0.0, 1.85, 6.2];
  let camLook: [number, number, number] = [0.0, 1.65, 0.0];
  let camFov = 42;

  if (t < 4.5) {
    // Shot 1: Medium-wide framing Benny on the meadow and the smiling Cloud overhead
    const u = t / 4.5;
    camPos = [lerp(-0.4, 0.1, u), 1.85, lerp(5.8, 6.3, u)];
    camLook = [0.0, 1.65, 0.0];
    camFov = 42;
  } else if (t < 10.0) {
    // Shot 2: Wide comparison framing Cloud (left), Benny (center), and 3D Elephant (right)
    const u = (t - 4.5) / 5.5;
    camPos = [0.0, 1.75, lerp(6.6, 6.2, u)];
    camLook = [0.0, 1.35, 0.0];
    camFov = 43;
  } else if (t < 15.0) {
    // Shot 3: Low-angle looking up at Benny & the Giant Cloud right above his head
    camPos = [-0.25, 1.45, 5.45];
    camLook = [-0.2, 1.68, 0.0];
    camFov = 41;
  } else if (t < 21.5) {
    // Shot 4: Closer push-in on the translucent Cloud showing billions of glowing 3D water droplets
    const u = (t - 15.0) / 6.5;
    camPos = [-0.35, lerp(2.1, 2.35, u), lerp(5.2, 4.45, u)];
    camLook = [-0.15, 2.35, 0.0];
    camFov = 39;
  } else if (t < 27.5) {
    // Shot 5: Medium-wide showing the Golden Warm-Air Updraft arrows rising from the meadow into the Cloud
    camPos = [-0.2, 1.85, 5.85];
    camLook = [-0.2, 1.65, 0.0];
    camFov = 42;
  } else if (t < 32.5) {
    // Shot 6: Wide celebratory shot as rain falls and the 3D Rainbow Arch blooms across the sky
    const u = smoothstep(27.5, 31.5, t);
    camPos = [0.0, lerp(1.85, 2.15, u), lerp(6.4, 7.2, u)];
    camLook = [0.0, 1.75, -0.5];
    camFov = 44;
  } else {
    // Shot 7: Final warm postcard shot with Benny, 3 Baby Bunnies, Elephant, Cloud & Rainbow
    const u = smoothstep(32.5, 36.0, t);
    camPos = [0.0, 2.05, lerp(6.8, 7.3, u)];
    camLook = [0.0, 1.65, -0.4];
    camFov = 43;
  }

  const rainbowProgress = smoothstep(28.0, 30.8, t);
  const talking = isVoiceActive(t);
  const blink = (t % 4.2) > 4.05;

  return (
    <AbsoluteFill style={{ backgroundColor: "#8FD3FF" }}>
      <ThreeCanvas shadows width={width} height={height}>
        <CameraRig pos={camPos} lookAt={camLook} fov={camFov} />

        {/* 3D Storybook Meadow World */}
        <MeadowWorld3D cloudDrift={t * 0.25} hillX={18.5} preset={preset} />

        {/* Vibrant 3D Rainbow Arch in Shots 6 & 7 */}
        <RainbowArch3D progress={rainbowProgress} />

        {/* The Giant Smiling 3D Cumulus Cloud + Water Droplets + Updrafts */}
        <HeroCloud3D
          position={cloudPos}
          scale={cloudScale}
          phase={t}
          showDropletsInside={showDropletsInside}
          showUpdrafts={showUpdrafts}
          showRain={showRain}
        />

        {/* Chubby 3D Cartoon Elephant ("100 Elephants!") */}
        {showElephant && (
          <CartoonElephant3D
            position={elephantPos}
            rotationY={elephantRotY}
            scale={elephantScale}
            phase={t}
            trumpet={t >= 4.8 && t <= 6.5}
          />
        )}

        {/* Benny the Bunny */}
        <Bunny3D
          position={bennyPos}
          rotationY={bennyRotY}
          scale={0.9}
          scarfColor={BENNY_PALETTE.scarfYellow}
          pose={bennyPose}
          phase={t}
          talking={talking}
          talkEnergy={0.65}
          blink={blink}
        />

        {/* Three Baby Bunnies (Pink, Mint, Lilac scarves) */}
        {showBabies &&
          babyConfigs.map((b, idx) => (
            <Bunny3D
              key={idx}
              position={[b.x, 0, b.z]}
              rotationY={0.1}
              scale={0.56}
              scarfColor={b.scarf}
              pose={t >= 32.5 ? "wave" : "cheer"}
              phase={t + idx * 0.35}
              talking={talking && t >= 32.5}
              talkEnergy={0.55}
              blink={blink}
            />
          ))}

        <PostProcessRig preset={preset} />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};

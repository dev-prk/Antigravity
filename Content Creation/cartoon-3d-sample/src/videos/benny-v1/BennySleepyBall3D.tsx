import React from "react";
import * as THREE from "three";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import {
  BENNY_PALETTE,
  Bunny3D,
  BunnyPose,
  RedBall3D,
  Butterfly3D,
  MeadowWorld3D,
  PostProcessRig,
  RenderPreset,
  clamp01,
  smoothstep,
  lerp,
} from "../../shared/benny3d";

export const BENNY_V1_FRAMES = 1200; // 40.0s @ 30fps

// Voice active windows (synced with scripts/build-benny-v1-audio.mjs)
const VOICE_WINDOWS: Array<[number, number]> = [
  [0.85, 2.15],   // Shot 1: "Can YOU make the ball move?"
  [3.05, 6.85],   // Shot 2: Song lines 1-2
  [7.0, 8.04],    // Shot 3: "The ball is sleeping." (followed by 8.05-10.05s silent pause)
  [10.15, 12.55], // Shot 4: "Let's push! Ready? Say push!"
  [14.1, 17.95],  // Shot 5: "Whoosh! Now it's rolling!" + Song lines 3-4
  [18.35, 21.45], // Shot 6: Baby Bunnies cheer
  [22.1, 27.4],   // Shot 7: Chorus 1
  [28.15, 31.6],  // Shot 8: Fluffy hill stop
  [32.15, 36.5],  // Shot 9: Chorus 2 repeat
  [37.05, 39.55], // Shot 10: "Bye-bye, friends! Hop, hop, hooray!"
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

export const BennySleepyBall3D: React.FC<{ preset?: RenderPreset }> = ({ preset = "final" }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;

  // -------------------------------------------------------------------------
  // 1. RED BALL PHYSICS & STATE (1st Law: Stays still until pushed at 14.0s,
  //    then rolls until stopped by the Big Fluffy Hill at 29.6s)
  // -------------------------------------------------------------------------
  let ballX = 0.0;
  let ballY = 0.0;
  let ballZ = 0.0;
  let ballRoll = 0.0;
  let ballSquash = 0.0;
  let ballSleeping = true;
  let showZzz = false;

  if (t < 3.0) {
    // Shot 1 (0:00-0:03): Ball zooms in from left foreground and freezes at x=0
    const zProgress = smoothstep(0.05, 0.78, t);
    ballX = lerp(-4.2, 0.0, zProgress);
    ballZ = lerp(1.6, 0.0, zProgress);
    ballRoll = (ballX + 4.2) / 0.52;
    ballSleeping = t >= 0.82;
    if (t >= 0.74 && t <= 0.95) {
      ballSquash = Math.sin(((t - 0.74) / 0.21) * Math.PI) * 0.65;
    }
  } else if (t < 14.08) {
    // Shots 2, 3, 4 (0:03-0:14): Ball sits completely still on the grass!
    ballX = 0.0;
    ballY = 0.0;
    ballZ = 0.0;
    ballRoll = 8.07; // frozen angle with white star clearly visible
    ballSleeping = true;
    showZzz = t >= 3.0 && t < 13.8;
  } else {
    // Shots 5, 6, 7, 8, 9, 10 (0:14-0:40): Kick at 14.08s -> Rolls -> Stops at Fluffy Hill (x=12.85)
    ballSleeping = false;
    showZzz = false;
    if (t >= 14.05 && t <= 14.32) {
      ballSquash = Math.sin(((t - 14.05) / 0.27) * Math.PI) * 0.85;
    }
    if (t < 28.0) {
      // Steady rolling across the sunny meadow from x=0 to x=11.4
      const u = clamp01((t - 14.08) / (28.0 - 14.08));
      // Fast initial kick impulse easing into steady constant velocity
      const dist = Math.pow(u, 0.92) * 11.4;
      ballX = dist;
    } else {
      // Shot 8 (28.0s - 29.7s): Decelerates up the soft slope of the Big Fluffy Hill and stops!
      const uStop = smoothstep(28.0, 29.65, t);
      ballX = lerp(11.4, 12.82, uStop);
      // Slight gentle climb up the base of the fluffy hill mound
      ballY = smoothstep(12.0, 12.82, ballX) * 0.26;
      if (t >= 29.4 && t <= 29.8) {
        ballSquash = Math.sin(((t - 29.4) / 0.4) * Math.PI) * 0.45;
      }
    }
    ballRoll = 8.07 + ballX / 0.52;
  }

  // -------------------------------------------------------------------------
  // 2. BUTTERFLY TRAJECTORY (Flutters in & lands on sleeping ball in Shot 2,
  //    rests peacefully through Shot 3's 2s pause, flies off on Kick in Shot 5)
  // -------------------------------------------------------------------------
  let showButterfly = t >= 2.8 && t <= 16.5;
  let bflyPos: [number, number, number] = [0, 2.5, 0];
  let bflyRotY = -0.5;
  let bflyFlap = t;

  if (t < 5.1) {
    const u = smoothstep(2.8, 5.1, t);
    bflyPos = [
      lerp(2.4, 0.04, u),
      lerp(2.6, 1.09, u) + Math.sin(t * 7) * 0.12 * (1 - u),
      lerp(1.2, 0.08, u),
    ];
    bflyRotY = -0.6;
  } else if (t < 13.95) {
    // Perched gently on top of the sleeping Red Ball! Slow peaceful wing breath
    bflyPos = [0.04, 1.09, 0.08];
    bflyRotY = -0.35;
    bflyFlap = t * 0.22;
  } else {
    // Flutters up into the sunny sky when Benny kicks the ball!
    const u = smoothstep(13.95, 16.5, t);
    bflyPos = [
      lerp(0.04, 3.5, u),
      lerp(1.09, 3.8, u) + Math.sin(t * 10) * 0.15,
      lerp(0.08, -1.5, u),
    ];
    bflyRotY = 0.65;
  }

  // -------------------------------------------------------------------------
  // 3. BENNY THE BUNNY BLOCKING & POSE across all 10 shots
  // -------------------------------------------------------------------------
  let bennyX = -1.45;
  let bennyZ = 0.12;
  let bennyRotY = 0.28;
  let bennyPose: BunnyPose = "idle";
  let bennyPhase = t;
  let kickProgress = 0;

  if (t < 3.0) {
    // Shot 1: Benny pops in at 0.75s-1.2s and asks "Can YOU make the ball move?"
    const popU = smoothstep(0.65, 1.18, t);
    bennyX = lerp(-3.1, -1.35, popU);
    bennyPose = t < 1.18 ? "hop" : "hook";
    bennyPhase = t < 1.18 ? (t - 0.65) * 2.2 : t;
    bennyRotY = 0.22;
  } else if (t < 7.0) {
    // Shot 2: Song lines 1-2 watching the sleeping ball & butterfly
    bennyX = -1.38;
    bennyPose = "idle";
    bennyRotY = 0.42;
  } else if (t < 10.05) {
    // Shot 3: "The ball is sleeping" + 2s silent pause -> Benny shrugs!
    bennyX = -1.32;
    bennyPose = "shrug";
    bennyRotY = 0.25;
  } else if (t < 13.85) {
    // Shot 4: "Let's push!" -> Benny leans in encouraging the viewer
    bennyX = -1.22;
    bennyPose = "encourage";
    bennyRotY = 0.18;
  } else if (t < 14.55) {
    // Shot 5a: Benny winds up and kicks the ball at 14.08s!
    bennyX = -0.92;
    bennyPose = "kick";
    kickProgress = clamp01((t - 13.85) / 0.65);
    bennyRotY = 0.85;
  } else if (t < 28.2) {
    // Shots 5b, 6, 7: Benny hops joyfully alongside the rolling ball!
    bennyX = ballX - 1.55;
    bennyZ = 0.15;
    bennyRotY = 0.65;
    if (t >= 23.45 && t <= 24.35) {
      bennyPose = "clap";
      bennyRotY = 0.25;
    } else if (t >= 25.35 && t <= 26.35) {
      bennyPose = "whoosh";
      bennyRotY = 0.35;
    } else {
      bennyPose = "hop";
      bennyPhase = t * 1.65;
    }
  } else if (t < 32.0) {
    // Shot 8: Ball slows & stops at the Big Fluffy Hill; Benny hops up and admires it
    const arriveU = smoothstep(28.2, 29.8, t);
    bennyX = lerp(9.85, 10.95, arriveU);
    bennyPose = t < 29.6 ? "hop" : "idle";
    bennyPhase = t < 29.6 ? t * 1.5 : t;
    bennyRotY = 0.45;
  } else if (t < 37.0) {
    // Shot 9: Chorus repeat ("Still stays still, clap clap! Rolling keeps rolling, whoosh!")
    bennyX = 10.95;
    bennyRotY = 0.12;
    if (t >= 33.5 && t <= 34.4) {
      bennyPose = "clap";
    } else if (t >= 35.4 && t <= 36.4) {
      bennyPose = "whoosh";
    } else {
      bennyPose = "cheer";
    }
  } else {
    // Shot 10 (37.0s - 40.0s): "Bye-bye, friends! Hop, hop, hooray!"
    bennyX = 10.95;
    bennyRotY = 0.05;
    bennyPose = t >= 38.15 && t <= 38.85 ? "cheer" : "wave";
  }

  // -------------------------------------------------------------------------
  // 4. THREE BABY BUNNIES (Pink, Mint, Lilac scarves - pop out in Shot 6 at 18.1s!)
  // -------------------------------------------------------------------------
  const showBabies = t >= 18.05;
  const babyConfigs = [
    { scarf: BENNY_PALETTE.scarfPink, popStart: 18.08, baseOffset: -1.1, z: -0.95 },
    { scarf: BENNY_PALETTE.scarfMint, popStart: 18.26, baseOffset: -0.15, z: -1.12 },
    { scarf: BENNY_PALETTE.scarfLilac, popStart: 18.44, baseOffset: 0.8, z: -0.95 },
  ];

  // -------------------------------------------------------------------------
  // 5. 10-SHOT CAMERA CHOREOGRAPHY (Exact framing from benny_production_pack.md)
  // -------------------------------------------------------------------------
  let camPos: [number, number, number] = [-0.6, 1.4, 4.2];
  let camLook: [number, number, number] = [-0.6, 0.9, 0.0];
  let camFov = 38;

  if (t < 3.0) {
    // Shot 1 (0:00-0:03): Close-up whip-pan with zooming ball, locking on Benny & Ball
    const panU = smoothstep(0.05, 0.85, t);
    camPos = [lerp(-2.4, -0.68, panU), 1.32, 3.65];
    camLook = [lerp(-2.8, -0.68, panU), 0.88, 0.0];
    camFov = 36;
  } else if (t < 7.0) {
    // Shot 2 (0:03-0:07): Wide meadow shot, slow push-in as butterfly lands on sleepy ball
    const u = (t - 3.0) / 4.0;
    camPos = [-0.55, lerp(1.75, 1.55, u), lerp(5.4, 4.5, u)];
    camLook = [-0.55, 0.92, 0.0];
    camFov = 40;
  } else if (t < 10.0) {
    // Shot 3 (0:07-0:10): Locked Close-Up on sleeping ball & shrugging Benny during 2s pause
    camPos = [-0.45, 1.18, 3.25];
    camLook = [-0.48, 0.78, 0.0];
    camFov = 35;
  } else if (t < 14.0) {
    // Shot 4 (0:10-0:14): Medium eye-level shot for "Let's push!" interactive pause
    const u = smoothstep(10.0, 13.8, t);
    camPos = [-0.62, 1.35, lerp(3.95, 3.65, u)];
    camLook = [-0.62, 0.9, 0.0];
    camFov = 38;
  } else if (t < 18.0) {
    // Shot 5 (0:14-0:18): Low-angle side tracking shot as Benny kicks & ball rolls!
    camPos = [ballX - 0.65, 1.15, 4.25];
    camLook = [ballX - 0.35, 0.82, 0.0];
    camFov = 40;
  } else if (t < 22.0) {
    // Shot 6 (0:18-0:22): Medium-wide surprise shot as 3 Baby Bunnies pop out of the grass!
    const u = smoothstep(18.0, 19.2, t);
    const focusX = lerp(ballX - 0.3, 6.4, 0.55);
    camPos = [focusX, 1.48 + Math.sin(u * Math.PI) * 0.12, 4.95];
    camLook = [focusX, 0.92, -0.35];
    camFov = 41;
  } else if (t < 28.0) {
    // Shot 7 (0:22-0:28): Tracking parade shot with gentle musical sway
    const swayY = Math.sin(t * 3.1) * 0.06;
    camPos = [ballX - 0.85, 1.52 + swayY, 5.15];
    camLook = [ballX - 0.65, 0.92, -0.25];
    camFov = 41;
  } else if (t < 32.0) {
    // Shot 8 (0:28-0:32): Locked side-wide shot as the Red Ball slows and stops at the Big Fluffy Hill
    camPos = [11.65, 1.62, 5.55];
    camLook = [11.85, 0.95, 0.0];
    camFov = 42;
  } else if (t < 37.0) {
    // Shot 9 (0:32-0:37): Medium group shot with slight celebratory orbit for Chorus 2
    const u = (t - 32.0) / 5.0;
    const orbitX = Math.sin((u - 0.5) * 0.55) * 0.85;
    camPos = [11.35 + orbitX, 1.48, 4.65];
    camLook = [11.35, 0.95, -0.25];
    camFov = 39;
  } else {
    // Shot 10 (0:37-0:40): Warm close-up / group farewell with slow peaceful pull-out
    const u = smoothstep(37.0, 40.0, t);
    camPos = [11.25, lerp(1.38, 1.48, u), lerp(4.05, 4.75, u)];
    camLook = [11.25, 0.95, -0.2];
    camFov = 38;
  }

  // Periodic natural eye blink
  const blink =
    (t > 2.4 && t < 2.55) ||
    (t > 6.1 && t < 6.25) ||
    (t > 9.4 && t < 9.55) ||
    (t > 13.1 && t < 13.25) ||
    (t > 20.5 && t < 20.65) ||
    (t > 26.8 && t < 26.95) ||
    (t > 31.2 && t < 31.35) ||
    (t > 36.2 && t < 36.35);

  const talking = isVoiceActive(t);

  return (
    <AbsoluteFill style={{ backgroundColor: "#8FD3FF" }}>
      <ThreeCanvas shadows width={width} height={height}>
        <CameraRig pos={camPos} lookAt={camLook} fov={camFov} />

        {/* 3D Painted Storybook Meadow, Fluffy Hill & Three-Point Lighting */}
        <MeadowWorld3D cloudDrift={t * 0.25} hillX={14.2} preset={preset} />

        {/* Benny the Bunny (True 3D Volumetric Rig) */}
        <Bunny3D
          position={[bennyX, 0, bennyZ]}
          rotationY={bennyRotY}
          scale={0.92}
          scarfColor={BENNY_PALETTE.scarfYellow}
          pose={bennyPose}
          phase={bennyPhase}
          talking={talking}
          talkEnergy={0.65}
          blink={blink}
          kickProgress={kickProgress}
        />

        {/* Three Baby Bunnies (Pink, Mint, Lilac scarves - pop out in Shot 6!) */}
        {showBabies &&
          babyConfigs.map((b, idx) => {
            const popElapsed = Math.max(0, t - b.popStart);
            const popScale = smoothstep(0, 0.28, popElapsed);
            const popBounceY =
              popElapsed < 0.45 ? Math.sin((popElapsed / 0.45) * Math.PI) * 0.65 : 0;

            let bx = 6.3 + b.baseOffset;
            let bRotY = 0.2;
            let bPose: BunnyPose = "cheer";
            let bPhase = t + idx * 0.35;

            if (t >= 22.0 && t < 28.2) {
              // Hop alongside Benny & the Red Ball in Shot 7
              bx = ballX - 0.8 + b.baseOffset * 0.85;
              bRotY = 0.55;
              if (t >= 23.45 && t <= 24.35) {
                bPose = "clap";
                bRotY = 0.15;
              } else if (t >= 25.35 && t <= 26.35) {
                bPose = "whoosh";
                bRotY = 0.25;
              } else {
                bPose = "hop";
                bPhase = t * 1.85 + idx * 0.4;
              }
            } else if (t >= 28.2 && t < 32.0) {
              const u = smoothstep(28.2, 29.8, t);
              bx = lerp(10.4 + b.baseOffset * 0.85, 11.55 + b.baseOffset * 0.78, u);
              bPose = t < 29.6 ? "hop" : "idle";
              bRotY = 0.25;
            } else if (t >= 32.0 && t < 37.0) {
              bx = 11.55 + b.baseOffset * 0.78;
              bRotY = 0.05;
              if (t >= 33.5 && t <= 34.4) bPose = "clap";
              else if (t >= 35.4 && t <= 36.4) bPose = "whoosh";
              else bPose = "cheer";
            } else if (t >= 37.0) {
              bx = 11.55 + b.baseOffset * 0.78;
              bRotY = 0.0;
              bPose = t >= 38.15 && t <= 38.85 ? "cheer" : "wave";
            }

            if (popScale <= 0.01) return null;

            return (
              <Bunny3D
                key={idx}
                position={[bx, popBounceY, b.z]}
                rotationY={bRotY}
                scale={0.58 * popScale}
                scarfColor={b.scarf}
                pose={bPose}
                phase={bPhase}
                talking={talking && t >= 18.3}
                talkEnergy={0.55}
                blink={blink}
              />
            );
          })}

        {/* The Red Ball with Raised 3D White Star & Sleeping/Awake Face */}
        <RedBall3D
          position={[ballX, ballY, ballZ]}
          rollAngle={ballRoll}
          sleeping={ballSleeping}
          showZzz={showZzz}
          zzzPhase={t}
          squash={ballSquash}
          scale={1.0}
        />

        {/* Animated 3D Butterfly */}
        {showButterfly && (
          <Butterfly3D
            position={bflyPos}
            rotationY={bflyRotY}
            flapPhase={bflyFlap}
            scale={1.15}
          />
        )}

        {/* Post-Processing Rig (supports draft vs final preset) */}
        <PostProcessRig preset={preset} />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};

import React from "react";
import { Composition } from "remotion";
import { BridgeShort, BridgeSample, BRIDGE_FRAMES, SAMPLE_FRAMES } from "./videos/bridge/Bridge";
import { SleepyBallShort, SLEEPY_BALL_FRAMES } from "./videos/sleepy-ball/SleepyBall";
import { BennySleepyBall3D, BENNY_V1_FRAMES } from "./videos/benny-v1/BennySleepyBall3D";

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="BennySleepyBall3D"
        component={BennySleepyBall3D}
        durationInFrames={BENNY_V1_FRAMES}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ preset: "final" as const }}
      />
      <Composition
        id="SleepyBall"
        component={SleepyBallShort}
        durationInFrames={SLEEPY_BALL_FRAMES}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="BridgeSample"
        component={BridgeSample}
        durationInFrames={SAMPLE_FRAMES}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="BridgeShort"
        component={BridgeShort}
        durationInFrames={BRIDGE_FRAMES}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};

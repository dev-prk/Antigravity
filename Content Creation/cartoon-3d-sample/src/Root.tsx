import React from "react";
import { Composition } from "remotion";
import { BridgeShort, BridgeSample, BRIDGE_FRAMES, SAMPLE_FRAMES } from "./videos/bridge/Bridge";

export const Root: React.FC = () => {
  return (
    <>
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

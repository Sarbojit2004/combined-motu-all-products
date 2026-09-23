import React from "react";
import { Composition } from "remotion";
import { REEL, VIDEO } from "./theme.ts";
import { REEL_PLAN, VIDEO_PLAN } from "./plan.ts";
import { Film } from "./Film.tsx";
import { FONT_FACE_CSS } from "./fonts.ts";

const style = document.createElement("style");
style.textContent = FONT_FACE_CSS;
document.head.appendChild(style);

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Reel" component={Film} durationInFrames={REEL.durationInFrames} fps={REEL.fps} width={REEL.width} height={REEL.height}
      defaultProps={{ canvas: REEL, plan: REEL_PLAN, mix: "mix-reel.wav" }} />
    <Composition id="Video" component={Film} durationInFrames={VIDEO.durationInFrames} fps={VIDEO.fps} width={VIDEO.width} height={VIDEO.height}
      defaultProps={{ canvas: VIDEO, plan: VIDEO_PLAN, mix: "mix-video.wav" }} />
  </>
);

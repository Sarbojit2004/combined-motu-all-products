import React from "react";
import { AbsoluteFill, interpolate } from "remotion";
import type { Canvas } from "../theme.ts";

// ─────────────────────────────────────────────────────────────────────────────
// TRANSITIONS — eight moves chosen from each shot's own seed, the larger ones
// held back for segment boundaries. Every shot's Sequence is extended past its
// end by the incoming move's length and the next shot is stacked on top, so an
// incoming shot animates over a still-live outgoing one and nothing ever dips
// to black between two shots.
//
// No filter: blur() anywhere — at 4K a full-surface Gaussian is a convolution
// over 8.3 million pixels on every frame. Every move here is transform,
// opacity, clip-path or a gradient.
// ─────────────────────────────────────────────────────────────────────────────

import { TRANS, TRANS_CUE, transitionFor, type TransitionKind } from "../transitions-data.ts";
export { TRANS, TRANS_CUE, transitionFor };
export type { TransitionKind };

const smooth = (p: number) => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2);
const out = (p: number) => 1 - Math.pow(1 - p, 3);

type Props = {
  kind: TransitionKind;
  f: number;
  accent: string;
  canvas: Canvas;
  children: React.ReactNode;
};

export const TransitionIn: React.FC<Props> = ({ kind, f, accent, canvas, children }) => {
  const n = TRANS[kind];
  const raw = Math.min(1, Math.max(0, f / n));
  if (f >= n) return <AbsoluteFill>{children}</AbsoluteFill>;

  const W = canvas.width;
  const H = canvas.height;
  const DIAG_DROP = canvas.portrait ? 22 : 40;
  const DIAG_DEG = -(Math.atan2((DIAG_DROP / 100) * H, 1.4 * W) * 180) / Math.PI;

  const e = out(raw);
  let style: React.CSSProperties = {};
  let streak: React.ReactNode = null;

  switch (kind) {
    case "fade":
      style = { opacity: smooth(raw) };
      break;
    case "punchIn":
      style = { opacity: Math.min(1, raw * 2.2), transform: `scale(${interpolate(e, [0, 1], [1.17, 1])})` };
      break;
    case "pullBack":
      style = { opacity: Math.min(1, raw * 2), transform: `scale(${interpolate(e, [0, 1], [0.86, 1])})` };
      break;
    case "slideUp":
      style = { transform: `translateY(${interpolate(e, [0, 1], [H, 0])}px)` };
      break;
    case "whipLeft":
    case "whipRight": {
      const from = kind === "whipLeft" ? W : -W;
      const x = interpolate(e, [0, 1], [from, 0]);
      style = { transform: `translateX(${x}px)` };
      streak = (
        <div
          style={{
            position: "absolute",
            top: 0,
            bottom: 0,
            width: W * 0.42,
            left: x - (kind === "whipLeft" ? W * 0.42 : -W),
            background: `linear-gradient(${kind === "whipLeft" ? 90 : 270}deg, ${accent}00 0%, ${accent}B0 62%, #FFFFFFE6 100%)`,
            opacity: interpolate(raw, [0, 0.4, 1], [0.85, 0.5, 0]),
          }}
        />
      );
      break;
    }
    case "wipeDiag": {
      const a = interpolate(e, [0, 1], [150, -30]);
      const b = a - DIAG_DROP;
      style = { clipPath: `polygon(-20% ${a}%, 120% ${b}%, 120% 220%, -20% 220%)` };
      streak = (
        <div
          style={{
            position: "absolute",
            left: "-20%",
            width: "140%",
            height: canvas.portrait ? 9 : 7,
            top: `${(a + b) / 2}%`,
            background: accent,
            boxShadow: `0 0 70px ${accent}`,
            opacity: interpolate(raw, [0, 0.82, 1], [1, 0.85, 0]),
            transform: `rotate(${DIAG_DEG}deg)`,
            transformOrigin: "50% 50%",
          }}
        />
      );
      break;
    }
    case "flash":
    default: {
      style = { opacity: Math.min(1, raw * 3) };
      streak = (
        <AbsoluteFill
          style={{
            background: `radial-gradient(ellipse 92% 62% at 50% 46%, #FFFFFF 0%, ${accent} 44%, ${accent}00 78%)`,
            opacity: interpolate(raw, [0, 0.22, 1], [0, 0.58, 0]),
          }}
        />
      );
      break;
    }
  }

  return (
    <>
      <AbsoluteFill style={style}>{children}</AbsoluteFill>
      {streak ? <AbsoluteFill style={{ overflow: "hidden", pointerEvents: "none" }}>{streak}</AbsoluteFill> : null}
    </>
  );
};

import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ACCENT, FONT, INK, TYPE, type ProductKey } from "../theme.ts";
import type { TimedCaption } from "../plan.ts";

// ─────────────────────────────────────────────────────────────────────────────
// THE CAPTION LOCKUP — carried over from the M-Series reel by instruction.
//
//     THE 848 HAS            lead-in   — display caps, small
//        4                   the word  — script face, accent colour, huge
//     MIC PREAMPS            tail      — display caps, medium
//
// The sentence is split AT its key word, so the script face always lands on
// the term the sentence turns on. The whole lockup arrives as one object, so it
// never depends on per-word timing and does not drift when the client's read
// runs faster or slower than the script.
//
// The overlay layer that owns this is held at TYPE_OPACITY (0.64) by the
// composition, so the picture reads through the letterforms; contrast is
// bought back with a hard, tight drop shadow rather than a scrim, because a
// scrim would hide exactly the picture the transparency exists to reveal.
// ─────────────────────────────────────────────────────────────────────────────

type Props = {
  caption: TimedCaption;
  startFrame: number;
  product: ProductKey;
  env: "light" | "dark";
  width?: number;
  align?: "left" | "center";
  /** Multiplier on the whole lockup — the film runs at 0.72 of the reel. */
  scale?: number;
  /** Widest the script word may run before it is stepped down, in px at scale 1. */
  maxKeyWidth?: number;
};

/** Splits a caption into lead-in / key word / tail around its emphasis. */
export const splitCaption = (t: string, e?: string) => {
  const words = t.trim().split(/\s+/).filter(Boolean);
  // Punctuation is stripped from BOTH sides of the comparison, so "AVB." still
  // matches an emphasis of "AVB" and "7.1.4" still matches itself.
  const norm = (x: string) => x.replace(/[^\w+-]/g, "").toLowerCase();

  if (e) {
    const target = e.split(/\s+/).filter(Boolean);
    for (let i = 0; i + target.length <= words.length; i++) {
      if (target.every((tw, k) => norm(words[i + k]) === norm(tw))) {
        return {
          before: words.slice(0, i).join(" "),
          key: words.slice(i, i + target.length).join(" "),
          after: words.slice(i + target.length).join(" "),
        };
      }
    }
  }
  let bi = 0;
  for (let i = 1; i < words.length; i++) {
    if (norm(words[i]).length > norm(words[bi]).length) bi = i;
  }
  return {
    before: words.slice(0, bi).join(" "),
    key: words[bi] ?? t,
    after: words.slice(bi + 1).join(" "),
  };
};

/** Trailing punctuation is dropped from the script word — a brush script
 *  carrying a full stop reads as a typo, not as punctuation. */
export const cleanKey = (k: string) => k.replace(/[.,;:?!]+$/, "");

export const Caption: React.FC<Props> = ({
  caption,
  startFrame,
  product,
  env,
  width,
  align = "left",
  scale = 1,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame - startFrame;
  const durF = Math.max(1, Math.round((caption.end - caption.start) * fps));

  const accent = ACCENT[product];
  const keyColor = accent.glow;

  const { before, key, after } = splitCaption(caption.t, caption.e);

  const enter = spring({ frame: local, fps, config: { damping: 200, mass: 0.55 }, durationInFrames: 14 });
  const keyIn = spring({ frame: local - 3, fps, config: { damping: 170, mass: 0.5, stiffness: 120 }, durationInFrames: 18 });
  const tailIn = spring({ frame: local - 6, fps, config: { damping: 200, mass: 0.5 }, durationInFrames: 14 });

  const outAt = durF - 7;
  const exit = local > outAt ? interpolate(local, [outAt, durF], [1, 0], { extrapolateRight: "clamp" }) : 1;

  const keyScale = interpolate(keyIn, [0, 1], [1.14, 1]);
  const keyTilt = interpolate(keyIn, [0, 1], [-3.2, -1.4]);

  const S = (n: number) => n * scale;

  // The script face is set at one size for short keys and stepped down for
  // longer ones, so a two-word key never runs past the safe margin.
  const keyLen = cleanKey(key).length;
  const fit = keyLen <= 6 ? 1 : keyLen <= 9 ? 0.86 : keyLen <= 12 ? 0.74 : keyLen <= 16 ? 0.6 : 0.5;
  const items: React.CSSProperties = {
    display: "flex",
    flexDirection: "column",
    alignItems: align === "center" ? "center" : "flex-start",
  };

  return (
    <div style={{ width: width ?? "100%", opacity: exit, ...items }}>
      {before ? (
        <div
          style={{
            fontFamily: FONT.display,
            fontSize: S(TYPE.before.size),
            letterSpacing: S(TYPE.before.track),
            color: INK.onDark,
            textTransform: "uppercase",
            lineHeight: 1.1,
            textShadow: `0 ${S(3)}px ${S(7)}px rgba(0,0,0,0.92), 0 0 ${S(3)}px rgba(0,0,0,0.75)`,
            opacity: enter,
            transform: `translateY(${interpolate(enter, [0, 1], [26, 0])}px)`,
            marginBottom: S(6),
            textAlign: align,
          }}
        >
          {before}
        </div>
      ) : null}

      <div
        style={{
          fontFamily: FONT.script,
          fontSize: S(TYPE.script.size) * fit,
          letterSpacing: S(TYPE.script.track),
          color: keyColor,
          lineHeight: 0.98,
          padding: `${S(18)}px ${S(26)}px ${S(30)}px 0`,
          marginLeft: S(-6),
          opacity: keyIn,
          transform: `translateY(${interpolate(keyIn, [0, 1], [40, 0])}px) scale(${keyScale}) rotate(${keyTilt}deg)`,
          transformOrigin: align === "center" ? "50% 70%" : "8% 70%",
          textShadow: `0 ${S(5)}px ${S(11)}px rgba(0,0,0,0.95), 0 0 ${S(5)}px rgba(0,0,0,0.8), 0 0 ${S(34)}px ${accent.glow}44`,
          whiteSpace: "nowrap",
        }}
      >
        {cleanKey(key)}
      </div>

      {after ? (
        <div
          style={{
            fontFamily: FONT.display,
            fontSize: S(TYPE.after.size),
            letterSpacing: S(TYPE.after.track),
            color: INK.onDark,
            textTransform: "uppercase",
            lineHeight: 1.06,
            opacity: tailIn,
            transform: `translateY(${interpolate(tailIn, [0, 1], [30, 0])}px)`,
            textShadow: `0 ${S(4)}px ${S(9)}px rgba(0,0,0,0.94), 0 0 ${S(4)}px rgba(0,0,0,0.78)`,
            maxWidth: "100%",
            textAlign: align,
          }}
        >
          {after}
        </div>
      ) : null}
    </div>
  );
};

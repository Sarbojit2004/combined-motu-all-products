import React from "react";
import { AbsoluteFill, Img, OffthreadVideo, interpolate, spring, staticFile, useVideoConfig } from "remotion";
import { ASSETS, type Asset } from "../assets.generated.ts";
import { ACCENT, FONT, INK, PRODUCT_NAME, type Canvas, type ProductKey } from "../theme.ts";
import type { Move, Shot } from "../plan.ts";

// ─────────────────────────────────────────────────────────────────────────────
// STAGING — every picture is shown COMPLETE (contained, never cropped to fit),
// over an ambient fill made from the picture itself, then moved like a camera
// on a gimbal: drift, zoom in/out, a rack focus in/out, a crane, an orbit.
//
// Rack focus is a crossfade to a pre-blurred "soft" copy — no CSS blur at 4K.
// ─────────────────────────────────────────────────────────────────────────────

const BY: Record<string, Asset> = Object.fromEntries(ASSETS.map((a) => [a.slug, a]));
export const asset = (slug: string) => BY[slug];

type Box = { x: number; y: number; w: number; h: number };
const contain = (ar: number, b: Box) => {
  const w = Math.min(b.w, b.h * ar);
  const h = w / ar;
  return { x: b.x + (b.w - w) / 2, y: b.y + (b.h - h) / 2, w, h };
};

/** Where the picture lives. Portrait keeps a band between the top bar and the captions. */
export const pictureBox = (c: Canvas, transparent: boolean): Box =>
  c.portrait
    ? transparent
      ? { x: 70, y: 1240, w: c.width - 140, h: 1160 }
      : { x: 0, y: 1150, w: c.width, h: 1320 }
    : transparent
      ? { x: 380, y: 560, w: c.width - 760, h: 1300 }
      : { x: 0, y: 0, w: c.width, h: c.height };

const smooth = (p: number) => {
  const x = Math.min(1, Math.max(0, p));
  return x * x * (3 - 2 * x);
};

/** A camera move as a transform plus how much of the soft copy shows. */
export const moveFor = (m: Move, p: number) => {
  const e = smooth(p);
  switch (m) {
    case "gimbalL":
      return { t: `translateX(${interpolate(e, [0, 1], [2.6, -2.6])}%) scale(1.07) rotate(${interpolate(e, [0, 1], [0.5, -0.5])}deg)`, soft: 0 };
    case "gimbalR":
      return { t: `translateX(${interpolate(e, [0, 1], [-2.6, 2.6])}%) scale(1.07) rotate(${interpolate(e, [0, 1], [-0.5, 0.5])}deg)`, soft: 0 };
    case "zoomIn":
      return { t: `scale(${interpolate(e, [0, 1], [1.0, 1.13])})`, soft: 0 };
    case "zoomOut":
      return { t: `scale(${interpolate(e, [0, 1], [1.13, 1.0])})`, soft: 0 };
    case "focusIn":
      return { t: `scale(${interpolate(e, [0, 1], [1.08, 1.0])})`, soft: 1 - smooth(p / 0.42) };
    case "focusOut":
      return { t: `scale(${interpolate(e, [0, 1], [1.0, 1.07])})`, soft: smooth((p - 0.6) / 0.4) * 0.92 };
    case "craneUp":
      return { t: `translateY(${interpolate(e, [0, 1], [3.2, -3.2])}%) scale(1.08)`, soft: 0 };
    case "orbit":
    default:
      return { t: `perspective(2600px) rotateY(${interpolate(e, [0, 1], [-7, 7])}deg) scale(${interpolate(e, [0, 1], [1.05, 1.1])})`, soft: 0 };
  }
};

type Common = { canvas: Canvas; f: number; dur: number; series: ProductKey; beat: number; t: number };

/** A studio for transparent renders: a lit sweep in the series colour, a floor, a reflection. */
const Studio: React.FC<{ canvas: Canvas; glow: string; f: number }> = ({ canvas, glow, f }) => (
  <>
    <AbsoluteFill style={{ background: `radial-gradient(ellipse 80% 55% at 50% ${canvas.portrait ? 44 : 46}%, #23232C 0%, #0E0E13 55%, #050507 100%)` }} />
    <AbsoluteFill style={{ background: `radial-gradient(ellipse 60% 34% at 50% ${canvas.portrait ? 62 : 72}%, ${glow}30 0%, ${glow}00 70%)` }} />
    <AbsoluteFill
      style={{
        opacity: 0.35,
        backgroundImage: `repeating-linear-gradient(90deg, rgba(255,255,255,0.05) 0 2px, rgba(0,0,0,0) 2px ${canvas.portrait ? 120 : 160}px)`,
        transform: `translateX(${(f * 0.6) % (canvas.portrait ? 120 : 160)}px)`,
      }}
    />
    <AbsoluteFill style={{ background: `linear-gradient(180deg, rgba(0,0,0,0) ${canvas.portrait ? 60 : 70}%, rgba(255,255,255,0.05) ${canvas.portrait ? 60.2 : 70.2}%, rgba(0,0,0,0.5) 100%)` }} />
  </>
);

const Ambient: React.FC<{ a: Asset; canvas: Canvas }> = ({ a }) => (
  <AbsoluteFill>
    <Img src={staticFile(a.amb)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: "scale(1.2)" }} />
    <AbsoluteFill style={{ background: "radial-gradient(ellipse 90% 70% at 50% 50%, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0.62) 100%)" }} />
  </AbsoluteFill>
);

export const StillShot: React.FC<Common & { slug: string; move: Move }> = ({ canvas, f, dur, series, slug, move }) => {
  const a = asset(slug);
  const p = f / Math.max(1, dur);
  const box = pictureBox(canvas, a.transparent);
  const r = contain(a.ar, box);
  const mv = moveFor(move, p);
  const glow = ACCENT[series].glow;
  const full = !canvas.portrait && !a.transparent && a.ar > 1.7;
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      {a.transparent ? <Studio canvas={canvas} glow={glow} f={f} /> : <Ambient a={a} canvas={canvas} />}
      <div
        style={{
          position: "absolute",
          left: r.x,
          top: r.y,
          width: r.w,
          height: r.h,
          transform: mv.t,
          transformOrigin: "50% 50%",
          boxShadow: a.transparent || full ? "none" : "0 30px 60px rgba(0,0,0,0.7)",
        }}
      >
        <Img src={staticFile(a.file)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }} />
        {mv.soft > 0.001 ? (
          <Img src={staticFile(a.soft)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: mv.soft }} />
        ) : null}
        {a.transparent ? (
          // The unit's reflection in the floor.
          <div
            style={{
              position: "absolute",
              left: 0,
              top: "100%",
              width: "100%",
              height: "100%",
              transform: "scaleY(-1)",
              opacity: 0.16,
              WebkitMaskImage: "linear-gradient(0deg, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 38%)",
              maskImage: "linear-gradient(0deg, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 38%)",
            }}
          >
            <Img src={staticFile(a.file)} style={{ width: "100%", height: "100%" }} />
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

/** Kling clips are 121 frames at 24 fps — played across their whole beat slot, first frame to last. */
const CLIP_SECONDS = 121 / 24;

export const BrollShot: React.FC<Common & { file: string; slot: number }> = ({ canvas, f, file, slot }) => {
  // The clip spans the slot plus the next shot's transition, so it is seen complete.
  const rate = CLIP_SECONDS / (slot + 0.5);
  const push = interpolate(f, [0, slot * 30], [1.0, 1.045], { extrapolateRight: "clamp" });
  const amb = file.replace(/\.mp4$/, "-amb.mp4");
  if (!canvas.portrait) {
    return (
      <AbsoluteFill style={{ overflow: "hidden", background: "#000" }}>
        <OffthreadVideo src={staticFile(file)} muted playbackRate={rate} style={{ width: "100%", height: "100%", transform: `scale(${push})` }} />
      </AbsoluteFill>
    );
  }
  const box = pictureBox(canvas, false);
  const r = contain(16 / 9, box);
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#000" }}>
      <OffthreadVideo src={staticFile(amb)} muted playbackRate={rate} style={{ width: "100%", height: "100%", objectFit: "cover", transform: "scale(1.25)" }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 90% 70% at 50% 50%, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.6) 100%)" }} />
      <div style={{ position: "absolute", left: r.x, top: r.y, width: r.w, height: r.h, transform: `scale(${push})`, boxShadow: "0 30px 60px rgba(0,0,0,0.75)" }}>
        <OffthreadVideo src={staticFile(file)} muted playbackRate={rate} style={{ width: "100%", height: "100%" }} />
      </div>
    </AbsoluteFill>
  );
};

/** DSP boards — CueMix screenshots on a lit console surface, flown in one after another. */
export const DspShot: React.FC<Common & { slugs: string[] }> = ({ canvas, f, dur, series, slugs, beat, t }) => {
  const { fps } = useVideoConfig();
  const glow = ACCENT[series].glow;
  const A = slugs.map(asset);
  const P = canvas.portrait;
  const p = f / Math.max(1, dur);
  const W = canvas.width;
  // Layout — portrait stacks, landscape runs side by side (three = one hero + two).
  let boxes: Box[];
  if (A.length === 1) boxes = [P ? { x: 110, y: 1180, w: W - 220, h: 1260 } : { x: 360, y: 420, w: W - 720, h: 1480 }];
  else if (A.length === 2)
    boxes = P
      ? [{ x: 150, y: 1120, w: W - 300, h: 660 }, { x: 150, y: 1830, w: W - 300, h: 660 }]
      : [{ x: 220, y: 520, w: 1640, h: 1300 }, { x: 1980, y: 520, w: 1640, h: 1300 }];
  else
    boxes = P
      ? [{ x: 90, y: 1120, w: W - 180, h: 800 }, { x: 90, y: 1960, w: (W - 220) / 2, h: 560 }, { x: W / 2 + 20, y: 1960, w: (W - 220) / 2, h: 560 }]
      : [{ x: 220, y: 440, w: 2220, h: 1460 }, { x: 2540, y: 440, w: 1080, h: 700 }, { x: 2540, y: 1200, w: 1080, h: 700 }];
  const logo = A.length === 1 && A[0].kind === "logo";
  const phase = ((t / beat) % 1 + 1) % 1;
  const pulse = Math.exp(-phase * 5);
  const drift = interpolate(smooth(p), [0, 1], [1.0, 1.05]);
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 85% 60% at 50% 45%, #171820 0%, #09090D 60%, #030304 100%)" }} />
      <AbsoluteFill
        style={{
          opacity: 0.5,
          backgroundImage:
            `repeating-linear-gradient(0deg, ${glow}14 0 2px, rgba(0,0,0,0) 2px 96px), repeating-linear-gradient(90deg, ${glow}14 0 2px, rgba(0,0,0,0) 2px 96px)`,
          transform: `perspective(1800px) rotateX(58deg) translateY(${P ? 900 : 520}px) translateZ(0) scale(2.2) translateY(${(f * 1.4) % 96}px)`,
          transformOrigin: "50% 100%",
        }}
      />
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 55% 36% at 50% 55%, ${glow}${logo ? "38" : "1C"} 0%, ${glow}00 72%)` }} />
      <AbsoluteFill style={{ transform: `scale(${drift})` }}>
        {A.map((a, i) => {
          const r = logo ? contain(1, { x: W / 2 - (P ? 520 : 480), y: (P ? 1810 : 1080) - (P ? 520 : 480), w: P ? 1040 : 960, h: P ? 1040 : 960 }) : contain(a.ar, boxes[i]);
          const inn = spring({ frame: f - i * 5, fps, config: { damping: 180, mass: 0.6 }, durationInFrames: 18 });
          return (
            <div
              key={a.slug}
              style={{
                position: "absolute",
                left: r.x,
                top: r.y,
                width: r.w,
                height: r.h,
                opacity: inn,
                transform: `perspective(2400px) translateY(${interpolate(inn, [0, 1], [90, 0])}px) rotateX(${interpolate(inn, [0, 1], [14, 0])}deg) scale(${logo ? 1 + pulse * 0.025 : 1})`,
                borderRadius: logo ? 0 : 22,
                overflow: logo ? "visible" : "hidden",
                boxShadow: logo ? "none" : `0 30px 60px rgba(0,0,0,0.78), 0 0 0 3px rgba(255,255,255,0.10), 0 0 0 ${2 + pulse * 4}px ${glow}55`,
                background: logo ? `radial-gradient(circle at 50% 50%, ${glow}${pulse > 0.5 ? "55" : "33"} 0%, ${glow}00 62%)` : undefined,
              }}
            >
              <Img src={staticFile(a.file)} style={{ width: "100%", height: "100%" }} />
            </div>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** One unit from each family, side by side — the family portrait. */
export const LineupShot: React.FC<Common & { slugs: string[] }> = ({ canvas, f, dur, series, slugs }) => {
  const { fps } = useVideoConfig();
  const A = slugs.map(asset);
  const P = canvas.portrait;
  const W = canvas.width;
  const n = A.length;
  const e = smooth(f / Math.max(1, dur));
  const cells: Box[] = P
    ? A.map((_, i) => ({ x: 160, y: 1140 + i * (1340 / n), w: W - 320, h: 1340 / n - 60 }))
    : A.map((_, i) => ({ x: 380 + (i % 2) * 1580, y: 520 + Math.floor(i / 2) * 700, w: 1500, h: 560 }));
  const seriesOf = (a: Asset): ProductKey => (a.series === "m" ? "m" : a.series === "ul828" ? "ul828" : "avb");
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Studio canvas={canvas} glow={ACCENT[series].glow} f={f} />
      <AbsoluteFill style={{ transform: `scale(${interpolate(e, [0, 1], [1.0, 1.06])}) translateX(${interpolate(e, [0, 1], [-1, 1])}%)` }}>
        {A.map((a, i) => {
          const c = cells[i];
          const r = contain(a.ar, { ...c, h: c.h - (P ? 70 : 90) });
          const inn = spring({ frame: f - i * 4, fps, config: { damping: 190, mass: 0.6 }, durationInFrames: 20 });
          const g = ACCENT[seriesOf(a)].glow;
          return (
            <React.Fragment key={a.slug + i}>
              <div style={{ position: "absolute", left: r.x, top: r.y, width: r.w, height: r.h, opacity: inn, transform: `translateY(${interpolate(inn, [0, 1], [60, 0])}px)` }}>
                <Img src={staticFile(a.file)} style={{ width: "100%", height: "100%" }} />
              </div>
              <div
                style={{
                  position: "absolute",
                  left: c.x,
                  width: c.w,
                  top: c.y + c.h - (P ? 58 : 74),
                  textAlign: "center",
                  fontFamily: FONT.display,
                  fontSize: P ? 50 : 56,
                  letterSpacing: 8,
                  color: g,
                  opacity: inn * 0.9,
                  textShadow: "0 4px 10px rgba(0,0,0,0.9)",
                }}
              >
                {PRODUCT_NAME[a.product] ?? a.product}
              </div>
            </React.Fragment>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const ShotView: React.FC<Common & { shot: Shot }> = (props) => {
  const { shot } = props;
  switch (shot.kind) {
    case "broll":
      return <BrollShot {...props} file={shot.file!} slot={shot.end - shot.start} />;
    case "dsp":
      return <DspShot {...props} slugs={shot.assets!} />;
    case "lineup":
      return <LineupShot {...props} slugs={shot.assets!} />;
    default:
      return <StillShot {...props} slug={shot.assets![0]} move={shot.move} />;
  }
};

/** The on-screen name for whatever the current shot shows. */
export const shotLabel = (s: Shot): string => {
  if (s.kind === "broll") return (s.label ?? "").split(" — ")[0].toUpperCase();
  if (s.kind === "dsp") {
    const a = asset(s.assets![0]);
    return a.kind === "cm5" || a.note === "CueMix 5" ? "CueMix 5" : "CueMix Pro";
  }
  if (s.kind === "lineup") return "THE MOTU FAMILY";
  const a = asset(s.assets![0]);
  return PRODUCT_NAME[a.product] ?? a.product.toUpperCase();
};

export { INK };

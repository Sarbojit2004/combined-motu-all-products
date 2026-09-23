import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ACCENT, FONT, INK, sec, type Canvas } from "../theme.ts";
import type { Icon, Plan, Section, Shot } from "../plan.ts";
import { GRAPHS } from "./Graphs.tsx";
import { shotLabel } from "./Shots.tsx";

// ─────────────────────────────────────────────────────────────────────────────
// THE BARS.
//
// TOP — no timeline, no section numbers. Three rows that rebuild at every
// section: a series badge; three spec icons whose numbers count up to the
// figure; and a live graph (the Soundcraft films' demonstratives) that
// changes every 16 beats and moves with the music.
//
// BOTTOM — a chip naming what is on screen right now, a ticker of the facts
// the captions have no room for, and four beat lights counting the bar.
// ─────────────────────────────────────────────────────────────────────────────

const CYCLE: Record<string, { g: string; value?: number }[]> = {
  hook: [{ g: "spectrum" }],
  family: [{ g: "spectrum" }, { g: "meters" }],
  family1: [{ g: "spectrum" }],
  lineup: [{ g: "spectrum" }],
  m: [{ g: "range", value: 120 }, { g: "latency", value: 2.5 }, { g: "meters" }, { g: "spectrum" }],
  ul828: [{ g: "io" }, { g: "range", value: 125 }, { g: "latency", value: 2.4 }, { g: "meters" }],
  ul: [{ g: "io" }, { g: "latency", value: 2.4 }, { g: "meters" }, { g: "spectrum" }],
  "828": [{ g: "io" }, { g: "range", value: 125 }, { g: "meters" }, { g: "latency", value: 2.4 }],
  avb: [{ g: "io" }, { g: "range", value: 125 }, { g: "latency", value: 2 }, { g: "network" }],
  switch: [{ g: "network" }],
  network: [{ g: "network" }, { g: "latency", value: 2 }],
  cm5: [{ g: "eq" }, { g: "comp" }, { g: "meters" }, { g: "eq" }],
  cmpro: [{ g: "comp" }, { g: "eq" }, { g: "meters" }, { g: "network" }],
  deploy: [{ g: "meters" }, { g: "spectrum" }],
  finale: [{ g: "spectrum" }, { g: "meters" }],
};

const Glyph: React.FC<{ kind: string; size: number; color: string }> = ({ kind, size, color }) => {
  const p = { stroke: color, strokeWidth: 2.2, fill: "none", strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  const body: Record<string, React.ReactNode> = {
    range: <><path d="M5 22 A11 11 0 0 1 27 22" {...p} /><path d="M16 22 L22 13" {...p} /><circle cx="16" cy="22" r="1.8" fill={color} /></>,
    latency: <><circle cx="16" cy="18" r="9" {...p} /><path d="M16 18 L16 12 M13 5 L19 5 M16 5 L16 9" {...p} /></>,
    rate: <path d="M3 16 Q6 6 9 16 T15 16 T21 16 T27 16 L29 16" {...p} />,
    io: <><path d="M4 11 L14 11 M10 7 L14 11 L10 15" {...p} /><path d="M28 21 L18 21 M22 17 L18 21 L22 25" {...p} /></>,
    gain: <><circle cx="16" cy="16" r="10" {...p} /><path d="M16 16 L22 10" {...p} /><path d="M7 25 L9 23 M25 25 L23 23" {...p} /></>,
    ch: <><path d="M6 9 L26 9 M6 14 L26 14 M6 19 L26 19 M6 24 L26 24" {...p} /></>,
    ports: <><rect x="6" y="9" width="20" height="15" rx="2" {...p} /><path d="M10 24 L10 20 L22 20 L22 24 M12 13 L12 16 M16 13 L16 16 M20 13 L20 16" {...p} /></>,
    dist: <><path d="M4 16 L28 16 M4 12 L4 20 M28 12 L28 20 M10 14 L10 18 M16 13 L16 19 M22 14 L22 18" {...p} /></>,
    units: <><rect x="5" y="6" width="22" height="6" rx="1.5" {...p} /><rect x="5" y="14" width="22" height="6" rx="1.5" {...p} /><rect x="5" y="22" width="22" height="6" rx="1.5" {...p} /></>,
    eq: <><path d="M8 5 L8 27 M16 5 L16 27 M24 5 L24 27" {...p} /><rect x="5" y="17" width="6" height="4" rx="1" fill={color} /><rect x="13" y="9" width="6" height="4" rx="1" fill={color} /><rect x="21" y="14" width="6" height="4" rx="1" fill={color} /></>,
    dyn: <><path d="M5 27 L16 16 L27 11" {...p} /><path d="M5 5 L5 27 L27 27" {...p} /></>,
    fx: <><path d="M5 16 Q9 8 13 16 Q17 24 21 16 Q25 8 29 16" {...p} /><path d="M5 22 Q9 18 13 22" {...p} opacity={0.5} /></>,
    mix: <><path d="M8 5 L8 27 M16 5 L16 27 M24 5 L24 27" {...p} /><rect x="5" y="10" width="6" height="5" rx="1" fill={color} /><rect x="13" y="19" width="6" height="5" rx="1" fill={color} /><rect x="21" y="7" width="6" height="5" rx="1" fill={color} /></>,
    aux: <><circle cx="8" cy="16" r="3" {...p} /><path d="M11 16 L20 8 M11 16 L20 16 M11 16 L20 24" {...p} /><circle cx="23" cy="8" r="2.5" {...p} /><circle cx="23" cy="16" r="2.5" {...p} /><circle cx="23" cy="24" r="2.5" {...p} /></>,
    series: <><rect x="4" y="11" width="7" height="10" rx="1.5" {...p} /><rect x="12.5" y="8" width="7" height="16" rx="1.5" {...p} /><rect x="21" y="5" width="7" height="22" rx="1.5" {...p} /></>,
    dsp: <><rect x="9" y="9" width="14" height="14" rx="2" {...p} /><path d="M13 5 L13 9 M19 5 L19 9 M13 23 L13 27 M19 23 L19 27 M5 13 L9 13 M5 19 L9 19 M23 13 L27 13 M23 19 L27 19" {...p} /></>,
    pre: <><rect x="12" y="4" width="8" height="14" rx="4" {...p} /><path d="M8 15 Q8 22 16 22 Q24 22 24 15 M16 22 L16 28 M11 28 L21 28" {...p} /></>,
  };
  return <svg width={size} height={size} viewBox="0 0 32 32">{body[kind] ?? body.series}</svg>;
};

const fmt = (v: number, target: number) => (Number.isInteger(target) ? Math.round(v).toString() : v.toFixed(1));

const IconCard: React.FC<{ icon: Icon; f: number; glow: string; w: number; h: number; pulse: number; delay: number }> = ({ icon, f, glow, w, h, pulse, delay }) => {
  const { fps } = useVideoConfig();
  const [kind, value, unit, label] = icon;
  const inn = spring({ frame: f - delay, fps, config: { damping: 170, mass: 0.55 }, durationInFrames: 18 });
  const count = interpolate(f - delay, [4, 30], [0, value], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) });
  const sweep = interpolate(f - delay, [6, 26], [-0.4, 1.4], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ic = h * 0.52;
  return (
    <div
      style={{
        position: "relative",
        width: w,
        height: h,
        borderRadius: h * 0.16,
        background: "linear-gradient(180deg, rgba(22,22,30,0.78) 0%, rgba(8,8,12,0.72) 100%)",
        border: `2px solid ${glow}55`,
        boxShadow: `0 18px 40px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.08)`,
        overflow: "hidden",
        opacity: inn,
        transform: `translateY(${interpolate(inn, [0, 1], [40, 0])}px) scale(${interpolate(inn, [0, 1], [0.92, 1])})`,
        display: "flex",
        alignItems: "center",
        gap: h * 0.12,
        padding: `0 ${h * 0.14}px`,
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          width: ic, height: ic, borderRadius: ic, flex: "none",
          display: "flex", alignItems: "center", justifyContent: "center",
          background: `${glow}1F`, border: `2px solid ${glow}`,
          boxShadow: `0 0 ${10 + pulse * 26}px ${glow}${pulse > 0.5 ? "AA" : "55"}`,
        }}
      >
        <Glyph kind={kind} size={ic * 0.66} color={glow} />
      </div>
      <div style={{ display: "flex", flexDirection: "column", minWidth: 0 }}>
        <div style={{ fontFamily: FONT.display, fontSize: h * 0.34, color: INK.onDark, lineHeight: 1, whiteSpace: "nowrap", fontVariantNumeric: "tabular-nums" }}>
          {fmt(count, value)}
          <span style={{ fontSize: h * 0.2, color: glow, marginLeft: h * 0.04 }}>{unit}</span>
        </div>
        <div style={{ fontFamily: FONT.display, fontSize: h * 0.105, letterSpacing: h * 0.016, color: INK.onDarkSoft, marginTop: h * 0.06, whiteSpace: "nowrap" }}>{label}</div>
      </div>
      {/* A light sweep across the card as its number lands. */}
      <div style={{ position: "absolute", top: 0, bottom: 0, width: w * 0.3, left: sweep * w - w * 0.15, background: `linear-gradient(90deg, ${glow}00, ${glow}33, ${glow}00)`, transform: "skewX(-18deg)" }} />
    </div>
  );
};

const Badge: React.FC<{ sec: Section; f: number; h: number; pulse: number }> = ({ sec: s, f, h, pulse }) => {
  const { fps } = useVideoConfig();
  const a = ACCENT[s.series];
  const inn = spring({ frame: f, fps, config: { damping: 180, mass: 0.5 }, durationInFrames: 16 });
  const wipe = interpolate(f, [0, 12], [0, 100], { extrapolateRight: "clamp" });
  return (
    <div style={{ display: "flex", alignItems: "center", gap: h * 0.22, opacity: inn, transform: `translateX(${interpolate(inn, [0, 1], [-50, 0])}px)` }}>
      <div
        style={{
          position: "relative",
          height: h,
          padding: `0 ${h * 0.38}px`,
          display: "flex",
          alignItems: "center",
          gap: h * 0.18,
          borderRadius: h * 0.5,
          background: a.key,
          clipPath: `inset(0 ${100 - wipe}% 0 0 round ${h * 0.5}px)`,
          boxShadow: `0 0 ${20 + pulse * 30}px ${a.glow}66`,
        }}
      >
        <div style={{ width: h * 0.26, height: h * 0.26, borderRadius: h, background: "#FFFFFF", opacity: 0.5 + pulse * 0.5, boxShadow: `0 0 ${pulse * 18}px #FFFFFF` }} />
        <div style={{ fontFamily: FONT.display, fontSize: h * 0.44, letterSpacing: h * 0.06, color: "#FFFFFF", whiteSpace: "nowrap" }}>{s.label}</div>
      </div>
      {s.sub ? (
        <div style={{ fontFamily: FONT.display, fontSize: h * 0.34, letterSpacing: h * 0.07, color: a.glow, whiteSpace: "nowrap", textShadow: "0 3px 8px rgba(0,0,0,0.9)", opacity: interpolate(f, [8, 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
          {s.sub}
        </div>
      ) : null}
    </div>
  );
};

const GraphPanel: React.FC<{ sec: Section; t: number; plan: Plan; w: number; h: number; fps: number }> = ({ sec: s, t, plan, w, h, fps }) => {
  const list = CYCLE[s.id] ?? [{ g: "spectrum" }];
  const blk = 16 * plan.beat;
  const idx = Math.max(0, Math.floor((t - s.start) / blk));
  const cur = list[idx % list.length];
  const lf = Math.round((t - (s.start + idx * blk)) * fps);
  const G = GRAPHS[cur.g];
  const a = ACCENT[s.series];
  const inn = interpolate(lf, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  const left = s.start + (idx + 1) * blk - t;
  const out = interpolate(left, [0, 0.2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const pad = h * 0.08;
  return (
    <div
      style={{
        width: w,
        height: h,
        borderRadius: h * 0.08,
        background: "linear-gradient(180deg, rgba(18,18,26,0.72) 0%, rgba(6,6,9,0.7) 100%)",
        border: `2px solid ${a.glow}40`,
        boxShadow: "0 18px 40px rgba(0,0,0,0.5)",
        padding: pad,
        boxSizing: "border-box",
        opacity: Math.min(inn, left < blk ? out : 1),
      }}
    >
      <G w={w - pad * 2} h={h - pad * 2} glow={a.glow} f={lf} t={t - plan.offset} beat={plan.beat} value={cur.value} io={s.top.io} />
    </div>
  );
};

export const TopBar: React.FC<{ plan: Plan; canvas: Canvas }> = ({ plan, canvas }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const s = plan.sections.find((x) => t >= x.start - 0.02 && t < x.end) ?? plan.sections[plan.sections.length - 1];
  const f = frame - sec(s.start);
  const a = ACCENT[s.series];
  const ph = ((((t - plan.offset) / plan.beat) % 1) + 1) % 1;
  const pulse = Math.exp(-ph * 5);
  const icons = s.top.icons ?? [];
  const exit = interpolate(s.end - t, [0, 0.12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const P = canvas.portrait;
  const L = canvas.safe.left;
  const W = canvas.width - canvas.safe.left - canvas.safe.right;
  if (P) {
    const cw = (W - 2 * 28) / 3;
    return (
      <div style={{ position: "absolute", left: L, top: canvas.safe.top, width: W, opacity: exit }}>
        <Badge sec={s} f={f} h={118} pulse={pulse} />
        <div style={{ display: "flex", gap: 28, marginTop: 36 }}>
          {icons.map((ic, i) => <IconCard key={s.id + i} icon={ic} f={f} glow={a.glow} w={cw} h={236} pulse={pulse} delay={4 + i * 4} />)}
        </div>
        <div style={{ marginTop: 32 }}>
          <GraphPanel sec={s} t={t} plan={plan} w={W} h={300} fps={fps} />
        </div>
      </div>
    );
  }
  return (
    <div style={{ position: "absolute", left: L, top: canvas.safe.top, width: W, height: 330, opacity: exit }}>
      <div style={{ position: "absolute", left: 0, top: 0 }}>
        <Badge sec={s} f={f} h={100} pulse={pulse} />
      </div>
      <div style={{ position: "absolute", left: 0, top: 140, display: "flex", gap: 24 }}>
        {icons.map((ic, i) => <IconCard key={s.id + i} icon={ic} f={f} glow={a.glow} w={560} h={190} pulse={pulse} delay={4 + i * 4} />)}
      </div>
      <div style={{ position: "absolute", right: 0, top: 0 }}>
        <GraphPanel sec={s} t={t} plan={plan} w={860} h={330} fps={fps} />
      </div>
    </div>
  );
};

export const BottomBar: React.FC<{ plan: Plan; canvas: Canvas; shots: Shot[] }> = ({ plan, canvas, shots }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const s = plan.sections.find((x) => t >= x.start - 0.02 && t < x.end) ?? plan.sections[plan.sections.length - 1];
  const shot = shots.find((x) => t >= x.start && t < x.end) ?? shots[shots.length - 1];
  const a = ACCENT[s.series];
  const beatN = (t - plan.offset) / plan.beat;
  const ph = ((beatN % 1) + 1) % 1;
  const inBar = Math.floor(((beatN % 4) + 4) % 4);
  const pulse = Math.exp(-ph * 5);
  const P = canvas.portrait;
  const H = P ? 112 : 92;
  const L = canvas.safe.left;
  const W = canvas.width - canvas.safe.left - canvas.safe.right;
  const label = shotLabel(shot);
  const lf = frame - sec(shot.start);
  const chipIn = interpolate(lf, [0, 7], [0, 1], { extrapolateRight: "clamp" });
  const items = s.ticker.length ? s.ticker : [a.tag];
  const text = items.join("   ◆   ") + "   ◆   ";
  const speed = P ? 5.2 : 6.5;
  const charW = H * 0.34 * 0.8;
  const loop = text.length * charW;
  const x = -((frame * speed) % loop);
  const sweep = (((beatN / 4) % 1) + 1) % 1;
  return (
    <div style={{ position: "absolute", left: L, width: W, bottom: P ? canvas.safe.bottom - 10 : 96, height: H }}>
      {/* Accent rule with a light that runs the length of it once per bar. */}
      <div style={{ position: "absolute", left: 0, right: 0, top: -10, height: 4, background: `${a.glow}55` }} />
      <div style={{ position: "absolute", top: -14, height: 12, width: W * 0.14, left: sweep * W * 0.86, background: `radial-gradient(ellipse at center, #FFFFFF 0%, ${a.glow} 40%, ${a.glow}00 72%)` }} />
      <div style={{ position: "absolute", inset: 0, borderRadius: H * 0.22, background: "linear-gradient(90deg, rgba(8,8,12,0.82), rgba(8,8,12,0.55))", border: "2px solid rgba(255,255,255,0.08)", overflow: "hidden", display: "flex", alignItems: "center" }}>
        <div
          style={{
            flex: "none",
            height: "100%",
            display: "flex",
            alignItems: "center",
            padding: `0 ${H * 0.34}px`,
            background: a.key,
            fontFamily: FONT.display,
            fontSize: H * 0.36,
            letterSpacing: H * 0.05,
            color: "#FFFFFF",
            whiteSpace: "nowrap",
            clipPath: `inset(0 ${(1 - chipIn) * 100}% 0 0)`,
            maxWidth: W * 0.45,
            overflow: "hidden",
          }}
        >
          {label}
        </div>
        <div style={{ position: "relative", flex: 1, height: "100%", overflow: "hidden" }}>
          <div style={{ position: "absolute", top: 0, bottom: 0, left: x, display: "flex", alignItems: "center", whiteSpace: "pre", fontFamily: FONT.display, fontSize: H * 0.34, letterSpacing: H * 0.04, color: INK.onDark }}>
            <span>{text}</span>
            <span>{text}</span>
            <span>{text}</span>
          </div>
          <div style={{ position: "absolute", inset: 0, background: "linear-gradient(90deg, rgba(8,8,12,0.9) 0%, rgba(8,8,12,0) 8%, rgba(8,8,12,0) 90%, rgba(8,8,12,0.9) 100%)" }} />
        </div>
        <div style={{ flex: "none", display: "flex", gap: H * 0.16, padding: `0 ${H * 0.3}px` }}>
          {[0, 1, 2, 3].map((k) => (
            <div key={k} style={{ width: H * 0.2, height: H * 0.2, borderRadius: H, background: k === inBar ? a.glow : "rgba(255,255,255,0.18)", boxShadow: k === inBar ? `0 0 ${8 + pulse * 18}px ${a.glow}` : "none", transform: `scale(${k === inBar ? 1 + pulse * 0.35 : 1})` }} />
          ))}
        </div>
      </div>
    </div>
  );
};

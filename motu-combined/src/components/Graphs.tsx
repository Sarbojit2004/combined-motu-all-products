import React from "react";
import { interpolate, random } from "remotion";
import { FONT, INK } from "../theme.ts";

// ─────────────────────────────────────────────────────────────────────────────
// DEMONSTRATIVES — the numbers drawn, not just printed. Every graph is SVG,
// sized to the box it is given, driven by the local frame f (so it builds in
// when it arrives) and by the music's beat phase (so it moves with the track).
// ─────────────────────────────────────────────────────────────────────────────

export type GraphProps = { w: number; h: number; glow: string; f: number; t: number; beat: number; value?: number; io?: [string, number, number][] };

const clamp = (x: number) => Math.min(1, Math.max(0, x));
const ease = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
const phaseOf = (t: number, beat: number) => ((t / beat) % 1 + 1) % 1;
const label = (s: number): React.CSSProperties => ({ fontFamily: FONT.display, fontSize: s, letterSpacing: s * 0.14, fill: INK.onDarkSoft });

/** A 32-band analyser that hits on every beat. */
export const Spectrum: React.FC<GraphProps> = ({ w, h, glow, f, t, beat }) => {
  const n = 32;
  const ph = phaseOf(t, beat);
  const hit = Math.exp(-ph * 4.2);
  const bw = w / n;
  const build = ease(f / 18);
  return (
    <svg width={w} height={h}>
      {Array.from({ length: n }).map((_, i) => {
        const base = 0.25 + 0.55 * Math.exp(-Math.pow((i - 6) / 9, 2)) + 0.2 * Math.exp(-Math.pow((i - 22) / 6, 2));
        const jit = 0.55 + 0.45 * Math.sin(t * (3 + random(`s${i}`) * 5) + i);
        const v = clamp(base * (0.45 + 0.55 * hit) * jit) * build;
        const bh = v * h;
        return <rect key={i} x={i * bw + bw * 0.14} y={h - bh} width={bw * 0.72} height={bh} rx={bw * 0.18} fill={glow} opacity={0.35 + v * 0.65} />;
      })}
    </svg>
  );
};

/** Dynamic range as a sweeping arc gauge that counts up to its figure. */
export const RangeArc: React.FC<GraphProps> = ({ w, h, glow, f, value = 120 }) => {
  const cx = w * 0.5, cy = h * 0.92, r = Math.min(w * 0.42, h * 0.8);
  const p = ease(f / 28) * (value / 140);
  const a0 = Math.PI, a1 = Math.PI + Math.PI * p;
  const pt = (a: number, rr = r) => [cx + rr * Math.cos(a), cy + rr * Math.sin(a)];
  const [x0, y0] = pt(a0), [x1, y1] = pt(a1);
  const s = h * 0.1;
  return (
    <svg width={w} height={h}>
      <path d={`M ${pt(Math.PI)[0]} ${pt(Math.PI)[1]} A ${r} ${r} 0 0 1 ${pt(0)[0]} ${pt(0)[1]}`} stroke="rgba(255,255,255,0.14)" strokeWidth={s * 0.55} fill="none" strokeLinecap="round" />
      <path d={`M ${x0} ${y0} A ${r} ${r} 0 0 1 ${x1} ${y1}`} stroke={glow} strokeWidth={s * 0.55} fill="none" strokeLinecap="round" />
      {Array.from({ length: 15 }).map((_, i) => {
        const a = Math.PI + (Math.PI * i) / 14;
        const [ax, ay] = pt(a, r * 0.8), [bx, by] = pt(a, r * (i % 2 ? 0.86 : 0.9));
        return <line key={i} x1={ax} y1={ay} x2={bx} y2={by} stroke="rgba(255,255,255,0.35)" strokeWidth={3} />;
      })}
      <text x={cx} y={cy - r * 0.22} textAnchor="middle" style={{ fontFamily: FONT.display, fontSize: s * 2.3, fill: INK.onDark }}>
        {Math.round(ease(f / 28) * value)}
        <tspan style={{ fontSize: s * 1.0, fill: glow }}> dB</tspan>
      </text>
      <text x={cx} y={cy} textAnchor="middle" style={label(s * 0.62)}>DYNAMIC RANGE</text>
    </svg>
  );
};

/** Round-trip latency — a signal leaves, returns, and the gap is measured. */
export const Latency: React.FC<GraphProps> = ({ w, h, glow, f, value = 2.5 }) => {
  const n = 120;
  const pts = (shift: number) =>
    Array.from({ length: n }).map((_, i) => {
      const x = (i / (n - 1)) * w;
      const u = i / (n - 1) - shift;
      const y = h * 0.45 - Math.exp(-Math.pow((u - 0.28) / 0.035, 2)) * h * 0.32 * Math.cos((u - 0.28) * 90);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });
  const draw = ease(f / 24);
  const gap = 0.32 * draw;
  const s = h * 0.1;
  return (
    <svg width={w} height={h}>
      <line x1={0} y1={h * 0.45} x2={w} y2={h * 0.45} stroke="rgba(255,255,255,0.12)" strokeWidth={2} />
      <polyline points={pts(0).join(" ")} fill="none" stroke="rgba(255,255,255,0.7)" strokeWidth={4} />
      <polyline points={pts(gap).join(" ")} fill="none" stroke={glow} strokeWidth={5} opacity={draw}  />
      <line x1={w * 0.28} y1={h * 0.78} x2={w * (0.28 + gap)} y2={h * 0.78} stroke={glow} strokeWidth={4} />
      <line x1={w * 0.28} y1={h * 0.7} x2={w * 0.28} y2={h * 0.86} stroke={glow} strokeWidth={3} />
      <line x1={w * (0.28 + gap)} y1={h * 0.7} x2={w * (0.28 + gap)} y2={h * 0.86} stroke={glow} strokeWidth={3} />
      <text x={w * (0.28 + gap) + s * 0.6} y={h * 0.84} style={{ fontFamily: FONT.display, fontSize: s * 1.5, fill: INK.onDark }}>
        {(value * draw).toFixed(1)} ms
      </text>
      <text x={0} y={h * 0.12} style={label(s * 0.62)}>ROUND-TRIP LATENCY · IN → OUT</text>
    </svg>
  );
};

/** Inputs and outputs per unit, as lit channel ladders. */
export const IoBars: React.FC<GraphProps> = ({ w, h, glow, f, io = [] }) => {
  const rows = io.length || 1;
  const rh = h / rows;
  const max = Math.max(...io.map((r) => Math.max(r[1], r[2])), 1);
  const s = Math.min(rh * 0.24, h * 0.1);
  const lw = w * 0.26;
  return (
    <svg width={w} height={h}>
      {io.map(([name, ins, outs], ri) => {
        const y = ri * rh;
        const cw = (w - lw) / max;
        const lit = (k: number, total: number) => clamp((f - ri * 6 - (k / total) * 18) / 4);
        return (
          <g key={name}>
            <text x={0} y={y + rh * 0.42} style={{ fontFamily: FONT.display, fontSize: s, fill: INK.onDark }}>{name}</text>
            <text x={0} y={y + rh * 0.8} style={label(s * 0.62)}>{Math.round(ease((f - ri * 6) / 22) * ins)} IN · {Math.round(ease((f - ri * 6) / 22) * outs)} OUT</text>
            {Array.from({ length: ins }).map((_, k) => (
              <rect key={`i${k}`} x={lw + k * cw} y={y + rh * 0.14} width={cw * 0.7} height={rh * 0.3} rx={cw * 0.2} fill={glow} opacity={0.15 + 0.85 * lit(k, ins)} />
            ))}
            {Array.from({ length: outs }).map((_, k) => (
              <rect key={`o${k}`} x={lw + k * cw} y={y + rh * 0.52} width={cw * 0.7} height={rh * 0.3} rx={cw * 0.2} fill="#FFFFFF" opacity={0.08 + 0.6 * lit(k, outs)} />
            ))}
          </g>
        );
      })}
    </svg>
  );
};

/** An AVB network: a switch at the centre, units locking on, packets on every link. */
export const Network: React.FC<GraphProps> = ({ w, h, glow, f, t, beat }) => {
  const cx = w / 2, cy = h / 2;
  const names = ["16A", "848", "10pre", "MAC", "16A", "848"];
  const nodes = names.map((n, i) => {
    const a = -Math.PI / 2 + (i / names.length) * Math.PI * 2;
    return { n, x: cx + Math.cos(a) * w * 0.38, y: cy + Math.sin(a) * h * 0.38 };
  });
  const s = h * 0.085;
  const ph = phaseOf(t, beat);
  return (
    <svg width={w} height={h}>
      {nodes.map((nd, i) => {
        const on = ease((f - 6 - i * 5) / 10);
        const k = (ph + i * 0.17) % 1;
        return (
          <g key={i} opacity={0.2 + 0.8 * on}>
            <line x1={cx} y1={cy} x2={cx + (nd.x - cx) * on} y2={cy + (nd.y - cy) * on} stroke={glow} strokeWidth={4} opacity={0.6} />
            <circle cx={cx + (nd.x - cx) * k} cy={cy + (nd.y - cy) * k} r={s * 0.18} fill="#FFFFFF" opacity={on} />
            <rect x={nd.x - s * 1.5} y={nd.y - s * 0.6} width={s * 3} height={s * 1.2} rx={s * 0.3} fill="#111118" stroke={glow} strokeWidth={3} />
            <text x={nd.x} y={nd.y + s * 0.28} textAnchor="middle" style={{ fontFamily: FONT.display, fontSize: s * 0.72, fill: INK.onDark }}>{nd.n}</text>
          </g>
        );
      })}
      <rect x={cx - s * 2.3} y={cy - s * 0.8} width={s * 4.6} height={s * 1.6} rx={s * 0.4} fill={glow} />
      <text x={cx} y={cy + s * 0.3} textAnchor="middle" style={{ fontFamily: FONT.display, fontSize: s * 0.8, fill: "#08080B" }}>AVB SWITCH</text>
    </svg>
  );
};

/** A 4-band parametric EQ, the bands breathing with the track. */
export const EqCurve: React.FC<GraphProps> = ({ w, h, glow, f, t }) => {
  const bands = [
    { f: 0.14, g: 0.22 + 0.08 * Math.sin(t * 1.3), q: 0.08 },
    { f: 0.36, g: -0.18 + 0.06 * Math.sin(t * 1.7 + 1), q: 0.07 },
    { f: 0.6, g: 0.14 + 0.1 * Math.sin(t * 1.1 + 2), q: 0.06 },
    { f: 0.84, g: 0.2 + 0.06 * Math.sin(t * 0.9 + 3), q: 0.1 },
  ];
  const build = ease(f / 22);
  const n = 140;
  const y = (x: number) => h * 0.5 - build * h * 0.9 * bands.reduce((acc, b) => acc + b.g * Math.exp(-Math.pow((x - b.f) / b.q, 2)), 0);
  const d = Array.from({ length: n }).map((_, i) => `${i ? "L" : "M"} ${(i / (n - 1)) * w} ${y(i / (n - 1))}`).join(" ");
  return (
    <svg width={w} height={h}>
      {[0.25, 0.5, 0.75].map((g) => <line key={g} x1={0} x2={w} y1={h * g} y2={h * g} stroke="rgba(255,255,255,0.08)" strokeWidth={2} />)}
      {[0.1, 0.3, 0.5, 0.7, 0.9].map((g) => <line key={g} y1={0} y2={h} x1={w * g} x2={w * g} stroke="rgba(255,255,255,0.06)" strokeWidth={2} />)}
      <path d={`${d} L ${w} ${h} L 0 ${h} Z`} fill={glow} opacity={0.12} />
      <path d={d} stroke={glow} strokeWidth={22} fill="none" opacity={0.18} /><path d={d} stroke={glow} strokeWidth={6} fill="none" />
      {bands.map((b, i) => (
        <circle key={i} cx={b.f * w} cy={y(b.f)} r={h * 0.05} fill="#08080B" stroke="#FFFFFF" strokeWidth={4} opacity={build} />
      ))}
      <text x={0} y={h * 0.1} style={label(h * 0.065)}>4-BAND PARAMETRIC EQ</text>
    </svg>
  );
};

/** A compressor's transfer curve with the signal riding it, and gain reduction beside it. */
export const CompCurve: React.FC<GraphProps> = ({ w, h, glow, f, t, beat }) => {
  const gw = Math.min(w * 0.7, h * 1.4);
  const th = 0.55, ratio = 4;
  const out = (x: number) => (x < th ? x : th + (x - th) / ratio);
  const ph = phaseOf(t, beat);
  const lvl = 0.35 + 0.55 * Math.exp(-ph * 3.2);
  const build = ease(f / 20);
  const n = 60;
  const d = Array.from({ length: n }).map((_, i) => {
    const x = i / (n - 1);
    return `${i ? "L" : "M"} ${x * gw} ${h - out(x) * h * build - (1 - build) * x * h}`;
  }).join(" ");
  const gr = Math.max(0, lvl - out(lvl));
  return (
    <svg width={w} height={h}>
      <rect x={0} y={0} width={gw} height={h} fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.1)" />
      <line x1={0} y1={h} x2={gw} y2={0} stroke="rgba(255,255,255,0.14)" strokeDasharray="10 10" strokeWidth={2} />
      <path d={d} stroke={glow} strokeWidth={20} fill="none" opacity={0.18} /><path d={d} stroke={glow} strokeWidth={6} fill="none" />
      <circle cx={lvl * gw} cy={h - out(lvl) * h} r={h * 0.045} fill="#FFFFFF" opacity={build} />
      <rect x={gw + w * 0.08} y={0} width={w * 0.07} height={h} fill="rgba(255,255,255,0.06)" />
      <rect x={gw + w * 0.08} y={0} width={w * 0.07} height={gr * h * 2.2} fill={glow} />
      <text x={gw + w * 0.18} y={h * 0.22} style={{ fontFamily: FONT.display, fontSize: h * 0.1, fill: INK.onDark }}>4:1</text>
      <text x={gw + w * 0.18} y={h * 0.36} style={label(h * 0.06)}>RATIO</text>
      <text x={gw + w * 0.18} y={h * 0.62} style={{ fontFamily: FONT.display, fontSize: h * 0.1, fill: glow }}>−{(gr * 24).toFixed(1)}</text>
      <text x={gw + w * 0.18} y={h * 0.76} style={label(h * 0.06)}>dB GR</text>
    </svg>
  );
};

/** Stereo meters — peak-hold, green to amber to red, riding the music. */
export const Meters: React.FC<GraphProps> = ({ w, h, glow, f, t, beat }) => {
  const ch = 8;
  const ph = phaseOf(t, beat);
  const cw = w / ch;
  const build = ease(f / 16);
  return (
    <svg width={w} height={h}>
      {Array.from({ length: ch }).map((_, i) => {
        const v = clamp((0.45 + 0.45 * Math.exp(-((ph + i * 0.07) % 1) * 3.5)) * (0.8 + 0.2 * Math.sin(t * 7 + i * 1.7))) * build;
        const segs = 20;
        return (
          <g key={i}>
            {Array.from({ length: segs }).map((_, k) => {
              const on = k / segs < v;
              const c = k > segs * 0.85 ? "#FF4B4B" : k > segs * 0.68 ? "#FFC24A" : glow;
              return <rect key={k} x={i * cw + cw * 0.16} y={h - (k + 1) * (h / segs) + 2} width={cw * 0.68} height={h / segs - 5} rx={3} fill={c} opacity={on ? 0.95 : 0.1} />;
            })}
          </g>
        );
      })}
    </svg>
  );
};

export const GRAPHS: Record<string, React.FC<GraphProps>> = {
  spectrum: Spectrum, range: RangeArc, latency: Latency, io: IoBars, network: Network, eq: EqCurve, comp: CompCurve, meters: Meters,
};

export { interpolate };

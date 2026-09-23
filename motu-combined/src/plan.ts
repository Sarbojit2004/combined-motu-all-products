import reelPlan from "./plan-reel.json";
import videoPlan from "./plan-video.json";
import type { TransitionKind } from "./transitions-data.ts";
import type { ProductKey } from "./theme.ts";

// ─────────────────────────────────────────────────────────────────────────────
// Types for the plan JSON written by scripts/plan.py — the one beat grid that
// the picture, the captions, the SFX and the music edit are all cut to.
// ─────────────────────────────────────────────────────────────────────────────

export type TimedCaption = { start: number; end: number; t: string; e?: string; beat?: boolean };

export type Move = "gimbalL" | "gimbalR" | "zoomIn" | "zoomOut" | "focusIn" | "focusOut" | "craneUp" | "orbit";

export type Shot = {
  kind: "still" | "broll" | "dsp" | "lineup";
  assets?: string[];
  id?: string;
  file?: string;
  label?: string;
  b0: number;
  b1: number;
  start: number;
  end: number;
  section: string;
  move: Move;
  trans: TransitionKind;
};

export type Icon = [kind: string, value: number, unit: string, label: string];

export type Section = {
  id: string;
  series: ProductKey;
  label: string;
  sub: string;
  start: number;
  end: number;
  drop: boolean;
  top: { graph?: string; value?: number; io?: [string, number, number][]; icons?: Icon[] };
  ticker: string[];
  captions: TimedCaption[];
};

export type Plan = {
  name: string;
  bpm: number;
  beat: number;
  offset: number;
  shots: Shot[];
  sections: Section[];
  outroAt: number | null;
  sfx: { at: number; cue: string }[];
};

export const REEL_PLAN = reelPlan as unknown as Plan;
export const VIDEO_PLAN = videoPlan as unknown as Plan;

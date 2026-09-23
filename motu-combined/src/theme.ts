// ─────────────────────────────────────────────────────────────────────────────
// THEME — MOTU combined film (M-Series · UltraLite-mk5 / 828 · AVB Series).
//
// The same system as the individual MOTU films: the brush-script key word and
// black sans, the three-tier caption lockup, the 64%-opaque typographic layer
// with a hard drop shadow, and no branding until the (landscape) end screen.
// What is new: one accent per SERIES, because this film moves between three
// families, and the colour is what tells a viewer which one is on screen.
// ─────────────────────────────────────────────────────────────────────────────

export type Canvas = {
  width: number;
  height: number;
  fps: number;
  durationInFrames: number;
  safe: { left: number; right: number; top: number; bottom: number };
  scale: number;
  portrait: boolean;
};

export const FPS = 30;
export const sec = (s: number) => Math.round(s * FPS);

/** 180.000 s vertical reel, 2160 × 3840. */
export const REEL: Canvas = {
  width: 2160,
  height: 3840,
  fps: FPS,
  durationInFrames: 5400,
  safe: { left: 132, right: 200, top: 300, bottom: 720 },
  scale: 1,
  portrait: true,
};

/** 300.000 s landscape video, 3840 × 2160. */
export const VIDEO: Canvas = {
  width: 3840,
  height: 2160,
  fps: FPS,
  durationInFrames: 9000,
  safe: { left: 200, right: 200, top: 120, bottom: 230 },
  scale: 0.72,
  portrait: false,
};

export const safeW = (c: Canvas) => c.width - c.safe.left - c.safe.right;
export const safeH = (c: Canvas) => c.height - c.safe.top - c.safe.bottom;

export const TYPE_OPACITY = 0.64;

export const GROUND = {
  light: "#F2EFE9",
  lightLift: "#FAF8F4",
  lightSink: "#E6E2D9",
  dark: "#07070A",
  darkLift: "#121218",
  darkSink: "#040405",
} as const;

export const INK = {
  onLight: "#16140F",
  onLightSoft: "#4A4740",
  onLightDim: "#A8A399",
  onDark: "#FBFAF7",
  onDarkSoft: "#B9B6AE",
  onDarkDim: "#5E5C57",
} as const;

export type ProductKey = "m" | "ul828" | "avb" | "all" | "shared";

export const ACCENT: Record<ProductKey, { key: string; glow: string; name: string; short: string; tag: string }> = {
  // M-Series — the desktop trio. Ember: warm, personal, the first interface.
  m: { key: "#C2410C", glow: "#FF8A4C", name: "M-SERIES", short: "M-SERIES", tag: "M2 · M4 · M6" },
  // UltraLite-mk5 & 828 — the studio pair. Teal: the display glass.
  ul828: { key: "#0E7C7B", glow: "#3FE3D2", name: "ULTRALITE-mk5 · 828", short: "ULTRALITE · 828", tag: "18 × 22 · 28 × 32" },
  // AVB — the network. Indigo: the cable, the rack.
  avb: { key: "#3446C9", glow: "#8B97FF", name: "AVB SERIES", short: "AVB SERIES", tag: "16A · 848 · 10pre · SWITCH" },
  // The film as a whole — the hook, the field, the family.
  all: { key: "#B8801E", glow: "#FFC24A", name: "MOTU", short: "ALL SERIES", tag: "M · ULTRALITE · 828 · AVB" },
  shared: { key: "#B8801E", glow: "#FFC24A", name: "MOTU", short: "ALL SERIES", tag: "M · ULTRALITE · 828 · AVB" },
};

/** What each asset's product code reads as on screen. */
export const PRODUCT_NAME: Record<string, string> = {
  m2: "MOTU M2", m4: "MOTU M4", m6: "MOTU M6", m: "M-SERIES",
  ul: "ULTRALITE-mk5", "828": "MOTU 828", ul828: "ULTRALITE-mk5 · 828",
  "16a": "MOTU 16A", "848": "MOTU 848", "10pre": "MOTU 10pre", avb: "AVB SERIES", switch: "AVB SWITCH",
};

export const FONT = {
  script: "'ReelScript', 'Brush Script MT', cursive",
  display: "'ReelDisplay', 'Archivo Black', 'Helvetica Neue', Arial, sans-serif",
} as const;

export const TYPE = {
  before: { size: 92, track: 5.6 },
  script: { size: 348, track: -2 },
  after: { size: 128, track: 2.2 },
  chapter: { size: 46, track: 6.0 },
  micro: { size: 30, track: 3.0 },
} as const;

// ── Contact — landscape end screen only ─────────────────────────────────────
export const CONTACT = {
  brand: "SHIVANSH ELECTRONICS",
  city: "KOLKATA",
  site: "www.shivanshelectronics.in",
  whatsapp: ["+91 98316 62458", "+91 89818 07755", "+91 91477 00677"],
  role: "Shivansh Electronics is the Exclusive Partner of MOTU",
  region: "for East & North-East India",
} as const;

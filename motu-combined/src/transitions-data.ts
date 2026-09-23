// Pure data for the transitions — no JSX, so Node scripts can import it to
// derive the SFX cue sheet from exactly the same table the film renders from.

export type TransitionKind =
  | "fade"
  | "wipeDiag"
  | "whipLeft"
  | "whipRight"
  | "punchIn"
  | "pullBack"
  | "slideUp"
  | "flash";

/** Frames each move takes. Longer than a cut, shorter than a dissolve. */
export const TRANS: Record<TransitionKind, number> = {
  fade: 11,
  wipeDiag: 13,
  whipLeft: 9,
  whipRight: 9,
  punchIn: 8,
  pullBack: 10,
  slideUp: 11,
  flash: 7,
};

/** The biggest moves are held back for the moments the narration also turns. */
const BOUNDARY: TransitionKind[] = ["wipeDiag", "whipLeft", "flash", "whipRight", "slideUp"];
const INSIDE: TransitionKind[] = ["punchIn", "pullBack", "fade", "slideUp", "punchIn", "wipeDiag"];

export const transitionFor = (seed: number, boundary: boolean, first: boolean): TransitionKind => {
  if (first) return "fade";
  return boundary ? BOUNDARY[seed % BOUNDARY.length] : INSIDE[seed % INSIDE.length];
};

/** Which SFX cue belongs under each move — the other half of gen_audio.py's table. */
export const TRANS_CUE: Record<TransitionKind, string> = {
  fade: "air-pass",
  wipeDiag: "gate-snap",
  whipLeft: "slide-air",
  whipRight: "slide-air",
  punchIn: "impact-soft",
  pullBack: "impact-soft",
  slideUp: "riser-short",
  flash: "chime-lift",
};

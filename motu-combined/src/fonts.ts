import { staticFile } from "remotion";

// ─────────────────────────────────────────────────────────────────────────────
// THE TYPE PAIRING — the same two roles as the M-Series reel, same files, same
// swap point:
//
//   script  role  ->  public/fonts/script.ttf   (Pacifico; drop Brittanic here)
//   display role  ->  public/fonts/display.ttf  (Archivo Black; drop Lo-Flicker here)
//
// Every size and offset is expressed relative to the role, so the lockup
// re-flows to whatever face is behind it.
// ─────────────────────────────────────────────────────────────────────────────

export const SCRIPT = "ReelScript";
export const DISPLAY = "ReelDisplay";

export const FONT_FACE_CSS = `
@font-face {
  font-family: '${SCRIPT}';
  src: url('${staticFile("fonts/script.ttf")}') format('truetype');
  font-weight: 400; font-style: normal; font-display: block;
}
@font-face {
  font-family: '${DISPLAY}';
  src: url('${staticFile("fonts/display.ttf")}') format('truetype');
  font-weight: 400 900; font-style: normal; font-display: block;
}
`;

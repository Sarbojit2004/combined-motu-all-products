import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { ACCENT, FONT, GROUND, TYPE_OPACITY, sec, safeW, type Canvas } from "./theme.ts";
import type { Plan } from "./plan.ts";
import { Caption } from "./components/Caption.tsx";
import { TRANS, TransitionIn } from "./components/Transitions.tsx";
import { ShotView } from "./components/Shots.tsx";
import { BottomBar, TopBar } from "./components/Bars.tsx";
import { Outro } from "./components/Outro.tsx";

// ─────────────────────────────────────────────────────────────────────────────
// THE FILM — one composition, two canvases, one plan (src/plan-*.json).
//
//   1. picture   every shot on the beat grid, each one overlapping the next by
//                the incoming transition so nothing ever dips to black
//   2. scrims    gradients only where the bars and captions sit
//   3. overlay   top bar · burned-in caption lockup (64%) · bottom bar
//   4. end screen  the landscape video only — the reel has none by request
// ─────────────────────────────────────────────────────────────────────────────

export type FilmProps = { canvas: Canvas; plan: Plan; mix: string };

const ShotLayer: React.FC<{ plan: Plan; i: number; canvas: Canvas }> = ({ plan, i, canvas }) => {
  const f = useCurrentFrame();
  const shot = plan.shots[i];
  const s = plan.sections.find((x) => x.id === shot.section)!;
  const dur = Math.max(1, sec(shot.end) - sec(shot.start));
  const t = shot.start + f / canvas.fps - plan.offset;
  return (
    <TransitionIn kind={shot.trans} f={f} accent={ACCENT[s.series].glow} canvas={canvas}>
      <ShotView shot={shot} canvas={canvas} f={f} dur={dur} series={s.series} beat={plan.beat} t={t} />
    </TransitionIn>
  );
};

const OutroLayer: React.FC<{ canvas: Canvas }> = ({ canvas }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ opacity: interpolate(f, [0, 14], [0, 1], { extrapolateRight: "clamp" }) }}>
      <Outro canvas={canvas} />
    </AbsoluteFill>
  );
};

export const Film: React.FC<FilmProps> = ({ canvas, plan, mix }) => {
  const S = canvas.scale;
  const end = plan.outroAt ?? canvas.durationInFrames / canvas.fps;
  const endF = Math.min(canvas.durationInFrames, sec(end));
  const sw = safeW(canvas);
  const P = canvas.portrait;

  return (
    <AbsoluteFill style={{ background: GROUND.dark, fontFamily: FONT.display }}>
      {plan.shots.map((s, i) => {
        const from = sec(s.start);
        const next = plan.shots[i + 1];
        const tail = next ? TRANS[next.trans] : plan.outroAt ? 16 : 0;
        const dur = Math.max(1, Math.min(canvas.durationInFrames, sec(s.end) + tail) - from);
        return (
          <Sequence key={i} from={from} durationInFrames={dur}>
            <ShotLayer plan={plan} i={i} canvas={canvas} />
          </Sequence>
        );
      })}

      <Sequence from={0} durationInFrames={endF}>
        {P ? (
          <>
            <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(4,4,6,0.78) 0%, rgba(4,4,6,0.5) 22%, rgba(4,4,6,0) 31%)" }} />
            <AbsoluteFill style={{ background: "linear-gradient(0deg, rgba(4,4,6,0.6) 0%, rgba(4,4,6,0.5) 26%, rgba(4,4,6,0) 40%)" }} />
          </>
        ) : (
          <>
            <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(4,4,6,0.72) 0%, rgba(4,4,6,0.42) 16%, rgba(4,4,6,0) 28%)" }} />
            <AbsoluteFill style={{ background: "linear-gradient(20deg, rgba(4,4,6,0.72) 0%, rgba(4,4,6,0.34) 28%, rgba(4,4,6,0) 48%)" }} />
          </>
        )}
      </Sequence>

      <Sequence from={0} durationInFrames={endF}>
        <AbsoluteFill style={{ opacity: 0.92 }}>
          <TopBar plan={plan} canvas={canvas} />
          <BottomBar plan={plan} canvas={canvas} shots={plan.shots} />
        </AbsoluteFill>
        <AbsoluteFill style={{ opacity: TYPE_OPACITY }}>
          {plan.sections.map((s) =>
            s.captions.map((c, i) => {
              const from = sec(c.start);
              const d = Math.max(1, Math.min(endF, sec(c.end)) - from);
              return (
                <Sequence key={`${s.id}-${i}`} from={from} durationInFrames={d}>
                  <div style={{ position: "absolute", left: canvas.safe.left, width: P ? sw : sw * 0.62, bottom: P ? canvas.safe.bottom + 150 : 250 }}>
                    <Caption caption={c} startFrame={0} product={s.series} env="dark" scale={S} />
                  </div>
                </Sequence>
              );
            }),
          )}
        </AbsoluteFill>
      </Sequence>

      {plan.outroAt ? (
        <Sequence from={endF} durationInFrames={canvas.durationInFrames - endF}>
          <OutroLayer canvas={canvas} />
        </Sequence>
      ) : null}

      <Audio src={staticFile(`audio/${mix}`)} />
    </AbsoluteFill>
  );
};

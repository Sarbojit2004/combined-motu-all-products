import React from "react";
import { AbsoluteFill, Img, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { ACCENT, CONTACT, FONT, GROUND, INK, type Canvas, safeW } from "../theme.ts";
import { SiteIcon, WhatsAppIcon } from "./Icons.tsx";

// ─────────────────────────────────────────────────────────────────────────────
// THE END SCREEN — the only place any brand mark appears.
//
// A dark room and a cream CARD inside it that the two logos are native to
// (both supplied logos are dark artwork on white plates). The card is also what
// makes three phone numbers legible: they sit on a solid ground.
//
// Portrait: one stacked card. Landscape: the logos and the distributor line on
// the left, the numbers and the website on the right.
// ─────────────────────────────────────────────────────────────────────────────

const WA = "#128C7E";
const SITE = "#1F5FD0";

export const Outro: React.FC<{ canvas: Canvas }> = ({ canvas }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = ACCENT.shared;
  const S = (n: number) => n * (canvas.portrait ? 1 : 0.78);

  const rise = spring({ frame: f, fps, config: { damping: 200, mass: 0.8 }, durationInFrames: 26 });
  const at = (d: number, dur = 16) => spring({ frame: f - d, fps, config: { damping: 200, mass: 0.5 }, durationInFrames: dur });
  const dolly = 1 + (Math.min(f, 240) / 240) * 0.035;

  const Room = (
    <>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 88% 52% at 50% 40%, #1B1B22 0%, #0C0C10 54%, #050507 100%)" }} />
      <AbsoluteFill
        style={{
          opacity: 0.42 * rise,
          backgroundImage:
            "repeating-linear-gradient(0deg, rgba(255,255,255,0.075) 0 2px, rgba(0,0,0,0) 2px 132px)," +
            "repeating-linear-gradient(90deg, rgba(255,255,255,0.075) 0 2px, rgba(0,0,0,0) 2px 132px)",
          transform: `scale(${dolly})`,
        }}
      />
      {Array.from({ length: 26 }).map((_, i) => {
        const rx = random(`ox${i}`);
        const ry = random(`oy${i}`);
        const rs = random(`os${i}`);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: rx * canvas.width,
              top: ry * canvas.height,
              width: 4 + rs * 7,
              height: 4 + rs * 7,
              borderRadius: "50%",
              background: "rgba(255,246,233,0.5)",
              opacity: (0.16 + rs * 0.3) * rise,
              transform: `translateY(${Math.sin((f + i * 24) / 78) * 22}px)`,
            }}
          />
        );
      })}
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 66% 32% at 50% 86%, ${accent.glow}14 0%, rgba(0,0,0,0) 72%)` }} />
    </>
  );

  // The four, once more, as a strip of names in their accents.
  const Strip = (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: S(44),
        opacity: at(4),
        transform: `translateY(${interpolate(at(4), [0, 1], [-30, 0])}px)`,
        flexWrap: "nowrap",
      }}
    >
      {([["m", "M-SERIES"], ["ul828", "ULTRALITE-mk5"], ["ul828", "828"], ["avb", "AVB SERIES"]] as const).map(([k, label], i) => (
        <React.Fragment key={label}>
          {i ? <div style={{ width: 12, height: 12, borderRadius: 6, background: "rgba(255,246,233,0.35)" }} /> : null}
          <div style={{ fontSize: S(80), letterSpacing: 6, color: ACCENT[k].glow, textShadow: "0 6px 14px rgba(0,0,0,0.9)", whiteSpace: "nowrap" }}>
            {label}
          </div>
        </React.Fragment>
      ))}
    </div>
  );

  const Logos = (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: S(74), paddingBottom: S(44), opacity: at(6) }}>
      <Img src={staticFile("logos/shivansh.png")} style={{ height: S(258), width: "auto" }} />
      <div style={{ width: 3, height: S(188), background: "rgba(24,22,20,0.16)" }} />
      <Img src={staticFile("logos/motu.png")} style={{ height: S(210), width: "auto" }} />
    </div>
  );

  const Role = (
    <div style={{ textAlign: "center", fontSize: S(43), letterSpacing: 3.0, lineHeight: 1.5, color: INK.onLightSoft, textTransform: "uppercase", opacity: at(12) }}>
      {CONTACT.role}
      <br />
      <span style={{ color: accent.key, letterSpacing: 4.0 }}>{CONTACT.region}</span>
    </div>
  );

  const Numbers = (
    <>
      {CONTACT.whatsapp.map((num, i) => {
        const p = at(20 + i * 6, 15);
        return (
          <div
            key={num}
            style={{
              display: "flex",
              alignItems: "center",
              gap: S(40),
              padding: `${S(30)}px 0`,
              borderBottom: "2px solid rgba(24,22,20,0.10)",
              opacity: p,
              transform: `translateX(${interpolate(p, [0, 1], [-30, 0])}px)`,
            }}
          >
            <WhatsAppIcon size={S(104)} color={WA} />
            <div style={{ fontSize: S(92), letterSpacing: 1.4, color: INK.onLight, fontVariantNumeric: "tabular-nums", whiteSpace: "nowrap" }}>{num}</div>
          </div>
        );
      })}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: S(34),
          padding: `${S(30)}px 0 ${S(6)}px`,
          opacity: at(42, 15),
          transform: `translateX(${interpolate(at(42, 15), [0, 1], [-30, 0])}px)`,
        }}
      >
        <SiteIcon size={S(98)} color={SITE} />
        <div style={{ fontSize: S(76), letterSpacing: 0.6, color: INK.onLight, whiteSpace: "nowrap" }}>{CONTACT.site}</div>
      </div>
    </>
  );

  const Footer = (
    <div style={{ textAlign: "center", paddingTop: S(40), fontSize: S(46), letterSpacing: 7, color: INK.onLightSoft, opacity: at(50, 16) }}>
      {CONTACT.brand} · {CONTACT.city}
    </div>
  );

  const cardStyle: React.CSSProperties = {
    background: `linear-gradient(180deg, ${GROUND.lightLift} 0%, ${GROUND.light} 62%, ${GROUND.lightSink} 100%)`,
    borderRadius: S(56),
    boxShadow: "0 46px 120px rgba(0,0,0,0.72)",
    border: "3px solid rgba(255,255,255,0.22)",
    opacity: rise,
  };

  if (canvas.portrait) {
    return (
      <AbsoluteFill style={{ background: GROUND.dark, fontFamily: FONT.display, overflow: "hidden" }}>
        {Room}
        <div style={{ position: "absolute", left: canvas.safe.left, width: safeW(canvas), top: canvas.safe.top + 40 }}>{Strip}</div>
        <div
          style={{
            position: "absolute",
            left: canvas.safe.left,
            width: safeW(canvas),
            top: "53%",
            transform: `translateY(-50%) translateY(${interpolate(rise, [0, 1], [90, 0])}px) scale(${interpolate(rise, [0, 1], [0.94, 1])})`,
            padding: "96px 82px 82px",
            ...cardStyle,
          }}
        >
          {Logos}
          {Role}
          <div style={{ height: 3, background: "rgba(24,22,20,0.14)", margin: "48px 0 12px", opacity: at(16) }} />
          {Numbers}
        </div>
      </AbsoluteFill>
    );
  }

  // Landscape: strip on top, one wide card with two columns.
  const cardW = Math.min(safeW(canvas), 3000);
  return (
    <AbsoluteFill style={{ background: GROUND.dark, fontFamily: FONT.display, overflow: "hidden" }}>
      {Room}
      <div style={{ position: "absolute", left: 0, right: 0, top: canvas.safe.top + 10 }}>{Strip}</div>
      <div
        style={{
          position: "absolute",
          left: (canvas.width - cardW) / 2,
          width: cardW,
          top: "56%",
          transform: `translateY(-50%) translateY(${interpolate(rise, [0, 1], [70, 0])}px) scale(${interpolate(rise, [0, 1], [0.95, 1])})`,
          padding: `${S(70)}px ${S(90)}px ${S(60)}px`,
          display: "grid",
          gridTemplateColumns: "1.05fr 1fr",
          columnGap: S(90),
          alignItems: "center",
          ...cardStyle,
        }}
      >
        <div>
          {Logos}
          {Role}
        </div>
        <div style={{ borderLeft: "3px solid rgba(24,22,20,0.14)", paddingLeft: S(70) }}>{Numbers}</div>
      </div>
    </AbsoluteFill>
  );
};

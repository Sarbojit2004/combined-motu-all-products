#!/usr/bin/env python3
"""THE PLAN — one beat grid drives picture, captions, SFX and the music edit.

"On & On" runs at 174 BPM (beat 0.344828 s, first beat at 0.2047 s in the
source). Every shot, caption and section boundary below is a whole number of
OUTPUT beats, so every cut lands on the music. This script writes:

    src/plan-reel.json   src/plan-video.json   — read by the Remotion film
    audio-src/edit-*.json                       — read by scripts/audio.py

Nothing downstream types a frame number.
"""
import json, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
A = json.load(open(os.path.join(HERE, "assets.json")))
BY = {a["slug"]: a for a in A}

BPM = 174.0
BEAT = 60.0 / BPM
SRC_FIRST_BEAT = 0.2047
FPS = 30

# ── B-roll: 5 kept from the first set + 6 deployment reveals ────────────────
BROLL = {
    "b01": ("broll/b01-control-room-stack.mp4", "10pre · 16A · 828 — control room"),
    "b04": ("broll/b04-guitar-rig.mp4", "828 · UltraLite-mk5 — guitar rig"),
    "b05": ("broll/b05-laptop-rig.mp4", "16A · 828 — laptop rig"),
    "b07": ("broll/b07-live-duo.mp4", "UltraLite-mk5 — live duo"),
    "b10": ("broll/b10-network-desk.mp4", "CueMix Pro — AVB network"),
    "d01": ("broll/d01-radio-onair.mp4", "848 · UltraLite-mk5 — on air"),
    "d03": ("broll/d03-worship-livestream.mp4", "16A · AVB Switch · M4 — worship livestream"),
    "d04": ("broll/d04-music-school.mp4", "828 · M2 — music school"),
    "d06": ("broll/d06-film-set.mp4", "UltraLite-mk5 · M2 — location sound"),
    "d07": ("broll/d07-creator-studio.mp4", "828 · M4 — creator studio"),
    "d08": ("broll/d08-atmos-post.mp4", "848 · M6 — Atmos post"),
}

# ── Product groups ─────────────────────────────────────────────────────────
G = {
    "m": ["m2", "m4", "m6", "m"],
    "ul": ["ul"],
    "828": ["828"],
    "ul828": ["ul", "828", "ul828"],
    "avb": ["16a", "848", "10pre", "avb"],
    "16a": ["16a"], "848": ["848"], "10pre": ["10pre"],
    "switch": ["switch", "avb"],
    "all": ["m2", "m4", "m6", "m", "ul", "828", "ul828", "16a", "848", "10pre", "avb", "switch"],
}
PHOTO = ["hero", "life", "panel", "render", "detail", "diagram", "badge", "bundle"]


class Pool:
    """Hands out assets least-used first, so every image gets its turn before any repeats."""

    def __init__(self, seed):
        self.used = {a["slug"]: 0 for a in A}
        self.rng = random.Random(seed)

    def take(self, products, kinds, n=1, avoid=()):
        cands = [a for a in A if a["product"] in products and a["kind"] in kinds and a["slug"] not in avoid]
        if not cands:
            raise SystemExit(f"no assets for {products} {kinds}")
        self.rng.shuffle(cands)
        cands.sort(key=lambda a: self.used[a["slug"]])
        out = cands[:n]
        for a in out:
            self.used[a["slug"]] += 1
        return [a["slug"] for a in out]


MOVES = ["gimbalL", "gimbalR", "zoomIn", "zoomOut", "focusIn", "focusOut", "craneUp", "orbit"]
T_VERSE = ["fade", "slideUp", "wipeDiag", "pullBack", "punchIn", "fade"]
T_DROP = ["punchIn", "whipLeft", "flash", "whipRight", "punchIn", "wipeDiag"]
T_BOUND = ["wipeDiag", "flash", "whipLeft", "whipRight", "slideUp"]
TRANS_CUE = {
    "fade": "air-pass", "wipeDiag": "gate-snap", "whipLeft": "slide-air", "whipRight": "slide-air",
    "punchIn": "impact-soft", "pullBack": "impact-soft", "slideUp": "riser-short", "flash": "chime-lift",
}


def build(name, sections, total_beats, offset, audio_edit, outro_beat=None):
    pool = Pool(name)
    rng = random.Random(name + "-moves")
    shots, secs, sfx = [], [], []
    t = lambda b: round(offset + b * BEAT, 4)

    for si, S in enumerate(sections):
        b0, b1 = S["from"], S["to"]
        brolls = dict(S.get("broll", []))  # start beat -> id
        dsp = list(S.get("dsp", []))  # list of lists of slugs
        step = S.get("step", 4)
        steps = S.get("steps")
        b = b0
        k = 0
        first = True
        while b < b1:
            if b in brolls:
                bid = brolls[b]
                shots.append({"kind": "broll", "id": bid, "file": BROLL[bid][0], "label": BROLL[bid][1],
                              "b0": b, "b1": b + 16})
                b += 16
            else:
                nxt = min([x for x in brolls if x > b] + [b1])
                if dsp:
                    grp = dsp.pop(0)
                    ln = S.get("dspStep", 4)
                    shots.append({"kind": "dsp", "assets": grp, "b0": b, "b1": min(b + ln, nxt)})
                    b += ln
                else:
                    ln = steps[k % len(steps)] if steps else step
                    ln = min(ln, nxt - b)
                    kinds = S.get("kinds", PHOTO)
                    mode = S.get("mode", "single")
                    if mode == "lineup" and ln >= 4:
                        # One render from each family, side by side.
                        slugs = [pool.take(G[g], ["render", "panel"])[0] for g in S.get("lineup", ["m", "ul", "828", "avb"])]
                        shots.append({"kind": "lineup", "assets": slugs, "b0": b, "b1": b + ln})
                    else:
                        slug = pool.take(G[S["group"]], kinds)[0]
                        shots.append({"kind": "still", "assets": [slug], "b0": b, "b1": b + ln})
                    b += ln
            sh = shots[-1]
            sh["section"] = S["id"]
            sh["move"] = MOVES[rng.randrange(len(MOVES))]
            if first:
                sh["trans"] = "fade" if si == 0 else T_BOUND[si % len(T_BOUND)]
            else:
                sh["trans"] = (T_DROP if S.get("drop") else T_VERSE)[rng.randrange(6)]
            if sh["kind"] == "broll":
                sh["trans"] = "flash" if S.get("drop") else "wipeDiag"
            first = False
            k += 1
        caps = []
        for c in S["captions"]:
            caps.append({"start": t(c[0]), "end": t(c[1]), "t": c[2], "e": c[3]})
        secs.append({"id": S["id"], "series": S["series"], "label": S["label"], "sub": S.get("sub", ""),
                     "start": t(b0), "end": t(b1), "drop": bool(S.get("drop")), "top": S.get("top", {}),
                     "ticker": S.get("ticker", []), "captions": caps})
        # A short riser ahead of each section, an impact on each drop's downbeat.
        if si > 0:
            sfx.append({"at": max(0, t(b0) - 0.42), "cue": "riser-short"})
        if S.get("drop"):
            sfx.append({"at": t(b0), "cue": "impact-deep"})

    for sh in shots:
        sh["start"] = t(sh["b0"]) if sh["b0"] > 0 else 0.0
        sh["end"] = t(sh["b1"])
        if sh["b0"] > 0:
            sfx.append({"at": max(0, sh["start"] - 0.05), "cue": TRANS_CUE[sh["trans"]]})
    for s in secs:
        for c in s["captions"]:
            sfx.append({"at": c["start"] + 0.03, "cue": "tick-glass"})
    end_s = round(offset + total_beats * BEAT, 4) if outro_beat is None else None
    plan = {
        "name": name, "bpm": BPM, "beat": BEAT, "offset": offset,
        "shots": shots, "sections": secs,
        "outroAt": t(outro_beat) if outro_beat is not None else None,
        "sfx": sorted(sfx, key=lambda x: x["at"]),
        "audio": audio_edit,
    }
    if outro_beat is not None:
        plan["sfx"].append({"at": t(outro_beat) - 0.15, "cue": "outro-bloom"})
    return plan


def dsp_groups(kind, singles, pairs=0, triples=0, logo=None):
    s = [a["slug"] for a in A if a["kind"] == kind]
    out = []
    if logo:
        out.append([logo])
    i = 0
    for _ in range(singles):
        out.append([s[i]]); i += 1
    for _ in range(pairs):
        out.append(s[i:i + 2]); i += 2
    for _ in range(triples):
        out.append(s[i:i + 3]); i += 3
    assert i == len(s), (kind, i, len(s))
    return out


# ════════════════════════════════════════════════════════════════════ REEL ══
# 522 output beats = 180.0 s. Source beats 16–432 then 496–602 (the drop-3
# pickup straight into the song's own ending). No end screen on the reel.
REEL_SECTIONS = [
    dict(id="hook", series="all", label="THREE SERIES", from_=0, to=16, group="all", mode="lineup", step=4,
         captions=[(0, 16, "THREE SERIES. ONE sound.", "sound")],
         top={"graph": "spectrum", "icons": [("series", 3, "", "SERIES"), ("units", 8, "", "INTERFACES"), ("dsp", 2, "", "DSP ENGINES")]},
         ticker=["M2 · M4 · M6", "ULTRALITE-mk5 · 828", "16A · 848 · 10pre · AVB SWITCH"]),
    dict(id="m", series="m", label="M-SERIES", sub="M2 · M4 · M6", from_=16, to=80, group="m", step=4,
         broll=[(32, "d04"), (64, "d07")],
         captions=[(16, 32, "MEET THE M-Series", "M-Series"), (32, 48, "ESS SABRE32 Ultra CONVERTERS", "Ultra"),
                   (48, 64, "120 dB DYNAMIC RANGE", "120 dB"), (64, 80, "2.5 ms ROUND TRIP", "2.5 ms")],
         top={"graph": "range", "value": 120, "icons": [("range", 120, "dB", "DYNAMIC RANGE"), ("latency", 2.5, "ms", "ROUND TRIP"), ("rate", 192, "kHz", "MAX RATE")]},
         ticker=["M2 · 2 IN / 2 OUT", "M4 · 4 IN / 4 OUT", "M6 · 6 IN / 4 OUT · 4 PREAMPS", "−129 dBu EIN", "USB-C"]),
    dict(id="ul828", series="ul828", label="ULTRALITE-mk5 · 828", from_=80, to=144, group="ul828", step=4,
         broll=[(96, "b04"), (128, "b07")],
         captions=[(80, 96, "UltraLite-mk5 · 18 IN, 22 OUT", "UltraLite-mk5"), (96, 112, "THE 828 · 28 IN, 32 OUT", "828"),
                   (112, 128, "74 dB OF PREAMP GAIN", "74 dB"), (128, 144, "125 dB DYNAMIC RANGE", "125 dB")],
         top={"graph": "io", "io": [["ULTRALITE-mk5", 18, 22], ["828", 28, 32]], "icons": [("io", 28, "×32", "828 I/O"), ("gain", 74, "dB", "PREAMP GAIN"), ("range", 125, "dB", "DYNAMIC RANGE")]},
         ticker=["ULTRALITE-mk5 · 18 × 22", "828 · 28 × 32", "2 FRONT COMBO PREAMPS", "3.9\" DISPLAY", "USB-C"]),
    dict(id="avb", series="avb", label="AVB SERIES", sub="16A · 848 · 10pre", from_=144, to=208, group="avb", steps=[4, 2, 2], drop=True,
         broll=[(160, "b01"), (192, "d01")],
         captions=[(144, 160, "THE AVB Series", "AVB"), (160, 176, "16A · 16 LINE IN, 16 OUT", "16A"),
                   (176, 192, "848 · THE STUDIO command CENTRE", "command"), (192, 208, "10pre · TEN MIC PREAMPS", "10pre")],
         top={"graph": "io", "io": [["16A", 32, 34], ["848", 28, 32], ["10pre", 26, 28]], "icons": [("range", 125, "dB", "DYNAMIC RANGE"), ("ch", 256, "", "CH TO COMPUTER"), ("latency", 2, "ms", "UNDER · ROUND TRIP")]},
         ticker=["THUNDERBOLT 4 · USB4", "64-CH MIXER · 26 AUX", "16A · 32 × 34", "848 · 28 × 32", "10pre · 10 PREAMPS"]),
    dict(id="switch", series="avb", label="AVB SWITCH", from_=208, to=224, group="switch", step=4,
         captions=[(208, 224, "AVB Switch · 5 PORTS, ONE CLOCK", "Switch")],
         top={"graph": "network", "icons": [("ports", 5, "", "AVB PORTS"), ("dist", 100, "m", "CAT-6 RUN"), ("units", 8, "", "UNITS CHAINED")]},
         ticker=["IEEE 802.1AS CLOCK", "5 AVB + 1 GIGABIT", "CAT-5e / CAT-6"]),
    dict(id="network", series="avb", label="ONE NETWORK", from_=224, to=288, group="avb", step=4,
         broll=[(224, "d03"), (256, "b05")],
         captions=[(224, 240, "128 CHANNELS OVER ONE cable", "cable"), (240, 256, "CAT-6 RUNS UP TO 100 m", "100 m"),
                   (256, 272, "Milan CERTIFIED AVB", "Milan"), (272, 288, "UNDER 2 ms ROUND TRIP", "2 ms")],
         top={"graph": "network", "icons": [("ch", 128, "", "CH PER UNIT"), ("dist", 100, "m", "PER CABLE"), ("latency", 2, "ms", "UNDER · ROUND TRIP")]},
         ticker=["MILAN CERTIFIED", "802.1AS gPTP", "UP TO 8 UNITS", "128 CH / UNIT"]),
    dict(id="cm5", series="ul828", label="CueMix 5", sub="ULTRALITE-mk5 · 828 DSP", from_=288, to=352, group="ul828",
         dsp=dsp_groups("cm5", 15, logo="logo-828-9-png"),
         captions=[(288, 304, "CueMix 5 · DSP ON BOARD", "CueMix 5"), (304, 320, "EQ, GATE, COMPRESSOR, reverb", "reverb"),
                   (320, 336, "loopback FOR STREAMING", "loopback"), (336, 352, "CONTROL FROM YOUR iPad", "iPad")],
         top={"graph": "eq", "icons": [("eq", 4, "", "EQ BANDS"), ("dyn", 2, "", "GATE · COMP"), ("fx", 1, "", "REVERB")]},
         ticker=["EQ", "GATE", "COMPRESSOR", "REVERB", "LOOPBACK", "iPad CONTROL", "STANDALONE"]),
    dict(id="cmpro", series="avb", label="CueMix Pro", sub="AVB DSP · 16A · 848 · 10pre", from_=352, to=416, group="avb",
         broll=[(352, "b10")],
         dsp=dsp_groups("cmpro", 0, triples=11, logo="logo-16a-1-png"),
         captions=[(352, 368, "CueMix Pro · AVB DSP", "CueMix Pro"), (368, 384, "4-BAND EQ · COMP · GATE", "4-BAND"),
                   (384, 400, "talkback, MONITOR GROUPS", "talkback"), (400, 416, "Wi-Fi CONTROL · STANDALONE", "Wi-Fi")],
         top={"graph": "comp", "icons": [("eq", 4, "", "EQ BANDS"), ("mix", 64, "", "CH MIXER"), ("aux", 26, "", "AUX BUSES")]},
         ticker=["macOS · WINDOWS · iPad · iPhone", "PATCHBAY", "TALKBACK", "MONITOR GROUPS", "Wi-Fi", "STANDALONE"]),
    dict(id="deploy", series="all", label="IN THE FIELD", from_=416, to=480, group="all", kinds=["life", "hero"], steps=[2, 2, 4], drop=True,
         broll=[(416, "d06"), (448, "d08")],
         captions=[(416, 432, "ON LOCATION", "LOCATION"), (432, 448, "FROM THE bedroom…", "bedroom"),
                   (448, 464, "…TO THE ATMOS stage", "stage"), (464, 480, "EVERY SESSION, covered", "covered")],
         top={"graph": "meters", "icons": [("series", 3, "", "SERIES"), ("units", 8, "", "INTERFACES"), ("range", 125, "dB", "UP TO")]},
         ticker=["FILM SETS", "STUDIOS", "STAGES", "CLASSROOMS", "CREATORS", "POST"]),
    dict(id="family", series="all", label="THE FAMILY", from_=480, to=522, group="all", mode="lineup", step=6,
         lineup=["m", "ul", "828", "avb"],
         captions=[(480, 504, "M-SERIES · ULTRALITE · 828 · AVB", "AVB"), (504, 522, "ONE family", "family")],
         top={"graph": "spectrum", "icons": [("series", 3, "", "SERIES"), ("units", 8, "", "INTERFACES"), ("dsp", 2, "", "DSP ENGINES")]},
         ticker=["M2 · M4 · M6", "ULTRALITE-mk5 · 828", "16A · 848 · 10pre · AVB SWITCH"]),
]

# ═══════════════════════════════════════════════════════════════════ VIDEO ══
# 870 output beats from source beat 0: the song's sections rearranged in
# 16-beat blocks (see VIDEO_AUDIO). End screen 290–300 s.
VIDEO_SECTIONS = [
    dict(id="hook", series="all", label="THREE SERIES", from_=0, to=32, group="all", mode="lineup", step=8,
         captions=[(0, 16, "THREE SERIES", "SERIES"), (16, 32, "ONE sound", "sound")],
         top=REEL_SECTIONS[0]["top"], ticker=REEL_SECTIONS[0]["ticker"]),
    dict(id="m", series="m", label="M-SERIES", sub="M2 · M4 · M6", from_=32, to=160, group="m", step=4,
         broll=[(48, "d04"), (96, "d07"), (144, "d06")],
         captions=[(32, 48, "MEET THE M-Series", "M-Series"), (48, 64, "M2 · M4 · M6", "M4"),
                   (64, 80, "ESS SABRE32 Ultra CONVERTERS", "Ultra"), (80, 96, "120 dB DYNAMIC RANGE", "120 dB"),
                   (96, 112, "−129 dBu PREAMP noise", "noise"), (112, 128, "2.5 ms ROUND TRIP", "2.5 ms"),
                   (128, 144, "M6 · 4 PREAMPS, 6 IN / 4 OUT", "M6"), (144, 160, "READY FOR THE field", "field")],
         top=REEL_SECTIONS[1]["top"], ticker=REEL_SECTIONS[1]["ticker"]),
    dict(id="ul", series="ul828", label="ULTRALITE-mk5", from_=160, to=224, group="ul", steps=[4, 2, 2], drop=True,
         broll=[(176, "b07")],
         captions=[(160, 176, "THE UltraLite-mk5", "UltraLite-mk5"), (176, 192, "18 IN, 22 OUT", "22"),
                   (192, 208, "2.4 ms ROUND TRIP", "2.4 ms"), (208, 224, "HALF-RACK, FULL studio", "studio")],
         top={"graph": "io", "io": [["ULTRALITE-mk5", 18, 22]], "icons": [("io", 18, "×22", "I/O"), ("latency", 2.4, "ms", "ROUND TRIP"), ("pre", 2, "", "COMBO PREAMPS")]},
         ticker=["2 FRONT COMBO PREAMPS", "8 LINE IN · 10 LINE OUT", "OPTICAL · S/PDIF · MIDI", "USB-C"]),
    dict(id="828", series="ul828", label="THE 828", from_=224, to=304, group="828", step=4,
         broll=[(256, "b04")],
         captions=[(224, 240, "THE 828", "828"), (240, 256, "28 IN, 32 OUT", "32"),
                   (256, 272, "74 dB OF PREAMP GAIN", "74 dB"), (272, 288, "125 dB DYNAMIC RANGE", "125 dB"),
                   (288, 304, "3.9-INCH display", "display")],
         top={"graph": "io", "io": [["ULTRALITE-mk5", 18, 22], ["828", 28, 32]], "icons": [("io", 28, "×32", "I/O"), ("gain", 74, "dB", "PREAMP GAIN"), ("range", 125, "dB", "DYNAMIC RANGE")]},
         ticker=["−129 dBu EIN", "TALKBACK", "FOOTSWITCH", "OPTICAL · S/PDIF · MIDI", "3.9\" DISPLAY"]),
    dict(id="cm5", series="ul828", label="CueMix 5", sub="ULTRALITE-mk5 · 828 DSP", from_=304, to=368, group="ul828",
         dsp=dsp_groups("cm5", 15, logo="logo-828-9-png"),
         captions=REEL_SECTIONS[6]["captions"], top=REEL_SECTIONS[6]["top"], ticker=REEL_SECTIONS[6]["ticker"]),
    dict(id="avb", series="avb", label="AVB SERIES", sub="16A · 848 · 10pre", from_=368, to=496, group="avb", steps=[4, 2, 2], drop=True,
         broll=[(384, "b01"), (432, "d01"), (464, "d08")],
         captions=[(368, 384, "THE AVB Series", "AVB"), (384, 400, "THUNDERBOLT 4 · USB4", "USB4"),
                   (400, 416, "16A · 16 LINE IN, 16 OUT", "16A"), (416, 432, "DC-coupled OUTPUTS", "coupled"),
                   (432, 448, "848 · THE STUDIO command CENTRE", "command"), (448, 464, "TALKBACK · A / B / C monitors", "monitors"),
                   (464, 480, "10pre · TEN MIC PREAMPS", "10pre"), (480, 496, "256 CHANNELS TO YOUR computer", "computer")],
         top=REEL_SECTIONS[3]["top"], ticker=REEL_SECTIONS[3]["ticker"]),
    dict(id="network", series="avb", label="AVB SWITCH · NETWORK", from_=496, to=560, group="switch", step=4,
         broll=[(512, "d03"), (544, "b05")],
         captions=[(496, 512, "AVB Switch · 5 PORTS, ONE CLOCK", "Switch"), (512, 528, "128 CHANNELS OVER ONE cable", "cable"),
                   (528, 544, "Milan CERTIFIED AVB", "Milan"), (544, 560, "CAT-6 RUNS UP TO 100 m", "100 m")],
         top=REEL_SECTIONS[5]["top"], ticker=REEL_SECTIONS[5]["ticker"] + REEL_SECTIONS[4]["ticker"]),
    dict(id="cmpro", series="avb", label="CueMix Pro", sub="AVB DSP · 16A · 848 · 10pre", from_=560, to=688, group="avb",
         broll=[(560, "b10")],
         dsp=dsp_groups("cmpro", 21, pairs=6, logo="logo-16a-1-png"), dspStep=4,
         captions=[(560, 576, "CueMix Pro · AVB DSP", "CueMix Pro"), (576, 592, "macOS, WINDOWS, iPad, iPhone", "iPad"),
                   (592, 608, "4-BAND EQ · COMP · GATE", "4-BAND"), (608, 624, "reverb ON EVERY MIX", "reverb"),
                   (624, 640, "patchbay · ROUTE ANYTHING", "patchbay"), (640, 656, "talkback, MONITOR GROUPS", "talkback"),
                   (656, 672, "Wi-Fi CONTROL", "Wi-Fi"), (672, 688, "RUNS standalone", "standalone")],
         top=REEL_SECTIONS[7]["top"], ticker=REEL_SECTIONS[7]["ticker"]),
    dict(id="family1", series="all", label="THREE SERIES", from_=688, to=704, group="all", mode="lineup", step=8,
         captions=[(688, 704, "ONE DESIGN family", "family")],
         top=REEL_SECTIONS[0]["top"], ticker=REEL_SECTIONS[0]["ticker"]),
    dict(id="deploy", series="all", label="IN THE FIELD", from_=704, to=768, group="all", kinds=["life", "hero"], step=4,
         captions=[(704, 720, "HOME studios", "studios"), (720, 736, "LIVE stages", "stages"),
                   (736, 752, "PODCAST & broadcast", "broadcast"), (752, 768, "POST & SCORING", "SCORING")],
         top=REEL_SECTIONS[8]["top"], ticker=REEL_SECTIONS[8]["ticker"]),
    dict(id="finale", series="all", label="EVERY SERIES", from_=768, to=832, group="all", steps=[2, 2, 4], drop=True,
         captions=[(768, 784, "M-Series", "M-Series"), (784, 800, "UltraLite-mk5 · 828", "828"),
                   (800, 816, "AVB · CueMix Pro", "AVB"), (816, 832, "ONE family", "family")],
         top=REEL_SECTIONS[9]["top"], ticker=REEL_SECTIONS[9]["ticker"]),
    dict(id="lineup", series="all", label="THE FAMILY", from_=832, to=840, group="all", mode="lineup", step=8,
         lineup=["m", "ul", "828", "avb"],
         captions=[(832, 840, "MOTU INTERFACES", "INTERFACES")],
         top=REEL_SECTIONS[9]["top"], ticker=REEL_SECTIONS[9]["ticker"]),
]
for S in REEL_SECTIONS + VIDEO_SECTIONS:
    S["from"] = S.pop("from_")

# Source-beat blocks for each film's bed — [src_from, src_to) in source beats.
REEL_AUDIO = [[16, 432], [496, 603]]
VIDEO_AUDIO = [[0, 32], [32, 96], [96, 160], [160, 224], [224, 240], [240, 304], [304, 368], [368, 432],
               [432, 496], [240, 304], [304, 368], [160, 224], [224, 240], [32, 96], [496, 560], [560, 603]]

if __name__ == "__main__":
    reel = build("reel", REEL_SECTIONS, 522, 0.0,
                 {"blocks": REEL_AUDIO, "startAt": 0.0, "duration": 180.0, "srcOffset": SRC_FIRST_BEAT})
    video = build("video", VIDEO_SECTIONS, 870, SRC_FIRST_BEAT,
                  {"blocks": VIDEO_AUDIO, "startAt": 0.0, "duration": 300.0, "srcOffset": SRC_FIRST_BEAT, "leadIn": True},
                  outro_beat=840)
    for p in (reel, video):
        assert abs(sum(b[1] - b[0] for b in p["audio"]["blocks"]) * BEAT) > 1
        json.dump(p, open(os.path.join(ROOT, "src", f"plan-{p['name']}.json"), "w"), indent=1)
        used = sorted({s for sh in p["shots"] for s in sh.get("assets", [])})
        nb = sum(1 for sh in p["shots"] if sh["kind"] == "broll")
        print(p["name"], "shots", len(p["shots"]), "brolls", nb, "unique images", len(used),
              "last shot end", p["shots"][-1]["end"], "outro", p["outroAt"])
    allimg = {a["slug"] for a in A if a["kind"] != "logo"}
    both = {s for p in (reel, video) for sh in p["shots"] for s in sh.get("assets", [])}
    print("images never shown:", sorted(allimg - both))

#!/usr/bin/env python3
"""Original score + sound design for "Andar Ki Adalat" V2, written to the V2 timeline.

Usage: score_v2.py <timeline_v2.json> <intro_s> <outro_s> <out.mid>
timeline_v2.json: [{"label": "12", "start": s, "dur": d}, ...] (start excludes the intro)

Leitmotif (A-minor theme) follows Riya: lonely piano at night -> bansuri for Maa -> music box for the
childhood memory -> C-major flute on the morning call. Courtroom colour: cello drone and choir.
Every "mirror truth" replay opens with a reversed-cymbal swell; Maa's lonely birthday has a
ticking clock; the twist ("आज कौन सी तारीख़ है?") drops all music to a heartbeat.
"""
import json, sys
import mido

TL = json.load(open(sys.argv[1])); OFF = float(sys.argv[2]); OUTRO = float(sys.argv[3]); OUT = sys.argv[4]
T = {c["label"]: (c["start"] + OFF, c["start"] + OFF + c["dur"]) for c in TL}
END = TL[-1]["start"] + TL[-1]["dur"] + OFF; FILM_END = END + OUTRO
S = lambda l: T[l][0]; E = lambda l: T[l][1]

events = []
PROG = {"piano": 0, "strings": 49, "cello": 42, "flute": 73, "box": 10, "choir": 52, "timp": 47,
        "pad": 89, "violin": 40, "bass": 43, "rev": 119, "wood": 115, "harp": 46}
CH = dict(zip(PROG, [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13]))  # channel 9 (drums) skipped

def note(i, t, d, p, v):
    events.append((t, mido.Message("note_on", channel=CH[i], note=p, velocity=max(1, min(127, int(v))))))
    events.append((t + max(0.05, d), mido.Message("note_off", channel=CH[i], note=p, velocity=0)))
def ramp(i, t0, t1, v0, v1, n=24):
    for k in range(n + 1):
        events.append((t0 + (t1 - t0) * k / n, mido.Message("control_change", channel=CH[i], control=11,
                                                              value=int(max(0, min(127, v0 + (v1 - v0) * k / n))))))
CH_ = {"Am": [45, 57, 60, 64], "F": [41, 53, 57, 60], "C": [48, 55, 60, 64], "G": [43, 55, 59, 62],
       "Dm": [38, 50, 53, 57], "E": [40, 52, 56, 59], "Em": [40, 52, 55, 59], "Bb": [46, 53, 58, 62],
       "A": [45, 52, 57, 61], "Cadd9": [48, 55, 62, 64], "Fmaj7": [41, 53, 57, 64]}
def arp(t0, t1, prog, bar, v, inst="piano"):
    t, k = t0, 0
    while t < t1 - 0.3:
        c = CH_[prog[k % len(prog)]]; L = min(bar, t1 - t)
        note(inst, t, L, c[0], v)
        for j, p in enumerate([c[1], c[2], c[3], c[2] + 12]):
            tt = t + j * bar / 4
            if tt < t1 - 0.2: note(inst, tt, t + L - tt, p, v - 12 + (6 if j == 3 else 0))
        t += bar; k += 1
def pad(i, t0, t1, prog, bar, v, octv=0):
    t, k = t0, 0
    while t < t1 - 0.3:
        c = CH_[prog[k % len(prog)]]; L = min(bar, t1 - t)
        for p in c[1:]: note(i, t, L + 0.05, p + 12 * octv, v)
        t += bar; k += 1
def drone(i, t0, t1, ps, v):
    for p in ps: note(i, t0, t1 - t0, p, v)
MIN = [(76, 1), (74, .5), (72, .5), (71, 1), (69, 1.5), (72, 1), (71, .5), (69, .5), (67, 1), (69, 2.5)]
MAJ = [(79, 1), (77, .5), (76, .5), (74, 1), (72, 1.5), (76, 1), (74, .5), (72, .5), (71, 1), (72, 2.5)]
def theme(i, t0, ns, beat, v, tr=0, limit=None):
    t = t0
    for p, b in ns:
        if limit and t > limit - 0.3: break
        note(i, t, b * beat * 0.95, p + tr, v); t += b * beat
    return t
def heart(t0, t1, per, v):
    t = t0
    while t < t1 - 0.1:
        note("timp", t, 0.3, 33, v); note("timp", t + 0.28, 0.3, 33, v * 0.7); t += per
def swell(t, v=70):  # reversed cymbal into a mirror replay
    note("rev", t - 1.6, 1.8, 60, v)
def ticks(t0, t1, v=55):
    t, k = t0, 0
    while t < t1:
        note("wood", t, 0.05, 76 if k % 2 == 0 else 77, v); t += 0.5; k += 1

# cold open + title
heart(0.3, 6.6, 1.1, 60); drone("bass", 0, 7.0, [33], 55); ramp("bass", 0, 7.0, 40, 100)
note("timp", 5.6, 2.0, 33, 100); note("timp", 7.0, 3.0, 33, 127)
drone("choir", 7.1, OFF - 0.3, [45, 52, 57, 64], 60); ramp("choir", 7.0, OFF, 110, 0)
theme("piano", 7.8, MIN[:4], 0.7, 50, 12)

# 1-4 night: lonely piano, the theme as she writes the list, strings as the fog comes in
arp(S("1"), E("4") - 0.5, ["Am", "F", "C", "G"], 3.2, 60)
theme("piano", S("3") + 0.5, MIN, 0.8, 66, 12)
drone("strings", S("4") + 2, E("4v") + 1.0, [57, 64, 69], 50); ramp("strings", S("4") + 2, E("4v"), 20, 100)

# 5-10 the courtroom: cello drone, glassy piano, choir breath when Judge Riya appears
drone("cello", S("5"), E("8b"), [45, 52], 70); ramp("cello", S("5"), S("6"), 30, 95)
for k, p in enumerate([88, 84, 89, 83, 88, 81, 86, 84]):
    note("piano", S("5") + 1.5 + k * 3.4, 2.5, p, 36)
note("timp", S("6") + 0.4, 2.5, 33, 105)
drone("choir", S("9") + 0.5, E("9"), [57, 64, 69], 55); ramp("choir", S("9"), E("9"), 20, 90)

def chapter(label):  # deep hit + harp gliss under each witness card
    note("timp", S(label) + 0.05, 2.0, 33, 115)
    for k, p in enumerate([57, 60, 64, 69, 72]): note("harp", S(label) + 0.3 + k * 0.08, 2.0, p, 60)
for c in ("c1", "c2", "c3"): chapter(c)

# part A - Riya's case: the sad progression walks under her accusations, heartbeat creeping in
arp(S("c1"), E("26b"), ["Am", "F", "Dm", "E"], 3.2, 48); pad("strings", S("c1"), E("26b"), ["Am", "F", "Dm", "E"], 3.2, 42)
ramp("strings", S("c1"), E("26b"), 45, 105)
heart(S("20"), E("26b"), 0.95, 54)
note("timp", S("22b") + 0.1, 2.5, 33, 120); drone("choir", S("22b"), E("22c"), [45, 52, 57], 55)
theme("flute", S("24") + 1.0, MIN, 0.9, 58, limit=E("23"))
# part B - the mirror: one reversed-cymbal swell opens it, glassy pads, the theme turns tender
swell(S("m1"), 80); drone("pad", S("m1"), E("29v"), [64, 69, 76], 48)
pad("strings", S("m1"), E("29v"), ["F", "Am", "Dm", "E"], 3.4, 36)
for k, p in enumerate([88, 84, 89, 83]): note("piano", S("m1") + 0.5 + k * 1.8, 2.5, p, 40)
for lab in ("19", "28"): swell(S(lab), 60)
for k, p in enumerate([81, 76, 79, 74, 76, 72]): note("piano", S("19") + 0.3 + k * 1.6, 3.0, p + 12, 40)
arp(S("28"), E("29v"), ["Am", "F", "C", "E"], 3.4, 42); theme("flute", S("28") + 1.0, MIN, 0.9, 60, limit=E("29v"))
drone("cello", S("29v"), E("29v") + 1.0, [45, 52], 70); ramp("cello", S("29v"), E("29v") + 1.0, 60, 0)
# 31-33 aftermath: a single violin thread
note("violin", S("31") + 1.0, E("31") - S("31") - 1.0, 88, 45); ramp("violin", S("31"), E("31"), 30, 60)
for k, p in enumerate([69, 72, 71, 69]): note("piano", S("31") + 2 + k * 2.2, 2.0, p, 36)
# 34 the twist: only a heartbeat, one low hit on "माँ का जन्मदिन"
heart(S("34"), E("34"), 1.0, 66); note("timp", S("34") + 6.4, 3.0, 31, 127); note("bass", S("34") + 6.4, 3.5, 31, 90)
# 35 Maa's lonely birthday: clock ticking, the theme very softly on flute
ticks(S("35"), E("35")); swell(S("35"), 55); theme("flute", S("35") + 1.0, MIN[:6], 1.0, 46)
# 36-39 childhood: music-box lullaby
# (childhood flashback removed from the cut)
# 40-42 the turn: harmony opens towards C major
arp(S("40"), E("41"), ["F", "G", "Em", "Am", "F", "G", "C", "C"], 2.6, 54)
pad("strings", S("40"), E("41"), ["F", "G", "Em", "Am", "F", "G", "C", "C"], 2.6, 48); ramp("strings", S("40"), E("41"), 50, 95)
# 43 the fourth name: single notes, then the swell
for k, p in enumerate([72, 71, 69, 64]): note("piano", S("43") + 0.5 + k * 1.6, 2.5, p, 50)
note("timp", S("43") + 6.4, 2.5, 36, 90)
# 44-47 forgiveness: full strings, violin carries the theme
arp(S("44"), E("47"), ["F", "C", "G", "Am", "F", "C", "G", "C"], 2.8, 54)
pad("strings", S("44"), E("47"), ["F", "C", "G", "Am", "F", "C", "G", "C"], 2.8, 60)
ramp("strings", S("44"), S("45") + 5, 50, 120); ramp("strings", S("45") + 5, E("47"), 120, 80)
theme("violin", S("45") + 0.5, MAJ, 0.9, 72, -12)
# 48 verdict: drone + choir + timpani roll, mirrors break into C major light
drone("cello", S("48"), S("48") + 6, [36, 43], 80); ramp("cello", S("48"), S("48") + 6, 50, 120)
drone("choir", S("48") + 1, E("48") + 1.5, [60, 67, 72, 76], 72); ramp("choir", S("48"), E("48"), 30, 120)
t = S("48") + 3
while t < S("48") + 6: note("timp", t, 0.12, 36, 50 + (t - S("48")) * 15); t += 0.12
note("timp", S("48") + 6.0, 3.5, 36, 127); drone("strings", S("48") + 6, E("48") + 2, [60, 64, 67, 72], 80)
# 49-57 morning: light piano, the theme in C major on flute; the dinner is the warmest moment
arp(S("49"), E("58"), ["C", "G", "Am", "F"], 2.6, 54); pad("strings", S("49"), E("58"), ["C", "G", "Am", "F"], 2.6, 42)
theme("flute", S("49") + 2.0, MAJ, 0.8, 58); theme("flute", S("53") + 0.5, MAJ, 0.85, 56)
theme("violin", S("56") + 0.5, MAJ, 0.9, 60, -12)
drone("choir", S("58") + 0.5, E("58"), [60, 67, 72], 42); theme("piano", S("58") + 1.0, MAJ, 0.9, 48, 12)
drone("strings", S("58") + 4, END + 2, [60, 64, 67, 74], 45); ramp("strings", S("58") + 4, END + 2, 60, 0)
# outro
arp(END + 1.0, FILM_END - 2.0, ["C", "G", "Am", "F"], 3.0, 44); pad("strings", END + 1, FILM_END - 1, ["C", "G", "Am", "F"], 3.0, 36)
theme("flute", END + 3.0, MAJ, 0.9, 52)
for p in CH_["Cadd9"]: note("piano", FILM_END - 5.0, 4.8, p, 40)
for i in ("piano", "strings", "flute"): ramp(i, FILM_END - 6.0, FILM_END, 100, 0)

mid = mido.MidiFile(ticks_per_beat=480); tr = mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage("set_tempo", tempo=1_000_000, time=0))
VOL = {"piano": 100, "strings": 90, "cello": 95, "flute": 95, "box": 90, "choir": 80, "timp": 105, "pad": 70,
       "violin": 100, "bass": 100, "rev": 70, "wood": 60, "harp": 80}
for i, c in CH.items():
    tr.append(mido.Message("program_change", channel=c, program=PROG[i], time=0))
    tr.append(mido.Message("control_change", channel=c, control=91, value=70, time=0))
    tr.append(mido.Message("control_change", channel=c, control=7, value=VOL[i], time=0))
    tr.append(mido.Message("control_change", channel=c, control=11, value=100, time=0))
events.sort(key=lambda e: (e[0], 0 if e[1].type == "note_off" else 1)); last = 0
for t, m in events:
    tick = int(round(t * 480)); tr.append(m.copy(time=max(0, tick - last))); last = max(last, tick)
mid.save(OUT); print("score length", round(FILM_END, 1))

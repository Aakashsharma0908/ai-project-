#!/usr/bin/env python3
"""Original score for "Riya - Andar Ki Adalat", written to the edit's timeline.

Usage: score.py <timeline.json> <intro_seconds> <outro_seconds> <out.mid>
The intro is the cold open (judge's voice over black, 0-7 s) plus the title card (7 s - intro end).
Render: fluidsynth -ni -F out.wav -r 48000 FluidR3_GM.sf2 out.mid

One leitmotif carries the whole film and changes with Riya:
  sad A-minor piano (alone at night) -> bansuri/flute (Maa's loneliness) ->
  music box (the childhood memory) -> C-major flute (the new morning, the call to Maa).
The courtroom has its own colour: cello drone, heartbeat timpani, choir at the verdict.
Music stops dead at the end of the scream (clip 29) so the silence of clip 30 hits.
"""
import json, sys
import mido

TL = json.load(open(sys.argv[1])); OFF = float(sys.argv[2]); OUTRO = float(sys.argv[3]); OUT = sys.argv[4]
TITLE = 7.0  # title card starts here
T = {c["clip"]: c["start"] + OFF for c in TL}
END = TL[-1]["start"] + TL[-1]["dur"] + OFF
def S(i): return T[i]
FILM_END = END + OUTRO
def E(i): return T[i + 1] if i < 48 else END

TPB = 480  # 60 bpm -> 1 beat == 1 second, so times below are in seconds
events = []  # (time, msg)

PROG = {"piano": 0, "strings": 49, "cello": 42, "flute": 73, "box": 10, "choir": 52,
        "timp": 47, "pad": 89, "violin": 40, "bass": 43}
# channel 9 is the GM drum kit, so it is skipped
CH = {k: n for n, k in zip([0, 1, 2, 3, 4, 5, 6, 7, 8, 10], ["piano", "strings", "cello", "flute", "box", "choir",
                                                          "timp", "pad", "violin", "bass"])}

def note(inst, t, d, p, v):
    c = CH[inst]
    events.append((t, mido.Message("note_on", channel=c, note=p, velocity=max(1, min(127, int(v))))))
    events.append((t + d, mido.Message("note_off", channel=c, note=p, velocity=0)))

def cc(inst, t, ctl, val):
    events.append((t, mido.Message("control_change", channel=CH[inst], control=ctl, value=int(max(0, min(127, val))))))

def ramp(inst, t0, t1, v0, v1, steps=24):
    for k in range(steps + 1):
        cc(inst, t0 + (t1 - t0) * k / steps, 11, v0 + (v1 - v0) * k / steps)

CHORD = {"Am": [45, 57, 60, 64], "F": [41, 53, 57, 60], "C": [48, 55, 60, 64], "G": [43, 55, 59, 62],
         "Dm": [38, 50, 53, 57], "E": [40, 52, 56, 59], "Em": [40, 52, 55, 59], "Bb": [46, 53, 58, 62],
         "A": [45, 52, 57, 61], "Cadd9": [48, 55, 62, 64], "Fmaj7": [41, 53, 57, 64]}

def piano_arp(t0, t1, prog, bar, v, high=0):
    t, k = t0, 0
    while t < t1 - 0.2:
        ch = CHORD[prog[k % len(prog)]]
        L = min(bar, t1 - t)
        note("piano", t, L, ch[0], v)
        up = [ch[1], ch[2], ch[3], ch[2] + 12 * (1 + high)]
        for j, p in enumerate(up):
            tt = t + j * bar / 4
            if tt < t1 - 0.1:
                note("piano", tt, max(0.3, t + L - tt), p + 12 * high, v - 12 + (6 if j == 3 else 0))
        t += bar; k += 1

def pad(inst, t0, t1, prog, bar, v, octave=0):
    t, k = t0, 0
    while t < t1 - 0.2:
        ch = CHORD[prog[k % len(prog)]]
        L = min(bar, t1 - t)
        for p in ch[1:]:
            note(inst, t, L + 0.05, p + 12 * octave, v)
        t += bar; k += 1

def drone(inst, t0, t1, pitches, v):
    for p in pitches:
        note(inst, t0, t1 - t0, p, v)

THEME_MIN = [(76, 1), (74, .5), (72, .5), (71, 1), (69, 1.5), (72, 1), (71, .5), (69, .5), (67, 1), (69, 2.5)]
THEME_MAJ = [(79, 1), (77, .5), (76, .5), (74, 1), (72, 1.5), (76, 1), (74, .5), (72, .5), (71, 1), (72, 2.5)]

def theme(inst, t0, notes, beat, v, transpose=0, limit=None):
    t = t0
    for p, b in notes:
        if limit and t > limit - 0.3: break
        note(inst, t, b * beat * 0.95, p + transpose, v)
        t += b * beat
    return t

def heartbeat(t0, t1, period, v, pitch=33):
    t = t0
    while t < t1 - 0.1:
        note("timp", t, 0.3, pitch, v); note("timp", t + 0.28, 0.3, pitch, v * 0.7)
        t += period

# ---------------------------------------------------------------- the score
SAD = ["Am", "F", "C", "G"]
# cold open: heartbeat in the dark under the judge's voice, one low hit on "tumne hi"
heartbeat(0.3, TITLE - 0.4, 1.1, 60)
drone("bass", 0.0, TITLE, [33], 55); ramp("bass", 0.0, TITLE, 40, 100)
note("timp", 5.6, 2.0, 33, 100)
# title card: one deep hit, a dark choir chord and the first notes of the theme, then silence
note("timp", TITLE, 3.0, 33, 127); note("bass", TITLE, OFF - TITLE, 33, 90)
drone("choir", TITLE + 0.1, OFF - 0.3, [45, 52, 57, 64], 60); ramp("choir", TITLE, OFF, 110, 0)
theme("piano", TITLE + 0.8, THEME_MIN[:4], 0.7, 50, transpose=12)

# 1-3 PG room, night: lonely piano; theme enters as she writes; strings + fog into the dream
piano_arp(S(1), E(3) - 0.5, SAD, 3.2, 60)
theme("piano", S(2) + 1.0, THEME_MIN, 0.8, 66, transpose=12)
drone("strings", S(3) + 3, E(3) + 1.5, [57, 64, 69], 50); ramp("strings", S(3) + 3, E(3), 20, 100)

# 4-6 waking in the courtroom: cello drone, glassy high piano, choir breath at the reveal
drone("cello", S(4), E(6), [45, 52], 70); ramp("cello", S(4), S(5), 30, 95)
for k, p in enumerate([88, 84, 89, 83, 88, 81]):
    note("piano", S(4) + 1.5 + k * 3.1, 2.5, p, 38)
note("timp", S(5) + 0.4, 2.5, 33, 105)
drone("choir", S(6) + 1, E(6), [57, 64, 69], 55); ramp("choir", S(6), E(6), 20, 90)

# 7-13 the witnesses: the sad progression keeps walking; drone under every courtroom cut
piano_arp(S(7), E(13), ["Am", "F", "Dm", "E"], 3.2, 48)
pad("strings", S(7), E(13), ["Am", "F", "Dm", "E"], 3.2, 40)
for c in (8, 10, 12):
    drone("cello", S(c), E(c), [45], 60)
theme("piano", S(13) + 1.0, THEME_MIN, 0.9, 54, transpose=12, limit=E(13))

# 14-21 Riya defends herself: heartbeat, rising strings; flashback 17 is a glassy memory
heartbeat(S(14), S(17), 1.0, 55)
pad("strings", S(14), S(17), ["Dm", "Bb", "F", "A"], 3.0, 50, octave=0)
for k, p in enumerate([81, 76, 79, 74, 76, 72]):
    note("piano", S(17) + 0.3 + k * 1.6, 3.0, p + 12, 40)
pad("strings", S(18), E(21), ["Dm", "Bb", "F", "A"], 3.0, 55)
ramp("strings", S(18), E(21), 60, 110)
heartbeat(S(20), E(21), 0.9, 62)
theme("flute", S(19) + 2.0, THEME_MIN, 0.8, 55, limit=E(19))

# 22-26 Maa alone: the theme on bansuri-like flute, tender piano
piano_arp(S(22), E(26), ["Am", "F", "C", "E"], 3.4, 44)
pad("strings", S(22), E(26), ["Am", "F", "C", "E"], 3.4, 36)
theme("flute", S(22) + 1.0, THEME_MIN, 0.9, 62)
theme("flute", S(25) + 3.0, THEME_MIN, 0.9, 50, limit=E(25))
theme("flute", S(26) + 4.0, THEME_MIN[:5], 1.0, 58, limit=E(26))

# 27-29 the climax: faster heartbeat, cello ostinato, crescendo into the scream, then nothing
heartbeat(S(27), E(29) - 3.5, 0.75, 70)
t = S(27)
while t < E(29) - 3.5:
    note("cello", t, 0.35, 45, 80); note("cello", t + 0.375, 0.35, 45, 70); t += 0.75
pad("strings", S(27), E(29) - 3.5, ["Dm", "Bb", "E", "E"], 2.5, 60)
ramp("strings", S(27), E(29) - 3.5, 50, 127); ramp("cello", S(27), E(29) - 3.5, 60, 127)
note("timp", E(29) - 3.6, 3.0, 33, 127)
drone("choir", S(29) + 2, E(29) - 3.5, [57, 64, 69, 76], 80)

# 30-31 aftermath: a single high violin thread and a few piano notes in the silence
note("violin", S(30) + 1.0, E(31) - S(30) - 1.0, 88, 45); ramp("violin", S(30), E(31), 30, 60)
for k, p in enumerate([69, 72, 71, 69]):
    note("piano", S(31) + 1 + k * 2.2, 2.0, p, 36)

# 32 first light: a soft F major
pad("strings", S(32), E(32), ["F", "C"], 5.0, 42); piano_arp(S(32), E(32), ["Fmaj7", "C"], 5.0, 40)

# 33-34 the truth: harmony turns (F G Em Am -> F G C), music becomes hopeful
piano_arp(S(33), E(34), ["F", "G", "Em", "Am", "F", "G", "C", "C"], 2.6, 56)
pad("strings", S(33), E(34), ["F", "G", "Em", "Am", "F", "G", "C", "C"], 2.6, 48)
ramp("strings", S(33), E(34), 50, 95)

# 35 childhood memory: the theme as a music box lullaby
theme("box", S(35) + 0.6, THEME_MAJ, 0.75, 70, transpose=12)
pad("pad", S(35), E(35), ["C", "F", "C", "G"], 2.5, 40)

# 36-39 forgiveness: everything opens, solo violin carries the theme, peak on Maa's hug
piano_arp(S(36), E(39), ["F", "C", "G", "Am", "F", "C", "G", "C"], 2.8, 54)
pad("strings", S(36), E(39), ["F", "C", "G", "Am", "F", "C", "G", "C"], 2.8, 60)
ramp("strings", S(36), S(37) + 5, 50, 120); ramp("strings", S(37) + 5, E(39), 120, 80)
theme("violin", S(37) + 0.5, THEME_MAJ, 0.9, 72, transpose=-12)
theme("flute", S(38) + 2.0, THEME_MAJ, 0.8, 55, limit=E(39))

# 40 the verdict: drone + choir + timpani roll crescendo, mirrors break into C major light
drone("cello", S(40), S(40) + 6, [36, 43], 80); ramp("cello", S(40), S(40) + 6, 50, 120)
drone("choir", S(40) + 1, E(40) + 1.5, [60, 67, 72, 76], 72); ramp("choir", S(40), E(40), 30, 120)
t = S(40) + 3
while t < S(40) + 6:
    note("timp", t, 0.12, 36, 50 + (t - S(40)) * 15); t += 0.12
note("timp", S(40) + 6.0, 3.5, 36, 127)
drone("strings", S(40) + 6, E(40) + 2, [60, 64, 67, 72], 80)

# 41-47 the new morning: light piano, the theme in C major on flute
piano_arp(S(41), E(47), ["C", "G", "Am", "F"], 2.6, 54, high=0)
pad("strings", S(41), E(47), ["C", "G", "Am", "F"], 2.6, 42)
theme("flute", S(41) + 2.5, THEME_MAJ, 0.8, 58)
theme("flute", S(43) + 1.5, THEME_MAJ, 0.85, 56, limit=E(43))
theme("flute", S(44) + 1.0, THEME_MAJ, 0.75, 60)
theme("piano", S(47) + 1.0, THEME_MAJ, 0.8, 50, transpose=12, limit=E(47))

# 48 ending: the theme one last time, slowing down, final open chord
t = theme("flute", S(48) + 1.0, THEME_MAJ[:5], 1.0, 58)
piano_arp(S(48), S(48) + 6.5, ["F", "G"], 3.2, 44)
for p in CHORD["Cadd9"] + [76]:
    note("piano", S(48) + 6.5, END - S(48) - 6.4, p, 50)
drone("strings", S(48) + 6.3, END + 2.0, [60, 64, 67, 74], 45); ramp("strings", S(48) + 6, END + 2, 60, 0)

# outro / end screen: the theme once more, softly, and a long fade
piano_arp(END + 1.0, FILM_END - 2.0, ["C", "G", "Am", "F"], 3.0, 44)
pad("strings", END + 1.0, FILM_END - 1.0, ["C", "G", "Am", "F"], 3.0, 36)
theme("flute", END + 3.0, THEME_MAJ, 0.9, 52)
for p in CHORD["Cadd9"]:
    note("piano", FILM_END - 5.0, 4.8, p, 40)
for inst in ("piano", "strings", "flute"):
    ramp(inst, FILM_END - 6.0, FILM_END, 100, 0)

# ---------------------------------------------------------------- write MIDI
mid = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage("set_tempo", tempo=1_000_000, time=0))
for inst, c in CH.items():
    tr.append(mido.Message("program_change", channel=c, program=PROG[inst], time=0))
    tr.append(mido.Message("control_change", channel=c, control=91, value=70, time=0))  # reverb send
    tr.append(mido.Message("control_change", channel=c, control=7, value=
              {"piano": 100, "strings": 90, "cello": 95, "flute": 95, "box": 90, "choir": 80,
               "timp": 105, "pad": 70, "violin": 100, "bass": 100}[inst], time=0))
    tr.append(mido.Message("control_change", channel=c, control=11, value=100, time=0))
events.sort(key=lambda e: (e[0], 0 if e[1].type == "note_off" else 1))
last = 0
for t, m in events:
    tick = int(round(t * TPB)); tr.append(m.copy(time=max(0, tick - last))); last = max(last, tick)
mid.save(OUT)
print("score length", round(FILM_END, 1), "s, events", len(events))

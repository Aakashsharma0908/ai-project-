#!/usr/bin/env python3
"""Hindi + English .srt files for the final cut (subtitles are kept out of the picture).

Usage: subtitles.py <timing.json> <timeline.json> <intro_s> <out_prefix>
timing.json: speech segments per source clip (from speech recognition); the words come from the script.
"""
import json, sys

SEG = {int(k): v for k, v in json.load(open(sys.argv[1])).items()}
TL, OFF, OUT = json.load(open(sys.argv[2])), float(sys.argv[3]), sys.argv[4]
T = {c["clip"]: c["start"] + OFF - c.get("in", 0.0) for c in TL}  # time of the source clip's 0 s
LEN = {c["clip"]: (c.get("in", 0.0), c.get("in", 0.0) + c["dur"]) for c in TL}

LINES = {  # clip: [(hindi, english), ...]
 4: [("मैं कहाँ हूँ... ये जगह कौन सी है?", "Where am I... what is this place?")],
 5: [("रिया शर्मा... तुम्हारे ख़िलाफ़ केस तुमने ही किया है।", "Riya Sharma... the case against you was filed by you.")],
 6: [("तुम... तुम मैं हो?", "You... you are me?")],
 7: [("तू हमेशा अपनी ही सुनती है, रिया।", "You only ever listen to yourself, Riya."),
     ("मैंने कुछ गलत नहीं कहा था।", "I didn't say anything wrong.")],
 8: [("मैंने बस सच बोला था...", "I only told you the truth..."),
     ("पर तूने उसे हमला समझ लिया।", "but you took it as an attack.")],
 9: [("तुम कभी सुनती ही नहीं, रिया।", "You never listen, Riya."),
     ("तुम भी तो मुझे समझते नहीं।", "And you never understand me either.")],
 10: [("तुमने मुझे सबके सामने छोटा किया!", "You humiliated me in front of everyone!"),
      ("मैंने बस तुम्हें रोकना चाहा था।", "I only wanted to stop you.")],
 11: [("खाना खाया, बेटा?", "Have you eaten, beta?"), ("हर बार वही सवाल, माँ।", "The same question every time, Maa.")],
 12: [("आपको मेरी कोई परवाह नहीं है।", "You don't care about me at all.")],
 14: [("तीन गवाह आएँगे।", "Three witnesses will come."),
      ("मुझे किसी की ज़रूरत नहीं। मैं सही हूँ।", "I don't need anyone. I am right.")],
 16: [("सच सुनने की हिम्मत है, रिया?", "Do you have the courage to hear the truth, Riya?"), ("हाँ...", "Yes...")],
 17: [("तुम्हारी कहानी में मैं कभी सही हो ही नहीं सकता...", "In your story, I can never be right..."),
      ("क्योंकि उसमें सिर्फ़ एक ही किरदार है।", "because it has only one character.")],
 18: [("माफ़ी?", "An apology?"), ("गलती उसकी थी।", "It was his fault.")],
 19: [("तू अकेली नहीं रह पाएगी।", "You won't be able to live alone.")],
 20: [("सबको लगता है मैं ही गलत हूँ।", "Everyone thinks I'm the one who's wrong.")],
 21: [("उन्हें मुझ पर कभी भरोसा था ही नहीं।", "They never trusted me."),
      ("उन्होंने मुझे कभी समझा ही नहीं।", "They never understood me.")],
 23: [("तुमने कभी सुना ही नहीं, सिर्फ़ जवाब दिया।", "You never listened. You only answered."),
      ("मैंने सुना था... मुझे लगा कोई मुझे सुन ही नहीं रहा।", "I did listen... I felt no one was listening to me.")],
 24: [("तू बात तो कर।", "At least talk to me."), ("अब कोई फ़ायदा नहीं।", "There's no point anymore.")],
 25: [("ठीक है बेटा...", "Okay, beta...")],
 26: [("मैं अकेली कैसे रहूँगी...", "How will I live alone...")],
 27: [("अब माँ की बारी है।", "Now it's Maa's turn.")],
 28: [("आपने मुझे कभी समझा ही नहीं, सिर्फ़ खाना पूछा।", "You never understood me. You only asked if I'd eaten.")],
 29: [("माँ से माफ़ी?", "An apology to Maa?"),
      ("मैं क्यों माँगूँ?! हर बार मेरे साथ ही क्यों होता है?!", "Why should I?! Why does it always happen to me?!")],
 32: [("अब सच वाली बात सुनो।", "Now hear the truth.")],
 33: [("सच ये है... तुम गलत नहीं थी, तुम थक गई थी।", "The truth is... you weren't wrong. You were tired.")],
 34: [("तुमने माँ को दुख दिया... पर जान-बूझ के नहीं।", "You hurt Maa... but not on purpose.")],
 36: [("माँ... मुझे माफ़ कर दो...", "Maa... please forgive me...")],
 38: [("मैं समझ गई, रिया।", "I understand, Riya.")],
 39: [("मैं तुम्हारे साथ हूँ।", "I'm with you.")],
 40: [("फ़ैसला सुनाया जाता है...", "The verdict is..."), ("ख़ुद को माफ़ कर दो।", "Forgive yourself.")],
 42: [("माँ, खाना खाया?", "Maa, have you eaten?")],
 43: [("खा लिया बेटा... तूने खाया?", "I have, beta... have you?")],
 48: [("कहानी ख़त्म नहीं... शुरू हुई है।", "The story hasn't ended... it has just begun.")],
}

def ts(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

cues = [(0.6, 6.2, LINES[5][0])]  # cold open: the judge's line over black
for clip, lines in LINES.items():
    segs = [(s, e) for s, e, _ in SEG.get(clip, [])]
    if segs:
        a, b = segs[0][0], segs[-1][1]
    else:
        a, b = 1.0, 6.0
    if clip == 34:  # the take repeats its last words; keep the first reading only
        b = min(b, 7.0)
    if len(segs) == len(lines):
        spans = segs
    else:
        tot = sum(len(h) for h, _ in lines); spans, t = [], a
        for h, _ in lines:
            d = (b - a) * len(h) / tot; spans.append((t, t + d)); t += d
    lo, hi = LEN[clip]
    for (s, e), ln in zip(spans, lines):
        s, e = max(s, lo), min(max(e, s + 1.2) + 0.3, hi)
        cues.append((T[clip] + s, T[clip] + e, ln))
    print(clip, [(round(s, 1), round(e, 1)) for s, e in spans], flush=True)

cues.sort()
for k in range(len(cues) - 1):  # no overlaps
    s, e, ln = cues[k]
    cues[k] = (s, min(e, cues[k + 1][0] - 0.05), ln)
for lang, idx in (("hi", 0), ("en", 1)):
    with open(f"{OUT}.{lang}.srt", "w", encoding="utf-8") as fh:
        for n, (s, e, ln) in enumerate(cues, 1):
            fh.write(f"{n}\n{ts(s)} --> {ts(e)}\n{ln[idx]}\n\n")
print("cues", len(cues))

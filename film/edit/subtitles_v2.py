#!/usr/bin/env python3
"""Hindi + English .srt for the V2 cut (uploaded to YouTube as separate caption tracks).

Usage: subtitles_v2.py <timeline_v2.json> <trims.json> <timing.json> <timing_extra.json> <intro_s> <out_prefix>
Timing comes from measured speech in each source clip; the words come from the edit decision list.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from v2_edl import SHOTS

TL = {c["label"]: c for c in json.load(open(sys.argv[1]))}
TRIM = {int(k): v for k, v in json.load(open(sys.argv[2])).items()}
TIM = {**{f"old:{k}": v for k, v in json.load(open(sys.argv[3])).items()},
       **{f"up:{k}": v for k, v in json.load(open(sys.argv[4])).items()}}
TIM["old:99"] = TIM.get("up:7596ce4e", [])  # VO 17 with its rebuilt last word
INTRO, OUT = float(sys.argv[5]), sys.argv[6]

EN = {
 "घर से दूर, पुणे में अकेली रहती हूँ… और मुझे लगता था, मेरी ज़िंदगी में सबने मुझे सिर्फ़ दुख दिया है।":
   "I live alone in Pune, far from home… and I used to feel that everyone in my life had only ever hurt me.",
 "रिया… आज तो फ़ोन उठा ले बेटा…": "Riya… at least today, pick up the phone, beta…",
 "नेहा… आरव… माँ। चौथा नाम… बाद में।": "Neha… Aarav… Maa. The fourth name… later.",
 "उस रात मैं सोई… और मेरी आँख खुली, अपने ही मन की अदालत में।": "That night I fell asleep… and woke up in the court of my own mind.",
 "मैं कहाँ हूँ… ये जगह कौन सी है?": "Where am I… what is this place?",
 "रिया शर्मा… तुम्हारे ख़िलाफ़ केस तुमने ही किया है।": "Riya Sharma… the case against you was filed by you.",
 "ये अदालत तुम्हारे मन की है। यहाँ शीशे झूठ नहीं बोलते।": "This court is your own mind. Here, the mirrors don't lie.",
 "तुम… तुम मैं हो?": "You… you are me?",
 "ये मेरा मन था… जहाँ मैं ही वकील थी, मैं ही जज… और मैं ही मुजरिम।": "This was my mind… where I was the lawyer, the judge… and the accused.",
 "तीन गवाह आएँगे।": "Three witnesses will come.",
 "मुझे किसी की ज़रूरत नहीं। मैं सही हूँ।": "I don't need anyone. I am right.",
 "नेहा… मेरी पंद्रह साल पुरानी सहेली। उसकी सगाई हो गई… और उसने मुझे बताया तक नहीं।":
   "Neha… my friend of fifteen years. She got engaged… and didn't even tell me.",
 "…और मुझे बताया तक नहीं?": "…and she didn't even tell me?",
 "पंद्रह साल की दोस्ती… और इसकी सगाई की ख़बर मुझे इंस्टाग्राम से मिली!": "Fifteen years of friendship… and I found out about her engagement on Instagram!",
 "आरव… जिससे मैंने सबसे ज़्यादा प्यार किया। मुझे लगता था, उसने मेरा साथ छोड़ दिया।":
   "Aarav… the one I loved the most. I thought he had abandoned me.",
 "जिससे सबसे ज़्यादा प्यार किया… वही छोड़ गया।": "The one I loved the most… is the one who left.",
 "तुमने मुझे सबके सामने छोटा किया!": "You humiliated me in front of everyone!",
 "मैंने बस तुम्हें रोकना चाहा था।": "I only wanted to stop you.",
 "माफ़ी?": "An apology?",
 "गलती उसकी थी।": "It was his fault.",
 "अब माँ की बारी है।": "Now it's Maa's turn.",
 "खाना खाया, बेटा?": "Have you eaten, beta?",
 "हर बार वही सवाल, माँ।": "The same question every time, Maa.",
 "और माँ… जो हर रोज़ बस एक ही सवाल पूछती थी — खाना खाया? मुझे वो सवाल बोझ लगता था।":
   "And Maa… who asked just one question every day — have you eaten? That question felt like a burden.",
 "तू अकेली नहीं रह पाएगी।": "You won't be able to live alone.",
 "आपको मेरी कोई परवाह नहीं है।": "You don't care about me at all.",
 "आपने मुझे कभी समझा ही नहीं, सिर्फ़ खाना पूछा।": "You never understood me. You only asked if I'd eaten.",
 "और फिर… शीशे ने मुझे वो दिखाया, जो उस दिन मैंने देखना ही नहीं चाहा।": "And then… the mirror showed me what I never wanted to see that day.",
 "रिया, मुझे तुझे कुछ बताना है…": "Riya, I have something to tell you…",
 "अच्छा छोड़, तू बता, तेरा दिन कैसा था?": "Never mind, you tell me — how was your day?",
 "तू बात तो कर।": "At least talk to me.",
 "अब…": "Now…",
 "कोई फ़ायदा नहीं।": "…there's no point.",
 "पर सच ये था… उसने बताने की बहुत कोशिश की थी। मैं ही अपने दुख में इतनी डूबी थी, कि उसकी ख़ुशी सुन ही नहीं पाई।":
   "But the truth was… she tried so hard to tell me. I was so drowned in my own pain that I couldn't hear her joy.",
 "रिया… प्लीज़, सब देख रहे हैं।": "Riya… please, everyone's watching.",
 "आज मेरा दिन बहुत ख़राब था, रिया…": "I had a really bad day today, Riya…",
 "तुम्हारा ख़राब था? पहले मेरा सुनो…": "Yours was bad? Listen to mine first…",
 "तुम्हारी कहानी में मैं कभी सही हो ही नहीं सकता…": "In your story, I can never be right…",
 "क्योंकि उसमें सिर्फ़ एक ही किरदार है।": "because it has only one character.",
 "पर उसने मुझे नहीं छोड़ा था… मैंने ही उसे कभी अपनी कहानी में जगह नहीं दी।":
   "But he never left me… I never gave him a place in my story.",
 "मैं अकेली कैसे रहूँगी…": "How will I live alone…",
 "ठीक है बेटा…": "Okay, beta…",
 "मुझे कभी दिखा ही नहीं… कि मेरे जाने के बाद, वो घर कितना ख़ाली हो गया था।": "I never saw… how empty that house became after I left.",
 "सच सुनने की हिम्मत है, रिया?": "Do you have the courage to hear the truth, Riya?",
 "हाँ…": "Yes…",
 "आज कौन सी तारीख़ है, रिया?": "What's the date today, Riya?",
 "…माँ का जन्मदिन।": "…Maa's birthday.",
 "कोई बात नहीं… बिज़ी होगी।": "It's alright… she must be busy.",
 "मैं अपने आँसुओं में इतनी डूबी रही… कि माँ के आँसू मुझे कभी दिखे ही नहीं।": "I was so drowned in my own tears… that I never saw Maa's.",
 "अहंकार हमेशा 'मैं' नहीं चिल्लाता… कभी-कभी वो आँसू पहनकर आता है।": "Ego doesn't always shout 'me'… sometimes it comes wearing tears.",
 "सच ये है… तुम गलत नहीं थी, तुम थक गई थी।": "The truth is… you weren't wrong. You were tired.",
 "चौथा नाम लिखो।": "Write the fourth name.",
 "…रिया।": "…Riya.",
 "माँ… मुझे माफ़ कर दो…": "Maa… please forgive me…",
 "मैं समझ गई, रिया।": "I understand, Riya.",
 "मैं तुम्हारे साथ हूँ।": "I'm with you.",
 "फ़ैसला सुनाया जाता है…": "The verdict is…",
 "ख़ुद को माफ़ कर दो।": "Forgive yourself.",
 "हाँ बेटा?": "Yes, beta?",
 "माँ… मैंने आपके सारे मैसेज पढ़ लिए। राजमा बचा है?": "Maa… I read all your messages. Is there any rajma left?",
 "तेरे लिए तो रोज़ थोड़ा बचाकर रखती हूँ।": "I save a little for you every single day.",
 "हैप्पी बर्थडे, माँ… सॉरी… मैं घर आ रही हूँ।": "Happy birthday, Maa… I'm sorry… I'm coming home.",
 "माफ़ी माँगना हार नहीं थी… वो मेरी सबसे बड़ी जीत थी।": "Saying sorry wasn't losing… it was my biggest win.",
 "खाना खाया?": "Have you eaten?",
 "आपके साथ खा रही हूँ, माँ।": "I'm eating with you, Maa.",
 "हम सबके मन में एक अदालत चलती है… जहाँ हम ख़ुद को हमेशा बेगुनाह मानते हैं। आज एक बार… अपने मन की तह तक जाकर देखिए।":
   "In all our minds, a court is always in session… where we always find ourselves innocent. Today, just once… look deep into your own mind.",
}

def ts(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

cues = [(0.6, 6.2, "रिया शर्मा… तुम्हारे ख़िलाफ़ केस तुमने ही किया है।")]  # cold open over black
for shot in SHOTS:
    label, src, tin, tout, look, subs = shot[:6]
    if not subs or label not in TL: continue
    c = TL[label]; o = shot[7] if len(shot) > 7 else {}
    if tin is None and tout is None and src.startswith("old:") and int(src[4:]) in TRIM:
        tin, tout = TRIM[int(src[4:])]
    tin = tin or 0.0; d = c["dur"]; tout = tin + d
    segs = [(s, e) for s, e, *_ in TIM.get(src, []) if e > tin and s < tout]
    a = max(segs[0][0], tin) - tin if segs else 0.4
    b = min(segs[-1][1], tout) - tin if segs else d - 0.4
    if len(segs) == len(subs): spans = [(max(s, tin) - tin, min(e, tout) - tin) for s, e in segs]
    else:
        tot = sum(len(x) for x in subs); spans, t = [], a
        for x in subs: L = (b - a) * len(x) / tot; spans.append((t, t + L)); t += L
    base = c["start"] + INTRO
    for (s0, e0), text in zip(spans, subs):
        cues.append((base + s0, base + min(d, max(e0, s0 + 1.2) + 0.3), text))
cues.sort()
for k in range(len(cues) - 1):
    s, e, t = cues[k]; cues[k] = (s, min(e, cues[k + 1][0] - 0.05), t)
missing = [t for _, _, t in cues if t not in EN]
assert not missing, f"no English for: {missing}"
for lang in ("hi", "en"):
    with open(f"{OUT}.{lang}.srt", "w", encoding="utf-8") as fh:
        for n, (s, e, t) in enumerate(cues, 1):
            fh.write(f"{n}\n{ts(s)} --> {ts(e)}\n{t if lang == 'hi' else EN[t]}\n\n")
print("cues:", len(cues))

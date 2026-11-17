"""Edit decision list for script V2 ("Andar Ki Adalat", see film/SCRIPT_V2.md).

Each shot: (label, source, in, out, look, subtitle lines, name card[, opts])
 source: "old:N"   -> clip N of the original 48-clip cut (clips/cNN.mp4, trims.json applies)
         "up:xxxx" -> an uploaded file whose name starts with xxxx
         "card"    -> a chapter card over black (text in opts["text"], length opts["dur"])
 in/out: seconds in the source (None = use trims / full length)
 look:   W warm real life, C mind-courtroom (letterbox), M mirror-truth replay, S sepia memory, G golden morning
 opts:   mute=[(a, b)]   silence those source seconds (stray / repeated words)
         gain=dB         audio gain
         crop=(x, y, w)  keep only this part of the frame (fractions; height follows 16:9)
         push=z          slow push-in to zoom z over the shot
         pic=(src, in)   picture from another clip while the sound stays (show who is speaking)
         fin/fout=(s, colour)  fade from / to black or white
         tag=text        small label in the corner for the first seconds (e.g. the mirror replays)
         split=((x0, w), (x1, w))  phone-call split screen from two vertical strips of the same frame
         speak=((a, b), (a, b))    when each side speaks (the other side is dimmed)
         hold=s          freeze the frame at `in` for s seconds with a slow push-in (continues a shot, no replay)
         slow=f          slow motion (source window plays f times slower, sound muted)
         phone=[(a, b)]  make those source seconds sound like a phone line
         pitch=(a, b, r)  re-pitch those source seconds by ratio r (tell two similar AI voices apart)
         narr=True       this shot is narration (subtitles in yellow)
         title=(t, sub)  chapter title over the picture for the first seconds
         vo=text         Riya's inner voice (narration); shown as yellow text until the voice clip exists

Fixes from the frame-by-frame review are noted inline.
"""
MIRROR_TAG = "शीशे का सच"

SHOTS = [
 # --- 1. hook and setup
 ("1",  "up:1a9d2885", None, 9.3, "W", ["घर से दूर, पुणे में अकेली रहती हूँ… और मुझे लगता था, मेरी ज़िंदगी में सबने मुझे सिर्फ़ दुख दिया है।"], None, {"narr": True, "fin": (2.0, "black")}),  # VO 1
 # Maa's voice note: only the lit phone is shown, so nobody on screen seems to say Maa's words
 ("2",  "up:2f6bfda3", None, 8.5, "W", ["रिया… आज तो फ़ोन उठा ले बेटा…"], None, {"tag": "माँ का वॉइसमेल"}),  # R1: only the phone is seen
 ("3",  "up:90613145", None, None, "W", ["नेहा… आरव… माँ। चौथा नाम… बाद में।"], None),
 ("4",  "old:3",  None, None, "W", [], None, {"fout": (1.5, "black")}),
 ("4v", "up:8cdaaabe", None, 8.9, "C", ["उस रात मैं सोई… और मेरी आँख खुली, अपने ही मन की अदालत में।"], None, {"narr": True, "fout": (1.0, "black")}),  # VO 2
 ("5",  "old:4",  None, None, "C", ["मैं कहाँ हूँ… ये जगह कौन सी है?"], None, {"fin": (1.5, "black")}),
 ("6",  "old:5",  None, None, "C", ["रिया शर्मा… तुम्हारे ख़िलाफ़ केस तुमने ही किया है।"], None),
 ("7",  "up:0f798bb4", None, 8.0, "C", ["ये अदालत तुम्हारे मन की है। यहाँ शीशे झूठ नहीं बोलते।"], None),
  ("9",  "old:6",  None, None, "C", ["तुम… तुम मैं हो?"], None, {"tag": "जज रिया — रिया का अपना मन"}),  # who is she?
 # the judge in this take has an older face: frame on Riya only, the question comes from off-screen
 # the channel's theme (मन की तह): the court is her own mind
 ("9v", "up:c3d574aa", None, 9.3, "C", ["ये मेरा मन था… जहाँ मैं ही वकील थी, मैं ही जज… और मैं ही मुजरिम।"], None, {"narr": True}),  # VO 16
 # --- 2. witness 1: Neha
 ("8a", "old:14", 0.0, 1.35, "C", ["तीन गवाह आएँगे।"], None),
 ("8b", "old:14", 3.7, None, "C", ["मुझे किसी की ज़रूरत नहीं। मैं सही हूँ।"], None),
 # --- part A: Riya's case - her three accusations
 ("c1", "up:76e8986c", None, None, "W", ["नेहा… मेरी पंद्रह साल पुरानी सहेली। उसकी सगाई हो गई… और उसने मुझे बताया तक नहीं।"], None, {"narr": True, "title": ("पहला गवाह — नेहा", "15 साल पुरानी दोस्त")}),
 ("n1", "up:70c5c1a3", None, None, "W", ["…और मुझे बताया तक नहीं?"], None),
 ("11", "up:6de22cd4", None, 8.0, "C", ["पंद्रह साल की दोस्ती… और इसकी सगाई की ख़बर मुझे इंस्टाग्राम से मिली!"], None),
 ("c2", "up:9e695c1c", None, None, "W", ["आरव… जिससे मैंने सबसे ज़्यादा प्यार किया। मुझे लगता था, उसने मेरा साथ छोड़ दिया।"], None, {"narr": True, "title": ("दूसरा गवाह — आरव", "जिससे रिया ने प्यार किया")}),
 ("n2", "up:19bf35dd", 1.4, None, "W", [], None),
 ("16", "up:f0d1f21f", 1.6, None, "C", ["जिससे सबसे ज़्यादा प्यार किया… वही छोड़ गया।"], None),
 ("18", "old:10", None, None, "C", ["तुमने मुझे सबके सामने छोटा किया!", "मैंने बस तुम्हें रोकना चाहा था।"], None),
 ("20", "old:18", None, None, "C", ["माफ़ी?", "गलती उसकी थी।"], None, {"mute": [(3.2, 4.6)]}),  # "माफ़ी" twice
 ("22a", "old:27", 0.0, 2.45, "C", [], None),
 ("22b", "old:27", 2.45, 3.95, "C", ["अब माँ की बारी है।"], None, {"pic": ("old:18", 0.0)}),
 ("22c", "old:27", 3.95, None, "C", [], None),
 ("24", "old:11", None, None, "W", ["खाना खाया, बेटा?", "हर बार वही सवाल, माँ।"], None, {"fout": (0.6, "black"), "title": ("तीसरा गवाह — माँ", "जिसे रिया पीछे छोड़ आई")}),
 ("c3", "up:9cc03cfd", None, None, "W", ["और माँ… जो हर रोज़ बस एक ही सवाल पूछती थी — खाना खाया? मुझे वो सवाल बोझ लगता था।"], None, {"narr": True}),
 ("23", "old:19", None, None, "W", ["तू अकेली नहीं रह पाएगी।"], None, {"fin": (0.8, "black")}),
 ("25", "old:12", None, None, "C", ["आपको मेरी कोई परवाह नहीं है।"], None),
 ("26a", "old:28", 0.0, 2.85, "C", ["आपने मुझे कभी समझा ही नहीं, सिर्फ़ खाना पूछा।"], None),
 ("26b", "old:28", 5.2, None, "C", [], None),  # Maa crying silently, then Riya
 # --- part B: the mirror shows what really happened, one truth after another
 ("m1", "up:71f4978b", None, 7.6, "C", ["और फिर… शीशे ने मुझे वो दिखाया, जो उस दिन मैंने देखना ही नहीं चाहा।"], None, {"narr": True, "crop": (0.07, 0.0, 0.86)}),  # VO 18 (its burned-in English captions framed out)
 ("13", "up:12889a77", None, 6.6, "M", ["रिया, मुझे तुझे कुछ बताना है…", "अच्छा छोड़, तू बता, तेरा दिन कैसा था?"], None,
        {"fin": (0.25, "white"), "title": ("शीशे का सच — नेहा", "जो उस दिन रिया ने सुना ही नहीं")}),
 ("14a", "old:24", 0.0, 1.1, "M", ["तू बात तो कर।"], None, {"crop": (0.0, 0.08, 0.40)}),
 ("14b", "old:24", 1.1, 2.4, "M", ["अब…"], None, {"crop": (0.40, 0.05, 0.50)}),
 ("14c", "old:24", 4.9, 9.5, "M", ["कोई फ़ायदा नहीं।"], None, {"crop": (0.0, 0.05, 0.75), "phone": [(4.9, 6.4)]}),
 ("14s", "up:d5d4c6a6", None, None, "M", ["पर सच ये था… उसने बताने की बहुत कोशिश की थी। मैं ही अपने दुख में इतनी डूबी थी, कि उसकी ख़ुशी सुन ही नहीं पाई।"], None, {"narr": True, "fout": (0.5, "black")}),
 ("19", "old:17", None, None, "M", ["तुम्हारी कहानी में मैं कभी सही हो ही नहीं सकता…", "क्योंकि उसमें सिर्फ़ एक ही किरदार है।"], None,
        {"fin": (0.25, "white"), "title": ("शीशे का सच — आरव", "जो रिया ने कभी देखा ही नहीं")}),
 ("19s", "up:cbc75f75", None, None, "M", ["पर उसने मुझे नहीं छोड़ा था… मैंने ही उसे कभी अपनी कहानी में जगह नहीं दी।"], None, {"narr": True, "fout": (0.5, "black")}),
 ("28", "up:905460ba", None, None, "M", ["मैं अकेली कैसे रहूँगी…"], None, {"fin": (0.25, "white"), "title": ("शीशे का सच — माँ", "रिया के जाने के बाद")}),
 ("27", "old:25", 0.0, 3.3, "M", ["ठीक है बेटा…"], None, {"fin": (0.25, "white")}),
 ("29", "up:4f62cd0e", None, None, "M", [], None, {}),
 ("29v", "up:2972e4e5", None, None, "M", ["मुझे कभी दिखा ही नहीं… कि मेरे जाने के बाद, वो घर कितना ख़ाली हो गया था।"], None, {"narr": True, "fout": (0.8, "black")}),
 ("31", "old:30", None, None, "C", [], None, {"mute": [(0, 99)]}),  # English line under the silence
 # --- 5. twist and the root
 ("10", "up:7b78fadc", None, None, "C", ["सच सुनने की हिम्मत है, रिया?", "हाँ…"], None),
 ("34", "up:a20d5c8e", None, None, "C", ["आज कौन सी तारीख़ है, रिया?", "…माँ का जन्मदिन।"], None),
 ("35", "up:9640527b", None, None, "M", ["कोई बात नहीं… बिज़ी होगी।"], None, {"fin": (0.25, "white")}),
 # the father looked young (like Aarav): keep the girl and Maa only, and end before he leans in
 # bridge instead of the childhood flashback: the twist lands on Riya's own blindness
 ("35s", "up:30a5d2d9", None, 8.6, "M", ["मैं अपने आँसुओं में इतनी डूबी रही… कि माँ के आँसू मुझे कभी दिखे ही नहीं।"], None, {"narr": True, "fout": (0.6, "black")}),  # VO 15
 ("40", "up:641e0ae5", None, None, "C", ["अहंकार हमेशा 'मैं' नहीं चिल्लाता… कभी-कभी वो आँसू पहनकर आता है।"], None),
 ("41", "old:33", None, None, "C", ["सच ये है… तुम गलत नहीं थी, तुम थक गई थी।"], None),
 # --- 6. verdict
 ("43", "up:0cdf3bcf", None, None, "C", ["चौथा नाम लिखो।", "…रिया।"], None),
 ("44", "old:36", None, None, "C", ["माँ… मुझे माफ़ कर दो…"], None),
 ("45", "old:37", None, None, "C", [], None, {"gain": -9}),
 ("46", "old:38", None, 8.8, "C", ["मैं समझ गई, रिया।"], None),  # stray "मैं" after 9 s cut
 ("47", "old:39", None, None, "C", ["मैं तुम्हारे साथ हूँ।"], None),
 ("48", "old:40", None, None, "C", ["फ़ैसला सुनाया जाता है…", "ख़ुद को माफ़ कर दो।"], None, {"fout": (1.2, "white")}),
 # --- 7. new morning: every setup pays off
 ("49", "old:41", 0.0, 5.0, "G", [], None, {"fin": (1.5, "white")}),
 ("50", "up:902b666f", 7.2, None, "G", ["हाँ बेटा?"], None),
 ("51b", "up:c862d4c9", None, None, "G", ["माँ… मैंने आपके सारे मैसेज पढ़ लिए। राजमा बचा है?"], None),
 ("52", "up:d5c0f8e7", 3.5, None, "G", ["तेरे लिए तो रोज़ थोड़ा बचाकर रखती हूँ।"], None),
 ("51", "up:0cd51bcb", None, None, "G", ["हैप्पी बर्थडे, माँ… सॉरी… मैं घर आ रही हूँ।"], None),
 ("53", "old:44", 1.0, 4.5, "G", [], None),
 ("54", "old:45", 3.0, 6.5, "G", [], None),
 ("55v", "up:1ae8be95", None, 9.0, "G", ["माफ़ी माँगना हार नहीं थी… वो मेरी सबसे बड़ी जीत थी।"], None, {"narr": True}),  # VO 7
 ("56", "up:f4f66b56", None, None, "G", ["खाना खाया?", "आपके साथ खा रही हूँ, माँ।"], None,
        {"pitch": (0.9, 2.1, 0.80)}),  # R5: Maa's line pitched down so the two voices differ
 # last image speaks to the viewer: everyone has this court inside
 ("58", "up:7596ce4e", None, None, "G", ["हम सबके मन में एक अदालत चलती है… जहाँ हम ख़ुद को हमेशा बेगुनाह मानते हैं। आज एक बार… अपने मन की तह तक जाकर देखिए।"], None, {"narr": True, "pic": ("up:2c870df4", 0.0)}),  # VO 17 over the mirror
 ("58h", "up:2c870df4", 9.9, None, "G", [], None, {"hold": 2.6, "mute": [(0, 99)], "fout": (2.0, "black")}),  # let the last word land, then fade
]

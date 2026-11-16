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

Fixes from the frame-by-frame review are noted inline.
"""
MIRROR_TAG = "शीशे का सच"

SHOTS = [
 # --- 1. hook and setup
 ("1",  "old:1",  0.0, 6.5, "W", [], None, {"fin": (2.0, "black")}),  # pace: 6.5 s is enough
 # Maa's voice note: only the lit phone is shown, so nobody on screen seems to say Maa's words
 ("2",  "up:d844e215", 1.5, None, "W", ["रिया… आज तो फ़ोन उठा ले बेटा…"], None,
        {"crop": (0.38, 0.42, 0.5), "push": 1.12}),
 ("3",  "up:90613145", None, None, "W", ["नेहा… आरव… माँ। चौथा नाम… बाद में।"], None),
 ("4",  "old:3",  2.5, None, "W", [], None, {"fout": (1.5, "black")}),  # start nearer the fog
 ("5",  "old:4",  None, None, "C", ["मैं कहाँ हूँ… ये जगह कौन सी है?"], None, {"fin": (1.5, "black")}),
 ("6",  "old:5",  None, None, "C", ["रिया शर्मा… तुम्हारे ख़िलाफ़ केस तुमने ही किया है।"], None),
 ("7",  "up:0f798bb4", None, 8.0, "C", ["ये अदालत तुम्हारे मन की है। यहाँ शीशे झूठ नहीं बोलते।"], None),
 ("8",  "old:14", None, None, "C", ["तीन गवाह आएँगे।", "मुझे किसी की ज़रूरत नहीं। मैं सही हूँ।"], None),
 ("9",  "old:6",  None, None, "C", ["तुम… तुम मैं हो?"], None, {"tag": "जज रिया — रिया का अपना मन"}),  # who is she?
 # the judge in this take has an older face: frame on Riya only, the question comes from off-screen
 ("10", "old:16", None, None, "C", ["सच सुनने की हिम्मत है, रिया?", "हाँ…"], None, {"crop": (0.36, 0.0, 0.64)}),
 # --- 2. witness 1: Neha
 ("c1", "card", None, None, "C", [], None, {"text": "पहला गवाह — नेहा", "sub": "15 साल पुरानी दोस्त", "dur": 2.6}),
 ("11", "up:6de22cd4", None, 8.0, "C", ["पंद्रह साल की दोस्ती… और इसकी सगाई की ख़बर मुझे इंस्टाग्राम से मिली!"], None),
 ("12", "old:7",  None, None, "W", ["तू हमेशा अपनी ही सुनती है, रिया।", "मैंने कुछ गलत नहीं कहा था।"], None,
        {"mute": [(1.95, 3.45)]}),  # stray second "रिया"
 ("13", "up:12889a77", None, 6.6, "M", ["रिया, मुझे तुझे कुछ बताना है…", "अच्छा छोड़, तू बता, तेरा दिन कैसा था?"], None,
        {"fin": (0.25, "white"), "tag": MIRROR_TAG}),
 # the phone call was one frame with both girls side by side: split into Neha's half, then Riya's half
 ("14a", "old:24", 0.0, 1.45, "M", ["तू बात तो कर।"], None, {"crop": (0.0, 0.0, 0.55)}),
 ("14b", "old:24", 1.45, None, "M", ["अब कोई फ़ायदा नहीं।"], None, {"crop": (0.45, 0.0, 0.55)}),
 ("15", "old:8",  None, None, "C", ["मैंने बस सच बोला था…", "पर तूने उसे हमला समझ लिया।"], None),
 # --- 3. witness 2: Aarav
 ("c2", "card", None, None, "C", [], None, {"text": "दूसरा गवाह — आरव", "sub": "जिससे रिया ने प्यार किया", "dur": 2.6}),
 ("16", "up:f0d1f21f", 1.6, None, "C", ["जिससे सबसे ज़्यादा प्यार किया… वही छोड़ गया।"], None),
 ("17", "old:9",  None, None, "W", ["तुम कभी सुनती ही नहीं, रिया।", "तुम भी तो मुझे समझते नहीं।"], None),
 ("18", "old:10", None, None, "C", ["तुमने मुझे सबके सामने छोटा किया!", "मैंने बस तुम्हें रोकना चाहा था।"], None),
 ("19", "old:17", None, None, "M", ["तुम्हारी कहानी में मैं कभी सही हो ही नहीं सकता…", "क्योंकि उसमें सिर्फ़ एक ही किरदार है।"], None,
        {"fin": (0.25, "white"), "tag": MIRROR_TAG}),
 ("20", "old:18", None, None, "C", ["माफ़ी?", "गलती उसकी थी।"], None, {"mute": [(3.2, 4.6)]}),  # "माफ़ी" twice
 # --- 4. witness 3: Maa
 ("21", "old:23", None, None, "C", ["तुमने कभी सुना ही नहीं, सिर्फ़ जवाब दिया।", "मैंने सुना था… मुझे लगा कोई मुझे सुन ही नहीं रहा।"], None),
 # "अब माँ की बारी है" is the veiled judge's line: cut to her while it is spoken, then back to Riya freezing
 ("22a", "old:27", 0.0, 2.45, "C", [], None),
 ("22b", "old:27", 2.45, 3.95, "C", ["अब माँ की बारी है।"], None, {"pic": ("old:18", 0.0)}),
 ("22c", "old:27", 3.95, None, "C", [], None),
 ("c3", "card", None, None, "C", [], None, {"text": "तीसरा गवाह — माँ", "sub": "", "dur": 2.4}),
 ("23", "old:19", None, None, "W", ["तू अकेली नहीं रह पाएगी।"], None, {"fin": (0.8, "black")}),
 ("24", "old:11", None, None, "W", ["खाना खाया, बेटा?", "हर बार वही सवाल, माँ।"], None, {"fout": (0.6, "black")}),
 ("25", "old:12", None, None, "C", ["आपको मेरी कोई परवाह नहीं है।"], None),
 ("26", "old:28", None, None, "C", ["आपने मुझे कभी समझा ही नहीं, सिर्फ़ खाना पूछा।"], None,
        {"mute": [(2.85, 4.7)]}),  # repeated words over Maa's face
 # stop before Maa stirs a ladle inside a closed pressure cooker
 ("27", "old:25", 0.0, 3.3, "M", ["ठीक है बेटा…"], None, {"fin": (0.25, "white"), "tag": MIRROR_TAG}),
 ("28", "old:26", None, None, "M", ["मैं अकेली कैसे रहूँगी…"], None, {"fin": (0.6, "black")}),
 ("29", "old:22", None, None, "M", [], None, {"fout": (0.8, "black")}),
 ("30", "old:29", None, None, "C", ["माँ से माफ़ी?", "हर बार मेरे साथ ही क्यों होता है?!"], None),
 ("31", "old:30", None, None, "C", [], None, {"mute": [(0, 99)]}),  # English line under the silence
 # --- 5. twist and the root
 ("32", "old:31", None, None, "C", [], None),
 ("33", "old:32", None, None, "C", ["अब सच वाली बात सुनो।"], None),
 ("34", "up:a20d5c8e", None, None, "C", ["आज कौन सी तारीख़ है, रिया?", "…माँ का जन्मदिन।"], None),
 ("35", "up:9640527b", None, None, "M", ["कोई बात नहीं… बिज़ी होगी।"], None, {"fin": (0.25, "white"), "tag": MIRROR_TAG}),
 ("36", "up:5d430d7f", None, None, "C", [], None, {"fout": (0.6, "black"), "tag": "छोटी रिया — 8 साल की"}),
 ("37", "up:468af977", 0.0, 6.2, "S", [], None, {"fin": (0.6, "black")}),  # father's English line cut off
 # the father looked young (like Aarav): keep the girl and Maa only, and end before he leans in
 ("38", "old:35", 0.0, 4.6, "S", [], None, {"crop": (0.0, 0.0, 0.62), "fout": (0.6, "black")}),
 ("39", "up:de2258c2", None, None, "C", ["माँ-पापा बुरे नहीं थे, बस थके हुए थे।", "पर इस बच्ची ने सीख लिया —", "दुख में ही कोई मुझे देखता है।"], None),
 ("40", "up:641e0ae5", None, None, "C", ["अहंकार हमेशा 'मैं' नहीं चिल्लाता… कभी-कभी वो आँसू पहनकर आता है।"], None),
 ("41", "old:33", None, None, "C", ["सच ये है… तुम गलत नहीं थी, तुम थक गई थी।"], None),
 ("42", "up:c45de9d7", None, None, "C", ["तुम्हें दिखने के लिए दुखी होने की ज़रूरत नहीं…", "तुम खुश रहोगी, तब भी मैं तुम्हें देखूँगी।"], None),
 # --- 6. verdict
 ("43", "up:0cdf3bcf", None, None, "C", ["चौथा नाम लिखो।", "…रिया।"], None),
 ("44", "old:36", None, None, "C", ["माँ… मुझे माफ़ कर दो…"], None),
 ("45", "old:37", None, None, "C", [], None, {"gain": -9}),
 ("46", "old:38", None, 8.8, "C", ["मैं समझ गई, रिया।"], None),  # stray "मैं" after 9 s cut
 ("47", "old:39", None, None, "C", ["मैं तुम्हारे साथ हूँ।"], None),
 ("48", "old:40", None, None, "C", ["फ़ैसला सुनाया जाता है…", "ख़ुद को माफ़ कर दो।"], None, {"fout": (1.2, "white")}),
 # --- 7. new morning: every setup pays off
 ("49", "old:41", 0.0, 6.5, "G", [], None, {"fin": (1.5, "white")}),
 ("50", "up:902b666f", 5.5, None, "G", ["हाँ बेटा?"], None),
 ("51", "up:0cd51bcb", None, None, "G", ["हैप्पी बर्थडे, माँ… सॉरी… मैं घर आ रही हूँ।"], None),
 ("51b", "up:c862d4c9", None, None, "G", ["माँ… मैंने आपके सारे मैसेज पढ़ लिए। राजमा बचा है?"], None),
 ("52", "up:d5c0f8e7", 3.5, None, "G", ["तेरे लिए तो रोज़ थोड़ा बचाकर रखती हूँ।"], None),  # line starts at 5.5 s
 ("53", "old:44", 0.0, 6.0, "G", [], None),
 ("54", "old:45", 2.0, 8.0, "G", [], None),
 ("55", "up:371fae17", 0.0, 7.5, "G", [], None, {"gain": -12}),
 ("56", "up:f51b022a", None, None, "G", ["खाना खाया?", "आपके साथ खा रही हूँ, माँ।"], None),
 ("57", "old:46", 0.0, 7.0, "G", [], None, {"fout": (2.5, "black")}),
]

"""Edit decision list for script V2 ("Andar Ki Adalat", see film/SCRIPT_V2.md).

Each shot: (label, source, in, out, look, subtitle lines, name card)
 source: "old:N"   -> clip N of the original 48-clip cut (clips/cNN.mp4, trims.json applies)
         "up:xxxx" -> an uploaded file whose name starts with xxxx
         "todo:X"  -> new clip X not delivered yet (placeholder card in previews)
 in/out: seconds in the source (None = use trims / full length)
 look:   W warm real life, C mind-courtroom (letterbox), M mirror-truth replay, S sepia memory, G golden morning
 audio:  optional dict: {"mute": [(a, b), ...]} silences those source seconds, {"gain": dB}
"""

SHOTS = [
 # --- 1. hook and setup
 ("1",  "old:1",  None, None, "W", [], None),
 ("2",  "up:d844e215", None, None, "W", ["रिया… आज तो फ़ोन उठा ले बेटा…"], None),
 ("3",  "up:90613145", None, None, "W", ["नेहा… आरव… माँ। चौथा नाम… बाद में।"], None),
 ("4",  "old:3",  None, None, "W", [], None),
 ("5",  "old:4",  None, None, "C", ["मैं कहाँ हूँ… ये जगह कौन सी है?"], None),
 ("6",  "old:5",  None, None, "C", ["रिया शर्मा… तुम्हारे ख़िलाफ़ केस तुमने ही किया है।"], None),
 ("7",  "up:0f798bb4", None, 8.0, "C", ["ये अदालत तुम्हारे मन की है। यहाँ शीशे झूठ नहीं बोलते।"], None),
 ("8",  "old:14", None, None, "C", ["तीन गवाह आएँगे।", "मुझे किसी की ज़रूरत नहीं। मैं सही हूँ।"], None),
 ("9",  "old:6",  None, None, "C", ["तुम… तुम मैं हो?"], None),
 ("10", "old:16", None, None, "C", ["सच सुनने की हिम्मत है, रिया?", "हाँ…"], None),
 # --- 2. witness 1: Neha
 ("11", "up:6de22cd4", None, 8.0, "C", ["पंद्रह साल की दोस्ती… और इसकी सगाई की ख़बर मुझे इंस्टाग्राम से मिली!"],
        "नेहा — 15 साल की दोस्त"),
 ("12", "old:7",  None, None, "W", ["तू हमेशा अपनी ही सुनती है, रिया।", "मैंने कुछ गलत नहीं कहा था।"], None,
        {"mute": [(1.95, 3.45)]}),  # stray second "रिया"
 ("13", "up:12889a77", None, 6.6, "M", ["रिया, मुझे तुझे कुछ बताना है…", "अच्छा छोड़, तू बता, तेरा दिन कैसा था?"], None),
 ("14", "old:24", None, None, "M", ["तू बात तो कर।", "अब कोई फ़ायदा नहीं।"], None),
 ("15", "old:8",  None, None, "C", ["मैंने बस सच बोला था…", "पर तूने उसे हमला समझ लिया।"], None),
 # --- 3. witness 2: Aarav
 ("16", "up:f0d1f21f", None, None, "C", ["जिससे सबसे ज़्यादा प्यार किया… वही छोड़ गया।"], None),
 ("17", "old:9",  None, None, "W", ["तुम कभी सुनती ही नहीं, रिया।", "तुम भी तो मुझे समझते नहीं।"], "आरव — जिससे प्यार किया"),
 ("18", "old:10", None, None, "C", ["तुमने मुझे सबके सामने छोटा किया!", "मैंने बस तुम्हें रोकना चाहा था।"], None),
 ("19", "old:17", None, None, "M", ["तुम्हारी कहानी में मैं कभी सही हो ही नहीं सकता…", "क्योंकि उसमें सिर्फ़ एक ही किरदार है।"], None),
 ("20", "old:18", None, None, "C", ["माफ़ी?", "गलती उसकी थी।"], None, {"mute": [(3.2, 4.6)]}),  # "माफ़ी" said twice (second at 3.9-4.4 s)
 # --- 4. witness 3: Maa
 ("21", "old:23", None, None, "C", ["तुमने कभी सुना ही नहीं, सिर्फ़ जवाब दिया।", "मैंने सुना था… मुझे लगा कोई मुझे सुन ही नहीं रहा।"], None),
 ("22", "old:27", None, None, "C", ["अब माँ की बारी है।"], None),
 ("23", "old:19", None, None, "W", ["तू अकेली नहीं रह पाएगी।"], "माँ"),
 ("24", "old:11", None, None, "W", ["खाना खाया, बेटा?", "हर बार वही सवाल, माँ।"], None),
 ("25", "old:12", None, None, "C", ["आपको मेरी कोई परवाह नहीं है।"], None),
 ("26", "old:28", None, None, "C", ["आपने मुझे कभी समझा ही नहीं, सिर्फ़ खाना पूछा।"], None,
        {"mute": [(2.85, 4.7)]}),  # "खाना पूछा" repeated over Maa's face - looked like Maa said it too
 ("27", "old:25", None, None, "M", ["ठीक है बेटा…"], None),
 ("28", "old:26", None, None, "M", ["मैं अकेली कैसे रहूँगी…"], None),
 ("29", "old:22", None, None, "M", [], None),
 ("30", "old:29", None, None, "C", ["माँ से माफ़ी?", "हर बार मेरे साथ ही क्यों होता है?!"], None),
 ("31", "old:30", None, None, "C", [], None, {"mute": [(0, 99)]}),  # English line "You are not alone"
 # --- 5. twist and the root
 ("32", "old:31", None, None, "C", [], None),
 ("33", "old:32", None, None, "C", ["अब सच वाली बात सुनो।"], None),
 ("34", "up:a20d5c8e", None, None, "C", ["आज कौन सी तारीख़ है, रिया?", "…माँ का जन्मदिन।"], None),
 ("35", "up:9640527b", None, None, "M", ["कोई बात नहीं… बिज़ी होगी।"], None),
 ("36", "up:5d430d7f", None, None, "C", [], None),
 ("37", "up:468af977", 0.0, 6.2, "S", [], None),
 ("38", "old:35", None, None, "S", [], None),
 ("39", "up:de2258c2", None, None, "C", ["माँ-पापा बुरे नहीं थे, बस थके हुए थे।", "पर इस बच्ची ने सीख लिया —", "दुख में ही कोई मुझे देखता है।"], None),
 ("40", "up:641e0ae5", None, None, "C", ["अहंकार हमेशा 'मैं' नहीं चिल्लाता… कभी-कभी वो आँसू पहनकर आता है।"], None),
 ("41", "old:33", None, None, "C", ["सच ये है… तुम गलत नहीं थी, तुम थक गई थी।"], None),
 ("42", "up:c45de9d7", None, None, "C", ["तुम्हें दिखने के लिए दुखी होने की ज़रूरत नहीं…", "तुम खुश रहोगी, तब भी मैं तुम्हें देखूँगी।"], None),
 # --- 6. verdict
 ("43", "up:0cdf3bcf", None, None, "C", ["चौथा नाम लिखो।", "…रिया।"], None),
 ("44", "old:36", None, None, "C", ["माँ… मुझे माफ़ कर दो…"], None),
 ("45", "old:37", None, None, "C", [], None, {"gain": -9}),
 ("46", "old:38", None, 8.8, "C", ["मैं समझ गई, रिया।"], None),  # cut stray "मैं" at 9.1 s
 ("47", "old:39", None, None, "C", ["मैं तुम्हारे साथ हूँ।"], None),
 ("48", "old:40", None, None, "C", ["फ़ैसला सुनाया जाता है…", "ख़ुद को माफ़ कर दो।"], None),
 # --- 7. new morning: every setup pays off
 ("49", "old:41", None, None, "G", [], None),
 ("50", "up:902b666f", 5.5, None, "G", ["हाँ बेटा?"], None),
 ("51", "up:0cd51bcb", None, None, "G", ["हैप्पी बर्थडे, माँ… सॉरी… मैं घर आ रही हूँ।"], None),
 ("52", "up:d5c0f8e7", None, None, "G", ["तेरे लिए तो रोज़ थोड़ा बचाकर रखती हूँ।"], None),
 ("53", "old:44", None, None, "G", [], None),
 ("54", "old:45", None, None, "G", [], None),
 ("55", "up:371fae17", None, None, "G", [], None, {"gain": -12}),
 ("56", "up:f51b022a", None, None, "G", ["खाना खाया?", "आपके साथ खा रही हूँ, माँ।"], None),
 ("57", "old:46", None, None, "G", [], None),
]

TODO_TITLES = {
 "F": "आरव पर इल्ज़ाम", "G": "ट्विस्ट: आज कौन सी तारीख़ है?", "H": "माँ का अकेला जन्मदिन",
 "I": "अहंकार आँसू पहनकर आता है", "J": "चौथा नाम", "K": "हैप्पी बर्थडे, माँ",
}

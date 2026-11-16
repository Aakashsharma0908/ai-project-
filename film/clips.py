#!/usr/bin/env python3
"""Single source of truth for the 48-clip short film.

Run:  python3 film/clips.py
Writes film/prompts/clip_01.txt .. clip_48.txt (one self-contained prompt per
clip, ready to paste into a video model) and film/prompts/ALL_CLIPS.md.

Video models have no memory between generations, so every prompt repeats the
full locked description of each character / location / look it uses.
"""
import json, re
from pathlib import Path

STYLE = ("10-second clip, cinematic, photorealistic, 16:9, natural film grain, "
         "shallow depth of field. No on-screen text, no subtitles, no captions, "
         "no readable writing on phones, paper or screens. "
         "All spoken dialogue is in Hindi, spoken exactly as written, natural lip sync.")

CHAR = {
 "RIYA": "RIYA: Indian woman, 26, wheatish skin, shoulder-length wavy black hair, small gold nose pin, grey oversized hoodie.",
 "JUDGE RIYA": "JUDGE RIYA: exactly the same face as RIYA (Indian woman, 26, wheatish skin, small gold nose pin), black hair worn open and neat, plain white cotton saree, calm still eyes, faint soft glow around her.",
 "LITTLE RIYA": "LITTLE RIYA: Indian girl, 8, two oiled plaits with red ribbons, white school shirt, navy pinafore.",
 "MAA": "MAA: Indian mother, 52, light green cotton saree, grey-streaked hair in a bun, small red bindi, thin spectacles.",
 "NEHA": "NEHA: Indian woman, 26, curly hair, mustard yellow kurti.",
 "AARAV": "AARAV: Indian man, 28, short trimmed beard, rectangular glasses, white shirt with sleeves rolled up.",
 "VEILED JUDGE": "VEILED JUDGE: a figure seated on a high judge's seat, fully covered by a sheer black veil, face not visible; calm, echoing female voice.",
}
LOC = {
 "PG ROOM": "PG ROOM: small Pune paying-guest room, narrow bed, one window, yellow lamp.",
 "COURTROOM": "COURTROOM: vast surreal old Indian colonial-era courtroom inside a mind, dark wooden benches, still ceiling fans, tall mirrors on every wall, fog on the floor, dark blue moody light.",
 "MAA'S HOME": "MAA'S HOME: modest Kanpur home with a wooden front door, small kitchen with a pressure cooker, small dining table with steel plates.",
}
LOOK = {
 "WARM": "LOOK: warm golden tones.",
 "TRUTH": "LOOK: cool blue-grey, desaturated tones.",
 "SEPIA": "LOOK: old 1990s sepia film look, soft and grainy.",
}

# (number, characters, location, look, shot description)
CLIPS = [
 (1, ["RIYA"], "PG ROOM", None, "Rainy night. RIYA sits on the bed holding a closed diary, staring at rain on the window. Slow push-in. Sound of rain. No dialogue."),
 (2, ["RIYA"], None, None, "Top-down close-up of an open diary page: three short lines scribbled in red ink, blurred and unreadable, and a fourth line left empty; a red pen rests beside it. RIYA's hand (grey hoodie sleeve) taps the pen on the empty fourth line. RIYA whispers: \"चौथा नाम... बाद में लिखूँगी।\""),
 (3, ["RIYA"], None, None, "Extreme close-up of RIYA's face: she slowly closes her eyes and a single tear rolls down. The rain sound fades to silence. No dialogue."),
 (4, ["RIYA"], None, None, "Dream world: RIYA walks down an endless spiral stone staircase into darkness; glowing glass shards holding blurry family memories float around her. Dark blue fog. Camera follows from behind. No dialogue."),
 (5, ["VEILED JUDGE"], "COURTROOM", None, "Wide shot: the VEILED JUDGE on the high seat, an empty wooden witness dock in the centre. Slow dolly forward, low hum. No dialogue."),
 (6, ["RIYA", "VEILED JUDGE"], "COURTROOM", None, "RIYA faces the VEILED JUDGE, fists clenched. RIYA: \"आज सबको उनके किए की सज़ा मिलेगी।\""),
 (7, ["RIYA"], "PG ROOM", "WARM", "Night. RIYA lies in bed, face lit by her phone screen, hurt. RIYA: \"पंद्रह साल की दोस्ती... और उसकी सगाई की खबर मुझे इंस्टाग्राम से मिली।\""),
 (8, [], None, None, "Extreme close-up: a wooden gavel strikes in slow motion, dust rises, one loud echoing knock. No dialogue."),
 (9, ["RIYA"], None, "TRUTH", "Outside a small café, daytime. RIYA reads something on her phone, her face falls; she holds back tears, quickly wipes her eyes, takes a breath, forces a smile and walks into the café. No dialogue."),
 (10, ["RIYA", "NEHA"], None, "TRUTH", "Inside the café, camera focused on RIYA. NEHA happily holds up a letter: \"मुझे जॉब मिल गई!\" RIYA, hand on her own chest: \"वाह, तुझे तो सब मिल जाता है... मेरा फिर रिजेक्ट हो गया।\" NEHA's smile slowly fades."),
 (11, [], None, "TRUTH", "Close-up of two coffee cups on a café table: one empty, one full and untouched, no steam. No dialogue."),
 (12, ["NEHA"], None, "TRUTH", "Apartment rooftop at dusk. NEHA on the phone, hesitates, smiles weakly: \"रिया, मुझे तुझे कुछ बताना... कुछ नहीं। तू बता, तेरा दिन कैसा था?\""),
 (13, ["RIYA", "VEILED JUDGE"], "COURTROOM", None, "VEILED JUDGE: \"उसने तुम्हें बताना क्यों बंद किया? ...माफ़ी माँगोगी?\" RIYA looks away, arms crossed: \"मैं क्यों माँगूँ? वो बदल गई।\""),
 (14, ["AARAV"], None, "WARM", "Apartment doorway. AARAV walks out with a backpack, not looking back. RIYA's voice off-screen: \"जिससे सबसे ज़्यादा प्यार किया... वही छोड़ गया।\""),
 (15, ["RIYA", "AARAV"], None, "TRUTH", "Roadside chai stall, evening. AARAV holds out two kulhad chai: \"सॉरी ना...\" RIYA turns away: \"तुम्हें मेरी परवाह ही नहीं।\""),
 (16, ["RIYA", "AARAV"], None, "TRUTH", "Bedroom at night. AARAV sits on the edge of the bed, exhausted: \"आज मेरा दिन बहुत खराब था, रिया...\" RIYA, her back to the camera, cuts him off: \"तुम्हारा खराब था? मेरा सुनो...\""),
 (17, ["AARAV"], None, "TRUTH", "Close-up of AARAV, eyes wet, defeated: \"तुम्हारी कहानी में मैं कभी सही हो ही नहीं सकता... क्योंकि उसमें सिर्फ़ एक ही किरदार है।\""),
 (18, ["RIYA", "VEILED JUDGE"], "COURTROOM", None, "VEILED JUDGE: \"माफ़ी?\" RIYA, jaw tight: \"गलती उसकी थी।\""),
 (19, ["RIYA", "MAA"], "MAA'S HOME", "WARM", "Front door, morning. RIYA pulls a suitcase out of the house. MAA, worried: \"तू अकेली नहीं रह पाएगी।\" RIYA rolls her eyes and leaves."),
 (20, ["RIYA"], "PG ROOM", None, "Evening. RIYA holds her phone on speaker, irritated. MAA's voice from the phone: \"खाना खाया? स्वेटर पहना?\" RIYA snaps: \"माँ, आप हर बार वही पूछती हो!\" and hangs up."),
 (21, ["RIYA"], "COURTROOM", None, "RIYA points at the empty witness dock, voice breaking: \"उन्हें मुझ पर कभी भरोसा था ही नहीं। उन्होंने मुझे कभी समझा ही नहीं।\""),
 (22, ["RIYA"], "PG ROOM", None, "Dark night. RIYA sits on the floor against the bed hugging her knees, crying; an office ID card lies on the floor, her phone face-down beside her. RIYA whispers: \"और जिस रात मैं सच में टूटी... तब कोई नहीं था।\""),
 (23, [], "PG ROOM", "TRUTH", "Slow push-in to the same face-down phone on the dark floor, vibrating again and again with a faint glow. No people, no dialogue."),
 (24, ["RIYA"], "PG ROOM", "TRUTH", "RIYA lies on her bed, bored, scrolling; the phone rings and she swipes to reject without looking. Close-up on her thumb. No dialogue."),
 (25, ["MAA"], "MAA'S HOME", None, "Kitchen. MAA lowers her old phone as the call ends: \"ठीक है बेटा...\" She goes back to stirring rajma; the pressure cooker whistles."),
 (26, ["MAA"], "MAA'S HOME", None, "An empty girl's bedroom, afternoon. MAA sits on the bed, gently smooths the pillow, eyes wet: \"मैं अकेली कैसे रहूँगी...\""),
 (27, ["MAA"], "MAA'S HOME", None, "Dining table, evening. MAA sets down two steel plates, looks at the empty chair, quietly puts one plate back. Only the clink of steel. No music, no dialogue."),
 (28, ["VEILED JUDGE"], "COURTROOM", None, "Slow push-in on the VEILED JUDGE: \"तुमने उनके हर सवाल को टोकना समझा... क्योंकि अहंकार को फ़िक्र भी कंट्रोल लगती है।\""),
 (29, ["RIYA", "VEILED JUDGE"], "COURTROOM", None, "VEILED JUDGE: \"माँ से माफ़ी?\" RIYA screams through tears: \"मैं क्यों माँगूँ?! हर बार मेरे साथ ही क्यों होता है?!\" The mirrors tremble, then complete silence."),
 (30, ["RIYA"], "COURTROOM", None, "Slow pull-back revealing the benches now filled with dark, silent silhouettes of people watching; RIYA small in the centre. No dialogue."),
 (31, ["VEILED JUDGE"], "COURTROOM", None, "Close-up: the VEILED JUDGE slowly raises her head toward the camera, dark blue rim light, a soft bell tone. No dialogue."),
 (32, ["JUDGE RIYA"], "COURTROOM", None, "Close-up of JUDGE RIYA, unveiled, on the high seat: \"अहंकार हमेशा नहीं कहता 'मैं बड़ी हूँ'... कभी वो आँसू पहनकर आता है।\""),
 (33, ["RIYA", "JUDGE RIYA"], "COURTROOM", None, "RIYA stares up in shock at JUDGE RIYA, who has her same face. JUDGE RIYA, gently: \"तुम्हारा दुख सच था, रिया... पर उस दुख में किसी और के दुख के लिए जगह नहीं बची।\""),
 (34, ["JUDGE RIYA"], "COURTROOM", None, "Close-up of JUDGE RIYA: \"तीन बार माफ़ी का मौका आया... तीनों बार तुमने कहा 'मैं क्यों?' दुख गलत नहीं था... वो दीवार अहंकार थी।\""),
 (35, ["LITTLE RIYA"], "COURTROOM", None, "LITTLE RIYA stands alone in the big wooden witness dock holding a report card, teary, a soft beam of light from above. No dialogue."),
 (36, ["LITTLE RIYA"], None, "SEPIA", "1990s Indian living room: LITTLE RIYA runs in holding up her report card; her father is busy on the phone, her mother tired and busy in the kitchen; nobody looks. Her smile fades. No dialogue."),
 (37, ["LITTLE RIYA"], None, "SEPIA", "1990s courtyard: LITTLE RIYA falls and cries holding her scraped knee; her mother and father rush over and hug her. No dialogue."),
 (38, ["JUDGE RIYA"], "COURTROOM", None, "Close-up of JUDGE RIYA, soft voice: \"माँ-पापा बुरे नहीं थे, बस थके हुए थे। पर इस बच्ची ने सीख लिया — दुख में ही कोई मुझे देखता है।\""),
 (39, ["RIYA", "LITTLE RIYA"], "COURTROOM", None, "Soft light. RIYA kneels and hugs LITTLE RIYA tightly. RIYA whispers: \"तुम्हें दिखने के लिए दुखी होने की ज़रूरत नहीं... तुम खुश रहोगी, तब भी मैं तुम्हें देखूँगी।\""),
 (40, [], "COURTROOM", None, "All the mirrors shatter in slow motion; warm golden morning light pours through the cracks. Soft flute music. No dialogue."),
 (41, ["RIYA"], "PG ROOM", None, "Early morning. RIYA wakes up, soft golden sunlight on her face, takes a deep calm breath. Birds chirping. No dialogue."),
 (42, ["RIYA"], "PG ROOM", None, "Top-down: the same diary open on the bed in morning light; RIYA's hand (grey hoodie sleeve) picks up a blue pen and writes slowly on the empty fourth line and beside the red lines. Writing not readable. No dialogue."),
 (43, ["RIYA"], None, None, "Close-up: RIYA's thumb hovers over her phone, hesitates, then taps send. Screen not readable. No dialogue."),
 (44, ["MAA"], "MAA'S HOME", None, "Kitchen, morning. The phone rings; MAA wipes her hands on her saree pallu and picks up on the first ring: \"हाँ बेटा?\""),
 (45, ["RIYA"], None, None, "RIYA stands by a sunny window, phone to her ear, crying and smiling: \"माँ... मैंने आपके सारे मैसेज पढ़ लिए। राजमा बचा है?\""),
 (46, ["MAA"], "MAA'S HOME", None, "Close-up of MAA on the phone in her kitchen: surprised, then tears, then a wide smile: \"पगली... तेरे लिए तो रोज़ थोड़ा बचाकर रखती हूँ।\""),
 (47, ["RIYA", "MAA"], "MAA'S HOME", "WARM", "Front door, afternoon (the same wooden door as clip 19). RIYA stands outside with her suitcase, nervous. The door opens; MAA and RIYA look at each other in a shy, awkward silence; then MAA quietly takes the suitcase from her hand. No dialogue."),
 (48, ["RIYA", "MAA"], "MAA'S HOME", None, "Dining table, warm afternoon light: two steel plates of rajma-chawal. MAA, a little hesitant, asks: \"खाना खाया?\" RIYA smiles softly: \"आपके साथ खा रही हूँ, माँ।\" MAA puts an extra spoon of rajma on RIYA's plate. Soft flute music."),
]

def prompt(n, chars, loc, look, shot):
    lines = [f"CLIP {n:02d} of 48.", STYLE]
    if chars:
        lines.append("CHARACTERS (keep identical face, hair, skin tone and clothes):")
        lines += ["- " + CHAR[c] for c in chars]
    if loc: lines.append(LOC[loc])
    if look: lines.append(LOOK[look])
    lines.append("SHOT: " + shot)
    return "\n".join(lines) + "\n"

def main():
    assert [c[0] for c in CLIPS] == list(range(1, 49))
    out = Path(__file__).parent / "prompts"; out.mkdir(exist_ok=True)
    md = ["# Short film — 48 clip prompts\n",
          "Paste each block into your video model as a separate 10 s generation. "
          "Save results as `clips/c01.mp4` .. `clips/c48.mp4`.\n"]
    for c in CLIPS:
        p = prompt(*c)
        (out / f"clip_{c[0]:02d}.txt").write_text(p, encoding="utf-8")
        md.append(f"## Clip {c[0]:02d}\n\n```text\n{p}```\n")
    (out / "ALL_CLIPS.md").write_text("\n".join(md), encoding="utf-8")
    (out / "clips.json").write_text(json.dumps(
        [{"clip": c[0], "characters": c[1], "location": c[2], "look": c[3], "prompt": prompt(*c)} for c in CLIPS],
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {len(CLIPS)} prompts to {out}")

if __name__ == "__main__":
    main()

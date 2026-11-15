# Playbook: story-montage

**For:** a narrated montage carried by one recurring character. The character is seen, not interviewed; a voiceover (or written lines) tells a small story about a place or event; the B-roll is people and texture. Travel, city, festival-as-story. Reel type `hybrid`: VO timing on the spoken lines, beats elsewhere (CLAUDE.md §4b/§4c).
**Source:** "Two Sides of Bangkok" (Dreamexplorers, 3:17, 3:2 landscape, French VO), measured by HQ on 2026-10-21. 150 detected cuts, all viewed; 112 real shots once the step-print stutters are merged.
**Status: untested here.** The reference download had **no audio track**, so the sound rules below are provisional until a pilot (or the reference with audio) confirms them. The first story-montage reel is this playbook's pilot: log every misfit as a CR. Pujo ki Asolei Sobar (external VO) is the closest existing reel.

## Pace and structure: the arc follows the story
The reference's shot length changes by section, never by habit. Measured medians (reference, 183 s of picture), with the 9:16 reel version at 45–60 s:

| Section | Reference | Reel (45–60 s) | What it does |
|---|---|---|---|
| **Sizzle hook** | 10 flashes of 4–7 frames (median 0.17 s), 0–2.3 s | 6–8 flashes of 4–6 frames, 0–1.5 s | The best moments of the whole reel, at a glance, before anything is explained |
| **Title over a real moment** | 2.2 s hold | 1.5–2 s | Small title over a quiet frame (prayer through candles) |
| **Prologue (optional)** | B&W, 5 shots, median 3.0 s | 2–3 shots, ~2.5 s | "Before": a map, a page, a room. Ends on a match cut into colour |
| **Character intro** | one 9.3 s hold | one 4–6 s hold | The character arrives; the VO sets the question |
| **Discovery** | median 1.0–1.2 s (min 0.4) | 0.9–1.2 s | Locals' faces, hands, fire, signs. The fastest stretch |
| **Chaos beat** (optional: an effect-list entry, effects-playbook §0) | 3.6 s of step-print | 1–2 s | Step-printed stutter on fast motion: the energy peak. Without it, cut the peak fast on real-speed shots |
| **Breather** | median 2.2 s | 1.5–2 s | A small human or funny moment (the 7-Eleven onigiri) |
| **Calm / sacred** | **locked 2.06 s** (1.86–2.14) | one bar per shot | The VO says time slows, and the cutting does: one shot per bar. 2.06 s is a 4/4 bar at ≈ 117 BPM |
| **Theme statement** | 3 shots of 2.0 s | 2 shots | Split screen with native-language words (below) |
| **Ending** | 2–4 s holds | 2–3 s holds | Golden or blue hour, the landmark, silhouettes, one human gesture (a high-five). Then the thank-you card |

- **The character is the thread.** They never speak to camera. Their reactions (looking up, laughing, eating, taking a photo) punctuate the B-roll every 10–15 s in the reference; in a reel, every 5–8 s.
- **Pick B-roll for people and texture:** shallow-focus environmental portraits of locals, hands at work, fire and steam, signage. The reference has very few empty wides.
- **Measure, then cut.** Run `teardown.py` on the reference you're matching; plan section by section from `analysis/beats.json`. The calm section cuts on bar downbeats.

## Camera and motion
- **Motion is mostly in camera:** slow-shutter crowds (ghosted walkers), panning speed-blur on bikes, handheld orbits around the character, symmetrical locked frames in sacred spaces. Digital push-ins are rare.
- **Step-print stutter** for the chaos beat, **only when the brief's effect list has it** (v0.12): `scripts/step_print.py` (12 images/s, each held 2–3 frames, long-shutter smear). Use it on traffic or people passing close, or on a fast but smooth camera move; on slow shots it barely reads. 1–2 s, at most twice per reel. **Only from a smooth camera path:** locked off, a steady pan, or stabilised to ≤ 2 px residual shake. Never on random handheld shake or from inside a moving vehicle, where every bump becomes a jump and the director reads it as glitchy (Diwali v3b). Check the render's hold shift (≤ 4 px) with `motion_audit.py --step-print` before placing it (effects-playbook §C).
- Everything else follows the cinematic-montage motion rules: no impact shakes on handheld, pushes only on steady holds.

## Type and graphics
- **Subtitles for the VO:** small serif, white, centred, low in frame, one line where possible. In 9:16 keep them above the bottom 320 px safe zone. They're the reel's only running text.
- **Title card:** small, wide-tracked serif caps with the place name in its own script underneath ("BANGKOK / กรุงเทพฯ"; for a Kolkata reel "KOLKATA / কলকাতা"). Over a real, quiet moment, never a plain background.
- **Credit line** ("A STORY BY …") small caps under the prologue's last shot.
- **Native-language words in the scene:** during the theme statement, the key words appear in the local script, small, placed in the picture's space (above a crowd, beside a wall), not as a caption. HyperFrames → ProRes 4444 on V5 (`motion-and-ai.md` §1).
- **Type style:** this playbook's quiet serif differs from the director profile's DIN Condensed. The brief must pick one and say so.

## Story devices (each one is a planned beat in the brief)
1. **Photo-print inserts.** The character raises a camera; a shutter click; then 3–6 of "their" photos as prints on paper, 0.7 s each on the beat, portrait and landscape alternating. `scripts/photo_prints.py` (graded stills in, ProRes out, on V4 in Normal mode so the paper stays neutral).
2. **B&W → colour reveal.** The prologue is black and white (`mono_500t` look). A **match cut on an object** (the newspaper in bed → the same newspaper in the street) carries into the first colour shot, and the colour arrives *inside* the shot as the object lowers.
   - Premiere: keyframe the V3 Lumetri Basic Saturation 0 → 100 over 12–18 frames. If the look is on the adjustment layer, key that layer.
   - Verify by render.
3. **Split screen for the theme.** "Two faces, one city": the frame splits into the two worlds.
   - Landscape splits left/right; **9:16 splits top/bottom**. Put the two clips on V1/V2. On each, Crop Top 25 % and Bottom 25 % (this keeps the middle band, 960 px). Then set Position Y −480 for the upper clip and +480 for the lower one. Verify by a still.
   - The native-language words sit in each half.
4. **Thank-you card** in the local language on black at the end ("ขอบคุณมากนะ กรุงเทพฯ"; for Kolkata "ধন্যবাদ কলকাতা"), 2–3 s. Then end.

## Transitions
- **Hard cuts everywhere.** The only exceptions are the match cut into colour and a fade to black at the end. No dissolves, no flashes, no light leaks. The sizzle and the stutter supply the energy.

## Sound (provisional: the reference had no audio)
- **The VO leads.** A1 peaks −6…−3 dB; music on A3 ducked to −18…−22 dB under the VO, about −8 dB in gaps (CLAUDE.md §2 table).
- **Music sections follow the story sections:** a lift into the discovery montage, the calm section on a sparser part of the track, the ending on the last phrase.
- **SFX only with a visible cause:** the shutter click on the first print (`sfx_prep.py` first); natural sound of bells or fire in the sacred section at −20 dB or quieter; a swish only on the stutter's fastest move (cinematic-montage rule). Never under subtitles.
- **Mixed version:** −14 LUFS ± 2, true peak ≤ −1 dBTP (`verify_render.py`).

## Colour and texture: muted, except red
**v0.8: camera-true is the default here too** (effects-playbook §A0). The goddess pilot built `muted_red` (below) and matched the preview, then the director dropped it for the camera's own colour ("over processed", then "colours all over the place"); v10b was approved camera-true. Offer `muted_red` as an option on the Round 2 sheet, not as the plan.

Measured on the reference's colour footage (17–183 s), on a 0–1 scale:

| | Reference | `muted_red` rule (when chosen) |
|---|---|---|
| Overall saturation | **0.34** | Low. Everything is calm |
| Reds | saturation **0.82**, 5 % of the frame | **Reds stay at full strength:** candles, lanterns, robes, sindoor |
| Midtones | hue **37°** | Gold (the studio's 30–45° gold target) |
| Shadows | R−B +0.06, slightly magenta | Warm red-brown, **not teal** |
| Highlights | G−M **+0.07**, hue 100° | Mint, pale |
| Blacks / whites | p02 0.024 (1.4 % crushed) / p98 0.90 (0.03 % clipped) | Deep but open blacks; whites roll off and never clip |

- **The look option is `muted_red`** in `scripts/look_preview.py`: Kodak 500T → 2383 at 35 % for the roll-off, then every hue more than 12° from red loses 55 % of its colour, with mint highlights and warm shadows.
  - Tested on four of our stills: saturation 0.54 → 0.36, reds kept.
  - **On festival footage it also mutes gold and saffron:** at 12–25 a gold Durga turns silver-grey. `--red-tolerance 25` keeps saffron (saturation 0.47); **45 keeps red and gold** and still mutes blue and green (saturation 0.54 → 0.50). On footage with gold idols, start at 45. Pick the tolerance per reel, with the director, from the preview sheet.
- **Premiere build** (V3 adjustment layer; effects-playbook §A3, verified on the goddess reel):
  - **Look:** `Kodak 5218 Kodak 2383 (by Adobe)`, picked from Lumetri → Creative → Look. It isn't a preset, so the director picks it, or computer use does with the director's OK.
  - **By script:** Creative Intensity 35 % and vignette −0.8.
  - **Hue vs Sat curve** on the same Lumetri, instead of Leave Color (Premiere 2026 has none): keep ±T° of red, ramp over about 20°, all other hues 46 %. It's a UI step: the curve can't be set by script.
  - **Mint highlights / warm shadows** (Creative tint wheels) are optional, also UI only. The goddess reel matched the preview without them.
  - **Verify by render** against the preview tile at the same tolerance.
- **B&W only for "before"** (the prologue).
- Grain: as cinematic-montage (none on night phone footage, ≤ 5 % otherwise).

## AI shots
- Not used in the reference. The story depends on real people and places, so real footage of them comes first. Generated people, the idol or a crowd only as the ladder's last step, labelled, and never as proof (`motion-and-ai.md` §3).

## QA thresholds for this style (review gate)
- **Section pacing:** each section's median shot within ±25 % of the brief's target (from the table above, scaled). The sizzle's flashes are 4–7 frames each. The calm section's cuts are within ±2 frames of the bar.
- **Colour:** every shot within its camera bands (`camera_fidelity.py`). Only if the director chose `muted_red`: overall saturation ≤ 0.40 while reds stay ≥ 0.7 (`colour_report.py`), with `camera_fidelity.py --look`. Clipped ≤ 0.5 %; prologue fully monochrome.
- **Character:** on screen at least every 15 s of reel time.
- **Transitions:** nothing but hard cuts, the one match cut, and the final fade.
- **Type:** subtitles and native-language words inside the safe zone, never over a face.

# Effects & Colour Playbook

Named moves the editor can propose in the brief's **Treatment** section. Every recipe uses Premiere Pro MCP tools. Effect names can differ between Premiere versions and languages, so check them once per session with `list_available_effects` and `list_available_transitions`.

**Before using any recipe, check `premiere-mcp-reality.md`** (same folder). Several tools named below are broken on Premiere 26.5.2 / MCP 1.2.9, and it gives the verified fallback for each. Verify every change by rendering a still, not by trusting the tool's reply.

**Golden rule:** Premiere's scripting API can't remove an effect once it's added. Plan what goes on each clip before applying anything, and change existing effects with `set_effect_property` instead of adding new ones. Check what's on a clip with `list_clip_effects` / `get_effect_properties`.

---

## 0. Restraint by default (v0.12)
**Why.** The director asked why our reels look glitchy, flickery, unnatural and grainy next to the reels they save. The 2026-11-15 diagnosis (`studio/reviews/quality-diagnosis-2026-11-15.md`) measured the 30 reels in their "Reel Concepts" collection and our 4 posted reels, as Instagram serves them.
- **The references are plain:**
  - real-time footage, hard cuts, long holds;
  - a camera that barely moves: median motion 1.8, against 6.1 (Goddess) and 8.3 (Pujo);
  - clean pictures: frame-to-frame noise 0.08, against 0.38–0.49;
  - 23 of 30 are horizontal frames.
- **Ours carried the treatment:**
  - slow motion made up from 25/30 fps in 6 of 7 reels (doubled arms, smear, "painted" faces);
  - a step-print on handheld footage ("glitchy");
  - Warp wobble;
  - punch-ins on night footage: a 2× crop raises the noise about 1.3–1.4× and doubles the size of the phone's noise-reduction blotches;
  - grain, sharpen, denoise and AI upscaling stacked round after round ("over-processed").
- **Instagram makes it worse for a small account.** It gives our reels its basic encode, which spends its bits on noise and motion and blocks the darks.

**The default treatment:**
- **Real time, hard cuts.** Footage plays at its own speed. A dissolve or a dip only where the brief places one (a section change, the ending).
- **Designed moves come only from the brief's effect list.** Nothing below is on by default:
  - speed ramps, slow motion, step-print, stutter, freeze, reverse (§C);
  - punch-ins, snap zooms, shakes (§B);
  - flashes, light leaks, whips, iris or shape wipes (§D, §A4);
  - footage inside type, text behind the subject (§E).

  The brief's Treatment lists each move it wants, with its shot and why. The director approves the list with the brief and sees each move on the preview. **Two or fewer per reel** is the guide: the references use almost none. A playbook's signature moves (creator-explainer's emphasis zooms, story-montage's chaos beat) are entries on that list, not automatic.
- **No synthetic slow motion** from footage shot below 2× the sequence rate: no Timewarp, Optical Flow or frame blending. Use real time, a longer hold, or a clip shot at 50/60 fps. The one exception: the director picks it on a full-rate phone sample of that exact shot.
- **Stabilise only what needs it.** First pick the steadier take or the steady part (`shake_report.py`, `motion_holds.py`). Warp only a shot that still fails the shake limits, and never one with an in-camera zoom or a whip.
- **No crop-in on noisy footage.** On night shots, or any shot whose camera file measures noise ≥ 0.15 (`quality_probe.py <clip> --whole`):
  - keep the base framing at ≥ 80 % of the camera width (§B);
  - no punch-ins or snap zooms;
  - for landscape footage, offer the 16:9 film frame first (§B option B).
- **Nothing added to the texture:**
  - no grain on footage that already shows noise (§A4);
  - no sharpening or clarity, including the depth-clarity pass, unless the director picks it on a phone sample;
  - no AI upscaling (Real-ESRGAN or similar).

  Denoise only lightly, only where noise shows at phone size, and decide it once. Never add one more fix per round: Pujo's stacked corrections were called over-processed.
- **Check it by numbers.** `scripts/quality_probe.py`, inside `pregate.py`, measures every shot's grain, motion, flicker and cadence against the references (`studio/reference-targets.json`):
  - grain above 0.50 fails;
  - grain above 0.30, motion above 4.3, a flicker pulse, or a repeat or jump inside a shot each get a full-rate strip for the reviewer.

The sections below are the **menu** for the brief's effect list, not a checklist.

## A. Colour (three stages, always in this order)

### A0. The default: camera-true (v0.8)
The director judges every reel against what the camera recorded. Five reels say the same thing: "over processed instead of looking HD" (goddess v6c), "why does everything look so over-processed" (Pujo v11). Pujo's posted final and goddess v10b were graded close to the camera and approved. So the default grade **corrects the camera's faults and stops there**:
- **Each shot is judged against its own camera file at the same framing**, never against a fixed number. `scripts/camera_fidelity.py` measures it (skill Phase 4):
  - brightness at or a little above the camera's. Lift dark night shots only until burn starts: any channel at 255 beyond the light sources on ≤ 2 % of the frame. Fixed targets (reel mean 0.40, no stretch under 0.30) burnt goddess v9c's night shots ("0:22 is burnt"); they're reported, never aimed at;
  - saturation within ±5 % and midtone hue within ±3° of the camera;
  - blacks crushed no more than the camera's own; whites never pulled below the camera unless they clip;
  - deliberate departures (a cast fix, blown highlights recovered) are named in the brief and passed to `--allow`.
- **No creative look by default** (§A3), and no Hue vs Sat curve.
- **No extra sharpening** (§0). Light denoise only on shots whose noise shows at phone size (After Effects `denoise`, `after-effects.md`), decided once, not added round by round.
- **Texture is optional** (§A4): never grain on night phone footage; elsewhere ≤ 5 %, only if the brief has it.

### A1. Primary correction: per clip, on the clip itself
Goal: neutral, correctly exposed footage with natural skin, as close to the camera file as its faults allow (§A0). Fix casts, blown or crushed areas and dark night exposure; don't restyle.
- Read `analysis/summary.md` and look at each `contact.png` first.
- Call `color_correct` **exactly once per clip**, with **only `contrast`, `temperature` and `tint`**. Every call adds a *new* Lumetri effect, and it can't be removed. It ignores brightness, highlights and shadows, and `saturation` turns the clip black and white.
- Then set Exposure (stops), Highlights, Shadows and Basic Saturation (0–200, 100 = neutral) by ExtendScript on that same Lumetri, and keep Creative Saturation at 100. See the reality doc's Lumetri recipe.
- Never call `color_correct` again on that clip. Note that `set_effect_property` hits only the first property with a given name.
- The "brightness +N" starting points below were written for `color_correct`. Exposure is in stops and there's no verified conversion, so start small (about +0.3 to +0.5 stops), then adjust by render.
- Starting points from the analyser:
  - the analyser reads the clip as dark → a small lift (about +0.3 to +0.5 stops), shadows +10…+20, then check `camera_fidelity.py`: lift only until burn starts (§A0)
  - "flat / log-like" → contrast +20…+35, saturation +10…+20 (or the camera's log→Rec709 LUT, applied once as the clip's only Lumetri via `apply_lut`)
  - warm cast → temperature −10…−25; cool cast → temperature +10…+25
  - green tint → tint +5…+15 (toward magenta); magenta tint → tint −5…−15
  - clipped highlights → highlights −20…−40
- Clips shot on the same setup: correct one, then `copy_effects_between_clips` to the rest.

### A2. Shot matching
Re-run `scripts/analyze_footage.py` on a frame export, or compare contact sheets. Adjacent shots should land within about ±0.04 exposure and ±0.03 warm/cool of each other, **without leaving their camera bands** (§A0): when matching would push a shot past them, let the neighbours differ as the camera recorded them. Tweak with `set_effect_property`.

### A3. Creative look: V3 adjustment layer only
**Optional, off by default (v0.8).** Use a look only when the director picks it over the camera-true grade on a camera | now | proposed sheet at phone size, plus a short phone sample of the hardest shots (skill Round 2). Stills alone weren't enough: goddess approved a baked look on stills and rejected it on the full reel. When a look is on, start at **30 % Creative Intensity**; the table's intensities show each look's full character. `camera_fidelity.py --look` then reports its colour shifts as WARN, while brightness, crush, burn and framing still FAIL.

One adjustment layer across the reel. `add_adjustment_layer` doesn't make a real one, so the director makes it with one manual click (reality doc). Place it on V3 with `add_to_timeline`, then on that layer:
- **look:** use the route the film table gives for the look.
  - **preset**: run `app.project.applyLumetriPreset("<preset name>")` on the selected layer clip.
  - **dropdown**: the director picks the look in Lumetri → Creative → Look. That's one click, or computer use with the director's OK. Most of Adobe's film looks are only in the dropdown.
  - **Never set the `Look` slot by script.** It's a dropdown index, not in file order. The first write loads some look, and later writes change the number but not the look (goddess CR).
  - Custom `.cube` LUTs from `assets/luts/` load the same manual way (Look → Browse).

  Then set Creative Intensity to the table's value, by script. It's the 2nd "Intensity", so set it by occurrence. Most looks sit at 40–80 %; a few are lower or higher (e.g. `muted_red` 35 %, mono 100 %);
- look contrast / temperature: on the same Lumetri, by script
- vignette via the Lumetri vignette properties (`set_effect_property`), amount −0.5…−1.5

**Warm looks push red.** Kodak 2393-style presets push oranges toward red. Correct with look-layer temperature plus a little green tint. Don't cool the clips: that turns orange skin and gold pink. Check with `colour_report.py --gold` (midtone hue 30–45°).

Look presets to propose:
| Name | Recipe |
|---|---|
| **Warm Film** | warm LUT (Kodak 2383-style) 60 %, contrast +15, saturation −10, temp +8, soft vignette, grain per §A4 |
| **Teal & Orange** | contrast +20, push shadows teal / highlights orange via LUT, skin kept natural, saturation +5 |
| **Moody Desat** | saturation −30, contrast +25, temp −8, crushed blacks (shadows −15), heavy vignette |
| **Clean Bright** | exposure +5, contrast +10, saturation +10, no grain: creator / lifestyle look |
| **Mono Drama** | `Black & White` on the adjustment layer, contrast +30, grain per §A4 |
| **Match Reference** | measure the reference with the analyser, mirror its exposure / contrast / warmth numbers |

**Scriptable built-in look presets** (`getAllLumetriPresetsList()` lists all 325):

| Look | Built-in preset | Status |
|---|---|---|
| Warm Film | `Fuji F125 Kodak 2393 (by Adobe)` | verified in `my-reel` and `puja-night-2` |
| Mono Drama | none: `Monochrome Kodak 5218 Kodak 2395 (by Adobe)` is dropdown only (film table: `mono_500t`) | not a preset. The presets list has only generic `Monochrome …` presets (untested) |
| Moody Desat | none: `SL BLEACH NDR` is dropdown only, at 40–60 % (film table: `bleach`) | not a preset. SpeedLooks presets are named per camera, e.g. `SL Noir Tri-X (Universal)`, and there's no Bleach family |
| Teal & Orange, Clean Bright | not mapped yet | Pick the closest from `getAllLumetriPresetsList()`, verify by render, and file a CR with the name so HQ can add it here |

#### Film-stock looks (Premiere's own film emulations)
Premiere ships Adobe's film-stock emulation LUTs: a camera negative (Kodak Vision 500T/250D, Fuji Eterna / F125 / Reala) printed to a print stock (Kodak 2383 / 2393 / 2395, Fuji 3510). All of them are in Lumetri → Creative → Look.
- **Only the five Fuji-negative looks are also built-in presets**, so only they can be applied by script (`applyLumetriPreset`, route **preset**).
- The Kodak 5218 / 5205 looks, the Monochrome film looks and the SpeedLooks are **dropdown only** (route **dropdown**).
- Source: Premiere 26.5's `Resources/LocalizedPresets/en_US/Effect Presets/Lumetri Presets.prfpset`, confirmed live on the goddess reel. Preset names are spelled differently from the LUT files ("Fuji Eterna 250D", not "Fuji ETERNA 250D"); use the table's spelling.
- **Preview them on the director's stills before choosing** (Round 2):
  ```
  .venv/bin/python scripts/look_preview.py raw/b-roll/<clip>.mov@<t> … -o projects/<reel>/analysis/looks [--looks id,id] [--intensity 0.4]
  ```
- The `exact` rows read **the same `.cube` Premiere uses**, from its Creative LUT folder, and blend it at the row's intensity. `≈` rows are approximations: SpeedLooks and the Monochrome looks aren't readable outside Premiere, and halation isn't a Premiere effect.

**Measured character** comes from `look_preview.py` at the listed intensity on 4 real stills (2026-10-21): the Durga idol and priest (C152, night), the night temple (my-reel C027), the daylight baul (stock 4221987) and the neon arches (C186). The numbers are the mean change from the source, on a 0–1 scale; hue is in degrees, where negative means toward red.

| id | Premiere look (route) | Intensity | Measured character | Lumetri on the V3 layer (by occurrence) | Best for |
|---|---|---|---|---|---|
| `k500t_2383` | dropdown: `Kodak 5218 Kodak 2383 (by Adobe)` | 50 % | Gentle: contrast +0.035, sat +0.013, warmth +0.018. **Hue +1.5° toward gold**, deep blacks kept, highlights roll off (clip 1.0 → 0.5 %) | Contrast +10, Shadows −5, vignette −0.8. No tint fix needed | **Night festivals and pandals**: the best-measured look for gold at night, when the director wants one |
| `k500t_2395` | dropdown: `Kodak 5218 Kodak 2395 (by Adobe)` | 50 % | **Lifts blacks** (crush 5.5 → 0 %), brighter +0.028, contrast −0.019, sat −0.038: a soft, faded print | Leave the fade for a memory feel; for depth, Blacks −10 and Contrast +10 | Calm, nostalgic and memory sections |
| `k250d_3510` | dropdown: `Kodak 5205 Fuji 3510 (by Adobe)` | 50 % | Clean and warm: contrast +0.024, sat +0.027, warmth +0.034, hue +1.6° | Contrast +5 | Daylight people and street |
| `f125_2393` | preset: `Fuji F125 Kodak 2393 (by Adobe)` (verified) | **40–50 %** | Darker −0.019, contrast +0.039, sat +0.051, warmth +0.048, **hue −1.0° toward red** (−2.4° on the arches), crush 7.4 % | **Verified recipe** (my-reel, puja-night-2): Contrast +15, Shadows −10, Basic Saturation 85–95, Temperature +4 and Tint −10 against the red push, vignette −0.8…−1.0. Check with `colour_report.py --gold` | Warm Film: rich warm night and day |
| `f125_2395` | preset: `Fuji F125 Kodak 2395 (by Adobe)` | 50 % | Lifted blacks, sat −0.030, **hue −3.1°, the strongest red push** | Tint −10…−15 and check gold hue; Blacks −5 | Soft portraits in daylight. Avoid on gold idols |
| `eterna_3510` | preset: `Fuji Eterna 250D Fuji 3510 (by Adobe)` (verified, kolkata) | 30–50 % (kolkata: 30 %) | **The most saturated** (+0.063) and warm (+0.060). Not pastel, despite Eterna's reputation | Creative Saturation 85 on night footage (it's already saturated) | Vivid colour: costumes, markets, daylight |
| `eterna_2395` | preset: `Fuji Eterna 250d Kodak 2395 (by Adobe)` | 50 % | **The brightest** (+0.039), lifted blacks, sat −0.024: airy and soft | Exposure −0.1 if skies clip | Gentle daytime, morning, nostalgia |
| `reala_2393` | preset: `Fuji Reala 500D Kodak 2393 (by Adobe)` | 40–50 % | Like `eterna_3510`: sat +0.060, warmth +0.057, crush 7.2 % | Shadows +5 if dark detail drops | Punchy colour with neutral hue |
| `mono_500t` ≈ | dropdown: `Monochrome Kodak 5218 Kodak 2395 (by Adobe)` | 100 % | B&W with the 2395 print's lifted blacks | Contrast +20, Blacks −10; grain per §A4 | Mono Drama: a black-and-white section or reel |
| `mono_eterna` ≈ | dropdown: `Monochrome Fuji ETERNA 250D Kodak 2395 (by Adobe)` | 100 % | Softer, brighter B&W | Contrast +15 | Gentle B&W memories |
| `cinestill` ≈ | dropdown: `Kodak 5218 Kodak 2383 (by Adobe)` + **halation bake** | 50 % | 500T plus a soft red bloom around point lights. Visible on bulbs against dark; **subtle on scenes that are already warm**. Clip stays ≤ 2 % after the look | As `k500t_2383`. Halation is baked per shot **before** Premiere (below) | Neon and bulb-lit night, concerts |
| `bleach` ≈ | dropdown: `SL BLEACH NDR` | 40–60 % | Contrast +0.094, sat −0.113, cooler −0.066, crush 8.6 % | Shadows +5 to keep detail; no skin warmth to rely on | Gritty, intense moments. Not for idols or faces that need warmth |
| `muted_red` ≈ | dropdown: `Kodak 5218 Kodak 2383 (by Adobe)` + Lumetri **Hue vs Sat** curve | 35 % | Sat 0.54 → 0.36 with reds kept (tolerance 12°); highlights toward neutral and mint. At `--red-tolerance 25` saffron stays too (sat 0.47). **At 12–25 a gold idol turns silver-grey; 45 keeps red and gold** and still mutes blue and green (sat 0.54 → 0.50) | **Hue vs Sat** on the same Lumetri (below), vignette −0.8. Premiere 2026 has **no Leave Color**. Mint / warm tints optional (UI only). **Verified by render** on the goddess reel at tolerance 45: a cool shot's sat 0.31 → 0.16 (preview) vs 0.26 → 0.16 (Premiere) | **story-montage**: muted calm where reds glow ("Two Sides of Bangkok"). **Festival footage with gold idols: start at tolerance 45** |

**Premiere build** (V3 adjustment layer; reality doc for the occurrence method):
1. Load the look by its route:
   - **preset**: select the layer clip, run `app.project.applyLumetriPreset("<name>")`, and deselect it. **If the layer already has a Lumetri, the preset adds a second one and inserts it before the old one** (kolkata v7). Find the look's Lumetri by `Look` ≠ 0 or a non-empty look path (prop 32), never by position, and neutralise the old one (or start from a layer with no Lumetri);
   - **dropdown**: the director picks it in Lumetri → Creative → Look on the V3 layer, or computer use does, with the director's OK. Don't trust the `Look` index readback as proof (2383 read as 11 on one reel); the render check in step 4 is the proof.
2. Set Creative Intensity, the **2nd** "Intensity", to the table value, on the look's Lumetri (step 1).
3. Set the table's adjustments by occurrence, then write the values back to a file (reality doc, Rule 2). Basic Saturation is 0–200, with 100 neutral.
4. **Verify by render (CLAUDE.md §2a):** export a still and compare it with the `look_preview.py` tile of the same frame at the same intensity, then run `colour_report.py --gold`.
   - `exact` looks should land within about 0.02 luma before the adjustments. **Creative Intensity mixes linearly (verified, kolkata):** at 30 % Eterna → 3510, Premiere matched the preview tile within 0.003 on luma, saturation and warmth on two night stills; crush rose a little less in Premiere (+0.5 %) than in the preview (+0.8–1.0 %).
   - The first reel to use a look reports the comparison in a CR, and HQ marks it verified here.

**Hue vs Sat (the `muted_red` look).** Premiere 2026 has no Leave Color effect anywhere: it's not in the Effects panel, not under Legacy, and QE can't find it. Build "muted except red" on the V3 layer's own Lumetri instead, with Curves → **Hue vs Sat**:
- **Keep** saturation unchanged within ±T° of red, where T is the `--red-tolerance` the director approved (45 on the goddess reel).
- **Ramp down** over about 20° beyond that. On the goddess reel the ramp ended at −65° and +62°.
- **All other hues at 46 %.** That matches the preview's 55 % decolour.
- **It's a UI step.** The curve (Lumetri property 58) and the Creative tint wheels are binary blobs that script can neither read nor set. The director draws it, or computer use does with the director's OK: 2 anchors at ±T°, 2 ramp points and 1 far point (e.g. blue) pulled to 46 %.
- **Then verify by render** against the preview tile at the same tolerance. The preview ramps over 10°, so Premiere keeps a little more of the neighbouring hues. On the goddess reel the cast change still matched.
- **Mint highlights and warm shadows** (Creative tint wheels) are optional, also UI only. On the goddess reel they weren't needed: the measured cast already matched the preview.

**Halation bake (the `cinestill` look):** the After Effects `glow` op has no colour setting, so it glows warm, not red. Bake the bloom with ffmpeg on the night shots that have bright point lights, then place the render and grade it like any clip:
```
ffmpeg -i <clip> -an -filter_complex "format=gbrp,split[c][h];[h]colorlevels=rimin=0.70:gimin=0.70:bimin=0.70,gblur=sigma=<width/36>,colorchannelmixer=rr=1.0:rg=0.2:gr=0.12:gg=0.12:br=0:bb=0.02[g];[c][g]blend=all_mode=screen:all_opacity=0.8,format=yuv422p10le,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv" -c:v prores_ks -profile:v 3 -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +write_colr <shot>_halation.mov
```
- Sigma scales with the frame: 30 at 1080 wide, 60 at 2160.
- Tested on 2 s of 4K C186: 3.6 s to render, all BT.709 tags.
- The render clips slightly more than the source (2.6 → 3.1 %) until the look's print roll-off pulls it back. Check `clip%` after the look, and raise the threshold to 0.75 if it's over 2 %.

**Starter LUTs** in `assets/luts/` (for manual loading in Lumetri → Creative → Look). They're generated by `scripts/gemini_generate_starter_pack.py`. A director's own LUTs in that folder take priority.

| Look | File | Notes from the HQ test on real footage |
|---|---|---|
| Warm Film | `gemini_warm_film_2383.cube` | Gentle warmth and roll-off. 60 % is a good start |
| Teal & Orange | `gemini_teal_and_orange.cube` | Blacks stay neutral (fixed in v0.2.3) |
| Moody Desat | `gemini_moody_desat.cube` | Best at taming a strong sodium / tungsten yellow cast |
| Clean Bright | `gemini_clean_bright.cube` | Subtle lift, +8 % saturation |
| (any, for flat footage) | `gemini_flat_contrast_boost.cube` | Strong contrast and saturation. Use 40–60 %. **Not** a camera log→Rec709 conversion |

### A4. Texture: V4 overlays
Grain, dust, light leaks and film burns from `assets/overlays/` go on V4 in a blend mode:
- `set_blend_mode` is broken, so set the mode by script with the enum: Overlay 19, Soft Light 23, Screen 22 (reality doc).
- **Fade V4 texture together with V1 at every fade to or from black.** Grain in Overlay over black reads as a grey veil (frame luma 0.24 instead of about 0 in the pilot).
- grain → Overlay or Soft Light, `set_clip_opacity`: **optional, only from the brief (§0); none on footage that already shows noise, ≤ 5 % otherwise (v0.8, v0.12)**; more only if the director asks.
  - "Already shows noise" means all night phone footage, and any clip at ≥ 0.15 on `quality_probe.py <clip> --whole`. Added grain on a noisy picture is what Instagram's basic encode turns into crawling blocks. The phone's 8-bit night footage already carries noise: the pilot's 40 % was "too much grain", and goddess's 10 % added to what the director called over-processed. Starter clip: `assets/overlays/gemini_film_grain_16mm.mp4`, a 4 s loop, so repeat it end to end across the reel.
- light leaks → Screen, 40–80 %, on transitions or emotional beats
- film burn / flash → Screen or Add, 3–8 frames, on hard cuts
- **soft bloom / mist (whole reel, Premiere-native; verified on kolkata, 13 shots):** per V1 shot, an identical copy on V2 (same item, in-point, start, Motion values and keys; remove its linked audio) with one Lumetri that keeps only the highlights (Exposure −2, Contrast 100, Shadows −100, Blacks −100, plus the V1 clip's own primary), Gaussian Blur **Amount** 20 (reality doc), Opacity 30 %, blend Screen (22). Against the approved ffmpeg mist tile it measured luma +0.009–0.020, p98 +0.001–0.019, saturation −0.002…−0.03. The first try (Exposure −1, Contrast 60, Amount 40, 40 %) was 3–5× too strong: hazy, p02 doubled. The V3 look grades V1 and V2 together. After Effects `glow` (`after-effects.md`) stays for halation on point lights
- green- or blue-screen stock elements (smoke, sparks, petals) → key them first into a ProRes 4444 alpha overlay with the `ffmpeg-color-grading-chromakey` skill (sample the screen colour, `despill`), then place them on V4/V5 in Normal mode

### A5. FFmpeg colour (outside Premiere)
The `ffmpeg-color-grading-chromakey` skill (imported, tested, with studio fixes) is for work **around** the Premiere grade, never instead of it:
- **look previews** on the director's stills for Round 2;
- **pre-rendered effect shots** the brief plans (keep-one-colour `colorhold`, sepia, a film look on one shot), swapped in like an After Effects render;
- **keying** green-screen elements;
- BT.709 tag fixes.

Don't grade the reel or its export there.

---

## B. Motion on V1 (the talking head / hero shots)

**Every move here is an entry on the brief's effect list (§0)**, except a gentle push on a steady hold. **Handheld footage:** no impact shake and no snap zoom. On top of real hand movement they read as jumps or shakes, which is how the director described them in the pilot. Put push/pull on the static holds from `motion.json` instead, and stabilise handheld moves (skill Phase 5).

**Framing (v0.8 default): for vertical footage, show at least 80 % of the camera frame's width.** Every enlargement magnifies the phone's 8-bit night noise. Goddess v8 showed about 67 % and looked "horrible" next to the camera file, while Pujo's approved final showed 86 %.
- For the director's vertical 4K clips (2160 wide) in the 1080 sequence: **Scale ≤ 62.5 %**. Width shown = 50 / Scale.
- Pushes are gentle, about +6 points of Scale over the shot (e.g. 56 → 62), in the subject's direction.
- Tighter only on a shot the brief names with its reason (a face, a detail), and never under 70 % of the width (Scale 71). **Never tighter than 80 % on night or noisy footage** (§0): a 2× crop raises the noise about 1.3–1.4× and doubles the size of the phone's noise-reduction blotches (26 clips, 2026-11-15).
- **Named moves** (a punch-in, a snap zoom, creator-explainer's emphasis zooms) may go tighter for their few frames. The floor applies to the shot's base framing; `camera_fidelity.py` samples mid-shot, so sample outside the move (`--at`) or list the shot in the brief's framing exceptions.
- **Landscape sources can't reach 80 % in 9:16** (full-bleed keeps about 32 % of the width). Show the director the options on their own stills with the IG bands, and record the pick in the brief. **Offer B first** (v0.12): it keeps the whole sensor, adds no noise, and is the shape of 23 of the 30 reels in the director's "Reel Concepts" collection. **A** full-bleed (state the % of width kept), **B** a 16:9 film frame (100 %), or **C** a 4:5 window, 1080×1350 centred in the safe area (≈ 45 %; kolkata's choice, used for every shot). Landscape phone shots recorded with Blackmagic Cam's orientation lock on arrive tagged as portrait and lying on their side: confirm each clip's rotation in Phase 1 (skill) before framing.
- `camera_fidelity.py` reports the width shown per shot (WARN under 80 %, FAIL under 70 %).

The Scale numbers in the table below assume 1080-wide footage; on 4K vertical clips, add the move to the framing scale (Slow push 56 → 62, not 100 → 106).

| Move | Recipe | Use for |
|---|---|---|
| **Punch-in** | razor at an emphasis word, Motion Scale 100→108 % on the second half (hard, no keyframe) | stressing a key word, hiding a jump cut |
| **Slow push** | `add_keyframe` Scale 100→106 % over the shot, `set_keyframe_interpolation` ease | hook, emotional lines |
| **Snap zoom** | Scale 100→125 % in 4–6 frames, ease-in | punchlines, reveals |
| **Impact shake** | Transform / Position keyframes ±12 px over 6 frames, decaying | bass hit, "boom" moments |
| **Reframe** | `set_clip_position` + `set_clip_scale` to keep eyes on the upper third | horizontal source in 9:16 |
| **Split-screen** | `crop_clip` + `set_clip_position` on V1/V2 | before/after, comparisons |

**Depth on Cinematic-mode footage (v0.9.2).** The blur is baked by `scripts/cine_bake.py` (skill Phase 1) at the **recorded focus and f-number**: that is the picture the director framed, and the recorded focus held steady on every Diwali clip measured (≤ 0.11 disparity within a shot), so it doesn't pump.
- **f/2.8 instead of f/2** (`--fnumber-for <clip>=2.8`) on shots where hands or tools move through the focal plane and the shot is slowed: at f/2 they shimmer once the slow motion interpolates them (Diwali).
- **Depth-aware clarity, from the phone's own depth map** (HQ test on Diwali C047, 2026-11-11; the director: "the depth and clarity can be better enhanced"). `cine_bake --disparity-out F` writes the recorded disparity (512×288 per frame) and the focus per frame. The pass then works like this:
  1. a light denoise;
  2. sharpening (radius 1.2) and local contrast (radius 12) **only on the plane the camera focused on**, using the mask exp(−((d − d_focus) / 0.25 d_focus)²);
  3. the bokeh is left as it is.

  **Only when the director picks it on a phone sample (§0, v0.12):** it sharpens, and sharpening read as over-processed on Goddess. On C047 it lifted near-plane detail 31 % (0.0101 → 0.0132) and the near/far separation from 1.69 to 2.36, with no change to the background. A depth map is what makes this work: an image-only focus mask couldn't separate the planes on night phone footage (in-focus edges scored only slightly above the bokeh, 1.27 against 1.17).
  - Scratch tool: `projects/_hqtest/tools/depth_clarity.py`; `scripts/depth_clarity.py` is in the v0.14 tools backlog.
  - Run it before Premiere, like denoise. The grade stays in Premiere.
- **f/1.4 instead of f/2 gains little when the background is already well out of focus** (C047 separation 2.42 against 2.36). Sharpen the focus plane instead.
- **Focus pulls** (`scripts/bin/cine_bake --rack`, between two screen regions or onto the recorded subject) **only when the director asks for one.** Diwali p1b's three pulls at f/1.4 read as "in and out focus" and were removed. Never add synthetic bokeh to non-Cinematic footage (director profile: Taste).

## C. Time

**Every move in this table is an entry on the brief's effect list (§0); none is on by default.** Synthetic slow motion from footage below 2× the sequence rate needs the director's pick on a full-rate phone sample of that shot.

| Move | Recipe | Notes |
|---|---|---|
| **Slow-mo B-roll** | **Source ≤ 30 fps (all the director's footage so far): After Effects Timewarp, Pixel Motion, at camera size** (`after-effects.md`), swapped in at 100 % with the Premiere framing re-applied. Premiere Optical Flow (QE `setSpeed` + `setTimeInterpolationType(2)`) only on calm shots, checked in motion | Goddess v10: Premiere Optical Flow fell back to frame blends on a night crowd (a doubled arm, a 12.5 Hz sharp/soft pulse) and failed review; AE Timewarp on the same shots passed. Speed-changed clips have reality-doc gotchas (in/out points, Scale keys). True slow-mo needs ≥ 50 fps footage |
| **Speed ramp** | razor the clip into parts → `speed_change` on the fast part. With this MCP it **keeps the timeline length and uses more source** (2.0 = 2× source) → `slip_edit {deltaSeconds}` the next part forward by the extra source used, so motion stays continuous | Real time-remap curves aren't scriptable. Recipe verified in `my-reel`; recheck if the MCP changes |
| **Freeze + text** | `freeze_frame` on the beat, then a title / HyperFrames card on top | "this is me 2 years ago" moments |
| **Rewind** | `reverse_clip` 0.3–0.6 s + rewind SFX | callbacks, "wait, go back" |
| **Stutter** | razor 3–4 identical 2-frame slices back-to-back | beat drops |
| **Step-print** | `scripts/step_print.py <clip> -o renders/fx/<shot>_step.mov --start S --dur D --fps <seq>`: 12 images/s, each held 2–3 frames, long-shutter smear (`--blur 3`). The render replaces the shot. Premiere's Posterize Time (12) does the hold without the smear | Chaos peaks: traffic or people passing close, or a fast but **smooth** move. It barely reads on slow shots. 1–2 s, at most twice a reel (story-montage). **The camera's path must be smooth** (v0.10.2): a locked-off frame, a steady pan, or a shot stabilised to ≤ 2 px residual shake. A step-print turns every bump into a 3-frame jump, so never use it on random shake, and never from inside a moving vehicle unless the frame is locked to the vehicle (Diwali v3b, "glitchy"). **Check the render before placing it:** `motion_audit.py <render> --shots <[[name,0,D]]> --step-print 0-D -o m.json` must show a hold shift ≤ 4 px. Pregate fails it otherwise |

## D. Transitions (between shots)

Default is a **hard cut** (§0). A non-cut transition goes only where the brief places one: a section change, the ending, or an entry on the effect list. The director's saved references use almost none. Never more than 3–4 per 30 s.

`add_transition` lands one cut off, so add transitions with the QE snippet in the reality doc and check each one's start/end. For fades to or from black, use **Dip to Black**: opacity keyframes didn't render on frame-rate-interpreted clips.
| Move | Recipe |
|---|---|
| **Flash cut** | `add_transition` Dip to White, 2–4 frames, + camera-click SFX |
| **Whip / zoom blur** | outgoing clip: Transform scale 100→140 % + Directional / Gaussian Blur ramp over the last 5 frames; incoming: reverse; + whoosh SFX |
| **Light-leak dissolve** | Cross Dissolve 8–12 frames + light-leak overlay on V4 in Screen mode |
| **Match cut** | cut on matching shape or motion between clips (planned in the EDL, not an effect) |
| **Glitch hit** | `VR Digital Glitch` (or RGB-split via Offset) for 3–6 frames + glitch SFX |
| **Blur reveal** | Gaussian Blur 60→0 over 10 frames at the start of a section |

## E. Type, graphics, captions (V5 + V2)

- **Music-montage words:** title + end card by default. Beat words only when the director supplies words that mean something (the pilot's "DUM · DUM · DURGA" read as meaningless and were cut).
- **Photo-print inserts** (story-montage): the character takes a picture, then the pictures appear as prints on paper. `scripts/photo_prints.py <graded stills or clip@t…> -o renders/fx/prints.mov --durations <beats> [--settle --flash --border 14 --tilt 1.5]` (3:4 / 3:2 print shapes). Place it on V4 in Normal mode, above the look. Shutter SFX on the first frame.
- **Split screen and native-language words** (story-montage): in 9:16, split top/bottom (Crop Top 25 % + Bottom 25 %, Position Y ±480). Put the key words in the local script, placed in the picture's space (HyperFrames on V5).
- Captions: phrase-aware, 2–4 words, safe zone (clear of top 220 px, bottom 320 px, right 120 px). Styles: *Clean* (white, subtle shadow), *Bold Kinetic* (key word highlighted in brand colour, pop-in), *Editorial* (serif, lower-third). Use `/embedded-captions` for animated styles, `create_caption_track` for clean ones.
- HyperFrames cards (`/motion-graphics`): stat callouts, lists, step numbers, maps, quotes. Render 1080×1920 alpha `.mov` → `renders/overlays/`.
- **Word cards (default for 1–2-word kinetic type):** `scripts/render_type_cards.py` renders 1080×1920 transparent PNGs. It handles the font, glow and shadow, and fails if the text leaves the safe zone. Place them on V5 with a 3-frame scale pop (Motion keyframes). Use HyperFrames for anything animated beyond a pop.
  - Anton and Bebas aren't installed by default. The macOS fallbacks are **DIN Condensed Bold** and **Impact**.
- **End cards:** composite the card over the actual outro frame (export a still) and check that it clears faces and the main subject. In the pilot, the first position sat on Durga's face.
- **Text behind subject:** `scripts/text_behind.py`, which is local and free. Use it on a steady hold of an idol or person against a contrasting background. It fails on busy, ornate full-frame close-ups, so test a still first (`motion-and-ai.md` §2).
- **Animated titles and graphics:** HyperFrames `/motion-graphics` → ProRes 4444 alpha on V5 (`motion-and-ai.md` §1).

## F. Sound design (A2 / A3)

**Which sounds, how often and how loud is the playbook's call** (`playbooks/<style>.md` → Sound). The two current playbooks disagree on purpose:
- `cinematic-montage` puts swishes on real fast motion, at about −13 dB;
- `creator-explainer` keeps silence as the default, gives every sound a visible cause, and never puts a whoosh under text.

The menu below is what's available, not a list to use everywhere.

**Where sounds come from**, best first (v0.11.0):
1. **The director's own recordings** and the clips' natural sound.
2. **Real recordings from Openverse** (`scripts/sfx_fetch.py`) for the sounds the footage implies: firecrackers, temple bells, dhak, traffic, a crowd.
   - CC0 and public domain by default. CC BY only with `--license cc0,by`, and then its credit goes in the Instagram caption. BY-SA, NC and ND are refused.
   - Claude can't hear, so the pick is made by listening with earshot: `get "<search>" --rank "<what it should sound like>"` downloads the top candidates and ranks them.
   - In a long recording, `earshot find <file> "<the moment>"` gives the trim.
   - `keep <file> --name <name> [--from S --to E]` copies the pick into `assets/sfx/openverse/` with its licence sidecar.
   - `sfx_fetch.py credits projects/<reel>/sfx` prints the credit lines for the Instagram package.
3. **Designed transition sounds:** the earshot set in `assets/sfx/earshot/` (`scripts/earshot_bank.py`), or the Gemini starter sounds.
   - Any other earshot bank sound renders by id, aimed at its cut: `earshot sfx render whoosh_fast/whip -o x.wav --sr 48000 --dur 0.8 --apex 0.30`. It's audited for clicks, cut tails and clipping on render.

The director judges a sound new to the studio by ear before a reel relies on it. Their A/B of the earshot set against the Gemini starter sounds (2026-11-12) decides which column is the default; until then it's the Gemini one.

| Moment | Gemini starter (`assets/sfx/`) | earshot set (`assets/sfx/earshot/`) |
|---|---|---|
| Hook / title | riser into sub-hit (`gemini_riser_sub_hit.wav`: the hit lands 1.0 s in, 0.70 s after `sfx_prep.py`) | `earshot_riser_dark` (peaks 0.99 s in, 0.78 s after prep) with `earshot_cut_hit_sub` on that peak |
| Whip / fast pan / flash transition | soft whoosh (`gemini_whoosh_soft.wav`); never under text | `earshot_whoosh_whip` (peak 0.30 s in: put the peak about 1 frame after the cut); `earshot_whoosh_swell` for a slow move; never under text |
| Punch-in / snap zoom | short swish or tick (`gemini_snap_swish.wav`) | `earshot_swish_flick` |
| Text pop | click / pop (`gemini_text_pop_click.wav`), only where the playbook allows a sound on type | `earshot_pop_soft` |
| Flash cut | camera shutter (`gemini_camera_shutter.wav`) | `earshot_shutter_dslr` |
| Reveal / big turn | bass drop (`gemini_bass_drop_boom.wav`) | `earshot_sub_drop` |
| Section change | — | `earshot_reverse_swell` (swells into the cut, peaks 0.52 s in, just after it) |
| Emotional turn | music drops out for 0.5–1 s (silence is an effect) | |

**Prepare SFX before placing them:**
```
.venv/bin/python scripts/sfx_prep.py assets/sfx/*.wav -o projects/<name>/sfx
```
It trims leading silence and peak-normalises to −3 dBFS. Originals are untouched. Library files differ about 10× in level and often start late, so this way one clip gain means the same thing for every file.
- **Place each SFX by its transient**, not its file start: the report gives the transient time (≈ 0 after prep, except risers and whooshes, whose peak is the sync point). It should land within 2 frames of its visual cause.
- **List every placed SFX** in the EDL's `audio` list (`file`, `start`, `in`, `gain_db`) or in `analysis/sfx_cues_v<N>.json`, in the same form. The pregate then finds each one in the export (`scripts/sfx_sync.py`):
  - missing, or more than 2 frames off its plan, is a FAIL;
  - a weak match, a level off the plan or masking in every band is a WARN that someone listens to;
  - with earshot installed, it also draws `sfx/sound_sheet.png` for the reviewer.

Music: cut on the beat for section changes, duck under speech, last note lands on the final frame.

**Loudness (every mixed export):** −14 LUFS integrated ± 2, true peak ≤ −1 dBTP. Instagram turns louder files down and leaves quieter ones quiet, and peaks above −1 clip in its encode. `scripts/verify_render.py` checks this (skill Phase 7); `--fix-loudness` writes a corrected copy with the picture copied. The IG upload version without music is judged on peak only (`--profile ig-quiet`).

**Setting levels:** `set_clip_volume {volumeDb}` writes silence. Set the clip's Level by script instead: `Level = 10^((dB − 15) / 20)` (0.17783 = 0 dB).

**After every export**, check the audio (`ffmpeg … -af volumedetect`, max_volume > −20 dB). If it's silent, rebuild the mix with `scripts/mix_from_edl.py` from the reel's `analysis/mix.json` and mux it onto the picture. Say so in the round notes.

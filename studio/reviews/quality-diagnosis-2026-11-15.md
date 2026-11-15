# Why the reels look glitchy, flickery, grainy and unnatural (HQ diagnosis, 2026-11-15)

The director asked why the studio's reels look worse than the reels they save: glitchy, flickering light, edits that feel off, unnatural and grainy. This compares:
- the 30 reels in the director's Instagram saved collection **Reel Concepts**;
- the 4 studio reels on the director's Reels tab: Diwali, Kolkata, Goddess, Pujo.

Every one was measured **as Instagram serves it**, with the same in-browser method, so Instagram's re-encode is in both sides. The local finals (6 reels), 7 local reference files, sample camera originals and the review history in all 7 reel logs were measured or read as well.

The probe began as a scratch script; its method is now `scripts/quality_probe.py` (v0.12.0). It reads every frame as luma at 540×960 and measures:
- **temporal noise** (`tnoise`): frame-to-frame change in flat, featureless areas, after removing any overall brightness shift. This is grain or noise "boiling".
- **motion**: the average frame-to-frame change, which shows how busy the camera is.
- **flicker**: alternating whole-frame brightness changes within a shot.
- **cadence**: repeated frames and jumps inside a shot.
- served frame rate and size.

## What the numbers say

### Picture, as Instagram serves it
3 windows of 3.5 s per reel (20 %, 50 %, 80 %).

| | Temporal noise (grain boil) | Motion (busyness) | Frame rate | Picture shape |
|---|---|---|---|---|
| **Reel Concepts, median of 30** | **0.08** | **1.8** | 18 at 30, 5 at 60, 4 at 24, 3 at 25 | **23 of 30 are horizontal** (16:9 or 4:3, shown with bars); 7 are full vertical |
| Pujo | **0.49**: noisier than 29 of 30 | **8.3**: busier than 29 of 30 | 30 | full vertical |
| Goddess | **0.38**: noisier than 27 of 30 | **6.1**: busier than 29 of 30 | 25 | full vertical |
| Kolkata | 0.12 | 2.5 | 25 | vertical frame with 4:5 windows |
| Diwali | 0.02 (very dark: luma 22 vs ~60) | 1.0 | 25 | 16:9 frame in 9:16 |

- Flicker as served was **not** above the references in these windows: our 0.02–0.15 against their median 0.08. The flicker the director sees is **specific shots**, not the whole reel (see cause 3).

### Camera originals: where the grain comes from
These are camera files from the Goddess shoot. Temporal noise is measured on the same 540×960 analysis, before any Instagram re-encode:

| Clip | Whole 4K frame (Scale 50) | 1.7× punch-in (Scale 85) | 2× punch-in (Scale 100) |
|---|---|---|---|
| C001 | 0.79 | 1.34 | 1.53 |
| C009 | 0.90 | 1.07 | 1.03 |
| C033 | 0.42 | 0.86 | 0.97 |
| C041 | 0.15 | 0.88 | 1.84 |

> **Superseded by the recheck below.** This measure reads camera motion as noise, and a crop doubles the motion in pixels. The table overstates both the noise and the crop effect. Rechecked on still frames only, night camera files are **3–6×** the reference median, and a 2× crop raises noise about **1.3–1.4×**, not up to 12×.

The Goddess shots were punched in to Scale 70–100 for a while (`projects/we-never-treated-her-like-a-goddess/project.md:153`, `:155`), then eased back to 54–62 after the director called them over-processed. Uski used 2.4–3.4× crops (`uski-aankhein/project.md:493`).

### After upload: what Instagram actually serves (measured 2026-11-15)
**Method.** In the Chrome tab:
- the encode tag comes from each video request's `efg` parameter;
- each copy's size comes from the last byte requested (playback was seeked to the end);
- detail and 8×8 blocking were measured on the same frames in Instagram's copy and in our export.

**What Instagram served:**

| Reel | Uploaded file | What Instagram made of it | Detail kept vs our export | 8×8 blocking |
|---|---|---|---|---|
| Kolkata (76 s) | H.264 High 1080p, 11.2 Mb/s | **only `dash_baseline_1_v1`: H.264 baseline, 720p, 1.39 Mb/s** | 76 % in dark shots, ~91–99 % elsewhere | **+20–28 %** (1.30 vs 1.08) |
| Goddess | H.264 High 1080p, 18.3 Mb/s | `vp9-basic-gen2` 720p + **1080p at 3.21 Mb/s** | 83–95 % | none added |
| Pujo | H.264 Main 1080p, 10.1 Mb/s | `vp9-basic-gen2` 720p + 1080p at 2.84 Mb/s | (not measured per frame) | |
| Diwali | H.264 High 1080p, 2.7 Mb/s | `vp9-basic-gen2` 720p + 1080p | | |
| References (3 of 4 checked) | | **`r2evevp9 … q20–q90`: Instagram's advanced ladder**, 8 quality rungs. one at q90 = 1.18 Mb/s and still clean | | |
| one reference | | `vp9-basic-gen2` 360p–1080p | | |

**What this means:**
- **Instagram picks the encode by expected watch time.** Meta's engineering posts say popular videos get the advanced (convex-hull, per-title) ladder and the most popular also an AV1 copy. Our reels, with small audiences, get the basic encode, and Kolkata got only the lowest tier: 720p H.264 baseline.
- The basic encodes treat **noise and fast motion worst**. They spend their bits on them and block in the darks. That is exactly what our footage has most of.
- **For Goddess and Pujo, Instagram's 1080p copy is close to our export** (83–95 % of the detail, no added blocking). The grain and motion the director sees on Instagram were already in our file. Instagram didn't add them.
- **For Kolkata, Instagram did make it worse.** It served 720p at an eighth of our bitrate, which made the darks blocky.
- **Our upload files were not the problem.** They were 1080×1920 H.264 at 10–18 Mb/s, uploaded from the iPhone with "Upload at highest quality" on (kolkata `project.md:304`).
- **The reference is clean at 1.2 Mb/s** because clean, calm pictures need few bits. Ours need far more than Instagram gives a small account.

Sources:
- [Meta: AV1 and watch-time-based encoding for Facebook and Instagram Reels (2023)](https://engineering.fb.com/2023/02/21/video-engineering/av1-codec-facebook-instagram-reels/)
- [Meta: HDR on Instagram for iOS (2025), on AV1 for the most popular videos](https://engineering.fb.com/2025/11/17/ios/enhancing-hdr-on-instagram-for-ios-with-dolby-vision/)
- [Later: upload high-quality reels](https://later.com/resources/videos/how-to-upload-high-quality-reels-on-instagram/), on the "Upload at highest quality" setting

### On the director's iPhone (iPhone Mirroring, 2026-11-15)
- **Instagram → Settings → Media quality:**
  - "Upload at highest quality" **on**;
  - "Use less mobile data" **off**;
  - HDR display on.

  The upload settings are right.
- **Views per reel:**

  | Reel | Views |
  |---|---|
  | Diwali | 501 |
  | Kolkata | 309 |
  | Pujo | 163 |
  | Goddess | 127 |

  The account total is 17.3K views in 30 days. Small audiences fit Instagram's basic encodes above.
- **Goddess's sound bar reads "Audio unavailable"** ("This audio is no longer available" when tapped). HQ first reported this as the reel playing silent. **That was wrong:** the director unmuted it and the voiceover plays (it was posted with its original voice). HQ can't hear through Mirroring and judged by the label, which isn't evidence of silence. Diwali ("Maa"), Kolkata (Original audio) and Pujo ("Jaago") show their audio names.
- The picture on the phone can't be judged through Mirroring, whose own stream is compressed. The served-copy measurements above stand in for it.

## Recheck: the camera library and the Blackmagic Cam settings (2026-11-15, later)
The director asked whether the footage or the camera settings are the problem.

**Method:**
- `scripts/ingest_report.py` read the app's metadata for all 487 clips in `~/Documents/Video /`.
- A still-frame noise measure ran on 4 s of each clip, with global camera shift removed and frames that still move skipped. It ran on the whole frame, and on a 2× centre crop for every third clip.
- The first measure (above, and `quality_probe.py` before this fix) read camera motion as noise: a daylight walking shot at ISO 39 scored 1.29. `quality_probe.py` now measures noise only on still frames (`still_motion` in `studio/reference-targets.json`).

**The footage moves.**
- Median motion across the 483 clips is **6.4**, against 1.8 for the references.
- 67 % of clips are busier than 26 of the 30 references.
- Only 124 clips held still long enough to measure noise at all.

**Night noise rises with ISO** (still frames, reference median 0.08):

| ISO | Clips measured | Median noise |
|---|---|---|
| ≤ 100 | 22 | 0.23 |
| 125–400 | 50 | 0.29 |
| 500–800 | 31 | 0.41 |
| 1000–1600 | 16 | 0.40 |
| > 1600 | 5 | 0.51 |

- **A 2× crop raises noise 1.3–1.4×** (median 1.32 across 26 clips, 1.40 on 4K clips). It also enlarges the phone's noise-reduction blotches.
- **At full size, night clips show smear and blocks, not grain.** The darks are waxy blotches from the iPhone's noise reduction plus 8-bit HEVC blocks (C234, ISO 2000). They crawl when the picture moves.

**The settings, per shoot night:**

| Night | Clips | Resolution | Frame rates | Shutter | ISO (median; ≥ 1000) | Exposure |
|---|---|---|---|---|---|---|
| Puja Oct 15 | 77 | **1920×1080, 13 Mb/s** | 25, 24 | 1/25 ×42, 1/24 ×12 | 800; 34 clips | mixed (21 clips auto ISO) |
| Puja Oct 16 | 62 | 4K | 25 | 1/33 ×45, 1/25 ×14 | 315; 5 | **auto** (ISO 39–1744, odd shutters) |
| Pujo Oct 17 | 30 | 4K | 30, 25 | **1/60 ×23** | **1250**; 16 | manual |
| Puja Oct 18 | 61 | 4K | 30 | **1/60 ×61** | 640; 13 | manual |
| Pujo Oct 19 | 32 | 4K | 30, 24 | **1/60 ×28** | 250; 3 | manual |
| Pujo Oct 20 | 66 | 4K | 25, 30 | 1/50 ×30, **1/60 ×28** | 250; 4 | manual |
| Pujo Oct 21 | 57 | 4K | 25 | 1/33 ×35, 1/50 ×11 | 200; 2 | **auto** |
| Kolkata (2 days) | 101 | 4K | 25 | 1/142, 1/50, 1/125, 1/96… | 39–100 | **auto** |
| Diwali (reel folder) | 19 | 4K | 25 | **1/50 ×11, 1/49 ×6** | 331; 0 | manual |

- Only **72 of 487** clips used the guide's 1/50 s.
- 149 used 1/60 s, which pulses under 50 Hz lamps.
- 170 used 1/24–1/35 s: each frame is exposed for most of its time, so handheld motion smears.
- Auto exposure (ISO values like 35, 315 and 1744; shutters like 1/142, 1/1126 and 1/3021) changes brightness and noise from shot to shot, and within a shot as the light changes.
- **Oct 15 was recorded in HD at a quarter of the bitrate**: a quarter of the pixels and data of every other night.
- Diwali, the cleanest reel as served, was the one shot closest to the guide: 4K25, 1/50 s, ISO about 330, still shots.

**What the edit added.**
- In Goddess v10b, C042's camera clip is still (motion 0.5) and clean. Its shot in the export moves at 5.9, because of the designed push (±8–12 % per shot, round 8).
- Every Goddess shot but one is above 4.3. The references are locked off.
- Grain and sharpening had been added and then removed by the director (round 6). The final carries the camera's noise, the pushes and two shots of synthetic slow motion.

## The causes, most important first

### 1. Grainy: noisy night phone footage, punched in, then processed
- **The source is the main cause.** It's iPhone 8-bit HEVC at night, through the phone's own noise reduction. 75 of 329 clips are ISO 1000+ (film-emulation skill notes), and some were shot at 1/33 or 1/25 (`we-never…/project.md:336`).
- **Punch-ins and reframes** to fill a vertical frame from 4K vertical or landscape footage multiply that noise (table above).
- **Processing stacked on top**, round after round:
  - grain overlays (12 % on puja-night-2; 10 % and then 4 % on Goddess; 40 % on my-reel);
  - Sharpen 20 (Goddess, "OVER PROCESSED INSTEAD OF LOOKING HD", `:517`);
  - heavy denoise that turned skin waxy (pujo round 11);
  - Real-ESRGAN AI upscaling that shimmered (uski, `:535`).
- Instagram's re-encode then turns the remaining noise into crawling blocks.
- The references are mostly daylight or controlled light, often a real camera, and shown at their full width. That's why they sit at 0.08.
- **Not every reference is clean.** The night-festival references picked for individual reels sit at 0.4–0.6 (`Video-92015`, `ref_audio_vo`, `ref1-filmmakerguy`, measured locally on their Instagram files). That is where Pujo and Goddess land.
- So the gap is with the **Reel Concepts taste** the director now saves, not with every night reel. Matching it needs cleaner footage, not just less processing.

### 2. Glitchy and jumpy: a moving camera, then synthetic fixes
- **Handheld walking shots and in-camera zoom steps** (Goddess C145 zooms in bursts, `:215`; puja-night-2 C087) are covered with Warp Stabilizer. Warp itself added judder and wobble (puja-night-2 `:59`, my-reel `:231`).
- **Slow motion made up from 25/30 fps footage** with Timewarp or Optical Flow. It gave doubled arms, ghosting, smear and "painted" faces in 6 of 7 reels:
  - Goddess `:893`;
  - pujo `:461`, `:507`, `:515`;
  - my-reel `:371`;
  - Diwali `:137`, `:872`.
- **Step-print stutter** on a handheld shot: Diwali's opening, "first few seconds are glitchy" (`:98`). It's still a standard section of the story-montage playbook.
- **Speed ramps and odd speeds** gave 1-2-1-2 cadences:
  - puja-night-2 at 150 % (`:62`);
  - my-reel at 250 % (`:235`);
  - pujo's one-frame speed jump from 1× to 0.54× (`:479`).
- **VFR drops**: pujo C004 lost 15 frames, a mid-shot jump (`:186`).
- **The references barely move.** 26 of 30 are below a motion of 4.3, and most are locked off or a slow move. Pujo (8.3) and Goddess (6.1) are busier than 29 of them.

### 3. Light flicker: shutter vs Indian 50 Hz mains, and LED lamps
- Pujo's 85 clips were shot at **30 fps with a 1/60 shutter** under 50 Hz lamps. That aliases to a 10 Hz pulse with rolling bands (`pujo…/project.md:327–331`).
- Post-production deflicker reduced it, but the director still saw "a lot of shots" flicker on the phone after round 13 (`:658`).
- The ingest check counts **144 flickering clips** in the shooting guide.
- The 25 fps clips at 1/50 were clean (`:332`).
- Flicker can't be fully removed in post: every fix leaves a 2–6 % residual or patches.
- On the Diwali reel, the Apple Cinematic-mode depth bake also **shimmered on jewellery and hair edges** (`could-not-go-home-diwali/project.md:363`).

### 4. Unnatural: correction and effects stacked on every shot
- Pujo's own log names it: "every round added a fix on top (denoise, clarity, auto-levels, forced cast, skin anchor ×2, face / toe lifts)… until the director called the whole thing over-processed" (`pujo…/project.md:847`).
- AI and stock inserts (Veo, Pexels) needed a fake handheld path and grain to sit in. CR stock-ai-blend is still open.
- The references show almost no visible processing: natural light, real-time motion, real lens depth.

### 5. The edit feels off: too many designed moves, and a mechanical rhythm
Our reels lean on designed effects:
- footage inside spinning letters (puja-night-2's "DURGA" hook);
- an iris wipe through black (uski at 7.7 s);
- zoom punches, text behind the subject, step-prints, ramps;
- same-take punch-in cuts that read as jump cuts (Diwali, pujo, Goddess);
- shot lengths that sit on the beat grid (median 2.2–3.2 s, evenly spaced). my-reel's retro: "one shot per bar read as mechanical".

The references are plain hard cuts and long holds.

**This comes from the studio's own rules.** CLAUDE.md says "Never just cut and stitch", and requires planned effects and transitions, texture, and motion on every reel. The director's saved taste is the opposite.

### 6. Shape: the director saves horizontal films; we crop phone footage to full vertical
- 23 of the 30 saved references are horizontal pictures (16:9 or 4:3) posted with bars.
- We fill 1080×1920 from the footage, which forces the punch-ins in cause 1.

### 7. Frame rate: minor, but measurable
- Instagram serves our reels at 25 fps (measured with `requestVideoFrameCallback`: every frame 0.040 s).
- iPhone screens refresh at 120/n Hz, and 25 doesn't divide evenly, so frames are held unevenly: a slight judder on pans.
- 27 of the 30 references are 24, 30 or 60 fps.
- This is likely, not yet tested on the director's phone.

## What would fix it (shipped in v0.12.0)
1. **Shooting guide.** This is the biggest lever, because post can't remove noise or flicker cleanly.
   - Shutter **1/50 or 1/100** under mains lamps, at any frame rate. 30 fps at 1/50 is flicker-free and plays evenly on iPhones.
   - **Never 1/60** in India.
   - Cap ISO, and prefer the main 26 mm lens at night (the biggest sensor).
   - Brace or use a gimbal; no in-camera zoom.
   - For slow motion, shoot 50 fps at 1/100 rather than synthesise it.
   - 10-bit if the app offers it on this phone.
2. **Restraint by default** (CLAUDE.md, effects playbook, story-montage playbook):
   - "camera-true and plain" is the default treatment;
   - a small effect budget per reel, approved in the brief;
   - no synthetic slow motion from ≤ 30 fps;
   - no step-print or ramps on handheld footage;
   - no grain on footage that already has noise;
   - no sharpen and no AI upscaling;
   - no punch-in beyond about 1.25× on night footage.
3. **Offer the horizontal frame** (16:9 or 4:3 inside 9:16) as a framing choice for cinematic montages. It keeps the full sensor width and matches 23 of 30 saved references.
4. **A pregate check against the director's own references.** Add temporal noise and motion to the pregate, measured like `qdiag.py`, with the Reel Concepts medians (0.08, 1.8) as the targets. Fail any shot far above them.
5. **Frame rate.** Deliver at the camera's rate. For new shoots, prefer 30 (or 24) at 1/50.

## Limits of this check
- The served-video measurement samples 3 windows per reel, not every frame.
- Kolkata happened to be served at 720p in this browser.
- puja-night-2 and uski aren't on the Reels tab, so they were measured from their local finals only.
- Playback on the phone was checked through iPhone Mirroring (settings, audio, views), not for picture detail. Frame strips were checked for the flagged spots.

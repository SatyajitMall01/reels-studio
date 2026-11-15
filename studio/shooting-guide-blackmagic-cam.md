# Shooting guide: Blackmagic Cam on iPhone

One page for the director, before a shoot. It's built from the 329 clips of the Pujo 2026 nights, as measured by `scripts/ingest_report.py` on 2026-10-27, and from the quality diagnosis of 2026-11-15 (`studio/reviews/quality-diagnosis-2026-11-15.md`), which found that most of the grain, flicker and jumpiness comes in at the shoot and can't be fully removed in the edit. Every rule fixes something that cost editing time or picture quality.

**What the camera gave us:** HEVC, **8-bit**, Rec.709, about 56 Mb/s, from Blackmagic Cam 3.5 on the iPhone 17. The full library (487 clips) was rechecked on 2026-11-15 (diagnosis, "Recheck"):
- **Shutter:** only 72 of 487 clips at 1/50 s.
- **Exposure on auto** on three nights (Oct 16, Oct 21, Kolkata): ISO 35–1744 and shutters such as 1/142 and 1/3021, changing between shots.
- **Oct 15 recorded in HD** (1920×1080 at 13 Mb/s), a quarter of the pixels and data of the other nights.
- **The camera moves:** the median clip moves at 6.4, against 1.8 for the saved references.
- **Frame rates:** five different rates (25, 30, 24, 24.9, 23.976), even within one night.
- **Flicker:** **144 clips flicker** under lamps (30 fps at a 1/60 s shutter).
- **White balance:** **93 of the 123 clips set at 5600 K came out orange** under warm pandal light.
- **Variable frame rate:** 10 clips; one dropped 15 frames and jumped mid-shot.
- **LUT:** whether a LUT was burned in is **not saved in the file**.

## Set once, before the night
| Setting | Use | Why |
|---|---|---|
| **Frame rate** | **One rate all night: 25 fps, or 30 fps once a test night has passed** | One rate means no conforming. The shutter, not the frame rate, stops lamp pulsing (next row), so 30 fps at 1/50 s is as safe as 25. 30 fps plays evenly on iPhone screens, which refresh at 120/n Hz; 25 doesn't divide into them, and Instagram serves our reels at 25 (measured 2026-11-15). 27 of the 30 Reel Concepts references are 24, 30 or 60 fps. **Untested here:** shoot one night at 30 fps at 1/50 s and compare it on the phone before switching |
| **Shutter** | **1/50 s** (shutter as speed, not auto); 1/100 s for slow motion | 1/50 s takes in exactly two lamp pulses per frame (lamps pulse 100 times a second), so the picture neither pulses nor bands, at 25 or 30 fps. **Never 1/60 under Indian lights**: Pujo's 85 clips at 30 fps and 1/60 s pulsed at 10 Hz with rolling bands, and deflicker in post still left "a lot of shots" flickering on the phone |
| **Slow-motion moments** | **2× the night's rate at 1/100 s** (50 fps for a 25 fps night, 60 fps for 30), then back | Only footage shot at 2× the reel's rate slows cleanly. Slow motion made up in the edit from 25/30 fps doubled arms, smeared and "painted" faces in 6 of 7 reels, so the studio no longer makes it by default. 1/100 s is still pulse-free |
| **Exposure** | **Manual. Set the shutter and ISO yourself**, so neither changes on its own | On auto, the app picks shutters that pulse under lamps (1/142, 1/96) or smear (1/25 to 1/35), and moves ISO from 35 to 1744 between shots, so brightness and noise jump at cuts and drift inside shots |
| **Resolution** | **4K at the app's highest quality**, phone held vertical. Check it reads 4K before the first shot | Oct 15 was recorded in HD at 13 Mb/s: a quarter of the pixels and data. The app stores 4K landscape with a rotation flag; Premiere and our tools handle that |
| **Holding the phone landscape** | **Yes, for a horizontal-frame reel**: the 16:9 film frame inside 9:16, the shape of 23 of the 30 Reel Concepts references. Decide per night, then hold every shot that way. Check the orientation lock (the iPhone's or the app's) is off, or write "landscape" in the slate Notes | A horizontal frame keeps the whole sensor width, with no crop and so no extra noise. Cropping a landscape shot to full 9:16 keeps only a third of its width. KOLKATA2026 was shot mostly landscape, but every clip was tagged portrait and lay on its side; nothing in the files said which way up, so 101 clips were sorted by eye |
| **Codec** | **HEVC 10-bit, or Apple Log, if your app version offers it**; otherwise HEVC at the highest bitrate | 8-bit bands and blocks when graded. 10-bit has four times as many levels per colour, so grades stay smooth. Apple Log needs a log → Rec.709 conversion in the edit, which the studio hasn't tested yet: **tell HQ before the first log shoot** |
| **Cinematic mode** | Fine to use for depth. The f-number can be changed after the shoot, and the recorded focus is kept | The blur isn't in the picture: Apple apps draw it from a depth track, so on the Mac it looks sharp until the studio bakes it (`cine_bake`, Diwali). It records 8-bit HEVC like the normal mode. Slowed shots of hands or tools crossing the focus shimmer at f/2; f/2.8 is safer there |
| **ISO** | As low as the scene allows: **aim for 800 or below at night**, above 1600 only when there's no other way. Open up and get closer to the light before raising ISO | 75 clips were shot at ISO 1000 or more. Noise is the main reason our reels look grainy next to the saved references: our camera files carry 3–6× their frame-to-frame noise, rising with ISO (0.23 at ISO 100 or below, 0.41 at 500–800, 0.51 above 1600, still frames, 2026-11-15). At full size, night darks are waxy blotches from the phone's noise reduction plus 8-bit blocks. Instagram gives a small account's reel a basic encode, which spends its bits on that noise and blocks in the darks. In 8-bit, noise also turns into blotches in dark areas |

## Every new location
1. **White balance: set it to the light and lock it.** Pandal and tungsten lamps: **3200 K**. Mixed LED street light: 4000–4500 K. Daylight: 5600 K. Unsure? Set it off a sheet of white paper. Never leave 5600 K under warm lamps.
2. **Protect the highlights, and expose so the subject reads.** Expose so lamps, idols' faces and gold keep detail. A slightly dark night is fine: the edit keeps night shots at the camera's exposure and lets the deepest shadows go black. It won't brighten them, because brightening multiplied the grain up to 3× on Goddess. A shot too dark to read (Goddess C017, recorded at 4 % brightness) is lost, and blown gold can't be brought back in 8-bit.
3. **LUT: for the monitor only.** Use it to judge the look, but don't burn it into the recording. If you do burn one in, **type its name in the clip's slate Notes** (or Project name). The ingest check reads it there; otherwise nobody can tell later.

## Every shot
- **Hold 5–10 s, with one camera move per shot.** The edit picks its best second, and a cut needs handles on both sides.
- **Main 26 mm lens** for most shots; 13 mm for wide pandals; 52 mm for faces in good light. **At night, prefer 26 mm**: 52 mm is a crop of the main sensor and 13 mm a smaller one, and both are noisier in low light. No digital zoom.
- **Frame it as it will be used.** The edit no longer crops in on night shots: a 2× crop raises the noise about 1.3–1.4× and doubles the size of the phone's noise-reduction blotches (measured on 26 clips). Step closer instead.
- **Hold still.** Lock off, brace against something, or use a gimbal; walk only with the app's stabilisation on. The saved references barely move (median motion 1.8). Our camera clips move at 6.4, and two in three are busier than 26 of the 30 references. Warp in Premiere can't fix a jerk, and stabilising adds wobble and crop.
- **Never zoom while recording.** In-camera zooms come in steps that read as jumps (Goddess C145's hook lurch, puja-night-2 C087).
- **Record 10 s of ambience** (dhak, crowd, conch) at each place. The sound mix uses it.

## After the shoot
Copy the card into `~/Documents/Video /<Pujo YYYY Mon DD>/` as now (the app's `Proxy` folder can stay; the studio skips it). Each reel session runs `scripts/ingest_report.py` on its clips in Phase 1. It reports what's above for every clip, and measures flicker and jumps frame by frame.

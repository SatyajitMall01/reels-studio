# Reference study: "The Art of Composition" and a graphics-led explainer (2026-11-15)

The director sent three posts with "learn", right after asking whether AI enhancement could make our footage production grade. HQ read each one in Claude in Chrome (the director's signed-in browser, read-only). It measured every frame in the page (cuts, frame rate, motion) and made contact sheets. Nothing was downloaded.

| Post | What it is | Served | Shots | Camera |
|---|---|---|---|---|
| [chowyhh × insta360, DcTjYUftCcv](https://www.instagram.com/p/DcTjYUftCcv/) (793K likes, Aug) | "The art of composition in London". Shot on a gimbal camera in log 4K | 1920×1440 (**4:3, horizontal**), 24 fps, 16.5 s | 5, cut at 4.8 / 7.7 / 10.6 / 13.6 s | Still on every shot. All the movement is the subject: a train blurring past, people on stairs, a street |
| [jdonswrld, DeQpEW9zIjC](https://www.instagram.com/p/DeQpEW9zIjC/) (110K likes, Oct) | The same format, **at night**: fireworks, a lantern alley, a radial neon light arch, a covered night market. Library song | 1080×608 (**16:9, horizontal**), 24 fps, 15.0 s | 5, cut **exactly every 3.0 s** | Still or slow on every shot (motion 0.2–2.9 on three sampled shots; 6.2 on one) |
| [life.with.akshat_, De9yxpuIG6X](https://www.instagram.com/p/De9yxpuIG6X/) (6.6K likes, Oct) | Creator explainer: "3 free tools that give your Claude video edits real sound effects" | 1080×1920, 30 fps, 41.6 s | 14 (about 3 s each); the graphics change about every 1.3 s | A plain, still face camera in a bedroom (median motion 1.2) |

The tools in the third post (Openverse, Real SFX, earshot) were already checked and adopted in v0.11.0. This study is about how its edit looks.

## What makes them look produced
1. **None of them uses AI enhancement.** The footage is ordinary, or plainly shot. The polish comes from four things: a still camera, composition, exposure, and graphics.
2. **The camera doesn't move; the subject does.** Every composition shot is locked off, and the energy comes from what crosses the frame. Our camera clips move at 6.4 against 1.8 (quality diagnosis); these sit at 0.2–3 on most shots.
3. **At night they expose for the lights and leave the shadows black.**
   - The jdonswrld night shots keep deep blacks around bright, saturated lights.
   - In-page noise on still frames read 0–0.16. That number isn't directly comparable with `quality_probe` (it was read at 1080×608 after Instagram's encode), but it is clean.
   - Our default grade does the opposite on dark night shots: effects-playbook §A0 and §A1 lift them +0.3 to +0.5 stops, with shadows +10 to +20, "until burn starts". In 8-bit, a lift multiplies the noise and the noise-reduction blotches in exactly the areas these references leave black.
4. **The horizontal frame hides noise.** A 16:9 frame inside 9:16 is 1080 px wide. From a 3840-wide landscape clip that's a 3.6× downscale, against 2× for our vertical 4K. Each output pixel averages about 3× more camera pixels, which smooths noise and blotches. This is a hypothesis, not yet measured on our clips. It adds to the shooting guide's case for landscape (no crop).
5. **A graphic device gives the shot a reason to be still.** The format:
   - a title over a moving-subject shot;
   - for each shot, a black card (about 0.6 s) with a red line diagram and its label ("PARALLEL LINES", "LEVEL CHANGE", "FRAME WITHIN A FRAME", "VANISHING POINT", "GOLDEN RATIO", "ONE POINT", "RADIAL", "RULE OF THIRDS");
   - the same diagram drawn over the shot;
   - the lines fading out after about a second, leaving the clean shot.

   That gives 5 shots of about 3 s each, cut on the music's bar. The viewer is invited to study a still frame, so stillness reads as intent, not as nothing happening.
6. **Graphics carry the explainer.** In the third post the footage is a plain talking head, and the frame does the work:
   - the top half is UI-style motion graphics (cream background, orange accent);
   - the bottom half is the face;
   - the middle runs full-screen graphics with one- or two-word kinetic captions in italic serif, the key word in orange;
   - the face returns for the call to action ("Comment SOUND").

## What it means for the studio
- **The answer to "can AI make it production grade" is mostly no, and these references show why.** Their quality comes from decisions made before and around the footage. AI restoration (Topaz) may still rescue single shots, and the rescue test stays proposed, but it is not what makes these look produced.
- **Proposed, for the director (BACKLOG, "From the reference study 2026-11-15"):**
  1. **Night grade test: don't lift.** On one Goddess or Pujo night shot, compare the current lift (+0.3 to +0.5 stops, shadows +10 to +20) with exposure for the lights and shadows left as the camera recorded them, or lowered. Measure `quality_probe` noise and judge at phone size. If it holds, §A0 / §A1 change their rule for night shots.
  2. **A "composition chapters" device** for cinematic-montage: HyperFrames line diagrams (red, thin, drawn on, fading out) on V5 as alpha overlays, with a black chapter card before each shot. It suits the footage we already have: pandal arches (radial), lanes of lights (one point), the idol inside its frame (frame within a frame), the crowd (rule of thirds). Five still 3 s shots plus cards make a 15–17 s reel. The original is a recognisable trend, so ours should use our own diagrams, type and colour, not a copy of its look.
  3. **Measure the downscale effect** on our own landscape clips: noise in a 16:9 frame inside 9:16 against a full-9:16 crop of the same clip.
  4. **Split-screen explainer** (graphics top, face bottom) as a named layout in the creator-explainer playbook, built with HyperFrames.

## Result: night grade test (2026-11-15, the director said "yes, test it")
**What the posted Goddess grade did** (`analysis/_v9e_grade.jsx`, carried into v10b): every dark night shot was brightened toward the round-9 brightness target:
- C027 +2.0 stops with Shadows +45;
- C017 +1.6 stops with Shadows +30 (first +3.05);
- C035 +1.2, C029 +1.1 with Shadows +22, C020 and C044 +0.9, C010 +0.6.

**Method** (`projects/_hqtest/tools/nightgrade_*.py`, numbers in `nightgrade_results_2026-11-15.json`):
- The same 3 s of camera frames, at 1080×1920, rendered three ways:
  - **A**, the posted lift, emulated and calibrated to the master's measured mean brightness (C027's calibrated exposure came out at +1.89 for Lumetri's +2.0);
  - **B**, the camera file as recorded;
  - **C**, camera tones kept with the deepest 3.5 % crushed to black.
- Each was encoded like an export (x264 CRF 16), then like Instagram's basic tier (VP9, 3 Mb/s).
- Noise was measured in **the same flat, dark picture areas** in every version, chosen on B.
- A first pass that let each version choose its own areas was discarded: brightening moves dark areas into the measured range.

| Shot | Lift | A vs camera, export: grain / boil | A vs camera, Instagram-like: grain / boil | C (crushed blacks) vs camera, export |
|---|---|---|---|---|
| C044 (ISO 39) | +0.9 stops | ×1.08 / ×1.04 | ×1.13 / ×1.65 | ×1.12 / ×1.07 (few deep blacks to crush) |
| C027 (ISO 251, 1/33) | +2.0, Shadows +45 | ×1.24 / ×1.42 | ×1.56 / ×1.98 | ×0.53 / ×0.33 |
| C017 (ISO 250, 1/60, 13 mm, camera brightness 0.04) | +1.6, Shadows +30 | ×3.4 / ×4.3 | ×3.0 / ×4.9 | ×0.64 / ×0.64 |

**Read:**
- **The night lift multiplies the grain, and Instagram's encode widens the gap.** The camera's low-level noise is partly smoothed away by the encode, the lifted noise much less.
- **The lift also changes the colour.** C027's black sky turns muddy olive, the "khaki" the Goddess reviews recorded.
- **Crushing only the deepest blacks removes most of the boil there**, which is what the night references do.
- **C017 is too dark in the camera to lift cleanly** (brightness 0.04). On black it reads as lights only. It's a shooting problem (13 mm, auto exposure, 1/60 s), not a grade problem.

**Limits:**
- A is an emulation of Lumetri, not a Premiere render. C017's emulation hit its exposure limit (+5) below the posted brightness, and burns the lights, which Premiere's Highlights −60 avoided; its ×3 is the least certain number.
- Three shots, one night.
- The director judges on the phone (`night_grade_test_phone.mp4`: each shot through the Instagram-like encode, A → B → C).

**Director's pick: C** (2026-11-15). Shipped in v0.12.1 as the night rule: §A0 / §A1 stop brightening dark night shots toward a brightness target:
- keep the camera's exposure;
- set the black point so the deepest shadows go black;
- protect the lights;
- a shot too dark to use without a big lift is dropped or reshot, not lifted.

Version C also raised saturation ×1.09–1.21, because a black point does. With Basic Saturation 90, C027 and C044 match the camera (`camera_fidelity` PASS), so the rule trims saturation back.

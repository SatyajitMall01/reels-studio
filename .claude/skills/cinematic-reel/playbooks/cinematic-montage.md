# Playbook: cinematic-montage

**For:** music-driven montages of places, festivals and events, with no speech (reel type `music-montage`; the montage stretches of a `hybrid`).
**Proven on:** my-reel (Durga Puja night, v10 final, 49.8 s) and puja-night-2 (v5, 55.6 s). Each rule cites its source.

## Pace and structure
- **The music decides the timing.** Get the beat grid first (`gemini_audio_and_beat_analyzer.py`); cuts land on beats, and section changes and hero shots land on accents or bar downbeats (CLAUDE.md §4c).
- **An energy arc, never one shot per bar.** Default arc: slow open → build → full → breath → payoff → outro. *Why:* my-reel v1 cut one shot per bar and read as mechanical, and you reopened it 5 times.
- **A slow open is allowed when the brief says so**, instead of a hard 3 s hook. *Source:* the director approved slow builds on both reels. Even then, something must move from frame 1, such as a push or a tilt.
- **Shot length:** take the reference's measured median as the target (`teardown.py`). Both reels landed at a median of about 1.6–1.8 s, with holds of 3–5 s on hero shots.
- **Pick the best moment, not the whole clip** (`selects_score.py`, then check by eye). Never repeat a subject or framing. *Source:* the v8 review flagged the same carved panel used twice, 9 s apart.

## Camera and motion
- **Restraint first** (effects-playbook §0, v0.12): real speed, hard cuts, a still or steady camera. Every designed move is an entry on the brief's effect list. The director's "Reel Concepts" references are locked-off or slow moves (median motion 1.8), and our busy handheld reels measured 6–8.
- **Handheld footage: no impact shakes or snap zooms.** They read as jumps on top of real hand movement. *Source:* my-reel round 2.
- **Digital push or pull only on steady holds** (`motion_holds.py`): 100→104–110 % over the shot, eased.
- **Prefer the steady take** (`shake_report.py`, `motion_holds.py`). Warp only shots that still fail the shake limits, then re-measure and scan for Warp banners.
- **Slow-mo: off by default** (§0). Real slow motion needs 50/60 fps footage. Synthetic (Timewarp or Optical Flow) only when the director picks it on a phone sample of that shot, and only on calm shots. *Source:* the C076 smear in v8; ghosts and "painted" faces in 6 of 7 reels.

## Type and graphics
- **A title and an end card only**; beat words only when the director supplies words that mean something. *Source:* the v1 words "DUM · DUM · DURGA" read as meaningless.
- **Animated title** with HyperFrames: focus-pull settle, the profile's DIN Condensed Bold in cream, gold glow (or a dark halo for a calm reel), placed per shot and **never on the subject** (`motion-and-ai.md` §1).
- **Text behind the subject:** only from the brief's effect list, at most one signature moment, on a steady hold of an idol or person against a contrasting background (`text_behind.py`). *Source:* "MAA" behind the folk Durga in puja-night-2.

## Transitions
- **Hard cut by default.** A dip to black at the end. A flash on a big hit or a whip on fast motion only from the brief's effect list (effects-playbook §0).
- **Never stack decorative looks**: no light leaks plus rays plus particles, and no Premiere *Light Leaks* transition (it strobes). *Source:* the v8 review and the pilot's QA. Dissolves only where the brief asks for them.

## Sound
- **The music leads.** Peaks −1…−3 dB, no ducking; natural sound muted or at −20 dB or quieter (CLAUDE.md §4c).
- **Swishes and whooshes: yes, but only on real fast motion**: a whip, a fast pan, a snap move or a flash transition. **Never under text or titles, and never just because a shot starts.** At about −13 dB in the mix, the level the director asked for in puja-night-2 ("louder swishes": raised from −18/−17 to −13 dB).
- **Risers into the big hits.** A sub-boom or bass drop on the 1–2 biggest accents, at −15…−18 dB.
- **Prepare every SFX** with `sfx_prep.py` (trim leading silence, peak −3 dBFS), and place it by its **transient**, not its file start.
- **Mixed version:** −14 LUFS ± 2, true peak ≤ −1 dBTP (`verify_render.py`; `--fix-loudness`). The IG version without music is judged on peak only.

## Colour and texture
- **Camera-true first** (effects-playbook §A0). Night festival footage already carries warm gold: keep it where the camera has it (hue 30–45° on warm shots, `colour_report.py --gold`), keep blue accent shots clean (G−M ≈ 0), and don't deepen blacks beyond the camera's.
- **Look choice: optional** (effects-playbook §A3). Only when the director picks a look over camera-true on the Round 2 sheet, preview the film-stock looks (`look_preview.py`):
  - On night footage, `Kodak 5218 Kodak 2383` measured the best fit for gold: hue +1.5° toward gold, blacks kept deep.
  - Warm Film (`Fuji F125 Kodak 2393`) is proven on both reels but pushes toward red.
  - Looks printed to 2395 lift the blacks: use them only when the brief wants a faded memory.
- **Warm looks push red:** fix it with the look layer's temperature plus a little green tint, never by cooling the clips.
- **Grain: none on footage that already shows noise (all night phone footage), ≤ 5 % otherwise and only from the brief, faded with the picture.** *Source:* 40 % was "too much grain" in my-reel round 2; goddess's 10 % added to what the director called over-processed.
- **Denoise dark shots lightly** in After Effects (`denoise`) when `quality_probe.py` or your eye shows noise, decided once, never stacked with sharpening. *Source:* my-reel v7, −12…−29 % dark-area noise; Pujo's waxy over-denoise.

## AI shots
- Rarely needed: both reels had **no gap** the footage couldn't fill. If one is needed, follow the ladder and policy in `motion-and-ai.md` §3. The idol or the crowd only when the brief names the shot, and never as proof.

## QA thresholds for this style (review gate)
- Every shot within its camera bands (`camera_fidelity.py`, effects-playbook §A0). Adjacent shots within ±0.04 luma unless their camera files differ more, a shot is a deliberate dark establisher, or it's a blue accent.
- No phones, raised hands with screens, or bald heads drifting into hero frames. Reframe or mask them. *Source:* the most common review finding on puja-night-2.
- Every cut within ±2 frames of its beat, except deliberate off-grid holds noted in the brief.

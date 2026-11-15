# Brief — written by the editor, approved by the director

> Claude writes this file after the interview and footage analysis. The director only answers questions, shares references, and approves. Don't fill it in by hand; ask Claude to change anything.

**Status:** draft / approved on ____

## 1. The idea
- **Reel type:** talking-head · music-montage · hybrid (sets the editing rules, CLAUDE.md §4)
- **Playbook:** cinematic-montage · creator-explainer · … (`.claude/skills/cinematic-reel/playbooks/`). **Overrides:** any playbook rule this reel changes, with the reason, or "none"
- **One-line concept:**
- **Story arc:** (setup → turn → payoff)
- **Goal:** (what the viewer should feel or do)
- **Audience:**
- **Target length:**

## 2. Hook (0–3 s)
- **Line / moment:** (talking-head: quote + timecode · music-montage: shot + timecode + accent beat)
- **Visual move:**
- **On-screen text:**

## 3. References → concrete parameters
| Reference | What we take from it | Measured |
|---|---|---|
| | | avg shot ___ s, first cut ___ s |

## 4. Treatment
### Pace
- Average shot length · cut style (hard / J-cut / match cut) · energy curve

### Colour
- **Primary correction (per clip, V1/V2):** what each clip needs (from `analysis/summary.md`)
- **Shot matching:** which clips must match which
- **Creative look (V3 adjustment layer):** none (camera-true, the default, effects-playbook §A0), or the look the director picked on the Round 2 sheet: name, intensity (start 30 %), why
- **Texture (V4):** none by default (and always none on footage that already shows noise: all night phone footage); otherwise grain ≤ 5 %, light leaks, vignette, halation
- **Camera-check exceptions:** shots allowed to depart from their camera file (`camera_fidelity.py --allow`), each with its reason
- **Framing:** for landscape footage, the pick from §B (the 16:9 film frame offered first). **Exceptions:** shots tighter than 80 % of the camera width, each with its reason (never on night footage)

### Effect list (restraint by default, effects-playbook §0)
Default: **none**. Real speed, hard cuts, still or steady camera, a dip to black at the end. Two or fewer is the guide.

| # | Move (from `effects-playbook.md`) | Shot / beat | Why this reel needs it |
|---|---|---|---|
| | e.g. real slow-mo (shot at 50 fps) · step-print · punch-in · flash · dissolve | | |

Synthetic slow motion from footage below 2× the sequence rate is listed only after the director picks it on a phone sample of that shot.

### Type & graphics
- Caption style · font · colours · position · motion graphics beats

### Sound
- Music (file / mood / BPM / beat grid from `analysis/audio_summary.md`) · SFX density · special moments (silence drop, bass hit)

## 5. Clips
| Clip | Role (A-roll / B-roll / hero) | Notes from the analysis |
|---|---|---|

### Line table (VO and dialogue reels)
One row per spoken clause, searched across the whole pool (`scripts/pick_sheet.py --all`). One subject per line; no person twice unless it's a callback.

| Line | Shot | What in the frame shows it |
|---|---|---|

## 6. Must-haves / must-NOT-haves
-

## 7. Open questions
-

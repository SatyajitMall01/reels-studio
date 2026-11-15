---
name: cinematic-reel
description: Turn the director's clips into a fully treated cinematic 9:16 Instagram Reel in Adobe Premiere Pro. Claude interviews the director, studies references, writes the brief, then cuts, colour-corrects, grades, adds effects, graphics, captions and sound design, and exports. Use when the user wants to make, edit or revise a reel.
---

# /cinematic-reel

The director answers questions, shares clips and references, and approves. **You write everything**: brief, cut list, treatment. This is never cut-and-stitch: every reel gets camera-true colour correction (a creative look only when the director picks one), motion, transitions, type and sound design, planned in the brief and taken from `effects-playbook.md` (same folder; read it before Phase 2).

**Every reel follows one editing playbook** (`playbooks/`, same folder): the style rules for its kind of video, meaning pace, camera, type, transitions, sound (including whooshes), colour and the QA thresholds. Pick it in Phase 0, record it in the brief, and read it before Phase 2. `effects-playbook.md` is the menu of moves; the playbook says which ones this reel uses.

Stop at the three **⏸ checkpoints**. Follow every rule in `CLAUDE.md`.

Argument: reel name (folder under `projects/`). If it doesn't exist, run `scripts/new_reel.sh <name>`.

**This is a reel session** (`studio/ARCHITECTURE.md`). Write only to:
- `projects/<name>/`;
- `studio/change-requests/`;
- `studio/retros/`;
- new files in `assets/`.

When the architecture falls short:
- work around it inside the reel;
- log the workaround in `project.md`;
- file a CR from `studio/change-requests/_TEMPLATE.md`.

Never patch `CLAUDE.md`, skills, scripts or the template.

**Two files to read once per reel:**
- `studio/director-profile.md`: handle, type style and working preferences. Don't re-ask anything it answers.
- `premiere-mcp-reality.md` (this folder): which Premiere tools are broken and the verified fallbacks.

**Any manual step for the director** goes out as a short numbered list naming the panel and menu path, ending "come back and say done".

 If `project.md` says `Pilot: yes`, append to `## Friction log` whenever something:
- is slow;
- fails;
- needs a guess;
- needs a manual step;
- needs a workaround.

---

## Phase 0: Interview the director
Read the `## Now` block at the top of `project.md` and its latest round (not the whole log), and `studio/director-profile.md`, first. If a round is already in progress, resume it. Check `Arch version` against `studio/VERSION`. If they differ:
- check `studio/CHANGELOG.md` for changes since then;
- adopt minor or patch changes at the start of the next round;
- ask the director before adopting a major change.

**Keep `## Now` current.** Rewrite it at the end of every round, in at most 30 lines: status, the locked sequence and latest export, approved decisions, open questions, next step. Once `project.md` passes about 4,000 words, move every round but the last two to `log/rounds.md`. The first five reels' logs reached 10–21k words and were reread at every session start.

Ask in **two short rounds**, with multiple choice wherever possible (AskUserQuestion when available). Never ask something the footage or a reference can answer.

**Round 1: the idea (ask before looking at footage)**
1. What's this reel about, in a sentence or two? What happens in the clips? Is anyone speaking (on camera or VO)? → sets **reel type**: `talking-head` · `music-montage` · `hybrid`. Record it in `project.md`.
   Then propose the **playbook** from `playbooks/README.md` (`music-montage` → `cinematic-montage`; `talking-head` → `creator-explainer`; `hybrid` with a voiceover and one recurring character → `story-montage`; other `hybrid` → both, by stretch). If nothing fits, use the closest one and file a CR for a new playbook.
2. What should viewers feel or do at the end? (laugh · learn · be inspired · follow · save · click link)
3. Who's it for?
4. Length? (15–20 s · 30–45 s · 60 s · whatever the story needs)
5. Branding, only if `studio/director-profile.md` doesn't already answer it: handle, type style, brand colours. Ask now, not at the end card. Anything new goes into `project.md` and a CR to update the profile.
6. References: 1–3 reels or creators whose *feel* they want. Ask them to drop video files in `projects/<name>/references/` or paste links. Instagram links often can't be fetched, so ask for a screen recording or the downloaded file.
7. Is the soundtrack existing audio: an Instagram library song, or another reel's original audio (often the reference's)? If yes, Phase 1 checks its Instagram page (library song or "Original audio", and who made it) and, for another creator's audio, whether the director has their OK. The cut then uses a guide copy (CLAUDE.md §4c). Pujo found out at the Share screen and rebuilt six versions.

**Round 2: taste (ask after analysing footage and references, so the options are concrete)**
Offer choices that fit *this* footage, for example:
- Look: **Camera-true (default, effects-playbook §A0)** · or a creative look on top: Warm Film · Teal & Orange · Moody Desat · Clean Bright · Mono Drama · Match reference. **Show, don't name:** put the camera-true frame first on a camera | camera-true | look sheet at phone size, from 3–4 of the director's own stills (night, a face, a wide), using `scripts/look_preview.py` for the looks (effects-playbook §A3 film table, with measurements). Offer at most 2–3 looks that fit the footage, at 30 %. If the director leans to a look, also send a 6 s phone sample of the 3 hardest shots: goddess approved a look on stills and rejected it on the full reel. Most film looks (all the Kodak ones, `muted_red`) are **dropdown only**: tell the director they're one manual pick in Phase 4, and that `muted_red`'s Hue vs Sat curve is a second UI step.
- Pace: calm (3–5 s shots) · medium (2–3 s) · fast (1–2 s), pre-selecting what the reference measured
- Effects intensity: subtle · signature moments only · heavy / stylised
- Captions / words: none · Clean · Bold Kinetic · Editorial. For music-montage, default to **title + end card only**. Use beat words only when the director supplies words that mean something; never invent filler words.
- Music: their file in `assets/music/` · mood + BPM for you to suggest
- Anything that must or must not happen

## Phase 1: Preflight & footage analysis
1. `verify_premiere_connection`. If it fails, stop and give the CEP panel steps. Read `premiere://config/get_instructions` once.
2. `get_project_info`, `list_sequences`, `list_project_items`.
   - **Premiere sample media:** Premiere 2026's New Project screen imports Adobe sample clips by default (`mediaPath` under `/Users/Shared/Adobe/Premiere Pro/*/Sample Media/`), plus an auto-built `Sequence 01`.
     - If you find them, list them for the director and ask before removing anything.
     - On a yes, remove them with the temp-bin delete in `premiere-mcp-reality.md` (`delete_multiple_project_items` and `delete_project_item` are broken), plus `delete_sequence`. Confirm with `list_project_items`. Only the project references go; Adobe's sample files on disk stay untouched.
     - Never delete a sequence the director made.
3. If the director's footage lives outside the studio, link it in for analysis rather than copying it; the originals stay untouched. Once the shortlist is chosen, copy those clips into `raw/`: the director wants copies of what a reel uses (director profile).
   ```
   scripts/link_footage.sh <name> "<source folder>" [a-roll|b-roll]
   ```
   **Ingest check first** (what the camera recorded, and what it means for the edit):
   ```
   .venv/bin/python scripts/ingest_report.py projects/<name>/raw -o projects/<name>/analysis --scan
   ```
   Read `analysis/ingest.md` and act on it:
   - **sequence fps:** the most common rate; conform the others in step 6;
   - **`FLICKER n%`:** deflicker those clips before colour, or pick other clips. Until HQ promotes a deflicker tool, use the workaround in CR mains-flicker;
   - **`jumps` / VFR gaps:** keep placed windows clear of the listed times;
   - **8-bit:** grade gently;
   - **colour casts and match groups:** these become Phase 4's starting corrections;
   - **LUT:** the camera doesn't record a burned-in LUT. If no slate note says so and a clip already looks graded on its stills, ask the director in Round 2.
   - **`cinematic`:** the clip was shot in Cinematic mode, and its depth of field is a separate track only Apple apps draw. Every tool here, Premiere included, sees it sharp. Run the analysers on the camera files as usual (for picking shots), but **from the first EDL on, bake before anything renders**:
     ```
     .venv/bin/python scripts/cine_bake.py --edl projects/<name>/analysis/edl_v<N>.json [--fnumber-for <clip>=2.8]
     ```
     It bakes each used span plus 0.48 s handles at the recorded f-number (ProRes 422 HQ, rotation kept, with sound) and writes `edl_v<N>_baked.json`. The storyboard, the preview, the pregate (so `camera_fidelity.py` compares against the bake, the director's intended picture) and the Premiere build all read that file. Re-run it after every EDL change; unchanged spans are reused. Focus pulls and other f-numbers: effects-playbook §B.

   Then run the analysers (no API key needed):
   ```
   .venv/bin/python scripts/analyze_footage.py projects/<name>/raw/a-roll projects/<name>/raw/b-roll -o projects/<name>/analysis
   .venv/bin/python scripts/analyze_footage.py projects/<name>/references -o projects/<name>/analysis/references --reference
   ```
   **Look at the `overview_*.jpg` sheets first.** They show every clip's middle frame, labelled. Use them to:
   - shortlist hero clips;
   - spot upside-down or sideways clips; orientation isn't auto-detected, so fix those with a 180° / 90° rotation and log it.
   - **Landscape phone footage** (the clips all carry the same −90 tag, so middle frames show them on their side): confirm each clip's rotation on frames turned both ways (+90 / −90) at its best steady moment, not its middle, and record it in `analysis/orientation.json`. Re-check any clip you'd call unusable at its best window before dropping it: on kolkata, 4 of 101 mid-frame calls were wrong, including one of the best shots. Then show the director the landscape framing options (effects-playbook §B).

   Then open the `contact.png` of each candidate and read `summary.md`. On dark shoots (night, stage, candle-lit), exposure is judged relative to the shoot's median, so "darker than the shoot" is the flag that matters. If a reference's contact sheet shows more distinct shots than the cut count, rerun it with `--scene-threshold 0.1`. Trust the count once two thresholds agree. Note per clip: exposure, colour cast, flat/log, fps (slow-mo headroom), orientation, what's actually in the shot, hero moments.

   **Measure the references** the same way we'll measure our cut:
   ```
   .venv/bin/python scripts/teardown.py --ref projects/<name>/references/<ref>.mp4 -o projects/<name>/analysis/teardown
   ```
   It gives cuts per minute, shot lengths, flashes, motion, picture (luma, contrast, saturation, warmth) and loudness. Put the numbers in the brief as targets.
4. Timing source, by reel type (CLAUDE.md §4):
   - **If the soundtrack is existing Instagram audio** (a library song, or another reel's original audio): open its Instagram page now and note whether it's a library song or "Original audio" and who made it, then cut to a stereo guide copy of it (CLAUDE.md §4c). Don't wait until posting.
   - `talking-head` / `hybrid`: transcribe the speech with `scripts/transcribe_reel.sh <name>` (local Whisper: free, offline, word-level), which produces `transcripts/takes_packed.md`. It reads `raw/a-roll/`, or the files you name: pass an external VO or the reference's audio (`scripts/transcribe_reel.sh <name> projects/<name>/audio/vo.wav`). Hindi or Bangla: add `--model large-v3-turbo --language hi` (or `bn`). `--scribe` uses ElevenLabs Scribe instead, when `.env` has a working key.
   - `music-montage` / `hybrid`: run the beat grid on the music track:
     ```
     .venv/bin/python scripts/gemini_audio_and_beat_analyzer.py --music assets/music/<track> -o projects/<name>/analysis
     ```
     Then read `analysis/audio_summary.md`. Use its **Energy / sections** table and **Candidate cuts** (best start/end for 15/30/45/60 s) to pick the music section. Check the labels by ear, since they're heuristic. No music yet: ask for it in Round 2. The EDL can't be planned without it.
5. `create_bin` (`01_A-Roll`, `02_B-Roll`, `03_Graphics`, `04_Textures`, `05_SFX`, `06_Music`), then import everything with the ExtendScript `importFiles` snippet in the reality doc. `import_folder` is broken, and `import_media` ignores `binName`. Confirm with `list_project_items`.
6. Conform outlier frame rates now, before anything is placed: `set_override_frame_rate` to the sequence fps (CLAUDE.md §3).
7. **Selects and motion** (music-montage / hybrid: always; talking-head: for B-roll). Run these in the background while Round 2 is asked:
   ```
   .venv/bin/python scripts/selects_score.py projects/<name>/raw/b-roll -o projects/<name>/analysis --skip <unusable ids>
   .venv/bin/python scripts/motion_holds.py projects/<name>/raw/b-roll -o projects/<name>/analysis --skip <unusable ids>
   ```
   `selects.md` ranks every clip's best 1 s moments (sharp, colourful, steady). `motion.json` gives each clip's static holds and pans. **Review the top moments by eye** (contact sheets / stills) before writing the EDL. The score can't judge meaning, faces or composition. In the pilot, this found better shots than picking from mid-frames.

→ Now ask **Round 2** of the interview.

## Phase 2: Write the brief + cut plan
1. Fill in `projects/<name>/brief.md` completely: **playbook** (and any rule this reel overrides, with the reason), idea, hook, references turned into measured parameters, **Treatment** (pace, colour stages A1–A4 with A3/A4 marked "none" unless the director picked a look or texture, named effects and transitions with their beats, type, sound), the **effect list** (every designed move: speed change, slow motion, step-print, zoom, shake, wipe, flash, type matte, text-behind, each with its shot and why; default **none**, two or fewer is the guide, effects-playbook §0), the framing (for landscape footage the 16:9 film frame is offered first, §B), the clip table, must/must-nots, open questions.
   For **music-montage**, the Treatment must also include:
   - **Energy arc:** which song sections go up or down and where the shot length changes. Default: slow open → build → full → breath → payoff → outro. **Never one shot per bar for the whole reel.** That read as mechanical in the pilot. The music may be edited (e.g. intro joined to the main section on a downbeat).
   - **Generated shots (if any):** every AI-generated shot gets its own row, labelled **AI-generated**, with the prompt, why the footage can't provide it (or why its footage and stock are unusable), the ladder steps already tried, and the cost from the `gen_video.py` dry run. The director approves each at Checkpoint 1 (`motion-and-ai.md` §3).
   - **Motion style:** which shots stay as handheld movement, which are held, and where digital push/pull goes (only on `motion.json` holds). Plus where slow-mo goes (calm shots only).
2. In `project.md`, under `## Round 1 — Proposal`:
   - 3 hook options with a recommendation. Talking-head hooks quote the line and its source timecode. Music-montage hooks give the shot, its source timecode and the accent beat it lands on;
   - EDL table: `# | clip | in | out | text / action | V1 move | V2/V5 | transition out | SFX`;
   - estimated runtime.
3. **VO and dialogue reels: the line table.** In the brief, one row per spoken clause: `line | shot | what in the frame shows it`. Search the whole pool for each line, not a themed shortlist: `scripts/pick_sheet.py projects/<name>/analysis --all -o projects/<name>/analysis/picks/pool.jpg`, then a sheet of the best 3–6 clips per line. One subject per line, and never the same person twice unless it's a callback (director profile). In the first five reels, 11 rounds went to shots that didn't show their line.
4. **Write the EDL as `analysis/edl_v1.json`** (format in `scripts/preview_edl.py`'s header): per shot the camera clip, in-point and speed, the planned framing in Premiere's terms (Scale, Position, keys for pushes, at least 80 % of the width), dissolves and fades, and its `line` and `shows`. The storyboard, the offline preview, the pregate and the Premiere build all read this one file.
5. **Storyboard and offline preview:**
   ```
   .venv/bin/python scripts/storyboard.py projects/<name>/analysis/edl_v1.json -o projects/<name>/analysis/storyboard_v1.jpg
   .venv/bin/python scripts/preview_edl.py projects/<name>/analysis/edl_v1.json -o projects/<name>/renders/previews/<name>_p1.mp4
   .venv/bin/python scripts/encode_master.py projects/<name>/renders/previews/<name>_p1.mp4 -o projects/<name>/renders/previews/<name>_p1_phone.mp4 --phone
   ```
   - The storyboard shows in / mid / out frames through the framing, with the overlays and the Instagram UI bands, so a face under a caption shows now.
   - The preview is the planned cut in the camera's own colour, with the VO or music, in a few minutes and without Premiere. Run the pregate on it (review-gate.md, with `--profile ig-quiet`, since its audio isn't loudness-matched) to catch jumps, black edges and framing before the build.
   - **Pace, picks, framing and slow-mo windows are settled on previews**; the build follows. Tell the director with every preview that its colour is the camera's, not the grade: goddess approved a look on stills and rejected it on the full reel.

### ⏸ Checkpoint 1: brief + cut plan
Give the director a short summary in chat: the concept, hook, look, 4–6 signature moments, runtime, and anything from their answers you couldn't honour. Send the storyboard and the phone preview as files. Wait for a yes or for changes. Notes on pace, picks or framing become a new EDL version and preview (`edl_v1b.json`), not a Premiere build.

## Phase 3: Rough cut (V1 / A1)
1. `duplicate_sequence`, or create a 1080×1920 sequence at the footage's most common frame rate (CLAUDE.md §3) → `Reel_<name>_v<round>`, then open it in the timeline. `create_sequence` needs an `.sqpreset`, so use `create_sequence_from_clips` on a clip that has the target size and fps.
2. Assemble the approved EDL (`analysis/edl_v<N>.json`) with `add_to_timeline_batch`, or razor + `ripple_delete` on the duplicate.
3. Reframe to 9:16 with the EDL's values (`set_clip_scale` / `set_clip_position`, Rotation, and the push keys), **showing at least 80 % of the camera width** on vertical footage (Scale ≤ 62.5 on vertical 4K clips, effects-playbook §B; landscape footage: the framing the brief records). Name any tighter shot and its reason in the brief.
   Then write `analysis/map_v<N>.json`, the shot map `camera_fidelity.py` and `pregate.py` read: per shot its reel start/end, camera clip, camera in-point and rate. Start from the EDL and correct it from a Premiere read-back; the formula is in `camera_fidelity.py`'s header.
4. Check with `get_timeline_gaps` (zero unintended gaps) and `get_timeline_summary` (matches the EDL).
5. A1: Constant Power crossfade at every cut (`batch_add_transitions`, ~1 frame). `save_project`.

## Phase 4: Colour (playbook §A, strictly in order; camera-true by default, §A0)
1. **A1 primary correction**: one `color_correct` per clip with contrast, temperature and tint only, then set exposure, highlights, shadows and saturation by script (playbook §A1, reality doc). Copy to same-setup clips with `copy_effects_between_clips`. Check the first clip by exported still before copying. Correct toward the camera file, not toward a number: fix casts, blown or crushed areas and dark night exposure, and stop.
2. **A2 shot match**: compare adjacent shots and fine-tune with `set_effect_property`, staying inside each shot's camera bands.
3. **A3 creative look: only if the director picked one in Round 2.** Ask for the manual step (create an Adjustment Layer; for a **dropdown** look, also pick it in Lumetri → Creative → Look on V3), place it on V3, apply a **preset** look with `applyLumetriPreset`, then set intensity (start at 30 %) and the table's adjustments by script (playbook §A3). `muted_red` adds the Hue vs Sat curve, a UI step. With no look, leave V3 empty, or disable an inherited layer **and** its Hue vs Sat curve.
4. **A4 texture (optional)**: none on night phone footage; elsewhere, only if the brief has it, grain ≤ 5 % on V4, with the blend mode set by script (enum in the reality doc) + `set_clip_opacity`. Fade V4 with the picture at every fade to black. No extra sharpening.
5. Export 3–4 still frames (or a short preview) and check skin tones and contrast with your own eyes. `save_project`.
6. **Colour QA against the camera** before review, on the ProRes master or the export:
   ```
   .venv/bin/python scripts/camera_fidelity.py <export> --map projects/<name>/analysis/map_v<N>.json -o projects/<name>/analysis/fidelity_v<N> [--allow <shots>] [--look] [--exclude-band 0.72,0.82]
   ```
   - It finds each shot's camera frame and framing and checks brightness, saturation, hue, crush, burn and width (effects-playbook §A0). Read `FIDELITY.md` and the camera | render sheet.
   - Fix every FAIL. A deliberate one (a cast fix, recovered highlights) goes in the brief and in `--allow`.
   - `colour_report.py --gold` still checks gold hue and shot-to-shot jumps.

## Phase 5: Motion, effects, B-roll, graphics, captions
Execute the Treatment from the brief, beat by beat:
1. V1 moves, playbook §B: only those on the brief's effect list, plus gentle pushes on steady holds (§0). **Not on handheld footage**: shakes and snap zooms read as "jumps" there, so use push/pull on holds. **No punch-ins on night footage.**
   **Stabilise only what needs it** (§0): pick the steadier take or part first (`shake_report.py`, `motion_holds.py`), then Warp only shots that still fail the shake limits, never one with an in-camera zoom or a whip. For speed-changed or interpreted clips, nest first: `seq.setInPoint/OutPoint`, target only V1, `createSubsequence(false)`, swap the nest in, then Warp the nest. Afterwards:
   - re-measure with `scripts/shake_report.py` (before vs after);
   - scan the export for Warp's "Analyzing" banner, a text band mid-frame.
2. B-roll on V2 at the trigger words, at real speed. Time effects (slow-mo, ramps, freeze, reverse, §C) only from the effect list.
3. Transitions at the planned cuts, §D. Hard cut is the default; a non-cut transition only where the brief places one (§0).
4. Graphics: HyperFrames motion graphics rendered as ProRes 4444 alpha and placed on V5, positioned per shot. Text-behind-subject goes on holds only, via `scripts/text_behind.py` (`motion-and-ai.md` §1–2).
5. Captions on V5, in the style from the brief and inside the safe zone.
6. After each group: `get_timeline_summary`, `list_clip_effects` on 2–3 clips to confirm nothing stacked twice, then `save_project`.

## Phase 5b: After Effects finishing (optional)
For shots that need **denoise, a real speed-ramp curve, Timewarp slow-mo or glow/halation**, follow `after-effects.md` (same folder). **Slow motion on ≤ 30 fps footage is off by default** (effects-playbook §0, v0.12): it ghosted, smeared or "painted" faces in 6 of 7 reels. When the director picks it on a full-rate phone sample of that shot, it goes through After Effects Timewarp (§C): Premiere's Optical Flow ghosted on goddess v10.
1. Write `analysis/ae_jobs.json` from the EDL.
2. Run `scripts/ae_roundtrip.py`, in the background, at about 4 min per shot.
3. Check every `_compare.png` and the before/after reports.
4. Swap the ProRes renders in at the same timeline positions.

Plan which shots go through After Effects in the brief's Treatment, and say so in the round summary. Stabilisation stays in Premiere (Phase 5): AE's Warp Stabilizer can't be run by script.

## Phase 6: Sound design & mix
- SFX on A2 where **this reel's playbook** allows them (its Sound section), from the menu in `effects-playbook.md` §F. Levels: the playbook's (cinematic-montage swishes about −13 dB; otherwise −14…−18 dB).
  - **Source real sounds first** (§F "Where sounds come from"): the director's own, then Openverse CC0 via `scripts/sfx_fetch.py`, picked with earshot's `--rank` and trimmed with `earshot find`, then the designed sets.
  - Run `scripts/sfx_prep.py`, place each by its transient, and list each one in the EDL `audio` list (or `analysis/sfx_cues_v<N>.json`) so the pregate can find it in the export.
  - Credit lines (`sfx_fetch.py credits`) go in `project.md`, and a CC BY credit in the Instagram caption.
  - A sound new to the studio goes to the director as an A/B before the reel relies on it.
- Music on A3:
  - section changes on the beat;
  - planned silence drops;
  - talking-head / hybrid: `setup_ducking` under A1 (−18…−22 dB under speech, about −8 dB in gaps);
  - music-montage: music leads, peaks −1…−3 dB, no ducking.
- A1:
  - talking-head: dialogue peaks −6…−3 dB;
  - music-montage: natural sound muted or ≤ −20 dB unless it adds impact.

## Phase 7: QA & export
1. `validate_project_for_export`, `check_offline_media`, `get_timeline_gaps`, `set_sequence_in_out_points`.
2. **Export a ProRes 422 master** → `renders/masters/<name>_v<round>_master.mov`, with the built-in "Match Source - Apple ProRes 422" `.epr` (path in the reality doc). Then encode the deliverables from it; Premiere's H.264 preset gave 9 Mb/s Main profile that looked blocky on the iPhone:
   ```
   .venv/bin/python scripts/encode_master.py renders/masters/<name>_v<round>_master.mov -o renders/exports/<name>_v<round>.mp4
   .venv/bin/python scripts/encode_master.py renders/masters/<name>_v<round>_master.mov -o renders/previews/<name>_v<round>_phone.mp4 --phone
   ```
   The `--phone` copy (≤ 29 MB) is the review copy sent to the director as a file. A reel whose audio is added in Instagram also gets an `_IG` master (the guide audio muted on a duplicate sequence) and its own encode.
   **Check the audio straight away** (`ffmpeg -af volumedetect`, max_volume > −20 dB). If it's silent, write `analysis/mix.json` and rebuild the audio with `scripts/mix_from_edl.py`. Note it in the round summary.
3. Run `analyze_footage.py` on the export, look at its contact sheet, and check the first 3 s plus 2–3 risky cuts with `scripts/cut_view.sh`.
4. **Verify the file** (codec, size, fps, bitrate, BT.709 tags, black or frozen frames, audio length, loudness):
   ```
   .venv/bin/python scripts/verify_render.py renders/exports/<name>_v<round>.mp4 --fps <seq fps> --expect <runtime>
   .venv/bin/python scripts/verify_render.py renders/exports/<name>_v<round>_IG.mp4 --profile ig-quiet   # no-music upload version
   .venv/bin/python scripts/verify_render.py renders/previews/<name>_v<round>_phone.mp4 --min-mbps <floor encode_master printed>
   ```
   Fix every FAIL before the review gate: `--fix-tags` for missing colour tags, `--fix-loudness` for a mix outside −14 ± 2 LUFS, `encode_master.py` for a Main-profile or low-bitrate file. Re-run on the fixed copy. The pregate (Phase 7b) runs this check again.
5. **Compare with the reference:** `scripts/teardown.py --ref <ref> --ours <export> -o analysis/teardown`. Read `COMPARE.md`, and either fix each gap beyond tolerance or say in the round notes why it's deliberate.

## Phase 7b: Review gate (every version, before the director sees it)
Follow `review-gate.md` (same folder):
1. Write the shot map (`analysis/map_v<N>.json`).
2. Run **`scripts/pregate.py`**: the file check, every-frame scan (`frame_scan.py`), the camera check and the contact sheets, in minutes and with no tokens. Fix every FAIL before going on.
3. Have the `reel-reviewer` agent on a **different model** judge it blind: a full review for a new cut, a focused one on the changed shots for a fix version (pregate's `render_diff`).
4. Save the report.
5. Fix or answer every blocker and major.
6. Re-run the gate, at most 2 loops, plus one focused check of the last fixes.
Never skip it because your own metrics passed: in the pilot, every shipped defect had passed metric QA.

### ⏸ Checkpoint 2: review the cut
Send the export path, runtime and a 3-line "what I did" summary. Ask the director to **watch it full-screen on a phone with sound**, then ask one question before accepting approval: "What would make it more cinematic?" (In the pilot, v1 was approved and then reopened five times.) On notes: start round N+1 and log the notes in `project.md`. Change only what was asked, on a new sequence version, then reply with a numbered list of changes mapped 1:1 to the notes. Route the notes first:
- **pace, picks, framing or slow-mo windows:** a new EDL version and offline preview; rebuild in Premiere once the director OKs the preview;
- **grade:** before any Lumetri change, show camera | now | proposed: `camera_fidelity.py` sheets of the current export and of a `preview_edl.py --only <the 3 hardest shots>` sample carrying the proposed `grade`, plus that 6 s sample on the phone. The sample's grade is approximate; say so.

Rewrite `## Now` when the round ends.

## Phase 8: Instagram package (after final approval)
Read `instagram-strategy.md` (same folder) first: where it disagrees with the `ig-*` pack, it wins. Using `ig-hook-extractor`, `ig-caption-writer`, `ig-hashtag-strategist` and `ig-humanizer`, write to `project.md` (and the caption to `deliver/caption.txt`):
- 3 first-line hooks (< 125 characters);
- the caption: hook in the first 125 characters, the subject named in plain search words, one concrete "send this to…" call to action, credits (voiceover, music, people who asked), humanised;
- **at most 5 hashtags, all on the reel's real subject**: no tool or brand tags;
- **the AI credit line**, since AI edited every studio reel: one detailed line on what AI did, with the footage and direction the director's. Use the verified handles in `instagram-strategy.md` (@claudeai, @adobevideo; never @premierepro);
- **the AI info label:** **on** only if the reel contains an AI-generated shot (`motion-and-ai.md` §3); **off** for AI-edited real footage;
- alt text, location, and the cover frame timecode;
- no collab invite and no Story share (director profile).

**Posting** happens only when the director asks for that post. Follow `ig-posting-reality.md` (iPhone Mirroring), and stop before Share: the director taps it. Check that "Upload at highest quality" is on before Share.

**After it's posted** (v0.12): check the reel as Instagram serves it, following `instagram-served-check.md` (same folder). Record in `project.md`:
- Instagram's encode tier (basic or advanced);
- the served resolution and bitrate;
- the detail kept against our export;
- that the reel's audio plays, by the director's ear: the "Audio unavailable" label isn't evidence (Goddess shows it and plays).

Our reels get Instagram's basic encode until they're popular, so the export has to survive it.

### ⏸ Checkpoint 3: approve the package.

## Phase 9: Retro (pilot reels; optional for others)
After the package is approved:
1. Fill in `projects/<name>/retro.md`. Use the friction log, every workaround and every CR already filed. Be concrete: name the tool, the step, how long it took and what you'd change.
2. Copy it to `studio/retros/<name>.md`.
3. Turn each "change the studio" item into a CR in `studio/change-requests/`, unless one is already filed.
4. Set `Status` in `project.md` to `done`. Tell the director: "N change requests filed for HQ. Run `/studio-hq` in the HQ session to apply them."


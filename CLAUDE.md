# Cinematic Reels Studio — Operating Contract

You are the **editor**. The user is the **director**. They hand you clips, answer your questions, and share references. **You write the brief, the cut plan and the treatment**, then turn the clips into a fully treated cinematic 9:16 Instagram Reel in Adobe Premiere Pro. You never make a creative call they'd want to make without showing it to them first.

**Never just cut and stitch, and never over-treat.** Every reel gets:
- per-clip colour correction and shot matching, **camera-true by default** (effects-playbook §A0);
- type and graphics;
- sound design;
- a creative look, texture and designed moves only where the director picks them. Designed moves are speed changes, slow motion, step-prints, zooms and shakes, wipes, flashes, and type mattes. The brief's **effect list** names each one, and the director approves it.

**Restraint is the default (v0.12, effects-playbook §0).** Footage plays at real speed, cuts are hard, and the camera is still or steady. The director's saved references are plain, and our treated reels read as glitchy, flickery, grainy and over-processed (`studio/reviews/quality-diagnosis-2026-11-15.md`). A talking head may take a gentle push (creator-explainer).

The menu is `.claude/skills/cinematic-reel/effects-playbook.md`. **Which** moves a reel uses, how often and how loud comes from its **editing playbook**, one per kind of video (`.claude/skills/cinematic-reel/playbooks/`: `cinematic-montage`, `story-montage`, `creator-explainer`). The brief names it.

## 0. How a reel moves through this studio

```
interview director  →  analyse clips + references  →  YOU write brief.md + EDL  →  storyboard + offline preview  →  ⏸ approve
  → rough cut (V1/A1) → colour: correct → match → look → texture (V1/V2, V3, V4)
  → motion, effects, B-roll, graphics, captions (V1/V2/V5) → sound design (A2/A3)
  → QA + export → ⏸ notes → new version … → Instagram package
```

- Each reel lives in `projects/<reel-name>/` (create with `scripts/new_reel.sh <reel-name>`).
- `brief.md` is written **by you** from the interview, the footage analysis and the references. The director approves it, and it then binds you. If the footage can't deliver what the director asked for (e.g. the hook line was never actually said, or slow-mo was requested on 30 fps footage), say so. Don't silently substitute.
- Ask the director questions in short multiple-choice rounds. Never ask what the footage or a reference already answers.
- `project.md` is the running log: approved hook, EDL, versions, notes from each review round. Update it after every round so the next session can pick up cold.
- The full step-by-step workflow is the `/cinematic-reel` skill (`.claude/skills/cinematic-reel/SKILL.md`).

## 0.1 Studio governance: HQ session vs reel sessions

Full detail is in `studio/ARCHITECTURE.md`.
- **Every reel is its own sub-project**, edited in its own session. Start the session at the `reels-studio/` root with `/cinematic-reel <reel-name>`.
- **One HQ session** (`/studio-hq`) owns the architecture: this file, `README.md`, `setup.sh`, `.mcp.json`, `.claude/`, `scripts/`, `studio/`, `projects/_template/`.
- **A reel session writes only to:**
  - its own `projects/<reel>/`;
  - `studio/change-requests/`;
  - `studio/retros/`;
  - `studio/ledger/` (append-only spend logs, written by scripts);
  - new files in `assets/`.

  This holds for shell commands too, not just Edit/Write.
- **When a reel session hits an architecture gap**, such as a wrong rule, a missing tool, a script bug or an unsupported reel type:
  - work around it inside the reel folder;
  - log the workaround in `project.md`;
  - file a CR in `studio/change-requests/` from `_TEMPLATE.md`;
  - never patch shared files.
- **Pilot reels** (`Pilot: yes` in `project.md`) also keep a `## Friction log` and write `retro.md` at the end. That's how the studio learns.

## 1. Taking direction

- Treat the director's notes as specific, not as vibes. "Make the hook punchier" means: shorter hook, earlier movement, harder cut — propose exactly what you'll change.
- After every review round, reply with a numbered list of the changes you made, mapped 1:1 to their notes, plus anything you could *not* do and why.
- Never re-cut approved sections unless asked. Version every round as a new sequence (`Reel_<name>_v2`, `_v3`…).
- When the director gives a reference ("like Ali Abdaal's reels", "Jason Cooperson style"), translate it into concrete parameters in `project.md` (cut rate, caption style, grade, music energy) and confirm before cutting.

## 2. Premiere Pro guardrails (non-negotiable)

MCP server: `premiere-pro` (npm `adobe-premiere-pro-mcp`, from hetpatel-11/Adobe_Premiere_Pro_MCP). With `PREMIERE_MCP_TOOLSET=full` all ~283 tools are listed; otherwise use `search_tools` → `invoke_tool`.

1. **Verify the bridge first.** Start every session with `verify_premiere_connection` (read-only). No mutations until Premiere reports connected. If it fails, tell the director to open `Window > Extensions > MCP Bridge (CEP)`, check Temp Directory = `/tmp/premiere-mcp-bridge`, click **Start Bridge**.
2. **Read the server's own instructions once per session**: resource `premiere://config/get_instructions`. Then read `.claude/skills/cinematic-reel/premiere-mcp-reality.md`. It lists which tools are broken on this Premiere/MCP version and the verified fallbacks.
2a. **Verify by render, never by the tool's reply.** Many tools report success without doing the work. After every colour, transition, opacity, blend or audio change, export a still (and check audio after every export) and confirm the change numerically and by eye. Read ExtendScript results by writing them to a file (reality doc, Rule 2).
3. **Duplicate before mutating.** `duplicate_sequence` before any razor / ripple delete / batch effect. The director's original sequence is the rollback point and is never edited.
4. **Read back after structural edits.** After `razor_timeline_at_time`, `ripple_delete`, `trim_clip`, `set_clip_properties`, `speed_change`: call `get_timeline_summary` or `get_timeline_gaps` and check the result matches the intent. QE can quantize to frame boundaries or quietly reject edits.
5. **Effects can't be removed via script.** Premiere's ExtendScript DOM has no "remove one effect" call, so plan before you apply:
   - **`color_correct` adds a new Lumetri every time it's called.** Call it exactly **once per clip**, and only with `contrast`, `temperature` and `tint`. It ignores the other values, and `saturation` turns the clip black and white. Set exposure, highlights, shadows and saturation on that same Lumetri by script (reality doc: Lumetri recipe). Check with `list_clip_effects` before touching a clip.
   - Per-clip *primary* correction (exposure, white balance, contrast) goes on the clip. Never put creative LUTs or stylised looks on V1/V2 clips.
   - The creative look (LUT, look contrast, vignette, B&W) goes on the **adjustment layer on V3**, and only when the director picked one: the default grade is camera-true (effects-playbook §A0). `add_adjustment_layer` doesn't make a real one, so the director creates it with one manual click (reality doc). Custom `.cube` LUTs can't be loaded by script. A look that has a built-in Lumetri preset is applied by script; any other look, including most of Adobe's film looks, the director picks from the Look dropdown, and so is any `.cube` the director loads by hand (playbook §A3 gives each look's route).
   - Exception: a camera log→Rec709 conversion LUT may be a clip's single Lumetri, applied with `apply_lut`.
6. **A sequence created by `duplicate_sequence` must be opened in the timeline** before QE-based tools (e.g. `delete_track`) can reach it.
7. **`detect_silence` runs ffmpeg on the source file**, not on the timeline. Convert its source-time ranges to sequence time before cutting.
8. **Save checkpoints.** `save_project` after each approved phase.

Correct tool names (the original architecture doc had two wrong):
- Audio crossfade → `add_transition` / `batch_add_transitions` with an audio transition (check `list_available_audio_transitions`; prefer *Constant Power*), ~30 ms (1 frame at 30fps).
- Speed ramp / slow-mo → `speed_change` (or `set_clip_speed_qe`).

## 3. 9:16 track architecture (every reel)

Sequence: **1080×1920**. **Frame rate = the most common frame rate in the footage** (from `analysis/summary.md`): 25 fps footage → 25 fps sequence, 29.97 → 29.97, 23.976/24 → 23.976. Never put 25 fps footage on a 30 fps timeline: every 5th frame repeats and motion stutters. Conform outlier clips (e.g. a few 24 fps clips in a 25 fps shoot) **by interpretation, before placing them**: `set_override_frame_rate {projectItemId, frameRate: <sequence fps>}`. Every frame then plays once and durations stay exact. Scale source in/out times by original_fps / sequence_fps, and note it in `project.md`. Interpreted audio shifts pitch about 4 %: fine for muted natural sound, but flag it on dialogue. Use `speed_change` only for creative speed. Only footage shot at ≥ 2× the sequence rate has true slow-mo headroom.

| Track | Content | Rules |
|---|---|---|
| **V5** | Captions & kinetic type | Above the grade, so text stays clean. 2–4 words per line, in the safe zone: clear of top 220 px, bottom 320 px, right 120 px (IG buttons). |
| **V4** | Texture overlays | Grain / light leaks / film burns from `assets/overlays/`, with `set_blend_mode` (Overlay / Soft Light / Screen) + `set_clip_opacity`. Optional, and only from the brief: never grain on footage that already shows noise (all night phone footage), ≤ 5 % otherwise (effects-playbook §A4). |
| **V3** | Creative look adjustment layer (optional) | Only when the director picked a look over camera-true (effects-playbook §A3). Spans the reel. Film look or LUT starting at 30 % (the §A3 rows give each look's full intensity), look contrast, vignette. Grades V1 + V2 only. |
| **V2** | B-roll & HyperFrames graphics | Each clip primary-corrected. Cutaways on visual nouns / emotional shifts. Real speed; time effects (slow-mo, ramps, freeze) only from the brief's effect list (effects-playbook §0). |
| **V1** | A-roll (talking head / hero action) | Primary-corrected. Reframed to 9:16, showing ≥ 80 % of the camera width on vertical footage (Scale ≤ 62.5 on vertical 4K); landscape footage takes the framing the director picks in the brief, the 16:9 film frame offered first (playbook §B). Gentle pushes on steady holds; punch-ins and snap zooms only from the effect list, never on night footage (playbook §0, §B). |
| **A1** | Dialogue (natural sound in `music-montage`) | Constant Power crossfade at every cut. Peaks −6 to −3 dB. Music-montage: muted or ≤ −20 dB (§4c). |
| **A2** | SFX | From `assets/sfx/`, on B-roll entries and graphic reveals, −14 to −18 dB. |
| **A3** | Music | From `assets/music/`. −8 dB in gaps, ducked to −18…−22 dB under speech (`setup_ducking` / `add_audio_keyframes`). Music-montage: lead track, peaks −1 to −3 dB, no ducking (§4c). |

## 4. Editorial rules

Every reel has a **reel type**: `talking-head`, `music-montage` or `hybrid` (`studio/ARCHITECTURE.md` §6). It's recorded in `brief.md` and `project.md`. §4a applies to all reels. §4b or §4c applies by type. A `hybrid` reel uses §4b for spoken stretches and §4c for the rest.

### 4a. All reels
- **3-second hook.** 0–3 s pairs the strongest moment with immediate visual motion (push-in, flash B-roll, or title card + riser).
- **Length**: default target 30–45 s unless the brief says otherwise. Say the actual runtime in every proposal.
- **No unapproved destructive assembly.** Propose the EDL + hook in `project.md` (or as soft `add_marker` markers) and get a yes before assembling.

### 4b. `talking-head`: speech drives the timing
- The hook is the strongest line from `takes_packed.md`.
- **Kill dead air** > 0.25 s (unless it's a deliberate dramatic pause the director wants), false starts, fillers (um, uh, like, you know), and repeated takes. Default to the last, most confident take.
- **J-cuts**: audio leads video by 2–4 frames on scene changes to keep it from feeling robotic.
- **Every cut lands on a word boundary** from the word-level transcript. Use `timeline_view.py` to visually check any cut that feels risky (filmstrip + waveform PNG).
- **Cut on the clause onset, by the waveform.** Whisper's word starts can run early (about 0.3 s on the goddess VO): find the clause in the transcript, then put the cut 0–2 frames before the speech starts on the waveform.

### 4c. `music-montage`: no speech, the music drives the timing
- **No transcription.**
- **Get the beat grid first.** Run `scripts/gemini_audio_and_beat_analyzer.py --music <track> -o projects/<reel>/analysis`. It gives BPM, every beat, every 4th beat and the strongest accents (`analysis/beats.json`). The hook and the EDL are planned on it.
- **Cuts land on beats.**
  - Section changes and hero shots go on accents or every 4th beat.
  - Fast sections can cut on every beat or every 2nd beat.
  - Never cut off the grid unless it's a deliberate hold.
- **Hook.** The strongest-looking shot plus motion, landing on the first accent. Trim the music so the reel opens close to its energy, not on a slow intro, unless the brief asks for a build.
- **Shot length follows the music's energy.** Use the reference's measured pacing as the target. The brief states an **energy arc** and a **motion style** (skill Phase 2). Never cut one shot per bar for the whole reel: the pilot's v1 read as mechanical.
- **Pick the best moment, not the whole clip.** For each shot, choose the part with the most motion or the cleanest composition (from the contact sheet).
- **Audio.**
  - Music on A3 at full level, with peaks around −1 to −3 dB and no ducking.
  - Natural sound from the clips on A1, muted or low (−20 dB or quieter) unless it adds impact.
  - SFX on A2 as usual.
- **Text.** Titles and kinetic type replace captions. Few words, timed to beats.
- **Music must be licensed**, in `assets/music/`. Instagram's in-app library audio can't be exported into Premiere. If the director plans to add IG audio at upload instead (a library song, or another reel's original audio):
  - cut to a **guide copy** of that exact audio (the reference's own track, extracted in stereo), so cuts land on its real beats and words;
  - deliver `_mix` (guide baked: archive only, never posted) and `_IG` (guide muted), and add the audio in Instagram with "Use audio" from 0:00;
  - check the audio's Instagram page (library song or "Original audio", and the creator) in Phase 1, not at posting. Pujo found out at the Share screen and rebuilt six versions.

## 5. Local tooling

- Ingest check (Phase 1, first): `scripts/ingest_report.py <raw> -o <analysis> --scan` reads what the camera recorded (codec, bit depth, fps and VFR, Blackmagic Cam white balance / shutter / ISO / lens), rates and measures mains flicker, finds dropped-frame jumps, and groups clips by shoot night and white balance. The director's camera settings are in `studio/shooting-guide-blackmagic-cam.md`.
- Cinematic-mode depth: `scripts/cine_bake.py --edl analysis/edl_v<N>.json` bakes Apple Cinematic Video's depth of field (ingest flag `cinematic`) into ProRes, because only Apple apps draw it. It writes `edl_v<N>_baked.json`, and previews, checks and Premiere use the bakes, never the sharp camera files (skill Phase 1).
- Footage & reference analysis: `scripts/analyze_footage.py` writes a contact sheet + exposure / white-balance / saturation / fps readings per clip, and with `--reference` the cut pacing. **Look at the contact sheets** before deciding colour or effects.
- Reference teardown: `scripts/teardown.py --ref <ref> [--ours <export>]` measures pacing, motion, picture and loudness the same way for both, and writes `COMPARE.md`.
- Planning and previews: `scripts/pick_sheet.py` (6 frames per clip from the analysis folders; the whole pool with `--all`), then, from `analysis/edl_v<N>.json`, `scripts/storyboard.py` (in / mid / out per shot through its framing, Instagram UI bands shaded) and `scripts/preview_edl.py` (the cut off the camera files with overlays and audio, in minutes, no Premiere; `--only` for a sample of chosen shots). Pace, picks and framing are settled on previews; the grade on the Premiere export.
- Camera check: `scripts/camera_fidelity.py <export> --map analysis/map_v<N>.json` finds each shot's camera frame and framing and checks brightness, colour, crush, burn and width against it (effects-playbook §A0). The default grade is judged this way, not against fixed numbers.
- Delivery: Premiere exports a ProRes 422 master; `scripts/encode_master.py` makes the H.264 High deliverables (~18 Mb/s) and `--phone`, a ≤ 29 MB review copy.
- Final file check: `scripts/verify_render.py <export>` (codec, H.264 High, 1080×1920, fps, bitrate ≥ 12 Mb/s, TV-range 4:2:0, BT.709 tags, black/frozen frames, −14 LUFS / −1 dBTP; `--profile ig-quiet` for the no-music version, and for the phone copy the `--min-mbps` floor `encode_master.py` prints).
- Pregate: `scripts/pregate.py` runs before every review gate (review-gate.md):
  - the file check;
  - the every-frame scan, where typed `--designed` spans allow only their own flags;
  - `scripts/motion_audit.py`: camera shake per shot, failing any step-print that jumps more than 4 px;
  - `scripts/quality_probe.py`: each shot's grain, busyness, flicker and cadence against the director's saved references (`studio/reference-targets.json`). Grain above the line fails; the rest get a strip for the reviewer;
  - the camera check;
  - `scripts/render_diff.py` (what changed since the last reviewed version);
  - the 2 fps sheets, plus full-rate strips of the hook, the designed spans, every REVIEW shot and every quality WARN.

  Every export passes it before the reviewer is called. A REVIEW shot is cleared only by the reviewer's verdict on its strip.
- Story devices: `scripts/step_print.py` (step-printed stutter render) and `scripts/photo_prints.py` (photo-print inserts on paper), used by the story-montage playbook.
- Look previews: `scripts/look_preview.py` renders Premiere's own film-stock looks (effects-playbook §A3) on the director's stills, for Round 2.
- FFmpeg colour and keying (look previews on stills, keying green-screen elements to ProRes 4444 alpha, pre-rendered effect shots): the `ffmpeg-color-grading-chromakey` skill. Never for the reel's grade, which stays in Premiere.
- Sound effects (effects-playbook §F):
  - `scripts/sfx_fetch.py` finds real CC0 recordings on Openverse, with no key. It ranks them by listening with earshot, keeps a pick with its licence and prints the credits.
  - `scripts/sfx_prep.py` trims leading silence and peaks at −3 dBFS before placing sounds.
  - `scripts/sfx_sync.py` finds each placed sound in the export's own audio, for the pregate.
  - earshot (`~/.local/bin/earshot`, MIT, pinned in `scripts/earshot_util.py`) is Claude's ears: `rank`, `find`, `sheet`, and a code-made bank (`scripts/earshot_bank.py` → `assets/sfx/earshot/`). Never use its `llm` command: it uploads audio. Generated or stock clips: `scripts/conform_clip.py` (frame rate, 1080×1920, colour match to the footage).
- Transcription: `scripts/transcribe_reel.sh <reel-name> [files]`, local Whisper by default (`scripts/transcribe_local.py`: free, offline, word-level, the same JSON as Scribe). `--scribe` uses ElevenLabs Scribe (`.vendor/video-use/helpers/transcribe.py`) when `.env` has a working `ELEVENLABS_API_KEY`.
- Packing: `pack_transcripts.py` → `projects/<name>/transcripts/takes_packed.md`. Read this, not raw frames.
- Cut inspection: `.vendor/video-use/helpers/timeline_view.py <video> <start> <end> -o out.png`.
- Watching a video without playing it: `scripts/watch.py` (2 fps contact sheets per shot, with the audio waveform). The **review gate** (skill Phase 7b, `.claude/skills/cinematic-reel/review-gate.md`) runs the `reel-reviewer` agent on a different model before every Checkpoint 2.
- Motion graphics (HyperFrames → ProRes 4444 alpha on V5), text behind the subject (`scripts/text_behind.py`), and AI-generated shots (`scripts/gen_video.py`: OpenRouter → Veo 3.1 Lite or Gemini Omni, no audio; Veo draft ≈ $0.12, then final ≈ $0.40; caps $4 and 4 shots per reel, $20/month; the last step of the bad-footage ladder; stills only, never a clip; labelled in the brief; Claude plans and checks them but can't make the frames; the Higgsfield MCP is connected, with Kling 3.0 pro its best gap fill in one test, caps of 90 credits per reel and 450 a month, logged in `studio/ledger/higgsfield-credits.jsonl`, and every call asks the director): `.claude/skills/cinematic-reel/motion-and-ai.md`. The prompt's light and colour come from the `film-emulation-prompts` skill: the scene is described ungraded, so the reel's look isn't applied twice.
- After Effects finishing (denoise, speed-ramp curves, Timewarp, glow): `scripts/ae_roundtrip.py` via `scripts/ae_bridge.py`. Rules and verified settings are in `.claude/skills/cinematic-reel/after-effects.md` (skill Phase 5b).
- Motion graphics: HyperFrames skills (`/hyperframes`, `/motion-graphics`, `/embedded-captions`, `/talking-head-recut`), rendered to `projects/<name>/renders/overlays/` as 1080×1920 (alpha `.mov` when it overlays footage).
- Instagram packaging: `ig-hook-extractor`, `ig-caption-writer`, `ig-hashtag-strategist`, `ig-humanizer` skills.

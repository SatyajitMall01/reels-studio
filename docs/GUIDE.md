# Cinematic Reels Studio: the complete guide

*From install to a posted reel. Studio v0.11.1, November 2026. The PDF copy of this guide is `docs/GUIDE.pdf`. Rebuild it with `scripts/build_guide_pdf.py` after editing this file.*

---

## Contents

1. What the studio is
2. What's in this repository, and what isn't
3. What you need
4. Installation, step by step
5. How the studio runs: HQ and reel sessions
6. Before you shoot
7. Making a reel, end to end
8. The 9:16 track layout
9. Editorial rules
10. Colour
11. Motion, effects, transitions and type
12. Sound design
13. AI-generated shots
14. Quality checks, the review gate and delivery
15. The Instagram package and posting
16. Giving notes and working in rounds
17. Tools reference
18. Working with Premiere through MCP
19. Changing the studio itself
20. Troubleshooting
21. Glossary
22. Credits and licences

---

## 1. What the studio is

Cinematic Reels Studio turns your own clips into a finished, cinematic **9:16 Instagram Reel** in **Adobe Premiere Pro**. The editor is Claude Code, driving Premiere through an MCP bridge. The roles are:

- **You are the director.** You shoot, hand over clips, answer short multiple-choice questions, share references, and approve or give notes.
- **Claude is the editor.** It writes the brief, the cut plan and the treatment, builds the reel in Premiere, checks it, and exports it. It never makes a creative call you'd want to make without showing it to you first.

**It never just cuts and stitches, and never over-treats.** Every reel gets:
- colour correction and shot matching for each clip, **camera-true by default** (the picture stays as close as possible to what the camera recorded);
- type and graphics;
- sound design;
- a creative look, film texture and designed moves (slow motion, ramps, step-prints, zooms, wipes, flashes) **only if you pick them** on the brief's effect list.

**Restraint is the default (v0.12).** Footage plays at real speed, cuts are hard, and the camera is still or steady. A 2026-11-15 study of the director's saved reference reels against the studio's posted reels found the references plain, calm and clean. The studio's treated reels read as glitchy, flickery and grainy. Most of that came from synthetic slow motion, crops on noisy night footage, stacked processing, and footage shot at 1/60 s under mains lamps (`studio/reviews/quality-diagnosis-2026-11-15.md`).

### Reel types
Each reel has a **type**, which decides what drives the timing:

| Type | What it is | Timing comes from |
|---|---|---|
| `talking-head` | Someone speaks to camera or in a voiceover | Word boundaries in a word-level transcript |
| `music-montage` | No speech: the music carries it | The music's beat grid |
| `hybrid` | A montage with spoken lines or VO moments | Words in the spoken parts, beats in the rest |

### Editing playbooks
On top of the type, each reel follows one **editing playbook**: the style rules for its kind of video (pace, camera, type, transitions, sound, colour and quality thresholds). They live in `.claude/skills/cinematic-reel/playbooks/`:

| Playbook | For |
|---|---|
| `cinematic-montage` | Music montages |
| `story-montage` | Narrated montages with one recurring character |
| `creator-explainer` | Talking to camera |

The menu of every look, move, transition and sound is `.claude/skills/cinematic-reel/effects-playbook.md`. The playbook says which items from it a reel uses, and how often.

---

## 2. What's in this repository, and what isn't

```
CLAUDE.md                         the editor's operating contract (rules Claude always follows)
README.md                         short overview and quick start
LICENSE                           MIT (folders with their own LICENSE keep it)
setup.sh                          one-time Mac setup (safe to re-run)
.mcp.json                         MCP servers: Premiere Pro bridge, Higgsfield (optional)
.env.example                      optional API keys (copy to .env, never commit .env)
skills-lock.json                  pinned versions of the third-party skills setup.sh installs
docs/                             this guide (Markdown + PDF) and the shooting guide PDF
.claude/
  skills/cinematic-reel/          the reel workflow (/cinematic-reel), playbooks, effects menu, Premiere notes
  skills/studio-hq/               the architecture workflow (/studio-hq)
  skills/ffmpeg-color-grading-chromakey/, film-emulation-prompts/   studio forks of MIT skills
  agents/reel-reviewer.md         the independent reviewer that checks every cut
  hooks/                          the guard that keeps reel sessions out of shared files, the paid-AI ask
  settings.json                   wires the hooks in
scripts/                          the studio's tools (section 17)
studio/
  ARCHITECTURE.md                 roles, file ownership, change requests, versioning
  VERSION, CHANGELOG.md           the studio's version and history
  BACKLOG.md                      planned and parked work
  change-requests/                requests from reel sessions to HQ (CR-*.md)
  retros/                         what each finished pilot reel taught the studio
  plans/                          larger plans
  reviews/                        outside reviews of the studio (claims to verify, not rules)
  upstream/                       drafted bug reports for third-party tools
  director-profile.example.md     blank template for your standing preferences
  shooting-guide-blackmagic-cam.md   one page for the camera, before a shoot
  ai-budget.json                  caps for paid AI generation
  ledger/README.md                what the local spend logs record
projects/
  _template/                      copied for every new reel
  _hqtest/                        HQ's test bench for new tools
  <reel>/                         one folder per reel (only its notes and code are in git)
assets/                           your LUTs, music, SFX, overlays, MOGRTs, presets (empty in git)
```

### Not in the repository
The repository is public, so these stay on your Mac and are git-ignored:

- **All media.** Camera clips (`raw/`), references, renders, exports and deliveries, music, voice takes, sound effects, fonts, LUTs and overlays. `assets/` holds only empty folders; `setup.sh` rebuilds a starter set of LUTs, grain and sound effects.
- **Anything copyrighted.** Songs, audio taken from reference reels, lyric transcripts.
- **Personal files.** `studio/director-profile.md` (made from the example by `setup.sh`), the spend ledgers in `studio/ledger/`, `.env` with your keys.
- **Generated analysis.** Each reel's `analysis/` and `transcripts/` folders.
- **Third-party tools.** `.venv/`, `.vendor/` and the third-party skills are installed by `setup.sh`.

For each finished reel the repository keeps its `brief.md`, `project.md` (the running log), `retro.md`, its research notes, its one-off `tools/` scripts and its HyperFrames graphics source. They're a record of how each reel was made. Their media isn't included, so they won't re-render on another machine.

---

## 3. What you need

**Hardware and system**
- A Mac (Apple Silicon or Intel), macOS 14 or later for the Cinematic-mode depth bake.
- About 3 GB of free disk for the tools and models, plus room for your footage.

**Software**
- **Adobe Premiere Pro** (the studio is built and tested on Premiere 2026). **After Effects 2026** is optional, used for slow motion, denoise and glow (section 11).
- **Claude Code**: the Claude desktop app (Code tab) or the `claude` CLI. A plan with access to two different models is best, because the review gate runs the reviewer on a different model from the editor.
- **Homebrew** (`https://brew.sh`). `setup.sh` uses it to install Node 20+, ffmpeg, Python 3 and `uv`.
- The Xcode **Command Line Tools** (`xcode-select --install`), only to build the Cinematic-mode depth bake.

**Optional accounts** (keys go in `.env`; nothing needs them by default)

| Key | Used for |
|---|---|
| `ELEVENLABS_API_KEY` | ElevenLabs Scribe transcripts (`transcribe_reel.sh --scribe`). Local Whisper is the free default |
| `PEXELS_API_KEY` | Stock B-roll search, only when you ask for stock |
| `OPENROUTER_API_KEY` | AI-generated shots (section 13) |
| Higgsfield | AI shots through the Higgsfield MCP, which signs in through its own page (no key in `.env`) |

---

## 4. Installation, step by step

1. **Get the code.**
   ```bash
   git clone https://github.com/SatyajitMall/reels-studio.git
   cd reels-studio
   ```
2. **Run the setup script.** It's safe to re-run: each step skips itself if it's already done.
   ```bash
   bash setup.sh
   ```
   It does six things:
   1. Checks the prerequisites: Homebrew, Node 20+, ffmpeg, Python 3. It builds `scripts/bin/cine_bake` if Swift is available.
   2. Installs the **Premiere Pro MCP server** (`adobe-premiere-pro-mcp`, from hetpatel-11/Adobe_Premiere_Pro_MCP) and its CEP panel.
   3. Clones **video-use** (cut inspection) into `.vendor/`, makes the Python environment `.venv/`, and installs local Whisper and the analysis libraries.
   4. Installs the agent skills: the Premiere MCP skill, **HyperFrames** (motion graphics) and the **Instagram** skills. It then generates the starter LUTs, sound effects and grain, installs **earshot** (the studio's sound-matching tool, pinned to a reviewed commit) and renders its sound set.
   5. Creates `.env` from `.env.example`, and `studio/director-profile.md` from the blank template.
   6. Runs the Premiere MCP health check.
3. **Finish inside Premiere Pro** (one time):
   1. Premiere Pro → Settings → Plugins → turn on **UXP developer mode**, then restart Premiere.
   2. Window → Extensions → **MCP Bridge (CEP)**.
   3. Set Temp Directory to `/tmp/premiere-mcp-bridge` → **Save Configuration**.
   4. **Start Bridge** → **Test Connection**.
4. **Optional keys.** Open `.env` and fill in only the keys you'll use (section 3). Never commit `.env`; it's git-ignored.
5. **Restart Claude.** Fully quit and reopen the Claude app, or start `claude` in this folder, so it loads `.mcp.json`, the skills and the hooks.
6. **Check it works.** Open a Code session at the `reels-studio/` root and ask Claude to verify the Premiere connection. It calls `verify_premiere_connection`, which needs Premiere open with a project loaded and the bridge started.

---

## 5. How the studio runs: HQ and reel sessions

The studio separates **making reels** from **changing how reels are made**.

- **One HQ session** (`/studio-hq`) owns the architecture:
  - `CLAUDE.md`, `README.md`, `setup.sh`, `.mcp.json`;
  - `.claude/` (skills, hooks, agents);
  - `scripts/`, `studio/`, `docs/`, `projects/_template/`.
- **Each reel is its own session** (`/cinematic-reel <reel-name>`). A reel session writes only to:
  - its own `projects/<reel>/`;
  - `studio/change-requests/` and `studio/retros/`;
  - `studio/ledger/` (through scripts);
  - new files in `assets/`.

**Always open sessions at the `reels-studio/` root**, never inside a reel folder: the Premiere MCP config and the skills load from the root.

**Enforcement.** `.claude/hooks/guard_architecture.py` denies edits to HQ-owned files from any session that isn't the current HQ. A prompt starting with `/studio-hq` claims HQ for that session.

**When a reel session hits a gap** (a wrong rule, a missing tool, a script bug, an unsupported reel type), it doesn't patch shared files. It:
1. works around the gap inside its own reel folder;
2. logs the workaround in its `project.md`;
3. files a change request in `studio/change-requests/` from `_TEMPLATE.md`.

HQ then accepts it (and versions the change), defers it to `BACKLOG.md`, or rejects it with a reason (section 19).

**Pilot reels** (`Pilot: yes` in `project.md`) also keep a friction log and write a retro at the end, which is how the studio learns.

---

## 6. Before you shoot

The one-page camera guide is `studio/shooting-guide-blackmagic-cam.md` (PDF: `docs/shooting-guide.pdf`). It was built from 329 measured festival-night clips shot with Blackmagic Cam on an iPhone. The short version:

- **One frame rate all night (25 fps, or 30 fps once tested) at a 1/50 s shutter.** The shutter is what stops flicker under India's 50 Hz lamps; 30 fps plays more evenly on iPhones. Never 1/60 s under mains lamps.
- **Slow-motion moments at twice the night's rate and 1/100 s** (50 fps for 25, 60 fps for 30). Only footage shot at twice the reel's rate slows cleanly; the studio no longer makes slow motion up by default.
- **Low ISO, the main 26 mm lens at night, and a still camera.** Noise is the main reason reels look grainy, and every crop in the edit multiplies it. Frame each shot as it will be used, hold still or use a gimbal, and never zoom while recording.
- **Shoot landscape for a horizontal-frame reel** (16:9 inside 9:16, the shape of most saved references).
- **Lock white balance to the light**: 3200 K under tungsten and pandal lamps, 4000–4500 K under mixed LED, 5600 K in daylight.
- **Protect the highlights.** A slightly dark night is fine; blown gold and crushed black can't be recovered in 8-bit.
- **A LUT on the monitor only.** If one is burned in, type its name in the clip's slate notes.
- **Hold each shot 5–10 s, with one camera move.** The edit picks the best second and needs handles.
- **Record 10 s of ambience** at every location.

---

## 7. Making a reel, end to end

### 7.1 Start the reel
```bash
scripts/new_reel.sh my-reel-name
```
This copies `projects/_template/` to `projects/my-reel-name/`. Then:
1. Put talking-head or main clips in `raw/a-roll/` and cutaways in `raw/b-roll/`. For a music-only reel, everything can go in `raw/b-roll/`. If the footage lives elsewhere, link it without copying:
   ```bash
   scripts/link_footage.sh my-reel-name "/path/to/your/footage"
   ```
2. Optionally, put 1–3 reference reels you like in `references/`. Screen recordings are fine; Instagram links often can't be fetched.
3. Open Premiere with a project open and the bridge started.
4. Open a **new** Code session at the `reels-studio/` root and type:
   ```
   /cinematic-reel my-reel-name
   ```

From here the session follows nine phases, with three points where it stops for you (**⏸ checkpoints**).

### 7.2 Phase 0: the interview
Claude reads the reel's `project.md` and your `studio/director-profile.md` first, so it never re-asks what's already answered. Then it asks two short multiple-choice rounds.

**Round 1, the idea** (before it looks at the footage):
- what the reel is about, and whether anyone speaks (this sets the reel type and the playbook);
- what viewers should feel or do at the end;
- who it's for, and how long it should be;
- branding, if the profile doesn't have it;
- references;
- whether the soundtrack is existing Instagram audio. If it is, Claude checks that audio's Instagram page now, not at posting time.

**Round 2, taste** (after analysing the footage, so the options are concrete):
- **look**: camera-true by default, or a creative look on top, shown on your own stills rather than named;
- **pace**: calm, medium or fast, pre-selected from what the reference measured;
- **effects intensity**, **captions and words**, **music**, and anything that must or must not happen.

### 7.3 Phase 1: preflight and footage analysis
1. Claude checks the Premiere connection and reads the project.
2. **Ingest check**: what the camera actually recorded (codec, bit depth, frame rate and variable frame rate, white balance, shutter, ISO), mains flicker, dropped-frame jumps, and clips grouped by shoot night and white balance:
   ```bash
   .venv/bin/python scripts/ingest_report.py projects/<reel>/raw -o projects/<reel>/analysis --scan
   ```
   Cinematic-mode clips get their depth of field baked from the first EDL on (`scripts/cine_bake.py`), because only Apple apps draw it.
3. **Footage analysis**: a contact sheet and exposure, white-balance, saturation and frame-rate readings for every clip, and the cut pacing of each reference:
   ```bash
   .venv/bin/python scripts/analyze_footage.py projects/<reel>/raw/a-roll projects/<reel>/raw/b-roll -o projects/<reel>/analysis
   .venv/bin/python scripts/teardown.py --ref projects/<reel>/references/<ref>.mp4 -o projects/<reel>/analysis/teardown
   ```
   Claude looks at the overview sheets itself, catching sideways clips, hero moments and what's really in each shot.
4. **Timing source**:
   - **speech**: a word-level transcript with local Whisper, `scripts/transcribe_reel.sh <reel>` → `transcripts/takes_packed.md`;
   - **music**: a beat grid, `scripts/gemini_audio_and_beat_analyzer.py --music <track>` → `analysis/beats.json` and `audio_summary.md`.
5. The footage is imported into Premiere bins, and odd frame rates are conformed by interpretation before anything is placed.
6. **Selects and motion**: `selects_score.py` ranks every clip's best one-second moments, and `motion_holds.py` finds static holds and pans.

### 7.4 Phase 2: the brief and the cut plan
Claude writes `brief.md` in full: the playbook, the idea, the hook, the references turned into measured targets, and the **treatment**. The treatment covers pace, the colour stages, the named effects and transitions on their beats, type and sound. A music montage also gets an **energy arc** and a **motion style**.

In `project.md` it proposes **3 hooks** (with a recommendation), the **EDL** (the shot list) and the estimated runtime. For VO and dialogue reels there's a **line table**, one row per spoken clause: `line | shot | what in the frame shows it`.

The EDL is saved as `analysis/edl_v1.json`, the single file that the storyboard, the preview, the checks and the Premiere build all read. Then Claude makes:
- a **storyboard** (`scripts/storyboard.py`): in, middle and out frame of every shot through its planned framing, with the Instagram UI bands shaded;
- an **offline preview** (`scripts/preview_edl.py`): the planned cut built straight off the camera files with the music or VO, in minutes, without Premiere;
- a **phone copy** of the preview (`scripts/encode_master.py --phone`).

The preview is in the camera's own colour, not the grade.

### ⏸ Checkpoint 1: brief and cut plan
You get a short summary (concept, hook, look, 4–6 signature moments, runtime, and anything Claude couldn't honour) plus the storyboard and the phone preview. **Say yes or give changes.** Notes on pace, picks or framing become a new EDL and preview (`edl_v1b.json`), still without touching Premiere.

### 7.5 Phase 3: the rough cut
- Claude works on a **duplicate sequence**, `Reel_<name>_v<round>`. Your original sequence is never edited.
- The sequence is **1080×1920** at the footage's most common frame rate.
- It assembles the approved EDL on V1/A1 and reframes each shot to 9:16. On vertical footage at least 80 % of the camera width stays visible.
- It writes the shot map (`analysis/map_v<N>.json`) and reads the timeline back to check there are no unintended gaps.
- It adds a one-frame Constant Power audio crossfade at every cut and saves.

### 7.6 Phase 4: colour
Strictly in this order (section 10):
1. primary correction per clip;
2. shot matching;
3. a creative look on V3, only if you picked one;
4. texture on V4, only if the brief has it.

Claude checks still frames by eye, then runs the camera check (`scripts/camera_fidelity.py`) against each shot's own camera file.

### 7.7 Phase 5: motion, effects, graphics, captions
The treatment is carried out beat by beat:
- moves on V1, and stabilisation for handheld moving shots;
- B-roll and time effects on V2;
- transitions where the brief plans them (a hard cut is the default);
- HyperFrames motion graphics as transparent ProRes 4444 on V5;
- captions on V5, inside the safe zone.

Phase 5b sends shots that need real slow motion, denoise or glow through **After Effects** by script (`scripts/ae_roundtrip.py`).

### 7.8 Phase 6: sound design and mix
- Sound effects go on A2 where the playbook allows them. Real recordings come first: your own, then CC0 sounds from Openverse (`scripts/sfx_fetch.py`), then the designed sets.
- Music goes on A3: ducked under speech, or leading the mix in a music montage.
- Dialogue goes on A1.

Levels are in section 8 and section 12.

### 7.9 Phase 7: quality checks and export
1. Claude exports a **ProRes 422 master**, then encodes the deliverables from it with `scripts/encode_master.py`: H.264 High at about 18 Mb/s, plus a phone review copy of 29 MB or less.
2. It checks the audio straight away.
3. It verifies the file with `scripts/verify_render.py`: codec, size, frame rate, bitrate, colour tags, black or frozen frames, and loudness (−14 LUFS, −1 dBTP).
4. It compares the cut with the reference (`teardown.py --ours`).

### 7.10 Phase 7b: the review gate
Before you see any cut, **a reviewer on a different model** watches it, and the editor never grades its own work:
1. `scripts/pregate.py` runs the scripted checks in minutes: the file check, an every-frame defect scan, a camera-shake audit, a picture-quality probe against your saved references, the camera check, a sound-effect sync check, what changed since the last version, and review sheets.
2. The `reel-reviewer` agent judges the cut blind against the brief.
3. Claude fixes or answers every blocker and major, then reruns the gate (at most two loops, plus one focused check of the last fixes).

Details are in section 14.

### ⏸ Checkpoint 2: review the cut
You get the export, the runtime, a 3-line summary and the review verdict. **Watch it full-screen on your phone with sound.** Claude asks one question before taking approval: *"What would make it more cinematic?"* Notes start a new round (section 16).

### 7.11 Phase 8: the Instagram package
After final approval, Claude writes:
- 3 first-line hooks (under 125 characters);
- the caption: the hook in its first 125 characters, plain search words, one concrete call to action, credits, and an AI credit line, humanised;
- at most 5 hashtags, all on the reel's real subject;
- the AI-info label (on only if the reel contains an AI-generated shot);
- alt text, location and the cover timecode.

The caption goes to `deliver/caption.txt`.

### ⏸ Checkpoint 3: approve the package
Posting happens only when you ask for it. Claude can prepare the post on your phone through iPhone Mirroring, but **you tap Share**.

### 7.12 Phase 9: the retro (pilot reels)
Claude fills in `retro.md` from the friction log, copies it to `studio/retros/`, files a change request for each "change the studio" item, and tells you to run `/studio-hq` to apply them.

---

## 8. The 9:16 track layout

Every reel uses the same tracks. The sequence is **1080×1920** at the footage's most common frame rate (25 fps footage gives a 25 fps sequence; never 25 fps footage on a 30 fps timeline). Odd clips are conformed by interpretation (`set_override_frame_rate`), not by speed change.

| Track | Content | Rules |
|---|---|---|
| **V5** | Captions and kinetic type | Above the grade, so text stays clean. 2–4 words a line. Safe zone: clear of the top 220 px, bottom 320 px and right 120 px |
| **V4** | Texture overlays | Grain, light leaks, burns, with a blend mode and opacity. Optional: never grain on night phone footage, 5 % or less otherwise |
| **V3** | Creative look adjustment layer | Only when you picked a look. Starts at 30 % intensity |
| **V2** | B-roll and graphics | Primary-corrected. Cutaways on visual nouns and emotional shifts. Time effects |
| **V1** | A-roll: the talking head or hero action | Primary-corrected, reframed to 9:16, pushes and punch-ins |
| **A1** | Dialogue (natural sound in a music montage) | Crossfade at every cut. Peaks −6 to −3 dB. Montage: muted or −20 dB or quieter |
| **A2** | Sound effects | −14 to −18 dB |
| **A3** | Music | −8 dB in gaps, ducked to −18…−22 dB under speech. Montage: leads, peaks −1 to −3 dB, no ducking |

---

## 9. Editorial rules

**Every reel**
- **The 3-second hook.** 0–3 s pairs the strongest moment with immediate motion: a push-in, flash B-roll, or a title card with a riser.
- **Length**: 30–45 s unless the brief says otherwise. Every proposal states the actual runtime.
- **No assembly without a yes.** The EDL and hook are proposed first.

**Talking-head (speech drives the timing)**
- The hook is the strongest line in the transcript.
- **Dead air over 0.25 s, false starts, fillers and repeated takes are cut.** The default is the last, most confident take.
- **J-cuts**: audio leads video by 2–4 frames on scene changes.
- **Every cut lands on a word boundary**, placed by the waveform 0–2 frames before the speech starts, because Whisper's word starts can run early.

**Music-montage (the music drives the timing)**
- **The beat grid comes first.** Cuts land on beats: section changes and hero shots on accents or every 4th beat, fast sections on every beat or every 2nd beat.
- **Shot length follows the music's energy**, never one shot per bar for the whole reel.
- **The best moment of each clip**, not the whole clip.
- **Titles and kinetic type replace captions**: few words, timed to the beat.
- **Music must be licensed.** If you'll add Instagram library audio at upload instead, the cut is made to a guide copy of that exact audio. The studio then delivers `_mix` (guide baked in, archive only) and `_IG` (guide muted, for upload).

---

## 10. Colour

Colour runs in stages, always in this order. The full recipes are in `effects-playbook.md` §A.

- **A0, the default: camera-true.** Each shot is corrected toward its own camera file, not toward fixed numbers: fix casts, blown or crushed areas and dark night exposure, then stop. `scripts/camera_fidelity.py` judges the result shot by shot against the camera frame.
- **A1, primary correction** on each clip. Premiere's `color_correct` tool is called exactly once per clip, for contrast, temperature and tint only. Exposure, highlights, shadows and saturation are then set by script on that same Lumetri, because the tool ignores them and its saturation setting turns the clip black and white.
- **A2, shot matching** between neighbouring shots, within each shot's camera limits.
- **A3, a creative look**, only if you picked one. It goes on an adjustment layer on V3, never on the clips. You create that layer with one manual click, because Premiere has no scripting API for adjustment layers. Looks with a built-in preset are applied by script; most film looks are picked from the Lumetri Look dropdown by you. `scripts/look_preview.py` shows the looks on your own stills before you choose.
- **A4, texture**: grain or leaks on V4, only if the brief has them.

---

## 11. Motion, effects, transitions and type

- **Restraint first** (playbook §0): every designed move is an entry on the brief's **effect list**, which you approve. Default none; two or fewer is the guide.
- **Motion on V1** (playbook §B): gentle pushes on held shots. Punch-ins and snap zooms only from the effect list, never on night footage, where a crop multiplies the noise. Shakes and snap zooms read as jumps on handheld footage. Claude picks the steadier take first and uses Warp Stabilizer only on shots that still shake, re-measured with `scripts/shake_report.py`.
- **Time** (§C): real speed by default. Real slow motion comes from footage shot at twice the sequence rate. Synthetic slow motion from 30 fps or slower (After Effects Timewarp) only when you pick it on a phone sample of that shot: it ghosted or smeared in 6 of 7 reels.
- **Transitions** (§D): the hard cut is the default. Other transitions go only where the brief places them.
- **Type and graphics** (§E): HyperFrames compositions rendered as 1080×1920 transparent ProRes 4444 and placed on V5. `scripts/text_behind.py` puts a word behind the subject, on held shots only. Story devices: `scripts/step_print.py` for a step-printed stutter, `scripts/photo_prints.py` for photo-print inserts.
- **After Effects** (`after-effects.md`): denoise, speed-ramp curves, Timewarp and glow, run by script through `scripts/ae_roundtrip.py` and swapped in at the same timeline position.

---

## 12. Sound design

Sound effects go on A2, only where the reel's playbook allows them. The menu is in `effects-playbook.md` §F.

**Where sounds come from**, in order:
1. your own recordings from the shoot;
2. **Openverse** CC0 or public-domain recordings: `scripts/sfx_fetch.py search|get|keep|credits` finds them, ranks them by listening with earshot, and keeps each pick with its licence sidecar in `assets/sfx/openverse/`;
3. the designed sets: the Gemini starter pack and earshot's code-made set (`scripts/earshot_bank.py` → `assets/sfx/earshot/`).

**Placing them.** `scripts/sfx_prep.py` trims leading silence and peaks each sound at −3 dBFS. Each placed sound is listed in the EDL's `audio` list, so the pregate's `scripts/sfx_sync.py` can find it in the export and check it's present, on its frame and audible above the music.

**Credits.** CC BY credits go in `project.md` and in the Instagram caption. A sound new to the studio goes to you as an A/B before a reel relies on it.

**Levels**: SFX at −14 to −18 dB (cinematic-montage swishes at about −13 dB). Music follows section 8.

---

## 13. AI-generated shots

AI video is the **last step** of the bad-footage ladder, for shots the footage can't provide. The rules are in `.claude/skills/cinematic-reel/motion-and-ai.md` §3:

- **Stills only go out**: a first and/or last frame is uploaded, never one of your clips.
- **Every AI shot is labelled "AI-generated" in the brief** and approved shot by shot at Checkpoint 1. Every paid run needs your yes, and AI footage is never used as proof.
- **OpenRouter** (`scripts/gen_video.py`, Google Veo 3.1 Lite or Gemini Omni, no audio): about $0.12 for a Veo draft, then about $0.40 for the final. Caps: $4 and 4 shots a reel, $20 a month (`studio/ai-budget.json`). Each paid call is logged to `studio/ledger/ai-spend.jsonl`, which stays local.
- **Higgsfield MCP** (optional): every call asks you first (`.claude/hooks/ask_paid_ai.py`). Caps: 90 credits a reel and 450 a month, logged in `studio/ledger/higgsfield-credits.jsonl`.
- **Prompts describe the scene ungraded** (`film-emulation-prompts` skill), so the reel's look isn't applied twice. Each shot is conformed to the footage with `scripts/conform_clip.py` and graded in Premiere like every other clip.

---

## 14. Quality checks, the review gate and delivery

**Verify by render, never by the tool's reply.** Many Premiere tools report success without doing the work. After every colour, transition, opacity, blend or audio change, Claude exports a still or checks the audio and confirms the change by numbers and by eye.

**The pregate** (`scripts/pregate.py`) runs before every review:
- `verify_render.py`: codec, H.264 High, 1080×1920, fps, bitrate of 12 Mb/s or more, TV-range 4:2:0, BT.709 tags, black or frozen frames, −14 LUFS / −1 dBTP;
- `frame_scan.py`: every frame, with typed `--designed` spans that allow only their own flags;
- `motion_audit.py`: camera shake per shot; a step-print that jumps more than 4 px fails;
- `quality_probe.py`: each shot's grain, busyness, flicker and cadence against the director's saved references (`studio/reference-targets.json`). Grain above the line fails; the rest get a full-rate strip;
- `camera_fidelity.py`: each shot against its camera file;
- `sfx_sync.py`: every placed sound found in the export;
- `render_diff.py`: what changed since the last reviewed version;
- 2 fps review sheets, plus full-rate strips of the hook, the designed spans, every shot marked REVIEW and every quality WARN.

**After posting**, Claude checks the reel as Instagram serves it (`instagram-served-check.md`): the encode tier, resolution, bitrate, and the detail kept against the export. A small account's reels get Instagram's basic encode: Kolkata got 720p H.264 baseline at 1.4 Mb/s. So the export has to be clean enough to survive it.

**The reviewer** (`.claude/agents/reel-reviewer.md`) runs on a model other than the editor's. It does a full review for a new cut, and a focused review of the changed shots for a fix version. It judges blind: it gets no QA conclusions from the editor. A REVIEW shot is cleared only by the reviewer's verdict on its strip. The report is saved unedited as `analysis/review_v<N>.md`, and every blocker and major is answered as fixed, intended or disputed with evidence.

**Delivery files** (in `projects/<reel>/renders/`):

| File | What it's for |
|---|---|
| `masters/<name>_v<N>_master.mov` | ProRes 422 master from Premiere |
| `exports/<name>_v<N>.mp4` | H.264 High deliverable, about 18 Mb/s |
| `previews/<name>_v<N>_phone.mp4` | Review copy for your phone, 29 MB or less |
| `exports/<name>_v<N>_IG.mp4` | Upload version with the guide audio muted, when you add Instagram audio in the app |

---

## 15. The Instagram package and posting

The rules are in `.claude/skills/cinematic-reel/instagram-strategy.md`; where they disagree with the Instagram skills, they win:
- the hook in the caption's first 125 characters, and the subject named in plain search words;
- one concrete "send this to…" call to action;
- at most 5 topical hashtags, with no tool or brand tags;
- one detailed AI credit line (what AI did; the footage and direction are yours);
- the AI info label on only for reels with an AI-generated shot.

**Posting** goes through the Instagram app, for its music library. Claude can prepare the post through iPhone Mirroring when you ask (`ig-posting-reality.md`), but you make the reuse and Photos-access choices and **you tap Share**. A scheduled post can't have its video swapped. To change the video, delete the scheduled post and set it up again with the new file.

---

## 16. Giving notes and working in rounds

**Specific notes work best**:
- "Open on the line about waking up at 5am."
- "Faster, about 2 s per shot."
- "Less grain."
- "Bold yellow captions, 3 words max."
- "Cut the part about protein shakes."
- "Make the ending feel like [reference]."

**How a round works**
- Each round is a **new sequence version** (`Reel_<name>_v2`, `_v3`…). Approved sections aren't re-cut unless you ask.
- Claude replies with a **numbered list of changes mapped 1:1 to your notes**, plus anything it couldn't do and why.
- **Pace, picks or framing** notes go through a new EDL and offline preview first.
- **Grade** notes get a camera | now | proposed comparison, and a 6 s phone sample of the hardest shots, before any Lumetri change.
- `project.md` keeps a `## Now` block at the top: status, the locked sequence, the latest export, the decisions, the open questions and the next step. A new session can pick up cold.
- When you give a reference ("like this creator's reels"), Claude turns it into measured parameters (cut rate, caption style, grade, music energy) and confirms them before cutting.

---

## 17. Tools reference

Run Python tools with the studio's environment: `./.venv/bin/python scripts/<tool>.py --help`.

**Setting up a reel**

| Tool | What it does |
|---|---|
| `new_reel.sh <name>` | Creates a reel folder from the template |
| `link_footage.sh <name> <folder>` | Links footage that lives elsewhere, without copying |
| `ingest_report.py` | What the camera recorded: codec, bit depth, fps, VFR, white balance, shutter, ISO, flicker, dropped-frame jumps, shoot groups |
| `cine_bake.py` (+ `cine_bake.swift`) | Bakes Apple Cinematic-mode depth of field into ProRes for the spans an EDL uses |
| `media_info.py` | Shared ffprobe helpers |

**Analysis and planning**

| Tool | What it does |
|---|---|
| `analyze_footage.py` | Contact sheets and per-clip exposure, white balance, saturation and fps; reference pacing with `--reference` |
| `teardown.py` | Measures a reference and your cut the same way (pacing, motion, picture, loudness) and writes `COMPARE.md` |
| `selects_score.py` | Scores every 1 s window and shortlists each clip's best moments |
| `motion_holds.py` | Finds static holds and pans in every clip |
| `pick_sheet.py` | 6 frames per clip with camera times, for picking shots by what they show |
| `gemini_audio_and_beat_analyzer.py` | Beat grid, accents, sections and loudness of a music track |
| `transcribe_reel.sh`, `transcribe_local.py` | Word-level transcripts with local Whisper (ElevenLabs Scribe with `--scribe`) |
| `storyboard.py` | Storyboard from an EDL: in / mid / out frames through the framing, with the Instagram UI bands |
| `preview_edl.py` | Offline preview of the cut straight off the camera files, no Premiere |
| `look_preview.py` | Premiere's film looks on your stills, for choosing a look |

**Effects, graphics and sound**

| Tool | What it does |
|---|---|
| `render_type_cards.py` | Kinetic-type word cards as transparent 1080×1920 PNGs |
| `text_behind.py` | A word behind the subject of a held shot |
| `step_print.py` | Step-printed stutter render |
| `photo_prints.py` | Photo-print inserts on paper |
| `conform_clip.py` | Makes an outside clip (AI, stock) or a still reel-ready: frame rate, 1080×1920, colour matched to the footage |
| `gen_video.py` | AI-generated shot through OpenRouter, within the caps, logged to the ledger |
| `ae_bridge.py`, `ae_roundtrip.py` | After Effects by script: Timewarp, denoise, ramps, glow |
| `sfx_fetch.py` | Finds, ranks and keeps CC0 sound effects from Openverse, with credits |
| `sfx_prep.py` | Trims and normalises sound effects |
| `earshot_util.py`, `earshot_bank.py` | Runs earshot; renders the studio's code-made sound set |
| `mix_from_edl.py` | Rebuilds a reel's audio mix with ffmpeg when Premiere's export is silent |
| `gemini_generate_starter_pack.py` | Generates the starter LUTs, sound effects and grain |

**Checking and delivering**

| Tool | What it does |
|---|---|
| `colour_report.py` | Per-shot colour QA on every frame (gold hue, shot-to-shot jumps) |
| `camera_fidelity.py` | Each shot of a render against its own camera file |
| `shake_report.py` | Per-shot camera shake, before and after stabilisation |
| `frame_scan.py` | Every-frame scan for short defects |
| `motion_audit.py` | Shake, jerk, jumps and step-print holds per shot |
| `sfx_sync.py` | Finds every placed sound effect in the export's audio |
| `render_diff.py` | What changed between two renders |
| `watch.py` | Watches a video without playing it: 2 fps contact sheets with the waveform |
| `cut_view.sh` | Filmstrip and waveform for a time range |
| `pregate.py` | Runs all the scripted checks before the review gate |
| `quality_probe.py` | Per-shot grain, busyness, flicker and cadence against the director's saved references |
| `verify_render.py` | Final file check (codec, size, fps, bitrate, colour tags, loudness) |
| `encode_master.py` | ProRes master → H.264 High deliverables and the phone copy |

**Studio maintenance**

| Tool | What it does |
|---|---|
| `check_tool_names.sh` | Checks that every Premiere MCP tool name the rules mention exists in the installed server |
| `build_guide_pdf.py` | Rebuilds `docs/GUIDE.pdf` and `docs/shooting-guide.pdf` from their Markdown |

---

## 18. Working with Premiere through MCP

The bridge is the `premiere-pro` MCP server (npm `adobe-premiere-pro-mcp`). With `PREMIERE_MCP_TOOLSET=full` (set in `.mcp.json`), all of its roughly 280 tools are listed. What's broken on this Premiere and MCP version, and the verified workarounds, is in `.claude/skills/cinematic-reel/premiere-mcp-reality.md`. The rules that matter most:

1. **Verify the bridge first** (`verify_premiere_connection`). Nothing changes until Premiere reports connected.
2. **Verify by render, not by the tool's reply.** For example, `add_transition` can land one cut off, `apply_lut` reports success and loads nothing, and `set_clip_volume` can silence a clip.
3. **Read script results through a file.** `execute_extendscript` returns `"undefined"`, so scripts write their results to a file.
4. **Duplicate before mutating.** The director's original sequence is the rollback point.
5. **Read back after structural edits** (razor, ripple delete, trim, speed): edits can be quantised to frames or quietly rejected.
6. **Effects can't be removed by script**, so they're planned before they're applied: one `color_correct` per clip, looks only on V3.
7. **Open a duplicated sequence in the timeline** before QE-based tools can reach it.
8. **Save checkpoints** after each approved phase.

---

## 19. Changing the studio itself

Run `/studio-hq` in one session to work on the architecture. HQ:
1. reads `studio/VERSION`, the latest `CHANGELOG.md` entry and `BACKLOG.md`, then surveys open change requests, new retros and reel status;
2. traces every change to evidence: a CR, a retro, a director request, or something it verified;
3. makes the smallest edit, in the file that owns the rule:

   | What | Where |
   |---|---|
   | Studio-wide rule | `CLAUDE.md` |
   | Workflow step | `.claude/skills/cinematic-reel/SKILL.md` |
   | Effect recipe | `effects-playbook.md` |
   | Tooling | `scripts/` |
   | New reels' files | `projects/_template/` |
   | Enforcement | `.claude/hooks/` |

4. tests what can be tested on real footage;
5. versions it with semver:
   - **major**: a reel in progress must change how it works, and needs the director's OK;
   - **minor**: a new capability, rule or reel type;
   - **patch**: a fix or clarification.

   Every version gets a dated `CHANGELOG.md` entry, and the CR's status is updated.

A reel records the version it started on. It picks up minor and patch changes at its next round.

**Change requests** are named `studio/change-requests/CR-<YYYYMMDD>-<reel>-<slug>.md` and made from `_TEMPLATE.md`. Each gets one of three outcomes: accepted (`done vX.Y.Z`), deferred (to `BACKLOG.md`) or rejected (with the reason).

---

## 20. Troubleshooting

| Problem | Fix |
|---|---|
| "Premiere not connected" | Premiere must be open with a project loaded, and the CEP panel must show the bridge started (Temp Directory `/tmp/premiere-mcp-bridge`). Still failing: right-click the panel → **Reload** |
| Health check | `premiere-pro-mcp --doctor` |
| `npm` permission errors (EACCES) installing the MCP server | Move npm's global prefix to your home folder (`npm config set prefix ~/.npm-global` and add `~/.npm-global/bin` to PATH), then re-run `setup.sh` |
| The Claude app can't find `premiere-pro-mcp` | GUI apps don't see your shell PATH. Link it where they look, e.g. `ln -s "$(which premiere-pro-mcp)" /opt/homebrew/bin/` |
| No transcript | `scripts/transcribe_reel.sh <reel>` (the first run downloads the Whisper model, about 0.5 GB). For an external voiceover, name the file |
| Export has no sound | Check with `ffmpeg -i <file> -af volumedetect -f null -` (max_volume should be above −20 dB). Rebuild the mix with `scripts/mix_from_edl.py` |
| Colour change "worked" but nothing changed | Expected with some tools: check by exported still (section 18) and follow the reality doc's fallback |
| `earshot` not found | It installs to `~/.local/bin`, which may not be on PATH. The studio's scripts find it there; or set `EARSHOT_BIN` |
| Hooks don't run | Restart Claude in the repo root so `.claude/settings.json` loads |

---

## 21. Glossary

| Term | Meaning |
|---|---|
| **A-roll / B-roll** | The main footage (talking head, hero action) / cutaways |
| **Brief** | `brief.md`: the approved plan for a reel, written by Claude, binding once approved |
| **Camera-true** | The default grade: each shot corrected toward its own camera file, no creative look |
| **CR** | Change request from a reel session to HQ |
| **EDL** | Edit decision list: the shot list, as `analysis/edl_v<N>.json` |
| **Guide audio** | A copy of Instagram audio used to cut to, muted in the upload version |
| **HQ** | The one session that owns the studio's architecture (`/studio-hq`) |
| **J-cut** | The next shot's audio starts a few frames before its picture |
| **MCP** | Model Context Protocol: how Claude drives Premiere |
| **Playbook** | A kind of video's style rules (`playbooks/`) |
| **Pregate** | The scripted checks before the review gate |
| **Review gate** | The independent review on a different model before you see a cut |
| **Shot map** | `analysis/map_v<N>.json`: each shot's reel time and camera source |
| **Treatment** | The brief's plan for pace, colour, effects, type and sound |

---

## 22. Credits and licences

The studio's own code and docs are under the MIT licence (`LICENSE`). It builds on:
- **Adobe Premiere Pro MCP** by hetpatel-11 (`adobe-premiere-pro-mcp`), the Premiere bridge;
- **video-use** by browser-use, for cut inspection and the Scribe helper;
- **HyperFrames** by HeyGen, for motion graphics;
- **earshot** by Leonxlnx (MIT), sound ranking and the code-made sound set, pinned in `scripts/earshot_util.py`;
- **faster-whisper**, for local transcripts;
- **Openverse**, for openly licensed sound effects (each keeps its own licence and credit);
- **Instagram skills** by sergebulaev;
- **ffmpeg**;
- the studio forks of `ffmpeg-color-grading-chromakey` and `color_grading_film_emulation` (MIT, licences in their folders).

Each is installed by `setup.sh` from its own source and keeps its own licence. None of the director's footage, music or other media is in this repository.

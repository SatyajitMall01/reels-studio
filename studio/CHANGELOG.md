# Studio Changelog

## 0.12.1 — 2026-11-15
**Night shots keep the camera's exposure; the black point takes near-black to black** (patch, safe mid-reel: a reel picks it up at its next grade round. Nothing already exported changes).

**Why.** The director sent three references with "learn" (`studio/reviews/reference-study-2026-11-15-composition-and-graphics.md`). The night one keeps deep blacks around bright lights and reads clean, while our default grade brightened dark night shots. The director said "yes, test it".
- **Test.** Three Goddess night shots, the same camera frames rendered three ways:
  - A, the posted lift (+0.9 to +2.0 stops, Shadows up to +45, emulated);
  - B, the camera as recorded;
  - C, camera tones with near-black taken to black.

  Each went through an export encode and an Instagram-like VP9 encode at 3 Mb/s, and was measured in the same flat dark areas.
- **Results:**
  - A raised dark-area grain ×1.08 / ×1.24 / ×3.4 and boil ×1.04 / ×1.42 / ×4.3 against the camera, more after the Instagram-like encode (boil up to ×4.9);
  - C cut the boil ×0.2–0.6 where the shadows went black;
  - A also turned C027's black sky muddy olive.
- **The director picked C on the phone.**

**What changed:**
- **effects-playbook §A0 / §A1.** Night shots (camera mean below 0.25) aren't brightened:
  - keep the camera's exposure;
  - Blacks down until what the camera recorded near-black (< 0.07) goes black;
  - Basic Saturation about 90, because a black point raises saturation (×1.09–1.21 measured; at 90, C027 and C044 match the camera);
  - protect the lights.

  A night shot too dark to read without a big lift is dropped or reshot, not lifted. Day shots keep the old rule: lift only until burn starts.
- **`scripts/camera_fidelity.py`:**
  - **luma:** a night shot lifted more than 0.03 over its camera WARNs ("a lift multiplies the grain"); darkening that near-black going black explains is allowed;
  - **crushed:** FAILs only above what the camera recorded near-black, + 2 points. Before, it counted any pixel under 0.03 against the camera's own, which failed untouched camera frames on night shots (C027 21.5 → 25.8 %, C017 71.2 → 73.9 %);
  - **saturation:** measured on camera tones above 0.15.
  - Tested on the nine test renders:
    - B (camera) PASSes on C027 and C044, and WARNs on C017 (saturation ×1.06);
    - A WARNs as a lifted night shot (and FAILs on the emulation's burnt lights and hue);
    - C with Saturation 90 PASSes on C027 and C044, and WARNs on C017 (saturation ×1.09).
- **Docs:** reel-reviewer (night blacks are intended; a lifted night shot is checked for grain), GUIDE §A0 and the shooting tip, and the shooting guide ("expose so the subject reads": the edit won't brighten a night shot).
- **Test tools:** `projects/_hqtest/tools/nightgrade_*.py`, results in `nightgrade_results_2026-11-15.json`.

**Limits:**
- A is an emulation of Lumetri, not a Premiere render.
- The Blacks setting that gives a 3.5 % black point in Lumetri isn't measured yet. The first reel graded under this sets it by render, against `camera_fidelity`, and reports it.

## 0.12.0 — 2026-11-15
**Restraint by default, a per-shot quality probe against the director's saved references, a shooting guide built on what the footage needs, and a post-upload check of what Instagram actually serves** (minor: reels in progress pick it up at their next round, CLAUDE.md §0.1).

**Why.** The director: "The videos are glitchy, the light flickers, the video flickers here and there, the edit looks off, and everything looks unnatural and grainy." HQ measured the evidence in `studio/reviews/quality-diagnosis-2026-11-15.md`:
- the 30 reels in the director's Instagram "Reel Concepts" collection and the 4 studio reels on their Reels tab, as Instagram serves them;
- the 6 local finals, 7 local references and sample camera files;
- the review history of all 7 reels.

**Findings:**
- **Noise.** The references sit at a temporal noise of 0.08 (median). Pujo is at 0.49 and Goddess at 0.38: noisier than 29 and 27 of the 30. A later recheck of all 487 camera clips, on still frames only, put them at 0.23–0.51 by ISO (3–6× the references), with a 2× crop adding about 1.3–1.4×. The first figures (0.4–0.9, crops up to 12×) had read camera motion as noise. `quality_probe.py` now measures noise on still frames only. The same recheck found the camera settings off: only 72 clips at 1/50 s, auto exposure on three nights, Oct 15 recorded in HD at 13 Mb/s, and a median camera motion of 6.4 against the references' 1.8 (shooting guide updated).
- **Motion.** The references sit at 1.8. Pujo is at 8.3 and Goddess at 6.1, busier than 29 of the 30.
- **Shape.** 23 of the 30 references are horizontal frames.
- **Treatment.** Synthetic slow motion ghosted or smeared in 6 of 7 reels. A step-print on handheld footage read as glitchy. Stacked grain, sharpen, denoise and AI upscaling were called over-processed.
- **Flicker** came from 30 fps at a 1/60 s shutter under 50 Hz lamps, which post-production couldn't fully remove.
- **Instagram's encode.** Instagram serves a small account's reels with its basic encode: Goddess and Pujo as VP9 basic 1080p at 2.8–3.2 Mb/s (83–95 % of the export's detail), Kolkata as only H.264 baseline 720p at 1.39 Mb/s, with +20–28 % 8×8 blocking. Most references get the advanced q20–q90 ladder.

**What changed:**
- **Restraint by default** (CLAUDE.md intro and §3; effects-playbook new **§0**, §A0, §A4, §B, §C, §D; SKILL.md Phases 2, 5, 5b; the cinematic-montage, story-montage and creator-explainer playbooks; `projects/_template/brief.md`):
  - real speed, hard cuts, a still or steady camera;
  - every designed move goes on the brief's new **effect list**, which the director approves. Default none, two or fewer is the guide;
  - no synthetic slow motion unless the director picks it on a phone sample;
  - Warp only on shots that still shake after picking the steady take;
  - no crop-in or punch-in on night or noisy footage, and the 16:9 film frame offered first for landscape footage;
  - no grain on footage that already shows noise, and no sharpening, clarity or AI upscaling unless picked;
  - denoise decided once, never stacked.
- **`scripts/quality_probe.py`** (new; run by `pregate.py` as check 2c). For every shot it measures temporal noise, motion, flicker (RMS and peak) and cadence (repeated frames, jumps), against `studio/reference-targets.json` (new: the Reel Concepts medians and provisional thresholds).
  - Noise above 0.50 fails. `--allow-noise <shot>` is only for a shot the director accepted.
  - Noise above 0.30, motion above 4.3, a flicker pulse above 2 levels, or a repeat or jump inside a shot each give a WARN plus a full-rate strip for the reviewer.
  - `--whole` measures a camera clip, to tell whether a source is already noisy.
  - Tested: Diwali v10d, 18 shots, PASS (noise 0.037). Goddess v10b FAILs (0.63, motion 6.3). A Goddess camera clip FAILs (0.52), so its noise comes from the shoot.
- **Shooting guide:**
  - the shutter, not the frame rate, stops lamp flicker;
  - 30 fps at 1/50 s marked for a test night, because 25 fps doesn't divide the iPhone's 120 Hz;
  - slow motion at 2× the night's rate at 1/100 s;
  - landscape for horizontal-frame reels;
  - ISO ≤ 800 at night, and the 26 mm lens at night;
  - frame each shot as it will be used (no crop-in later);
  - hold still, and never zoom while recording.
- **`instagram-served-check.md`** (new, skill folder), plus a Phase 8 step. After posting, record:
  - Instagram's encode tier, served resolution and bitrate;
  - the detail kept against the export, using read-only snippets in Claude in Chrome;
  - **that the audio plays**, by the director's ear.

  Before Share, check that "Upload at highest quality" is on. The phone check (iPhone Mirroring) found:
  - "Upload at highest quality" on, and "Use less mobile data" off;
  - views of 127–501 per reel;
  - Goddess's sound bar reading "Audio unavailable". HQ first took that to mean silence. The director unmuted it and the voiceover plays, so the label is now recorded as not evidence.
- **Director profile** (local): the Reel Concepts collection recorded as the target look. Slow motion off unless picked, or shot at 2×. Stabilise only what still shakes.
- **Docs:** GUIDE.md (§1, shooting, §11, pregate, tools), ARCHITECTURE §2 (`studio/reviews/`, `studio/reference-targets.json`). The BACKLOG process and tools batches move to v0.13 and v0.14.

**Reels in flight:**
- my-reel (build), and Pujo and Goddess (packaging) pick this up at their next round.
- Nothing already exported changes.
- The probe's thresholds are provisional, from 6 reels. HQ recalibrates them after the first reel cut under v0.12.

## 0.11.1 — 2026-11-14
**Public GitHub repo: a clean layout, a complete guide with PDFs, and nothing personal or copyrighted in git** (patch, safe mid-reel: no workflow rule changed; reel sessions see only that their media stays out of git, as before). The director asked for the repo on GitHub with a clean structure and enough guides, and chose a public repo, reel text and code only, MIT, every branch pushed, and history rewritten so the personal files leave it.
- **`.gitignore` rebuilt for a public repo.** Reel folders keep only text and code (`.md .py .sh .swift .jsx .html .json .txt`), minus their `audio/ music/ sfx/ grade/ stock/ renders/ transcripts/ .hyperframes/ assets/` folders and the Real-ESRGAN binaries. Before this, `git add -A` would have added 601 files and 1.1 GB, including commercial songs, audio from reference reels, the director's voice takes, posted reels and lyric transcripts. Now it's 371 files, 3.3 MB.
- **Personal files are local only**:
  - `studio/director-profile.md` is git-ignored, with a blank `studio/director-profile.example.md` that `setup.sh` copies into place;
  - `studio/ledger/*.jsonl` is git-ignored, with `studio/ledger/README.md` explaining both logs (`gen_video.py` already creates its ledger on first use);
  - the three files were removed from every commit on every branch with `git filter-branch`. A full bundle of the old history was saved first.
- **Set aside, not pushed** (BACKLOG open decision): `scripts/gemini_ig_studio_cli.py` (it publishes to Instagram directly), `scripts/gemini_setup_premiere_mcp.sh` and `GEMINI_IG_STUDIO_INTEGRATION.md` stay on the Mac, git-ignored. `GEMINI_ARCHITECTURE_REVIEW.md` moved to `studio/reviews/gemini-architecture-review-2026-10-15.md`, and BACKLOG points there.
- **The complete guide**: `docs/GUIDE.md` (22 sections, from install to a posted reel), built from CLAUDE.md, the skill, ARCHITECTURE and the review gate, plus `docs/GUIDE.pdf` (19 pages) and `docs/shooting-guide.pdf`.
  - `scripts/build_guide_pdf.py` rebuilds the PDFs: markdown-it-py (CommonMark and tables, so lists and code render as on GitHub), then headless Chrome with a throwaway profile, on A4 with page numbers.
  - `setup.sh` installs `markdown-it-py` into `.venv`.
- **README rewritten for public readers**: what you need, setup, making a reel, layout, what's not in the repo, licence and credits. The long sections moved into the guide.
- **`LICENSE`: MIT.** Folders with their own licence keep it (the two forked skills).
- **ARCHITECTURE §2**: rows added for `docs/`, `LICENSE`, `.gitignore` and `studio/reviews/`, plus local-only notes on the profile, the ledger and reel media.
- **Personal paths**: 36 old per-reel scripts now use `$HOME` / `Path.home()` instead of `/Users/<name>`; every edited script passed `bash -n` / `py_compile`. Five lines keep the absolute path: four ExtendScript `var K` paths in old Premiere build scripts, which Premiere needs absolute, and one Adobe Fonts path.

## 0.11.0 — 2026-11-12
**Real sound effects, and the pregate checks every one in the export** (minor, safe mid-reel: sourcing is opt-in, and the new pregate step runs only when an EDL `--map` lists sound effects or `--sfx-cues` is given; Diwali's maps have none). The director picked "Openverse + earshot" after HQ checked three tools from a post (Openverse, Real SFX, earshot) at their source.
- **Openverse → `scripts/sfx_fetch.py`** (`search`, `get`, `keep`, `credits`).
  - Verified 2026-11-12: there's no key. Anonymous use allows 20 requests a minute, 200 a day and 240 results per search; responses are cached for 24 h.
  - `category=sound_effect` drops every Freesound result, so it isn't used.
  - Files are Freesound's 128 kb/s MP3 previews.
  - CC0 hits: whoosh 240, firecracker 155, temple bell 57.
  - Licences: CC0 / PDM by default; CC BY only on request, marked credit_required; BY-SA, NC, ND and Sampling+ refused.
  - `keep` writes a new WAV plus a licence sidecar into `assets/sfx/openverse/` and never overwrites.
  - Tested on "temple bell": 6 downloads, ranked by earshot (5 "strong"), a `find` trim, `keep`, its overwrite refusal, `sfx_prep`, `credits`.
- **earshot v0.4.1** (github.com/Leonxlnx/earshot, MIT, commit `4ac3d2a`, pinned in `scripts/earshot_util.py`). Reviewed before install:
  - it shells out only to ffmpeg/ffprobe;
  - its models (CLAP, Apache-2.0; AST, BSD-3) are pinned safetensors revisions;
  - the network is used only for that one model download;
  - Gemini upload exists only in the `llm` extra, which isn't installed.

  Installed with `uv tool` as a CLI at `~/.local/bin/earshot`, with 1.1 GB of models in `~/.cache/earshot`; `setup.sh` installs the same pin.
- **earshot set → `scripts/earshot_bank.py`.** Nine code-made sounds in `assets/sfx/earshot/` (riser, sub hit, whip, swell, flick, shutter, pop, sub drop, reverse swell).
  - Seeds are fixed, so a re-render is byte-identical (checked by md5).
  - All nine are clean on earshot's audit. No recorded audio, so no credit.
  - The director has a 31 s A/B against the Gemini starter sounds. The Gemini column stays the default in effects-playbook §F until their verdict.
- **`scripts/sfx_sync.py` + pregate step 3b.** Every placed sound effect, from the EDL `audio` list or a cue sheet, is found in the export's own audio by its file's waveform: GCC-PHAT, with a local refinement for sub-bass.
  - Missing, or more than 2 frames off its plan: FAIL.
  - A weak match, a level outside −6…+9 dB of the plan, or masking in every band: WARN.
  - With earshot installed it also draws `sfx/sound_sheet.png` for the reviewer.
  - Validated on kolkata v6 / v6_3 and puja-night-2 v5c:
    - all 13 real placements were found on frame;
    - all 8 fakes were rejected (the same files at wrong times);
    - a 3-frame shift read −3.0 frames.
  - The masking line (−10 dB) has no ground truth yet.
- **Rejected, with the measurements:**
  - **earshot's own cue sync** for this job: in a music-led mix some onset is always near. It scored a cue with no sound effect "on frame" (puja), and on kolkata its hit rate equalled chance (0.333 vs 0.336).
  - **Real SFX (Clipwing):** it mixes outside Premiere into a new MP4, its 78 bundled sounds are UI clicks, and it needs `ffmpeg-full`.
- **Rules:**
  - effects-playbook §F gets "Where sounds come from" (the director's own, then Openverse, then the designed sets), both columns, and an "SFX in the EDL" line;
  - skill Phase 6;
  - CLAUDE.md §5;
  - review-gate.md and the reel-reviewer brief (the reviewer judges Sound from `SFX_SYNC.md` and the sheet);
  - README `assets/sfx/`.
- **Numbering:** the queued process and tools batches move to v0.12 and v0.13 (BACKLOG).
- **Next:** the director's A/B verdict, which decides §F's default column. The first reel that hears a buried effect logs its `sfx_sync` number in a CR, to set the masking line.

## 0.10.3 — 2026-11-11
**Higgsfield MCP connected, behind a director-only gate** (patch, safe mid-reel). The director asked to connect Higgsfield. On 2026-11-10 they planned to use it with Fable 5.2, "because those give better results".
- **`.mcp.json`:** Higgsfield's official server `https://mcp.higgsfield.ai/mcp`, over streamable HTTP. It signs in with OAuth through Higgsfield's Clerk login (`claude-code` is a listed client; probed: 401 plus protected-resource metadata). There's no API key. It needs a paid Higgsfield plan. Every session loads it on start, after the director signs in once with `/mcp`.
- **Guard:** `permissions.ask: ["mcp__higgsfield"]` in `.claude/settings.json`, plus a new PreToolUse hook `.claude/hooks/ask_paid_ai.py` (matcher `mcp__higgsfield__.*`) that returns `ask` with the tool and its input. Every Higgsfield call needs the director's yes, because every MCP generation spends credits on any plan and the ledger only counts OpenRouter dollars. Hook tested: it asks on a Higgsfield call, stays silent on other tools and on bad input.
- **Rule:** motion-and-ai.md §3 ("Higgsfield (MCP)"), with a pointer in CLAUDE.md §5. A reel uses it only when the brief names it.
- **Caps (director, 2026-11-11):** 90 credits per reel and 450 per calendar month for the whole studio, HQ tests included, on top of the OpenRouter dollar caps. The 4 shots and 24 s per reel count both providers together. Every job is appended to a new `studio/ledger/higgsfield-credits.jsonl`, seeded with the three test jobs (November so far: 119 of 450). Totals come from that file, not from Higgsfield's `transactions`, which also holds the director's own use.
- **Surveyed and priced** (2026-11-11, from a Fable 5.2 session, every call approved by the director, 0 credits spent):
  - about 140 tools;
  - 59 video models, 21 of which take a start + end frame;
  - balance 4,246 credits on `max`;
  - `get_cost: true` prices a job without submitting it.

  The price table is in motion-and-ai.md §3: Veo 3.1 Lite 6, Kling 3.0 pro 7, Omni 9 (720p) or 13 (1080p), Seedance 2.0 48, Cinema Studio 4.0 64 credits per 4 s.
- **C047 gap-fill test** (2026-11-11, 119 credits, director approved; balance 4246.49 → 4127.49). The same stills and prompt as the Omni test, run on Kling 3.0 pro (7), Seedance 2.0 (48) and Cinema Studio 4.0 (64). Each charge matched its `get_cost` price.
  - **Kling 3.0 pro landed closest to still B of any model tested:** 4.3 off at 4.00 s, against Omni's 6.9. Spliced into the real take, its seams measured 0.012 and 0.009, against the camera's 0.009. It invented a masked motorbike rider passing close, although the prompt and its "Avoid:" list already ruled that out, so the rule is to check every Kling draft and re-roll one that invents.
  - **Seedance 2.0 and Cinema Studio 4.0 don't hold the end frame.** Seedance ends on another view; Cinema Studio hard-cuts to another street at 2.54 s. Cinema Studio needs `mode: "omni_reference"` for stills (the 422 from `t2v` isn't charged).
  - The full table is in motion-and-ai.md §3.
- **Next:** the dollar value of a credit on the director's plan. The Higgsfield CLI and the `higgsfield-ai/skills` pack aren't installed: they're third-party, so that waits for the director's OK.

## 0.10.2 — 2026-11-11
**The review gate can't be talked past** (patch, safe mid-reel; blocker CR from could-not-go-home-diwali). The director asked "how certain glitchy videos are passing the review cut". Diwali v3b's opening step-print was made from a handheld shot inside a moving auto, so every held image jumped 6–21 px. It passed pregate and four reviews.

**Why it passed (each cause verified in the scripts):**
1. **The editor's own `--designed` spans excused every scan flag inside them.**
2. **The reviewer saw only 2 fps sheets.** It can't see an 8 Hz jerk, and it took the brief's "driver static" as a fact.
3. **The reel-local motion numbers had no limit,** so they decided nothing.
4. **No rule said what a step-print may be made from.**
5. **The checklist had no "is it cinematic?" line.**

**What changed:**
- **New `scripts/motion_audit.py`** (promoted from the reel's tool, made general). It measures camera shake per shot on the frame's **outer ring**, so a moving subject isn't counted (Diwali S1's hands), with `--window` for 4:3 and 4:5 reels.
  - **A step-print whose held images jump more than 4 px off the smooth path FAILs.**
  - **Camera jerk p95 above 6, or a jump above 8 px, marks the shot REVIEW.**

  On v3b: shot 01 FAILs (7.9 px), the reel's other step-print passes (0.3 px, a steady source), and shot 18 goes to REVIEW (jerk 7.9). The Diwali session had pulled shot 18's frames as a suspect too.
- **`pregate.py`:**
  - **typed designed spans** (`T0-T1:fade|end-card|title|step-print|flash|transition|freeze`). Each type allows only its own scan flags: v3b's blur flash inside the step-print now FAILs. An untyped span allows black only;
  - runs the motion audit;
  - writes **full-rate strips** (`strips/`, every frame at the sequence's rate, cropped to `--window`) of the hook, every designed span and every REVIEW shot.

  Tested on v3b in three ways: typed spans FAIL on shot 01; the old untyped call FAILs with a "type the span" hint; with shot 01 passed off as a title, it still lands in REVIEW, which the editor can't waive.
- **`watch.py`:** `--crop x,y,w,h`; at full rate it lands on each frame (it used to sample midway and slip into the next shot).
- **The reviewer (`reel-reviewer.md`):**
  - reads every strip and gives each one a verdict;
  - treats a designed span as the editor's intent to be judged, and **the brief as intent, not fact**;
  - gets a **Cinematic** line: steady motion, a sharp subject, clear intent, and an effect in the hook that reads as a fault is a major.

  `review-gate.md`: REVIEW shots can't be waived by the editor, and focused reviews still read the hook and designed-span strips.
- **Step-print source rule** (effects-playbook §C, story-montage): only from a smooth camera path (locked off, a steady pan, or ≤ 2 px residual shake), never random shake or the inside of a moving vehicle. Check the render's hold shift before placing it.
- **CLAUDE.md §5:** the pregate line names the motion audit and the strips.

Reels in flight: could-not-go-home-diwali, at its next gate. It must type its spans and pass `--window 0,505,1080,810`; shot 01 needs a steadier source or real-time playback.

## 0.10.1 — 2026-11-11
**First Veo vs Omni gap-fill test** (patch, safe mid-reel). The director approved both runs ($0.40). Both models got the same two stills, 4 s apart, from Diwali C047, and the real 4 s between them was the ground truth.

- **Veo 3.1 Lite** ($0.12):
  - smooth (biggest frame step 0.022, against the camera's 0.012);
  - but it invented traffic beside the auto, including a man on a motorbike with his face visible.
- **Gemini Omni** ($0.28):
  - kept the street close to the real one;
  - turned the driver's head into profile, which the prompt said to avoid;
  - popped at 3.36 s (a 9× frame step) snapping toward the last still.
- **Neither landed exactly on still B.**
- **Rule (`motion-and-ai.md` §3):** Veo Lite is the default for gap fills. Omni waits until its end snap is solved. Never cut straight from a gap-fill's last frame into the real shot.
- **`gen_video.py` fix:** Omni refused `generate_audio: false` (400, not charged), so models without a silent price now ask for the sound they bill, and `conform_clip.py` strips it.
- Files: `projects/_hqtest/renders/gen/cmp_c047_*` (both drafts, `side_by_side_phone.mp4`, the sheet and the numbers).
- **Round 2, Omni with the camera block** (1080p, 4 s, $0.42, the director asked):
  - no pop (biggest frame step 0.017, was 0.106), lands on still B, the driver faces forward, nothing invented near the camera;
  - best of the three, so it's the pick for gap fills (one test).
  - Spliced into the real C047 in place of 3–7 s (`cmp_c047_spliced_*`), after a sharpness match (it was 1.4× crisper, so `gblur` sigma 1.0), a saturation match (×1.14) and 3-frame seam dissolves. The seams measured 0.012 and 0.011, against the camera's 0.009, and the frame scan flags only the camera clip's own end.
  - `scripts/gap_fill.py` added to the v0.12 backlog.
- **Depth-aware clarity** (director: "the depth and clarity can be better enhanced"):
  - **`cine_bake --disparity-out F`** writes the phone's recorded depth map (Float16 512×288 per frame, plus focus per frame in `F.json`).
  - **The pass:** denoise, then sharpening and local contrast only on the focus plane. On C047, near-plane detail rose 31 % and near/far separation went from 1.69 to 2.36, with the bokeh unchanged.
  - **The AI fill:** its bokeh and near-plane detail were matched to the camera's, so its separation went from 1.18 to 2.30, against the real parts' 2.36. Seams 0.012 against a 0.009 frame step.
  - f/1.4 over f/2 gained little (2.42 against 2.36).
  - An image-only focus mask failed on night phone footage, so the depth map is needed.
  - Effects-playbook §B; `scripts/depth_clarity.py` added to the v0.12 backlog.
- **Cinematic at generation** (director: "add the cinematic effect while creating the video itself"). `film-emulation-prompts` gets a **camera block** that goes in every prompt:
  - shallow depth of field matched to the reel's bakes, naming what is sharp and what falls off;
  - an angle and height with a reason;
  - the lens;
  - one motivated, steady move (dolly, gimbal or tripod, so it intercuts with phone footage);
  - a foreground layer and natural motion blur.

  The colour stays ungraded, since Premiere's look would otherwise land twice. Gap fills keep the angle of their stills. The negative list adds deep focus, everything sharp, shaky camera and jerky motion. `motion-and-ai.md` §3 and the director profile now say the same.

## 0.10.0 — 2026-11-11
**AI shots as the last step of a bad-footage ladder** (minor: new capability and a policy change, safe mid-reel; reels pick it up at their next round). Decided with the director on 2026-11-10; plan in `studio/plans/ai-shots-plan.md`.

Why: the director wants AI video wherever stock doesn't fit or our own footage is bad, and asked for Claude Fable 5.2 to make it in-house.
- **Checked:** Fable 5.2 (`claude-fable-5-2`, released 2026-11-09) is "Text and images → text" on Anthropic's model page, and Anthropic has released no video generation, frame filling or stabilisation.
- **So:** Claude plans, prompts and checks each shot, and the frames still come from a paid video model.

**Policy (director, 2026-11-10):**
- AI is the last step of the **ladder**:
  1. fix locally for free: Warp, After Effects Pixel Motion for gaps under about 1 s, denoise, a crop within the width floor;
  2. another take;
  3. free stock;
  4. a code-built shot;
  5. a paid AI shot from stills.
- It **may show the subjects** (before: never), and is still never proof.
- **Stills only:** no clip is ever uploaded.
- **Caps $4, 4 shots and 24 s per reel; $20 a month** (before: $2, 2 shots, 16 s; $10).

**`gen_video.py`:**
- `--model omni` (Gemini Omni 1.2 Flash, 3–15 s). A first and a last still fill the frames between them.
- Omni has no silent price, so the estimate includes sound (4 s 720p draft $0.28, 8 s 1080p final $0.83). A negative prompt is written into the prompt for models that take none.
- Stills are checked against what the model accepts. The ledger records the stills and `sound_billed`, and the label names the model.
- **Removed:** `--provider google`. Its Veo `-preview` models on the Gemini API were shut down on 2026-10-22 (Google's video docs), so the route was dead. OpenRouter is the only provider. `.env.example` says `GEMINI_API_KEY` is unused.
- Verified by dry runs only (nothing spent):
  - Veo draft $0.12; Omni draft between two Diwali stills $0.28; Omni final $0.83;
  - a 5 s Veo duration and a missing still are refused.

**Other changes:**
- **Rules:** `motion-and-ai.md` §3 (the ladder, Omni, gap filling, no fallback, the widened policy); director profile; CLAUDE.md §5; SKILL Phase 2 (the AI row lists the ladder steps tried); `film-emulation-prompts` rule 1; the story-montage and cinematic-montage AI sections; `instagram-strategy.md` (say when a generated shot shows a person).
- **`reel-reviewer`:** AI-shot checks for finger counts, bending tools, a generated person's face or clothes drifting or not matching their real shots, gibberish text, details dropped from the anchor still, and gap-fills whose motion doesn't continue. Any of these on a generated subject is a major.
- **`studio/ai-budget.json`:** new caps and policy text.
- The planned batches move up one version: process **v0.11**, tools **v0.12** (BACKLOG and the kolkata CRs).

**Not done:** the first Omni shot. A Veo vs Omni comparison on the same Diwali still pair, about $0.40, runs only with the director's OK on that run.

## 0.9.2 — 2026-11-10
**Cinematic-mode depth bake** (patch, safe mid-reel), with the director's go-ahead ("Promote now").

Why: the director shot the Diwali pool in Blackmagic Cam's Cinematic mode for its shallow depth of field, and saw it on the phone but not on the Mac. Apple Cinematic Video stores a sharp picture plus a depth track (`dish`) and focus metadata (`mebx`). Only Apple frameworks draw the blur, so Premiere, ffmpeg and every studio script showed it sharp, and nothing in ingest said so (CR-20261109-could-not-go-home-diwali-cinematic-depth).

- **New `scripts/cine_bake.swift`**, promoted from the Diwali reel's tool, built to `scripts/bin/cine_bake` by `setup.sh` (git-ignored). It renders the depth with Apple's Cinematic framework (`CNRenderingSession`, macOS 14+) at the recorded focus and f-number (`--fnumber` overrides), into ProRes 422 HQ with BT.709 tags and the source's rotation tag. Two fixes over the reel version:
  - `--audio` no longer hangs (it wrote a 0-byte file): sound is now read and written alongside the picture;
  - `--start` snaps to the nearest camera frame, and frames before it are dropped, so t = 0 is exactly that camera frame (verified: a passthrough bake's first frame differs by 0.34 grey levels from camera frame 3, against 1.9–2.1 from its neighbours).
- **New `scripts/cine_bake.py`:**
  - `--check` lists the Cinematic clips (Diwali: 18 of 19; app proxies skipped);
  - `--edl` bakes every Cinematic clip an EDL uses, over the used span plus 0.48 s handles (spans under 1 s apart share a bake), with sound. It writes `raw/baked/<camera stem>_f<F>_<start>-<end>.mov`, `analysis/bake_map_<edl>.json` and `analysis/<edl>_baked.json` (clips repointed, `src_in` shifted);
  - non-Cinematic shots are left alone, unchanged bakes are reused, and `--fnumber-for C062=2.8` sets one clip's f-number.

  Tested on a 4-shot Diwali EDL (2 bakes, 5.1 s of 4K in 1.7 s); `preview_edl.py` renders the baked EDL.
- **`ingest_report.py`:** a `cinematic` flag (format tag `com.apple.quicktime.cinematic-video-intent=1` or a `dish` track) with what to do, and the recorded aperture in the Lens column.
- **Rules:**
  - SKILL Phase 1: bake from the first EDL on, before anything renders. Storyboard, preview, pregate (so `camera_fidelity.py` compares against the bake) and the Premiere build read `edl_v<N>_baked.json`;
  - CLAUDE.md §5: a one-line pointer;
  - effects-playbook §B: depth as recorded; f/2.8 for slowed hands and tools crossing the focus; focus pulls only when the director asks (Diwali p1b's pulls read as "in and out focus").
- **Shooting guide:** a Cinematic mode row: fine for depth, the blur needs the bake, f/2.8 is safer for slowed hands.
- **Director profile:** shoots Cinematic mode for depth; wants the depth as shot, with no pulls unless asked.

Reels in flight: could-not-go-home-diwali keeps its own `tools/cine_bake` (same output, apart from the fixes above) and can switch at its next bake.

## 0.9.1 — 2026-11-08
**Kolkata pilot fixes** (patch, safe mid-reel). The first batch from the kolkata retro and its 12 CRs, triaged with the director; the rest is planned as v0.10 (process) and v0.11 (tools, with Batch C) in `BACKLOG.md`.

Why: kolkata (hybrid, 76.2 s, 26 shots) took 8 rounds and 16 gate runs, and its retro logs about 22 hours of friction. This patch takes the parts that are rules, notes and small script fixes.

- **Frame-rate crash fixed in four scripts.** On the director's rotation-tagged camera files, ffprobe's csv output reads `25/1,`, so `shake_report.py`, `colour_report.py`, `frame_scan.py` and `render_diff.py` all failed with `ValueError: '1,'` (verified). New `scripts/media_info.py` `fps_of` (ffprobe JSON, avg → r_frame_rate fallback) replaces their parsers; all four now run on a kolkata camera clip.
- **`look_preview.py`** keeps each still's own aspect per row, so portrait and landscape stills can share a sheet.
- **`pregate.py --reviewed / --reviewed-map`**: the last export that **passed** the gate, not just the previous export (kolkata's scope after an unreviewed v8 missed the title change). `--prev` stays as the old name; `review-gate.md` updated. Tested end to end on kolkata v8b → v8c.
- **`ae_roundtrip.py` `time_remap` `"blend": "pixel"`** (or `"mix"`): Pixel Motion frame blending for speed ramps. It has to sit on the footage layer inside the nested source comp; on the outer layer alone a 100 → 40 % ramp still rendered 21 of 37 slow frames as exact repeats, with it inside 0 of 37.
- **Reality doc:** `applyLumetriPreset` on a clip with a Lumetri adds a second one *before* it (find the look by `Look` ≠ 0); QE transitions come back shorter and one-sided without a handle; `setInPoint` + `overwriteClip` can land 1 frame early (read-back snippet); Warp's status codes (104 running, 408 done); Gaussian Blur's **Amount**; the new glow effects untested; `export_frame` fails on a missing folder; `$.evalFile` fails silently on an empty file.
- **effects-playbook:**
  - §A3: `eterna_3510` verified (kolkata, 30 %); **Creative Intensity mixes linearly** (verified within 0.003 of the preview tile); preset step 1 finds the look's Lumetri by `Look` ≠ 0.
  - §A4: the Premiere-native **soft bloom** (a V2 highlight copy, Screen 30 %) with kolkata's verified numbers.
  - §B: the 80 % width rule is for vertical footage; landscape footage gets full-bleed, a 16:9 frame or a 4:5 window, picked by the director (also CLAUDE.md §3 V1, SKILL Phase 3).
- **SKILL Phase 1:** landscape phone footage: confirm each clip's rotation on frames turned both ways at its best moment, record `analysis/orientation.json`, re-check "unusable" clips at their best window.
- **`motion-and-ai.md` §3:** with stock allowed, search stock video *and photos* before proposing an AI shot (kolkata: $0.64 on an AI tram, then a real photo).
- **`film-emulation-prompts`:** rule 6, words Veo takes literally (signs, regional objects); the Daylight street row's sunny and overcast wordings, from kolkata's two drafts.
- **`instagram-strategy.md`:** a Cover section (the grid shows a 3:4 crop; full 9:16 cover, upload from the camera roll).
- **Shooting guide:** holding the phone landscape (check the orientation lock, or note it on the slate).
- **Director profile:** lyrics and montages get one shot per line too; the song carries the story (never the reference's song by default); few but strong Pujo shots in a city reel; stabilise handheld moves by default; plain cuts; their own title words and characterful type; the KOLKATA2026 orientation note and the kolkata content row.
- `SKILL.md`'s `edl_v1b` example now reads `edl_v1b.json`, so `check_tool_names.sh` passes again (all tool names exist in server 1.2.9).

CRs: kolkata film-emulation-first-use and look-preset-second-lumetri done; landscape, soft-bloom, song-research, montage-line-table, preview-fx, cover-title-type, footage-catalogue, late-round-edits and stock-intake partly done; lyric-shot-skill accepted for v0.10.

## 0.9.0 — 2026-11-04
**Offline previews first, local transcripts** (Batch B of the v0.8 plan, `studio/plans/v0.8-plan.md`, with the director's go-ahead).

Why: the first five reels took about 11 director rounds each. 17 rounds were about pace or story, and 11 about shots that didn't show their line. Each was found on a Premiere export, while five reels shared one Premiere. ElevenLabs Scribe returned 401 on three reels in a row.

- **New `scripts/preview_edl.py`** (promoted from Pujo's `tools/preview_assemble.py`, which built v6–v10 while Premiere was busy). It renders the cut from **one EDL file**, `analysis/edl_v<N>.json`, straight off the camera files, in minutes:
  - Premiere-style Scale and Position, with keys (ease or linear), and Rotation;
  - speed and conform through `rate` (0 = a freeze);
  - dissolves centred on the cut, fades, stills and black, V5 overlays (PNG or alpha video);
  - the VO / music tracks and each shot's own sound;
  - an "offline preview · colour approximate" label in the top band.

  It checks first, and renders nothing on a missing clip, a shot that runs past its clip, an overlap or an unknown key. It reports the width shown per shot and any framing that leaves black edges. `--only` renders chosen shots back to back (a grade sample) with a re-timed EDL beside it. Tested on goddess (13 shots, 29.84 s, rendered in 48 s). Ungraded, `camera_fidelity.py` puts every shot within 0.005 luma, saturation × 0.98–1.00 and < 1° hue of its camera file. The 0.553 slow-mo shot repeats 44 % of its frames and the conformed 30 fps shot none. The pregate runs on it.
- **The EDL is the shot map:** `camera_fidelity.py`, `render_diff.py` and `pregate.py` take the EDL object (`"shots"`) as well as a plain map list. The storyboard, the preview, the pregate and the Premiere build read the same file.
- **New `scripts/storyboard.py`** (from goddess, uski and Pujo, rebuilt for the third time by a reel). It shows in / mid / out frames through each shot's framing, with the overlays on screen and the **Instagram UI bands shaded**. Labels give the clip, its in-point, speed or conform, the width shown (orange < 80 %, red < 70 %), and the line the shot carries.
- **New `scripts/pick_sheet.py`** (from goddess and Pujo). It shows 6 frames per clip with camera times, and the shoot date and time decoded from Blackmagic names (clip numbers repeat across shoots). `--all` covers the whole pool.
- **Measurement fix in `camera_fidelity.py`:**
  - frames are now decoded with exact YUV→RGB rounding (`accurate_rnd+full_chroma_int`). ffmpeg's default read every frame about 0.007 darker, with about 1 point more "crushed";
  - v0.8.0 read camera and render the same way, so its camera-vs-render deltas hold to about 0.0005. Absolute numbers (reel mean luma, crushed %) now read true;
  - found because the preview baked the bias in on decode.
- **Local Whisper is the studio transcriber.**
  - New `scripts/transcribe_local.py` uses faster-whisper 1.2.1, installed in `.venv` by `setup.sh`. It decodes audio with ffmpeg and writes the Scribe JSON shape, so `pack_transcripts.py` and `timeline_view.py` read it unchanged. On the goddess VO: 78 words in 4 s on `small`.
  - `transcribe_reel.sh` uses it by default. It takes files (an external VO or a reference's audio), plus `--model` and `--language` (`large-v3-turbo` for Hindi or Bangla); `--scribe` keeps ElevenLabs.
  - The key is optional in `setup.sh`, README and `.env.example`.
  - Removed `scripts/gemini_transcribe_fallback.py`: no backend was installed, so it never ran (backlog G2).
- **CLAUDE.md §4b:** cut on the clause onset, placed on the waveform 0–2 frames before the speech; Whisper's starts ran 0.3 s early on goddess.
- **SKILL:**
  - **Phase 0:** reads `project.md`'s new **`## Now`** block and the latest round, not the whole log. `## Now` is rewritten every round, and old rounds move to `log/rounds.md` past about 4,000 words (logs reached 10–21k words).
  - **Round 1:** question 7, "is the soundtrack existing audio?".
  - **Phase 1:** copy the shortlist into `raw/` (the director wants copies), and transcribe with local Whisper.
  - **Phase 2:**
    - a **line table** for VO and dialogue reels: one row per clause, searched across the whole pool;
    - the EDL JSON;
    - the storyboard and the phone preview, sent at Checkpoint 1;
    - pregate on previews (`--profile ig-quiet`).
  - **Pace, picks, framing and slow-mo windows are settled on previews**, and Checkpoint 1 notes become a new EDL and preview, not a Premiere build.
  - **Phase 3:** builds from the EDL's values.
  - **Checkpoint 2 routes notes:**
    - pace, picks and framing → a new preview first;
    - grade → camera | now | proposed, plus a 6 s `--only` sample on the phone, before any Lumetri change.
- **Reviewer:** a "Pictures and words" major for a shot that doesn't show its line, a picture change in a pause, or the same person on two lines. **review-gate.md:** the EDL is the map for a preview.
- **Director profile** (CRs uski and Pujo director-profile, goddess):
  - a new **Taste** section: natural and HD, never processed; pictures change on the words; literal depiction; vary the people; the deity only with a reason; steady moves; drama from holds and slow motion;
  - judged on the phone, with review copies sent as files;
  - copies, not links;
  - stock only on the director's ask;
  - the footage paths and `<shoot>:<clip>` naming;
  - the existing-audio habit;
  - the five reels in the content table.
- **Templates:** `project.md` gets `## Now` (approved decisions moved into it); `brief.md` gets the line table.
- **CRs:**
  - done: uski director-profile and Pujo director-profile;
  - goddess pilot-notes: items 1, 5, 7, 11, 25 and 40, and 23 in part;
  - Pujo pool-survey, external-vo-audio and premiere-ops: in part;
  - uski script-gaps: items 4 and 24;
  - puja-night-2 script-bugs: item 5.

  Deferred to the backlog: the copy mode of `link_footage.sh` (Batch C), the VO onset refiner, and the beat analyser's speech warning.
- **Reviewed before release** by an independent agent (Sonnet), with synthetic clips whose every frame carries its number. Fixed and retested:
  - duplicate shot names rendered the wrong framing (now an error);
  - a dissolved shot that starts on its clip's first frame ran one frame late;
  - a dissolve handle before reel frame 0 misaligned its shot;
  - `--only` kept the full runtime;
  - unknown keys on overlays, audio tracks and the EDL, negative rates and rotation keys rendered silently (now errors). A dissolve on the first shot or after a gap is a warning;
  - every overlay was loaded at once, and video overlays' ffmpeg kept running (now loaded on first use and released after);
  - every render left a temp folder;
  - `transcribe_local.py` kept a transcript made with another model or language, and stopped on a clip with no audio;
  - `transcribe_reel.sh` gets `--force`, `--vad` and clear errors for a missing value or an unknown option.

  Found while retesting: bicubic resampling at a sub-pixel offset added about 1 point of crush on a dark shot. Static shots are now copied by an integer crop from the prescaled frame, which also renders faster.
- **Reels in flight:** goddess and Pujo have locked pictures and aren't affected. A reel mid-edit (my-reel) picks this up at its next round (minor version). The next reel starts on 0.9.0.

## 0.8.0 — 2026-11-01
**Camera-true pictures, cheaper review** (Batch A of the v0.8 plan, `studio/plans/v0.8-plan.md`, approved by the director; evidence from all five reels, 23 CRs and 4 retros).

Why: 55 director rounds across five reels, 20 of them on colour or image quality ("over processed instead of looking HD", goddess v6c). The review gate ran 59 times and failed 47, at ~200k tokens a run, which used up the week's Fable allowance. HQ's own round-9 brief for goddess gave fixed brightness targets that burnt night shots in v9c; this release grades against each shot's camera file instead.

- **Grade: camera-true by default** (effects-playbook new §A0; §A1–A4; CLAUDE.md opening list, §2.5, §3 V1/V3/V4 rows; SKILL Round 2 and Phase 4; the three playbooks' colour lines):
  - each shot is corrected toward its own camera file: brightness at or a little above it, lifted only until burn starts (any channel at 255 beyond light sources ≤ 2 %), saturation ±5 %, hue ±3°, crush no worse than the camera's;
  - fixed brightness numbers are reported, never aimed at;
  - **no creative look by default.** A look is used only when the director picks it on a camera | camera-true | look sheet plus a 6 s phone sample, starting at 30 %. `muted_red` becomes an option in story-montage;
  - **texture is optional:** never grain on night phone footage, ≤ 5 % elsewhere when the brief has it (was 10–15 % on every reel); no extra sharpening. The brief template now records the look, the texture and the camera-check and framing exceptions.
- **Framing: ≥ 80 % of the camera width** (Scale ≤ 62.5 on vertical 4K), pushes ~+6, tighter only when the brief names the shot (effects-playbook §B, SKILL Phase 3, CLAUDE.md V1 row). Named moves (punch-ins, snap zooms) may go tighter for their few frames; landscape sources are judged against the widest 9:16 framing they allow.
- **New `scripts/camera_fidelity.py`.** It finds each shot's camera frame and framing by edge matching (±0.4 s, any scale), rebuilds the camera image at that framing, and checks brightness, saturation, hue, crush, burn and width shown. `--allow` for deliberate departures, `--look` when a chosen look is on. A missing clip, a shot past the render's end, no framing found or a weak match FAILs (fix the map or `--allow` it). Tested on goddess: v8b FAILs 13 of 14 shots (darker, crushed, muted, 61–78 % width), v9e passes except its two named fixes; all 14 framings found. On Pujo's final (30 fps, a warm baked look) all 7 framings were found; the look's colour shifts show as WARN with `--look`, and its real departures (one shot 0.07 darker than its camera, one more crushed, two at 61–64 % width) still FAIL.
- **Delivery: a ProRes master, then `scripts/encode_master.py`** (H.264 High, CRF 16 capped at 20 Mb/s, BT.709, TV range; `--phone` makes a ≤ 29 MB review copy). Goddess v10b: 18.5 Mb/s, SSIM 0.986, PSNR 43.0 dB and no level shift against the master; `aq-mode 3` gained nothing, so it isn't used. The phone copy is capped at the delivery bitrate, and the script prints the `--min-mbps` floor to verify it with. Untagged masters get BT.709 tags set on the frames. `verify_render.py` now fails Main profile, < 12 Mb/s (`--min-mbps`) and yuvj420p; a low bitrate from its own x264 CRF ≤ 18 encode is a WARN (simple content), and `--allow-black T0-T1` waives designed black anywhere in the reel. Reality doc: the "Match Source - Apple ProRes 422" preset path.
- **Slow motion:** After Effects Timewarp (Pixel Motion, at camera size) is the default on ≤ 30 fps footage; Premiere Optical Flow only on calm shots (effects-playbook §C, after-effects.md, SKILL Phase 5b). Reality doc: a speed-changed clip's in/out are source ÷ speed, its Scale keys don't run the full ramp, Optical Flow falls back to frame blends. **`ae_roundtrip.py`** now detects the phone's −90° rotation flag and feeds AE an upright ProRes HQ trim (tested: 2160×3840, first frame identical to the camera's). The reviewer gets the measured slow-mo bar.
- **Review gate** (review-gate.md, reel-reviewer.md, SKILL Phase 7b):
  - **new `scripts/pregate.py`** runs `verify_render`, `frame_scan` (any flag outside a `--designed` span fails), `camera_fidelity`, `render_diff` and `watch` in about 2.5 min with no tokens, and the reviewer is called only on a pass. It clears old outputs first, and a check that crashes or writes nothing counts as a FAIL;
  - **new `scripts/render_diff.py`**: the frame spans and shots that changed since the last reviewed version (colour at 54×96, so H.264 noise doesn't count but a saturation-only change does), whether the audio is identical, and whether the cut moved. Exact on goddess v9d→v9e (4 shots) and v10→v10b (the 2 slow-mo shots);
  - **focused reviews** of the changed shots for fix versions (or of the sound, for a sound-only change), full reviews for new cuts, and one focused check of the last fixes after loop 2. review-gate.md now gives a worked shot-map example and a runnable pregate command;
  - **the reviewer is no longer pinned to Fable:** the editor passes a model other than its own (Fable for Opus, Opus for Fable or Sonnet, then the remaining one when that's out of credits), names its own model in the prompt, and the reviewer refuses to run on the same one;
  - the reviewer gets the camera sheet and the rule that a shot darker, flatter, more muted, tighter or more burnt than its camera file is a major.
- **CLAUDE.md §4c:** IG audio added at upload is cut to a **guide copy** of that exact audio (not a stand-in at the same BPM); `_mix` is archive-only, `_IG` has the guide muted; the audio's IG page is checked in Phase 1. §5 lists the new tools.
- **CLAUDE.md §4c** also has a step in SKILL Phase 1: when the soundtrack is existing Instagram audio, check its page then.
- **Cleanup:** removed `studio/harness/settings.json` (an unused copy of `.claude/settings.json`); `.gitignore` ignores `__pycache__/`; README's script line and colour steps; `projects/_template/renders/masters/` and `previews/`.
- **Reviewed before release** by an independent agent (Sonnet). Its findings were fixed and retested: pregate failing open on a crashed check, camera_fidelity crashes on a bad map, designed black only allowed at the end, the phone-copy floor, landscape width, and leftover look/grain wording.
- **CRs:** goddess pilot-notes 26, 30, 33, 36–38 done, 39 done except AE Timewarp's `vector_detail` option (backlog); pujo correction-stacking, uski script-gaps (a) and puja-night-2 review-gate done in part; pujo reference-grade-match (force-match) and lens-bokeh (synthetic bokeh) rejected in part.
- **Reels in flight:** goddess (posting) and Pujo (ready to share) have locked pictures and aren't affected. The next reel starts on 0.8.0. A reel mid-edit picks this up at its next round (minor version).

## 0.7.4 — 2026-10-30
**AI-shot prompts that leave the grade to Premiere** (director's request: "a studio-scoped version of the film-emulation skill, for AI-shot prompts only, fixed to our measured film table").
- **New skill `film-emulation-prompts`**, a studio fork of mcpmarket's `color_grading_film_emulation` (MIT, `LICENSE` in the folder; tracked through a `.gitignore` exception). It writes the light and colour block of a `gen_video.py` prompt:
  - **the scene described ungraded**, as the director's phone records it: lens, vertical 4K, light source and direction, natural white balance, clean image;
  - **no film-stock names, grades, grain, halation or letterbox in the prompt**, because the V3 look and V4 grain grade AI shots like every clip, and a baked look would get the look twice;
  - a standard `--negative` list;
  - a light table for the studio's usual scenes (pandal, LED street, sodium, diyas, daylight, river at dusk);
  - for each film-table look id, what the look adds (our measurements), what the prompt should give it, and what to leave out. For example, `muted_red` needs the story's reds and gold clearly in frame; `cinestill` needs bare bulbs against dark, but never "glow";
  - **a draft check by numbers** (`colour_report.py` against the anchor shot: luma ±0.04, warm/cool ±0.03, no lifted blacks, teal shadows, grain or bars) before asking for the final.

  The original's film-stock lore is dropped where our measurements contradict it ("500T cool shadows", "Eterna pastel").
  **Untested:** the first reel to use it reports in a CR.
- **`motion-and-ai.md` §3 "How":** steps 2 and 4 use the skill and the draft check. CLAUDE.md §5 points at it.
- **Reviewed, not imported: `ffmpeg-lut-grade` 1.0.0** (mcpmarket tarball). Its read: it overlaps `ffmpeg-color-grading-chromakey`, ships no licence, and its renders break studio rules (x264 CRF 18 with `-c:a copy`, no BT.709 tags; it relies on `zscale`, which this ffmpeg lacks). One idea went to the backlog: a Hald identity through Premiere for exact previews of dropdown-only looks.

## 0.7.3 — 2026-10-29
**Film looks: preset or dropdown, and `muted_red` without Leave Color** (CR-20261028-we-never-treated-her-like-a-goddess-pilot-notes, items 8, 12, 14, 16; director's request).
- **Each look now names its route in Premiere.** Premiere 26.5's own preset file (`Lumetri Presets.prfpset`), confirmed live on the goddess reel:
  - **preset**, applied by script with `applyLumetriPreset`: only the five Fuji-negative film looks (F125 → 2393 / 2395, Eterna 250D → 3510 / 2395, Reala 500D → 2393), with their preset spelling ("Fuji Eterna 250D …", not the LUT file's "ETERNA");
  - **dropdown**, picked in Lumetri → Creative → Look by the director (or by computer use with their OK): the Kodak 5218 / 5205 looks, the Monochrome film looks and `SL BLEACH NDR`. The v0.6.2 table called all of them scriptable, which was wrong.
  - **Never write the Lumetri `Look` slot by script.** It's a dropdown index: later writes change the number, not the look.
- **`muted_red` rebuilt for Premiere 2026, which has no Leave Color effect:**
  - the V3 Lumetri's **Hue vs Sat** curve keeps ±T° of red, ramps over about 20°, and sets all other hues to 46 %. It's a UI step: the curve and the tint wheels can't be set by script;
  - **verified by render** on the goddess reel against the preview;
  - **tolerance 45 for gold idols:** at 12–25, gold turns silver-grey.
- **Intensity:** the CLAUDE.md V3 row now defers to each look's §A3 value (usually 40–80 %; `muted_red` 35 %, mono 100 %) instead of a flat 40–80 %.
- **Files:**
  - `effects-playbook.md` §A3: look bullet, presets table, film table, build steps, and a new Hue vs Sat recipe;
  - `story-montage.md` Colour;
  - `premiere-mcp-reality.md` (`apply_lut` row, the adjustment-layer step);
  - SKILL Round 2 and Phase 4;
  - `CLAUDE.md` §2.5 and the §3 V3 row;
  - `scripts/look_preview.py`: each look marked `preset:` or `dropdown:`, muted_red's label and the `--red-tolerance` help.
- **Still open in that CR:** Pillow can't shape Bangla, the transcription fallback, link_footage's reference-folder skip, clip keys, the cross-project active sequence, the export bridge, safe zones on the storyboard, and colour_report's hue sample.

## 0.7.2 — 2026-10-28
**Instagram strategy and posting rules** (CR-20261027-pujo-ki-asolei-sobar-ig-strategy-posting, applied with the director's go-ahead).
- **`cinematic-reel/instagram-strategy.md`** (studio-owned; it overrides the third-party `ig-*` pack where they disagree):
  - at most 5 hashtags, all on topic, no tool or brand tags;
  - keywords in the caption text, plus alt text and location;
  - the ranking signals (watch time, likes per reach, sends per reach) and one "send this to…" call to action;
  - the 2026 originality rule;
  - the **AI-credit line** with verified handles (@claudeai, @adobevideo; @premierepro is not Adobe);
  - **AI info label:** on only when the reel contains an AI-generated shot; off for AI-edited real footage.

  The research figures come from the reel session's sources and are marked for a yearly re-check.
- **`cinematic-reel/ig-posting-reality.md`:** what works when posting through iPhone Mirroring:
  - key-press typing (no `?`, `_`, emoji or paste);
  - slow-drag scrolling and lagging sliders;
  - phone locked, full-screen approval;
  - firm rules: only on the director's ask; the director taps Share; reuse consent and Photos access are the director's; touch nothing else in the account.
- **Skill Phase 8** is rewritten to match. `motion-and-ai.md` §3 states both label cases.
- **Director profile:** a new Instagram section (AI credit line, no collab invites, no Story share, topical hashtags, posting via the app).
- **Backlog:** a "made with AI" behind-the-scenes playbook; a Graph API posting path once the director's account is set up.

## 0.7.1 — 2026-10-27
**Ingest check and the camera shooting guide** (director's request: "how are you getting these raw videos").
- **What the footage really is**, from all 329 clips:
  - Blackmagic Cam 3.5 on an iPhone 17, not a Blackmagic camera body: HEVC Main **8-bit** Rec.709, about 56 Mb/s, no log;
  - mixed 25 / 30 / 24 / 23.976 fps, 10 variable-rate clips;
  - **144 clips at high mains-flicker risk** (30 fps at 1/60 s);
  - 93 of 123 clips at 5600 K show an orange cast under warm lamps;
  - **a burned-in LUT is not recorded anywhere in the file.**
- **`scripts/ingest_report.py`** (Phase 1, first step):
  - reads codec, bit depth, colour tags, rotation, bitrate, nominal vs average fps, and the app's white balance, shutter, ISO, lens and slate note;
  - takes 3 stills per clip for black and white points, saturation and casts;
  - rates flicker from shutter × fps × `--mains`.
  - With `--scan` it decodes every frame to measure flicker (lock-in on the alias cycle, whole frame and 6 bands), dropped-frame gaps and isolated picture jumps.
  - It groups clips by **shoot night** (from the recording time, after-midnight clips joined to the evening before) and white balance, as Phase 4's match groups.
  - It writes `analysis/ingest.md` and `ingest.json`.
  - Verified against what Pujo ki Asolei Sobar found by hand: C004's jump at 12.53 s (15 dropped frames), C028's flicker (3.9 % / 6.1 %), C043 safe. A full card of 329 clips takes 2 min; a reel's 54 clips with `--scan` take 2¼ min.
- **`studio/shooting-guide-blackmagic-cam.md`:** one page covering:
  - 25 fps at 1/50 s (50 fps at 1/100 s for slow motion);
  - white balance set to the light (3200 K in pandals);
  - 10-bit or Apple Log if the app offers it, with Apple Log untested in the edit;
  - ISO low, highlights protected;
  - LUT for the monitor only, or its name in the slate notes;
  - 5–10 s holds and ambience.
- The director profile gets a Camera section. README links the guide. `CLAUDE.md` §5 and skill Phase 1 run the ingest check.
- **CRs:** `mains-flicker` and `vfr-jump-qa` are **partly done**: detection and measurement on the raw clips. Deflicker promotion and the `frame_scan.py` export checks stay in the backlog.

## 0.7.0 — 2026-10-21
**Third editing playbook, `story-montage`, with its tools** (director's request, from the "Two Sides of Bangkok" teardown).
- **`playbooks/story-montage.md`:** a narrated montage carried by one recurring character, measured from the reference (150 cuts viewed; 112 real shots once the step-prints are merged).
  - **Section arc:** sizzle hook of 4–7-frame flashes → title over a real moment → optional B&W prologue → a long character hold → discovery at ~1.1 s → a step-print chaos beat → a breather at ~2 s → a calm section locked to one shot per bar (2.06 s ≈ 117 BPM) → split-screen theme → ending holds and a thank-you card in the local script. Scaled to a 45–60 s reel.
  - **Devices:** photo-print inserts, B&W → colour reveal on a match cut, top/bottom split screen with native-language words.
  - **Colour:** measured and turned into rules: sat 0.34, reds 0.82, gold mids at 37°, mint highlights, warm shadows, whites rolled off.
  - **Status:** untested. The reference had no audio, so the sound rules are provisional.
  - Chosen in Phase 0 for `hybrid` reels with a VO and one recurring character.
- **`scripts/step_print.py`:** the step-printed stutter as a render. Long-shutter smear (`tmix`), 12 images/s, re-timed to the reel's fps so each image holds 2–3 frames, ProRes 422 HQ with BT.709 tags. It measures the holds it produced. Tested on 4K C186 at 25 and 30 fps: holds 2–3 frames, 12.0 images/s, 2.7 s to render 2 s.
- **`scripts/photo_prints.py`:** photo-print inserts.
  - Graded stills or `clip@t` on a fine-grained off-white paper with a soft shadow, cropped to 3:4 / 3:2 print shapes.
  - Per-print durations for beat sync; optional settle, tilt, border and a white shutter flash.
  - ProRes with BT.709 tags, plus a sheet and timings.
  - Tested on mixed portrait and landscape footage: 5 prints rendered in 5.5 s.
- **`muted_red` look** in `look_preview.py`: 500T print at 35 %, then a hue-only "leave red" pass modelled on Premiere's Leave Color (Using Hue), plus mint highlights and warm shadows.
  - On 4 of our stills: sat 0.54 → 0.36 with reds kept.
  - `--red-tolerance 25` keeps saffron (0.47).
  - Added to the film table with its Premiere build, which is unverified by script.
- **`teardown.py` fix:** `--ours` is now optional, so Phase 1 can measure references alone (writes `TEARDOWN.md`). Before this, the skill's Phase 1 command failed. Contact sheets now keep the video's aspect (landscape references were squashed).
- Wired into the effects menu (§A3 film table, §C Time, §E Type), the playbook index, Phase 0, `CLAUDE.md` §5 and the README.

## 0.6.2 — 2026-10-21
**Film-stock look table with tested previews and Premiere settings** (director's request, after the external "color-grading-film-emulation" skill turned out to be prompt words only).
- **Premiere's own film emulations are now mapped** (effects-playbook §A3, film table): 12 looks with their exact `applyLumetriPreset` name, intensity, measured character, the Lumetri adjustments for the V3 layer, and what each suits.
  - The looks: Kodak Vision 500T and 250D, Fuji F125, Eterna and Reala, each printed to Kodak 2383 / 2393 / 2395 or Fuji 3510; two Monochrome looks; CineStill 800T with halation; bleach bypass.
  - Found on disk: Premiere ships 115 LUTs, including Adobe's film emulations as plain `.cube` files.
- **`scripts/look_preview.py`**: renders those looks on the director's stills (or `clip@time`) as a labelled sheet plus measurements (the same stats as `colour_report.py`).
  - `exact` looks read **the same `.cube` Premiere uses**, blended at the intensity.
  - `≈` looks are approximations, since SpeedLooks `.itx` and the Monochrome `.look` files aren't readable outside Premiere, and halation isn't a Premiere effect.
  - Wired into Round 2 ("show, don't name").
- **Tested on 4 real stills:** Durga and priest at night, the night temple, a daylight baul, neon arches. Findings now in the table:
  - 500T → 2383 moves hue +1.5° toward gold, so it's the best night fit;
  - F125 → 2393 (the proven Warm Film) and F125 → 2395 push toward red (−1.0° / −3.1°);
  - every 2395 print lifts the blacks to 0 % crush;
  - Eterna → 3510 is the most saturated, not pastel.
- **Halation bake** for the CineStill look: the AE `glow` op has no colour setting, so the red bloom is an ffmpeg render, tuned on crops to stay at ≤ 2 % clipping after the look. Tested on 4K footage, with BT.709 tags.
- `check_tool_names.sh` now ignores look ids defined in `look_preview.py`. They share the snake_case shape of tool names.
- **Verified in Premiere:** only `Fuji F125 Kodak 2393 (by Adobe)` (my-reel, puja-night-2; its recipe is in the table). The other rows are named from Premiere's own LUT folder. Their first reel use verifies them by render (backlog).

## 0.6.1 — 2026-10-21
**Imported skill: `ffmpeg-color-grading-chromakey`** (director's request), from josiahsiegel/claude-plugin-marketplace (MIT; licence kept in the skill folder; commit `9ae4e4a`).
- **Scoped to work around the Premiere grade**, never instead of it:
  - look previews on the director's stills (Round 2, "show, don't name");
  - pre-rendered effect shots the brief plans (keep-one-colour, sepia, film look);
  - keying green-screen elements to ProRes 4444 alpha;
  - BT.709 tag fixes.

  Its auto-trigger description was rewritten so reel sessions don't grade the reel in ffmpeg.
- **Every recipe was tested** on ffmpeg 9.0.2, with a real my-reel still and a test green screen. Fixed and re-verified:
  - "keep only red" came out fully grey; replaced with `colorhold` / `hsvhold`;
  - animated `colorbalance` / `colortemperature` errored; animated with `sendcmd`. `eq` time expressions need `eval=frame`;
  - the dream glow blended in YUV and went magenta; now blends in RGB;
  - the chromakey start of 0.3 made a warm subject see-through; now sample the screen colour and start at 0.10–0.15;
  - colour-balance despill tinted the whole subject; now uses the `despill` filter;
  - a no-op "LUT intensity" recipe was removed;
  - ProRes overlays were half-tagged; now `setparams` + `write_colr`.
- **Studio notes:**
  - teal & orange, the `vintage` preset and the 35mm chain overshoot on warm night footage;
  - HDR → SDR needs `zscale`, which this ffmpeg lacks;
  - no `drawtext`, so sheets are labelled with Pillow.
- Wired into `effects-playbook.md` (§A4 keying, new §A5), the skill's Round 2 look question and `CLAUDE.md` §5.
- **Tracked in git as a studio fork** (`.gitignore` exception, like `cinematic-reel`). Unlike third-party skills, it isn't reinstalled by `setup.sh`, so our fixes stay.

## 0.6.0 — 2026-10-19
**Editing playbooks, plus our own file, sound and AI-clip tools** (director's decision: "multiple editing playbooks for different kinds of videos"). Ideas came from the WeAreNoCode YouTube Editor kit; all code is the studio's own.
- **Editing playbooks** (`.claude/skills/cinematic-reel/playbooks/`): one file per kind of video, holding its style rules (pace, camera, type, transitions, sound, colour, QA thresholds), each with its reason and source.
  - `cinematic-montage`: proven, distilled from my-reel and puja-night-2. Swishes go only on real fast motion, never under text, at about −13 dB (the director's puja-night-2 note).
  - `creator-explainer`: untested, adapted from the kit's 16:9 rules to 9:16. Silence by default, every sound needs a visible cause, never a whoosh under text; top-anchored punch-ins 118–125 %; a card never covers the face.
  - The brief names its playbook and any overrides. Phase 0 proposes it. The reviewer reads it and judges against its QA thresholds.
  - The README covers how a liked result becomes a new playbook.
- **`scripts/verify_render.py`**: the final file gate (Phase 7). Checks codec, 1080×1920, fps, bitrate, 4:2:0, BT.709 tags, duration, audio/video length, black frames outside the end fade, frozen stretches, true peak ≤ −1 dBTP, and −14 ± 2 LUFS (`mix`) or peak only (`ig-quiet`).
  - `--fix-tags` remuxes losslessly with tags.
  - `--fix-loudness` writes a −14 LUFS copy with the picture copied.
  - Tested on my-reel v10 (PASS, −11.5 LUFS warned; fixed copy −14.0 / −4.4 dBTP) and puja-night-2 v5b_IG (PASS).
- **`scripts/conform_clip.py`**: makes AI, stock or still clips reel-ready. Frame-for-frame retime to the reel's fps, `--start` to skip the settle-in, 1080×1920 crop, audio stripped, ProRes 422 HQ with BT.709 tags, `--match <still>` colour transfer (`.cube`), and still → push-in. Tested on the Veo test draft.
- **`scripts/teardown.py`**: measures the reference and our cut the same way (pacing incl. flashes, motion, picture, loudness) and writes `COMPARE.md` flagging gaps beyond tolerance. Used in Phase 1 for targets and in Phase 7 to compare.
- **`scripts/sfx_prep.py`**: trims leading silence and peak-normalises SFX to −3 dBFS, reporting the transient time. SFX are placed by their transient.
- **Sound and loudness rules:** `effects-playbook.md` §F now points to the playbook for which sounds to use and adds −14 LUFS / −1 dBTP for every mixed export.
- **AI-shot rules** (`motion-and-ai.md` §3): never proof, never two in a row, 2–5 s, check the draft against its still, conform with `conform_clip.py`, and turn on Instagram's AI label at posting (Phase 8). Added to the reviewer's checklist.
- The kit is kept as a gitignored reference in `assets/reference-kits/` (its scripts are not run).

## 0.5.3 — 2026-10-18
- **First real AI video call verified**, approved by the director. Test shot: a push into the temple courtyard, starting from a C027 still.
  - OpenRouter → Veo 3.1 Lite draft (720p, 4 s, no audio).
  - Charged **$0.12 = estimate**; the ledger is correct.
  - Output 720×1280, 4.0 s, no audio track.
  - The `data:` URL first frame works: frame 0 matched our still at 0.6/255.
  - 0 frame-scan flags.
- **Learned: Veo outputs 24 fps.** Conform it to the reel's rate on import. `motion-and-ai.md` §3 has the verified facts.

## 0.5.2 — 2026-10-18
**AI video moved to OpenRouter, with a cost structure** (director's decision).
- **`scripts/gen_video.py` rewritten:**
  - default provider is OpenRouter (`OPENROUTER_API_KEY`), model `google/veo-3.1-lite`, **audio off**;
  - Google Gemini API direct stays as a fallback (`--provider google`; it always bills audio);
  - **draft** mode (720p, 4 s, ≈ $0.12) and **final** mode (1080p, 8 s, ≈ $0.40), replacing the old 1080p-with-audio default (≈ $0.96);
  - **prices are read live** from OpenRouter's public video model list on every run, so they never go stale;
  - unsupported durations and resolutions are rejected before sending;
  - the ledger records **the actual cost OpenRouter reports** per job;
  - optional `--first-frame` / `--last-frame` stills from the director's footage.
- **Caps** (`studio/ai-budget.json`), all checked before anything is sent:
  - $10/month;
  - per reel: $2, 2 final shots, 16 s of generated footage;
  - per shot: 3 drafts + 1 final.

  All were tested against a temporary ledger; failed or uncharged jobs don't count.
- **Utilisation structure** (`motion-and-ai.md` §3):
  - no raw footage ever goes to a paid API; all analysis is local;
  - the reviewer sees contact sheets only;
  - only stills go up as first or last frames;
  - generated shots stay under 25 % of a reel's runtime.
- The director profile and `CLAUDE.md` are updated, and `OPENROUTER_API_KEY` placeholders added to `.env` and `.env.example`.

## 0.5.1 — 2026-10-18
**Motion graphics, text behind the subject, AI video**, from the YouTube workflow review. The director approved tests A and B and setup C.
- **A, motion graphics** (HyperFrames `/motion-graphics`):
  - The test title "DURGA PUJA 2026" went through director → builder → check → render: ProRes 4444 with alpha, 1080×1920, 25 fps, 3.0 s, rendered in 7 s.
  - It composited cleanly over real Puja shots.
  - Learned: placement must be per shot ("2026" sat on the gold Durga's crown).
  - The Premiere import isn't verified yet: Premiere was in use by a reel session.
- **B, text behind the subject: new `scripts/text_behind.py`.**
  - Local `remove-background` matte (CPU, 4 fps), then footage + glowing word + cut-out, with a compare strip and a frame scan.
  - Verified: clean and stable on the blue Durga, both as a still and as 2 s of handheld video with 0 scan flags.
  - Weak on wide shots; it fails on busy ornate close-ups (the gold Durga matte turns to mush).
  - The word is fixed to the screen, so use it on holds only.
- **C, AI video: new `scripts/gen_video.py`** (Google Veo 3.1 via the Gemini API, the director's choice).
  - Dry run by default.
  - Monthly budget in `studio/ai-budget.json` (**$10**); spend is logged to `studio/ledger/ai-spend.jsonl`, and over-budget calls are refused.
  - `--why` is required, per the policy "only when footage can't".
  - Output goes to `renders/gen/` with an "AI-generated" sidecar.
  - Prices were checked on Google's pricing page: Fast 1080p is $0.12/s, so ≈ $0.96 per 8 s shot.
  - Verified: the dry run, the budget refusal and the missing-key stop. **A real call isn't verified yet**: it needs the director's `GEMINI_API_KEY` (a placeholder was added to `.env` and `.env.example`).
- **New `.claude/skills/cinematic-reel/motion-and-ai.md`** with all three recipes and their limits. Also updated:
  - skill Phase 2 (generated shots listed with cost) and Phase 5 (V5 graphics, text-behind on holds);
  - playbook §E;
  - `CLAUDE.md` tooling and ownership;
  - the director profile's AI policy;
  - the guard hook's carve-out for `studio/ledger/`, and an `ARCHITECTURE.md` row for it.

## 0.5.0 — 2026-10-17
**Review gate + watch**, from the "Claude edits every video" workflow (Nishant Chahar), adapted to this studio.
- **New `scripts/watch.py`:** samples any video at N fps into labelled contact sheets, one per shot (`--shots`) or per section, with the audio waveform under each sheet, plus `index.md` / `index.json`. Takes about 9 s for a 50 s reel.
- **New `scripts/frame_scan.py`:** checks every frame for blur or smear dips, frozen frames, flicker and black or white frames. Takes about 2 s. It catches what 2 fps sheets can't: on my-reel v8 it flagged C073's camera jerks (30.40 and 30.88 s) and C076's Timewarp smear (37.96 s) to within a few frames.
- **New `.claude/agents/reel-reviewer.md`:** an independent reviewer on a **different model** (Fable) that judges a render blind against the brief and the director profile, and returns a verdict plus a defect table.
- **New skill Phase 7b + `review-gate.md`:** every version goes through the gate before Checkpoint 2.
  - Step 0 keeps `brief.md` current.
  - At most 2 fix loops.
  - Every blocker and major is answered as fixed, intended or disagree.
- **Calibration on my-reel v8**, blind vs the pilot's frame-by-frame QA:
  - 5 of 8 failing shots caught fully, 2 partly, 1 missed (ray haze);
  - 12 extra real issues found;
  - the misses led to the frame scan and a haze check.
- **Fix: `ae_roundtrip.py` `frame_match` and the compare still now rotate the source like the job.** v0.4.1 falsely failed `rotate: 180` shots; v8 s06 and s09 now pass.
- `CLAUDE.md` tooling lines for watch and the review gate.

## 0.4.1 — 2026-10-17
After Effects fixes from my-reel v7 (pilot reports).
- **Fix: Timewarp retimed from the start of the source file, not the shot's in-point.**
  - With `layer.startTime = -in_s`, Timewarp sampled (t + in_s) × speed. On C076 (in 15.96 s, 60 %) the output showed source 9.6–11.7 s.
  - Every shot is now built as a source comp starting at the in-point, and all ops apply to that nested comp.
  - Verified: frame 0 = in-point on C076 and on the C077 ramp (in 7.6 s); duration 2.11 s ÷ 0.6 = 3.52 s.
  - My v0.4.0 check missed this: its stills didn't match, and I blamed the still's timing instead of the render.
- **Fix: a pre-trimmed source went black after its media ended** on slow-mo shots. The source comp outlasts the output, so it's fixed; verified, no black tail. Pre-trimming is no longer needed.
- **New `frame_match` check** in `ae_roundtrip.py`: output frame 0 vs the source around the in-point, accounting for 24→25 fps conforms. It warns loudly on a mismatch, and the result is logged.
- **Glow defaults** are now threshold 80 / radius 25 / intensity 0.25, after 70 / 0.5 clipped 21–54 % of pixels on night shots. The docs note that glow shots need exposure checks against their neighbours.
- **Docs:** v7 denoise results (−12…−29 % dark-area noise), the frame_match step, and pre-trimming no longer needed.

## 0.4.0 — 2026-10-17
**After Effects finishing** (CR-20261017-my-reel-after-effects-bridge).
- **New `scripts/ae_bridge.py`:**
  - runs ExtendScript in the director's running AE via osascript `DoScript` with a file loader, and returns JSON;
  - `verify` checks the connection, and `effects` checks effect match names.
- **New `scripts/ae_roundtrip.py`:** jobs JSON → one AE project per shot → `aerender` ProRes 422 → before/after still + log.
  - Ops: `denoise`, `timewarp`, `time_remap` (true eased speed ramps), `glow`, `grain`.
  - Safety: it never touches another open AE project.
- **Verified by render on my-reel footage:**
  - Remove Grain needs Viewing Mode 4; it gets studio defaults that keep texture;
  - Timewarp and the time-remap ramp are clean;
  - Glow is `ADBE Glo2`.
- **Rejected:** Warp Stabilizer by script. It never analyses and renders a "Click Analyze to begin." banner, so stabilising stays in Premiere.
- **New `.claude/skills/cinematic-reel/after-effects.md`** + skill **Phase 5b**, and a `CLAUDE.md` tooling line.
- **Fix:** `shake_report.py` / `colour_report.py` crashed on files where ffprobe lists the stream twice (found testing ProRes output).
- **Backlog:** kumoproductions AE MCP (dependency decision), Adobe's own AE MCP (beta-gated), paid plugins (Neat Video, Twixtor, RSMB, Deep Glow), aerender speed, a ProRes 422 HQ template.

## 0.3.2 — 2026-10-17
Montage craft from my-reel rounds 2–6 (CR-20261016-my-reel-montage-craft).
- **Brief (skill Phase 2, CLAUDE.md §4c):** music-montage briefs state an **energy arc** (default: slow open → build → full → breath → payoff → outro) and a **motion style**. Never one shot per bar throughout.
- **New scripts**, generalised from the pilot's and tested on v6 (numbers match the pilot's reports):
  - `selects_score.py`: best 1 s moments per clip, shoot-wide ranking;
  - `motion_holds.py`: static holds and pans per clip;
  - `shake_report.py`: per-shot jitter for before/after stabilisation;
  - `colour_report.py`: per-frame colour QA with montage targets and a gold-hue check.
- **Playbook:**
  - no shake or snap zoom on handheld footage (push/pull on holds instead);
  - Optical Flow slow-mo allowed at 25 fps on calm shots;
  - grain 10–15 % by default;
  - warm-look red-push warning;
  - music-montage words default to title + end card.
- **Skill Phase 5:** Warp Stabilizer on handheld moves by default (nest recipe for speed-changed or interpreted clips), then re-measure and scan for Warp banners.
- **Skill Phase 4:** colour QA on every frame before review.
- **Checkpoint 2:** the director watches full-screen with sound, and gets one "what would make it more cinematic?" question.

## 0.3.1 — 2026-10-16
The rest of the first pilot's feedback (`my-reel` retro + 5 CRs). Main lesson: **many Premiere MCP tools report success without doing the work.**
- **New `.claude/skills/cinematic-reel/premiere-mcp-reality.md`:** every broken or partly working tool on Premiere 26.5.2 / MCP 1.2.9, with the fallback the pilot verified. It covers import, delete, colour, adjustment layer, LUT, blend mode, transitions, volume, slip, razor, export presets, silent export and script results. CLAUDE.md §2 now requires **verify by render, never by the tool's reply**.
- **Conform by interpretation (CLAUDE.md §3):** outlier frame rates are fixed with `set_override_frame_rate` before placement, not with `speed_change`.
- **Colour (CLAUDE.md §2.5, playbook §A1/§A3/§A4):**
  - `color_correct` only for contrast / temperature / tint, plus a Lumetri script recipe for the rest;
  - the adjustment layer is one manual step for the director;
  - looks use built-in Lumetri presets (custom `.cube` files can't be loaded by script);
  - blend-mode enum documented;
  - V4 fades with the picture.
- **Transitions / sound / export:**
  - QE transition snippet and Dip-to-Black fades;
  - volume formula;
  - built-in `.epr` paths;
  - mandatory audio check after export;
  - new **`scripts/mix_from_edl.py`**, the fallback that rebuilds the mix and muxes it onto the picture.
- **Type:** new **`scripts/render_type_cards.py`** renders PNG word and end cards with a safe-zone guard and a system-font fallback. End cards must be checked over the real outro frame.
- **New `studio/director-profile.md`:** handle, type style and working preferences, read by every reel in Phase 0, so branding is asked once.
- **Speed ramp recipe** rewritten for how `speed_change` actually behaves.
- **Upstream:** 15 issues drafted in `studio/upstream/premiere-mcp-issues.md` (not filed).

## 0.3.0 — 2026-10-16
First pilot feedback applied. Both change requests are from `my-reel`.
- **CR-20261016-my-reel-beat-summary → `gemini_audio_and_beat_analyzer.py`:**
  - "4-Bar Downbeats" is renamed "Bar downbeats (every 4th beat)", and the bar length is shown;
  - the beat range is stated (the beatless intro and outro are now visible);
  - a new **Energy / sections** table labels intro, build, drop, breakdown and outro from per-bar loudness;
  - new **Candidate cuts** give the best 3 start/end pairs for 15/30/45/60 s, scored on energy, first hit ≤ 3 s, a clean ending and starting on a phrase;
  - the dialogue table only appears when clips are passed.

  Tested on Dum Durga: the sections match the pilot's hand-made map, and the 30 s candidates include its chosen 61.9 s start.
- **CR-20261016-my-reel-footage-overview → `analyze_footage.py`:**
  - new `overview_<n>.jpg`: labelled mid-frame thumbnails, 20 per sheet, built from frames already grabbed (no extra decoding);
  - new `--norm auto|talking-head|shoot`: by default, a shoot with median exposure < 0.30 is judged relative to its own median. On `my-reel` that's 19 darker and 7 brighter clips, instead of 70/77 "underexposed".
  - **Not done: auto upside-down detection.** On the pilot's 5 known upside-down clips, the top-vs-bottom brightness and detail heuristics were spread across the whole range, and the metadata of upside-down and upright clips is identical apart from timestamps. Upside-down clips are spotted on the overview sheets instead. That check found 3 more likely ones (C014, C015, C020).
- **Skill Phase 1:** look at the overview sheets first, then the candidates' contact sheets; use the energy/sections table and candidate cuts to pick the music section.

## 0.2.5 — 2026-10-16
- **Skill Phase 1: handle Premiere sample media.**
  - Premiere 2026's New Project screen imports 17 Adobe sample clips and a `Sequence 01` by default. This was found in `my-reel.prproj`.
  - The reel session now lists them and asks the director before removing the project references.
- **Bridge verified end to end:** `verify_premiere_connection` → connected (Premiere 26.5.2).

## 0.2.4 — 2026-10-16
- **`link_footage.sh`:**
  - new `references` role, which links into `projects/<reel>/references/`;
  - footage roles now skip reference folders (`*ref*rence*`, which also matches the director's "Refference" spelling), so a reference reel can't be linked in as footage.
- **`analyze_footage.py`: default `--scene-threshold` lowered from 0.3 to 0.15.**
  - On `my-reel`'s dark, beam-lit reference, 0.3 found 3 cuts (5.4 s average).
  - The count settles at 8 cuts from 0.15 down to 0.1 (2.4 s average, 1.6 s median), which matches the contact sheet.
- **Skill Phase 1:** cross-check the reference cut count against its contact sheet.

## 0.2.3 — 2026-10-16
- **Starter asset pack adopted (G1).** `scripts/gemini_generate_starter_pack.py` was reviewed and run. It generates:
  - 5 LUTs in `assets/luts/`;
  - 6 SFX in `assets/sfx/`;
  - a 16mm grain loop in `assets/overlays/`.

  The files are git-ignored and can be regenerated. `setup.sh` now generates them when no LUTs exist.
- **Fixes to the generator after testing on real `my-reel` frames:**
  - Teal & Orange turned pure black navy. The tint now fades in from black.
  - The "Log to Rec709" LUT was a contrast curve, not a real camera conversion. It's renamed `gemini_flat_contrast_boost.cube` so it can't be mistaken for the clip-level log LUT that CLAUDE.md §2.5 allows.
- **Playbook:**
  - §A3 maps each look to its LUT file, with notes from the test;
  - §A4 adds a stronger grain range (40–60 %), because 30 % is barely visible;
  - §F names each SFX file and notes they're placeholders.

## 0.2.2 — 2026-10-16
Found while preparing the first pilot (`my-reel`: 77 iPhone 17 / Blackmagic Cam clips, mostly 25 fps).
- **Rule: sequence frame rate matches the footage** (CLAUDE.md §3, skill Phase 3).
  - The most common frame rate in the footage wins.
  - Outlier clips are conformed with `speed_change`.
  - This replaces the old "30 fps default", which would have made 25 fps footage stutter.
- **New: `scripts/link_footage.sh <reel> <dir> [a-roll|b-roll]`.**
  - Symlinks footage that lives outside the studio into `raw/` and records it in `raw/SOURCES.md`.
  - Originals are never copied or moved.
  - Skips macOS `._*` files and camera `Proxy/` folders.
  - Safe to re-run.
- **Fix: `analyze_footage.py` skips `._*` metadata files** when scanning a folder.

## 0.2.1 — 2026-10-16
- **New: `scripts/check_tool_names.sh`.** It lists the Premiere MCP server's tools over stdio and fails if any tool name in `CLAUDE.md` or the cinematic-reel skill and playbook doesn't exist. Premiere doesn't need to be running. Result today: all 52 names are valid against server 1.2.9 (283 tools).
- **Gemini review triage.**
  - G4 (move graphics above the grade): rejected by the director.
  - G5 (wrong tool names): rejected; the check above shows the claim is false.
- Guard hook installed (`.claude/settings.json`).

## 0.2.0 — 2026-10-15
- **HQ / reel-session split.**
  - Each reel is its own sub-project, edited in its own session.
  - One HQ session owns the architecture (`studio/ARCHITECTURE.md`).
- **Guard hook.** `.claude/hooks/guard_architecture.py` blocks edits to HQ-owned files from reel sessions. The hook is staged in `studio/harness/settings.json`. It becomes active once installed into `.claude/settings.json`.
- **Change requests.** Reel sessions file them in `studio/change-requests/`, and HQ triages them with `/studio-hq`.
- **Pilot programme.**
  - Every pilot reel keeps a friction log.
  - Every pilot reel writes a `retro.md`, copied to `studio/retros/`.
- **Reel types.** `talking-head`, `music-montage` and `hybrid` are now defined. Music-montage cuts on the music's beat grid and skips transcription.
- **`project.md` fields.** The template now records the architecture version, reel type and pilot flag. `new_reel.sh` fills in the version.

## 0.1.0 — 2026-10-15
- Initial bootstrap. Covers:
  - `CLAUDE.md` contract;
  - `/cinematic-reel` skill and effects playbook;
  - analysis and transcription scripts;
  - Premiere MCP setup.

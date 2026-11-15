# HQ Backlog

Architecture work not yet done. HQ triages it at the start of each `/studio-hq` session. Change requests from reels are linked here when deferred.

## Next: kolkata batches (triaged 2026-11-08) and Batch C
v0.9.1 shipped the rules, notes and small fixes from the kolkata retro and its 12 CRs. v0.9.2 (Cinematic depth bake) and v0.10.0 (AI shots and the bad-footage ladder, `studio/plans/ai-shots-plan.md`) came in between, and v0.11.0 (real sound effects: Openverse, earshot, `sfx_sync.py`) took the next number on the director's request of 2026-11-12, and v0.12.0 (restraint by default and the quality probe, from the director's quality complaint of 2026-11-15) took the next one, so the process batch is now **v0.13** and the tools batch **v0.14**. Still open from v0.10.0: the Veo vs Omni comparison run (about $0.40, director's OK). The rest, in order, each with the director's go-ahead in an HQ session:
- **v0.13, process (kolkata's biggest losses: story ~5 h, song ~3 h, title and cover ~2 h):**
  - a line table for **every** reel type, by lyric meaning for songs, and a **story check** in `review-gate.md` / `reel-reviewer` (CR montage-line-table 1–2);
  - the `lyric-shots` skill the director asked for (CR lyric-shot-skill), tested on the kolkata song first;
  - a song-research step after the story spine, a "⏸ song audition" checkpoint, `song-research.md` and `scripts/song_fit.py` (CR song-research 1–3);
  - title words and a type sheet in Round 2, `scripts/make_title.py`, an `assets/fonts/` README, and a Phase 8 cover step (CR cover-title-type 1, 2, 4).
- **v0.14, tools (with Batch C below):**
  - `scripts/depth_clarity.py`, from `projects/_hqtest/tools/depth_clarity.py` (HQ C047, 2026-11-11). It uses `cine_bake --disparity-out` for denoise plus sharpening and local contrast on the focus plane only. With an AI fill it also matches the fill's bokeh and near-plane detail to the camera's, measured. It should run from the EDL next to `cine_bake.py`;
  - `scripts/gap_fill.py`, from `projects/_hqtest/tools/gap_fill_splice.py` (HQ C047 test, 2026-11-11). It puts an AI gap fill into a camera clip: bake-aware, upright, matched to the camera's colour, saturation and measured sharpness, with seam dissolves, and it reports the seam frame steps against the camera's. Also landscape and window support in `conform_clip.py`, which today crops to 1080×1920 only;
  - `scripts/preview_fx.py` (stabilise, motion-compensated slow-mo, ramps, whips, Screen overlays) and a shake ranking of planned windows (CR preview-fx);
  - `scripts/stock_search.py` (Pexels video and photos; the director adds the free key to `.env`) and a repeated-frame intake check with `conform_clip.py --dedup` (CR stock-intake);
  - an upright orientation sheet, an EDL `window` key in the preview and storyboard, and `camera_fidelity.py` decoding upright and measuring inside the window (CR landscape 1, 5, 6, 8);
  - `scripts/premiere_swap.py` on the ExtendScript library, and `frame_scan.py` ignoring V5 overlay regions (CR late-round-edits);
  - `shake_report.py --background`, played/unplayed beats in the beat grid, mist and film-stack previews in `look_preview.py`.
- **C, tools that save hours** (v0.8 plan, approved in outline 2026-11-01): a shared ExtendScript library (`scripts/es/studio.jsx`, including the read-back that writes `map_v<N>.json`, set Lumetri by occurrence and by `Look` ≠ 0, the in-point read-back, and transitions that warn when they come back short); a one-reel-at-a-time Premiere lock; a full-resolution pre-screen of candidate windows (zoom steps, jerks, flicker, orientation, faces/phones in the IG bands; also the pregate items CR puja-night-2-review-gate still lists); `<shoot>:<clip>` identity across the analysers, the `link_footage.sh` reference skip and a `link_footage.sh --copy --only <clips>` mode (CR pujo pool-survey); HTML word cards for Bangla/Devanagari. (The `shake_report` fps parse is done in v0.9.1.)
- **Open decisions for the director:**
  - a shared footage catalogue, `studio/footage/<shoot>.md`, that reel sessions append to (an ARCHITECTURE change; CR footage-catalogue 1–2);
  - Bengali shaping: try `brew install fribidi` (Pillow's wheels load it at run time; needs the director's OK), else the HTML cards;
  - ~~delete or set aside the untracked `scripts/gemini_ig_studio_cli.py`~~ **set aside 2026-11-14** (v0.11.1, public repo): it, `gemini_setup_premiere_mcp.sh` and `GEMINI_IG_STUDIO_INTEGRATION.md` stay on the director's Mac, git-ignored, never pushed. The CLI can publish to Instagram directly, which the studio doesn't do (the director taps Share).

## Untriaged: external review (`studio/reviews/gemini-architecture-review-2026-10-15.md`, added 2026-10-15 by another tool)
Each item needs to be verified before it's adopted. The scripts it ships (`scripts/gemini_*.py`) haven't been reviewed yet.

| # | Claim | Verify by | Status |
|---|---|---|---|
| G1 | `assets/` is empty, so the LUT / SFX / grain steps have nothing to use. A starter pack generator is offered | Already true: assets are empty. Decide between a generated starter pack and real licensed assets | **done** v0.2.3: starter pack adopted, with 2 LUT fixes. Real licensed assets can be added alongside it at any time |
| G2 | `transcribe.py` exits when there's no ElevenLabs key. A local Whisper fallback is offered | Read `.vendor/video-use/helpers/transcribe.py`. Test the fallback on a talking-head pilot | **done differently** v0.9.0: the studio's own `scripts/transcribe_local.py` (faster-whisper) is the default; the offered `gemini_transcribe_fallback.py` was removed (no backend installed, never ran) |
| G3 | There's no loudness or beat-grid measurement. A librosa analyser is offered | Review the script, then run it on the first music-montage pilot | **partly adopted** v0.2.0: the beat grid was reviewed and tested on a 120 BPM click track (read 117.5 BPM, beats placed within about 1 frame). Used by §4c. The loudness half hasn't been reviewed |
| G4 | HyperFrames graphics on V2 sit under the V3 grade and get discoloured | Valid concern. Decide on a track layout change (graphics above the grade) | **rejected** 2026-10-16 by the director. Graphics stay on V2, under the grade |
| G5 | `set_clip_opacity` / `speed_change` / `reverse_clip` may not exist as tools | Grep the tool registry in the installed `adobe-premiere-pro-mcp` package | **rejected** 2026-10-16. Claim is false. All 52 tool names in the rules exist in server 1.2.9 (283 tools), including the 3 named. Rerun `scripts/check_tool_names.sh` after any MCP upgrade |
| G6 | Premiere tone-maps iPhone HLG before grading, so a Log LUT blows it out | Check on the first iPhone HDR clip in a pilot | open. `my-reel` footage is Rec.709 SDR, so it isn't tested there. Since v0.6.1: the ffmpeg route can't tone-map either (no `zscale` in this build), so Premiere is the only path for now |
| G7 | `scripts/gemini_setup_premiere_mcp.sh` (added 2026-10-16): setup with an npm fallback for a root-owned `/usr/local`, plus CEP debug mode for CSXS 9–16 (doctor covers 10–12) | Fold its npm-prefix fallback into `setup.sh`. Enable more CSXS versions only if the panel doesn't show in Premiere | open. File left untracked |

## From the my-reel retro (deferred)
- Template `.prproj` with a pre-made 1080×1920 adjustment layer and sequence presets. This would remove the one manual step (CR color-tools 3b).
  - Lead from Uski Aankhein: a sequence cloned from one that already has the V3 adjustment layer carries it along, so no manual step was needed there. Verify, then document it in the reality doc as the default route for later versions.
- Root cause of the silent Premiere export (upstream draft #15). Needs a minimal repro project.
- Map built-in Lumetri presets for Teal & Orange, Moody Desat, Clean Bright and Mono Drama (playbook §A3) as reels verify them.
- MCP smoke test: extend `check_tool_names.sh` to import and delete a dummy file in a scratch project, so tool regressions are caught after upgrades.
- File the upstream issues (the director decides).

## After Effects (from v0.4.0)
- Option: `@kumoproductions/mcp-aftereffects` (MIT, released 2026-10-16, 1 contributor, no panel needed). It's a richer AE MCP; adopting it is a dependency call for the director. Revisit once it has more history.
- AE 26.5 ships Adobe's own MCP server (`Contents/Required/MCP Server.plugin`). It's disabled behind a beta gate; recheck in later AE builds.
- Paid plugins (director decides): Neat Video (much stronger denoise than Remove Grain), Twixtor, RSMB, Deep Glow.
- `aerender` starts a second AE per shot (about 4 min each). If render time hurts, try `-reuse` or rendering from AE's own queue.
- ProRes 422 HQ needs a custom output-module template made once in AE's UI; today we use "High Quality" (ProRes 422).

## Motion graphics / AI (from v0.5.1)
- ~~Verify the Premiere import of a HyperFrames ProRes 4444 alpha MOV on V5~~: verified on puja-night-2 (CR-20261018-puja-night-2-motion-ai, item 1).
- ~~Verify the first real OpenRouter call~~: done 2026-10-18 ($0.12, `data:` URL first frame OK, 24 fps output). Still unverified: the Google fallback (its `predictLongRunning` vs `generateContent` note), if it's ever needed.
- Text behind the subject on moving shots needs motion tracking: either track the word to the subject, or limit it to holds (as now).
- Gemini Omni video-to-video restyle (the creator's "text behind the head"): not on Google's pricing page as of 2026-10-18. `text_behind.py` covers the need locally for free.
- A per-format motion-graphics kit (reusable title, end card and lower-third in the director's style) once v0.5.1-style formats exist.
- **Null Motion (nullmotion.com): parked 2026-11-12 by the director.** The director asked to add it "for motion graphics which we can use in future". HQ checked the site:
  - **What it is:** a paid editor that runs in a browser tab (Null Studio). You sign in with Google and pay through Stripe.
  - **Plans:** the motion-graphics library comes only with Creator ($29 a month, or $21 billed yearly) or Studio ($99, or $69 yearly). Starter ($10) doesn't include it.
  - **The MCP:** a local server at `127.0.0.1:4350/mcp` with 17 tools, which edits Null's own timeline only while its tab is open. Setup: `claude mcp add --transport http null-studio http://127.0.0.1:4350/mcp`.
  - **Export:** MP4 only (1080p from the MCP, 4K in the browser on Creator), with no transparent background.
  - **Templates:** 13 live ones (titles, lower thirds, kinetic type) and 45 pre-rendered transparent overlays. The overlays are landscape 1920×1080 and in a tech/creator style (charts, leaderboards, chat bubbles, confetti).
  - **Source code:** the GitHub repos it links (blixvip/NullMotion, arnoldwender/nullmotion) return 404. The other "nullmotion" repos are 0-star accounts, so there's no code to review.

  **Why parked:**
  - Graphics have to sit on V5 above the grade with a transparent background (HyperFrames → ProRes 4444). Null's MP4 would arrive baked onto footage.
  - It's a second editor competing with Premiere.
  - HyperFrames already makes 9:16 titles, lower thirds and kinetic type with a transparent background.

  **Look again if** Null exports with a transparent background (ProRes 4444, or WebM with alpha), ships 9:16 overlays in a style that fits the reels, and its local server's code can be reviewed. If adopted, it goes behind the same ask-first guard as Higgsfield, after the director subscribes.

## From v0.6.0 (playbooks + the WeAreNoCode kit)
- **Group B: talking-head tools (next minor version):** an audio cut audit (clipped words at cut edges; his most important finding), a paper-cut script from the transcript, dead-air detection on the cut, and camera-move helpers (local transcription: done in v0.9.0) for the `creator-explainer` rules. Build them before or during the first talking-head pilot.
- **VO timing (CR pujo external-vo-audio, goddess pilot-notes 23):** a speech-band onset refiner for Whisper's early word starts (first 5 ms frame within 8 dB of the word's peak), promoting Pujo's `tools/vo_timing.py`; a warning from the beat analyser when the track carries speech; maybe a `voiceover` sub-type of `hybrid`.
- **`creator-explainer` needs its pilot.** Every rule is adapted from 16:9 YouTube; log every misfit as a CR.
- **Premiere lock:** three reel sessions contend for one Premiere. A lock file (session, reel, since) checked before mutating tools, released at wrap-up.
- ~~A final re-review step after the review gate's last loop~~: done in v0.8.0 (one focused check of the last fixes).
- `CR-20261017-my-reel-directional-blur-scan`: one-directional smear and blur straddling a cut in `frame_scan.py`.
- `colour_report.py`: exclude designed fades from the crushed-shadows count.
- `CR-20261017-my-reel-qa-visual-review` leftovers.
- After Effects ops still missing: handles on trimmed shots, and a `vector_detail` setting on `timewarp` (goddess CR item 39). (`light_rays` dropped: the director called the rays and leaks "cringe and less production grade" on my-reel v8.)
- From CR pujo lens-bokeh (deferred in v0.8.0): the per-shot stabilisation bake and its QA (first / mid / last frames, stability on a background ROI).
- ffmpeg build without libzimg (`zscale`) and freetype (`drawtext`). An ffmpeg with both would enable HDR → SDR tone-mapping and labelled sheets in one pass. That's an install the director decides on (it changes a system tool).
- Film-stock looks (v0.6.2): only `Fuji F125 Kodak 2393 (by Adobe)` is verified in Premiere.
  - The first reel that uses another look confirms the name with `getAllLumetriPresetsList()` and compares the Premiere still with the `look_preview.py` tile. That also tests whether Lumetri's Intensity mixes linearly.
  - It reports by CR, and HQ marks the row verified.
- **story-montage (v0.7.0) needs its pilot.** Pujo ki Asolei Sobar is the closest reel.
  - Unverified in Premiere: setting Leave Color (Using Hue) and the Lumetri Highlight / Shadow Tint wheels by script, Posterize Time, and the Lumetri saturation keyframes for the B&W → colour reveal.
  - Ask the director for the reference **with audio** to replace the provisional sound rules.
- **Footage (from v0.7.1):**
  - promote Pujo's `deflicker.py` to `scripts/`, with display-domain estimation by default (CR mains-flicker);
  - `frame_scan.py` export checks: `flicker` (≤ 1.5 % per tile), `jump`, `ghost`, `translation` (CR vfr-jump-qa);
  - **test an Apple Log / 10-bit HEVC clip** through Premiere before the first log shoot (the conversion LUT can't be applied by script: `apply_lut` is broken);
  - `teardown.py` misses dissolves (scene threshold), so cuts are undercounted on reels that use them (seen on Uski Aankhein).
- **Instagram (from v0.7.2):**
  - a "made with AI" behind-the-scenes reel playbook, for the tool and brand story (kept off topical posts);
  - a Graph API posting path (the pack's Publora flow or the `instagram:configure` plugin) for reels with their own licensed audio, once the director sets up the account;
  - re-check the strategy figures in `instagram-strategy.md` yearly.
- **Looks and AI shots (from v0.7.4):**
  - **Exact previews of dropdown-only looks.** Run a Hald CLUT identity (`ffmpeg -f lavfi -i haldclutsrc=level=8 -frames:v 1 hald8.png`) through Premiere's V3 look once per look, export the frame, and use it with `haldclut` in `look_preview.py`. That would make the `≈` looks exact: SpeedLooks (encrypted `.itx`), the Monochrome film looks, and `muted_red` with its Hue vs Sat curve. It needs Premiere free of reel sessions. The idea comes from the ffmpeg-lut-grade skill review; this ffmpeg has `haldclutsrc` and `haldclut`;
  - **verify `film-emulation-prompts`** on the first reel with an AI shot (draft numbers against its anchor, in a CR). A cheaper option, only with the director's OK for ≈ $0.24: two drafts of one prompt, with and without film-stock words, compared by `colour_report.py`.
- After Effects `glow` op: add Glow Colors (A & B, red/orange), so CineStill halation can be done in AE instead of the ffmpeg bake.
- Instagram plugin: needs the director's Graph API token via `instagram:configure`. Read-only use (insights, comments) recommended; posting only with approval per post.

## Known gaps
- Music-montage runs on CLAUDE.md §4c rules, which haven't been tested in Premiere yet. The first pilot validates them.
- The guard hook was installed 2026-10-16. Its deny path hasn't been confirmed from a real reel session yet. The first pilot should hit it once, on purpose.

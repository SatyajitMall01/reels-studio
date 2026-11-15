# Cinematic Reels Studio

You direct, Claude edits, in Adobe Premiere Pro. You drop in your clips, answer a few questions and share references. Claude **writes the brief**, then turns the clips into a fully treated cinematic 9:16 Instagram Reel, never just cuts stitched together. Every reel gets:
- colour correction per clip and matching between shots;
- a camera-true grade, plus a creative look or film texture when you pick one;
- punch-ins and camera moves;
- speed ramps and transitions;
- graphics and captions;
- sound design;
- an independent review on a second model before you see any cut.

It runs on **Claude Code** driving **Premiere Pro** through an MCP bridge, with a set of local tools for analysis, previews, quality checks and delivery.

📘 **The complete guide**, from install to a posted reel: [`docs/GUIDE.md`](docs/GUIDE.md) · [PDF](docs/GUIDE.pdf)
🎥 **Before you shoot**: [`studio/shooting-guide-blackmagic-cam.md`](studio/shooting-guide-blackmagic-cam.md) · [PDF](docs/shooting-guide.pdf)

## What you need
- A Mac with **macOS 14+**, **Homebrew**, and **Adobe Premiere Pro** (built on Premiere 2026; After Effects 2026 is optional).
- **Claude Code**: the Claude desktop app's Code tab, or the `claude` CLI.
- Optional keys in `.env` (ElevenLabs, Pexels, OpenRouter). Nothing needs them by default: transcripts use local Whisper.

## One-time setup (≈15 min)

1. Clone and run the setup script (safe to re-run):
   ```bash
   git clone https://github.com/SatyajitMall01/reels-studio.git
   cd reels-studio
   bash setup.sh
   ```
   It installs:
   - the Premiere MCP bridge, ffmpeg and local Whisper;
   - the HyperFrames and Instagram skills;
   - earshot and the starter LUTs, sound effects and grain.

   It also creates `.env` and your `studio/director-profile.md` from their templates.
2. In **Premiere Pro** (one time):
   - Settings → Plugins → turn on **UXP developer mode**, then restart Premiere;
   - Window → Extensions → **MCP Bridge (CEP)**;
   - set Temp Directory to `/tmp/premiere-mcp-bridge` → **Save Configuration** → **Start Bridge** → **Test Connection**.
3. Quit and reopen the Claude app (or start `claude` in this folder).

## Making a reel

```bash
scripts/new_reel.sh gym-morning-routine
```
1. Put your main or talking-head clips in `projects/gym-morning-routine/raw/a-roll/` and cutaways in `raw/b-roll/`. If your footage lives somewhere else, link it without copying: `scripts/link_footage.sh gym-morning-routine "/path/to/footage"`.
2. Optionally, put reference reels you like in `references/`.
3. Open Premiere with a project open and the bridge started.
4. Open a **new** Code session at the `reels-studio/` root and say **`/cinematic-reel gym-morning-routine`**.

Claude will:
1. Interview you in two short multiple-choice rounds.
2. Analyse every clip and reference.
3. Write the brief, plus a storyboard and an offline preview. ⏸ *You approve.*
4. Cut a duplicate sequence; your original is never touched.
5. Do the colour (camera-true unless you pick a look), motion, graphics, captions and the sound mix.
6. Pass the scripted checks and an independent review. ⏸ *You review on your phone and give notes; each round is a new version.*
7. Write the Instagram package. ⏸ *You approve; you tap Share.*

The guide covers every phase, rule and tool.

## How the studio runs
- **HQ session** (`/studio-hq`): one chat that owns the architecture, meaning the rules, skills, scripts, hooks and templates.
- **Reel sessions** (`/cinematic-reel <name>`): a new chat per reel, which only touches `projects/<name>/`. A reel session that hits a gap files a change request in `studio/change-requests/` instead of patching the studio.
- A hook (`.claude/hooks/guard_architecture.py`) enforces the split.

Details are in [`studio/ARCHITECTURE.md`](studio/ARCHITECTURE.md), and history is in [`studio/CHANGELOG.md`](studio/CHANGELOG.md).

## Repository layout
```
CLAUDE.md          the editor's operating contract (tracks, guardrails, editing rules)
docs/              the complete guide (Markdown + PDF) and the shooting guide PDF
.claude/           skills (/cinematic-reel, /studio-hq), the reviewer agent, hooks
scripts/           the studio's tools: analysis, previews, storyboards, checks, delivery, sound, After Effects
studio/            architecture, version, changelog, backlog, change requests, retros, plans, guides
projects/_template the folder every new reel starts from
projects/<reel>/   each finished reel's brief, log, retro, research and one-off tools (notes and code only)
assets/            your LUTs, music, SFX, overlays, MOGRTs, presets (folders only; filled locally)
```

## What's not in this repository
The repository is public. It holds the studio's code, rules and each reel's written record, and nothing else:
- **No media.** Camera footage, music, voice, renders, deliveries, fonts, LUTs and sound effects stay on the director's Mac. `setup.sh` regenerates the starter assets.
- **Nothing copyrighted.** No songs, audio from reference reels, or lyric transcripts.
- **Nothing personal.** No `.env`, no director profile, no spend ledgers.

The reel folders' notes describe how each reel was made. Without their media they won't re-render elsewhere.

## Troubleshooting
- **"Premiere not connected"**: Premiere must be open with a project loaded, and the CEP panel must show the bridge as started. If it still fails, right-click the panel → **Reload**.
- **Health check**: `premiere-pro-mcp --doctor`.
- **No transcript**: `scripts/transcribe_reel.sh <reel>` (local Whisper; the first run downloads about 0.5 GB).
- More in the guide, section 20.

## Licence and credits
MIT, see [`LICENSE`](LICENSE). Folders with their own licence keep it. Built on:
- the Adobe Premiere Pro MCP server (hetpatel-11);
- video-use (browser-use);
- HyperFrames (HeyGen);
- earshot (Leonxlnx);
- faster-whisper;
- Openverse;
- the Instagram skills (sergebulaev);
- ffmpeg.

Each is installed by `setup.sh` and keeps its own licence.

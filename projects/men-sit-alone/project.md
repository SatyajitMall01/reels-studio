# Project Log

| Field | Value |
|---|---|
| Reel name | men-sit-alone |
| Status | brief (Phase 0: interview Round 1) |
| Reel type | music-montage |
| Playbook | cinematic-montage (proposed; pace set in Round 2) |
| Arch version | 0.12.0 |
| Pilot | yes |
| Current round | 0 |
| Premiere project | |
| Latest sequence | |
| Latest export | |

## Now
<!-- Rewritten at the end of every round, in at most 30 lines. A new session reads this block and the latest round only (skill Phase 0). -->
- **Status:** Phase 0. Folder created 2026-11-15 (`scripts/new_reel.sh`, arch 0.12.0). Interview Round 1 put to the director. No clips, references or brief yet. Nothing in Premiere.
- **Locked sequence:** none · **Latest export:** none
- **Approved decisions:**
  - Working title: "Men Sit Alone"
  - Hook: —
  - Target runtime: about 60 s
  - Reel type: music-montage (no speech) → playbook cinematic-montage; end feeling: reflect (quiet, lingering ending)
  - Grade: camera-true (v0.12 default, effects-playbook §A0) unless the director picks a look in Round 2
  - Effects: restraint default (effects-playbook §0): real speed, hard cuts, steady camera; designed moves only from the brief's effect list
  - Caption style: —
  - Music / audio route: Instagram audio added at upload → guide copy in the cut, `_mix` (archive) + `_IG` (upload) (CLAUDE.md §4c). Which audio: open
- **Open questions:** the idea in 1–2 sentences; what the clips show and where they live (or not shot yet); who it's for; 1–3 references; which IG audio (song name or reel link) and, if it's another creator's original audio, whether the director has their OK.
- **Next step:** log Round 1 answers → set reel type + playbook → link footage → `ingest_report.py --scan` → analysers → Round 2.

## Friction log
<!-- Pilot reels: one line each time something is slow, fails, needs a guess, a manual step or a workaround. Format: `- [phase] what happened → workaround → CR filed? (CR id / no)` -->

<!-- The editor appends one section per round below: "## Round N — Proposal", "## Round N — Director notes", "## Round N — Changes made". Once this file passes about 4,000 words, move every round but the last two to log/rounds.md. -->

## Round 0 — Setup (2026-11-15)
- Started from the HQ session on the director's request; only the working title is known.
- Studio v0.12.0 (in the working tree, not yet committed): restraint by default; pregate runs `quality_probe.py` against `studio/reference-targets.json` (the "Reel Concepts" collection: median temporal noise 0.08, motion 1.8, 23 of 30 horizontal frames). Night footage: no punch-ins tighter than 80 % width. Landscape footage: the 16:9 film frame is offered first.
- Director profile read: handle @satyajitmall, DIN Condensed Bold fallback, camera-true taste, Blackmagic Cam on iPhone 17. Branding not re-asked.
- No shoot folder for this reel under `~/Documents/Video /` (only KOLKATA2026, Puja/Pujo Oct 15–21, Pujo ki Sobar, Uski Ankehe).

## Round 1 — Interview (asked 2026-11-15)
Questions put: who speaks (→ reel type / playbook) · what viewers should feel or do · length · soundtrack route · in text: the idea in 1–2 sentences, what the clips show and where they are, who it's for, 1–3 references.

### Answers (2026-11-15)
| Question | Answer | Means |
|---|---|---|
| Who speaks | No speech, music only | reel type `music-montage`; playbook `cinematic-montage`; no transcription; beat grid from the guide audio (`gemini_audio_and_beat_analyzer.py`) |
| End feeling | Feel it, reflect | quiet, lingering ending; no hard CTA in the picture |
| Length | About 60 s | longer than the 30–45 s default; runtime follows the chosen audio section |
| Soundtrack | Instagram audio at upload | cut to a stereo guide copy; check the audio's IG page (library song or "Original audio", creator) in Phase 1, not at posting |

Still open (asked in chat): idea, footage location, audience, references, which audio.

## Instagram package
<!-- Filled in after final approval. -->

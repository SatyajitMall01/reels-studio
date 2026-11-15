# Motion graphics, text behind the subject, AI video (skill Phases 2 and 5)

These are three capabilities HQ tested on 2026-10-18 (v0.5.1), inspired by the "Claude edits every video" workflow. Each one has a verified recipe and a known limit.

## 1. Motion graphics (HyperFrames → transparent overlay → Premiere V5)
**Use for:** animated titles, end cards, lower-thirds, stat or map hits, kinetic words. Short, designed and unnarrated.

**How:**
1. Load `/hyperframes`. It routes a short animated title to `/motion-graphics`, which runs a director subagent, then a builder subagent, then checks.
2. Make the project under `projects/<reel>/graphics/<name>/`. Before planning, write its `design.md` from `studio/director-profile.md`:
   - font, with a local file copied in (DIN Condensed Bold on this Mac);
   - palette: cream `#F5E6C8` + gold `#D4A017`;
   - no glitter;
   - safe zone;
   - **25 fps** or the reel's rate;
   - transparent background.
3. Check, then take proof snapshots, then render: `npx hyperframes render --format mov --fps <reel fps> -o renders/<name>-alpha.mov`. That gives **ProRes 4444 with alpha**. The HQ test rendered a 3 s 1080×1920 title in 7 s.
4. Composite-check it over the real shot before placing it: `ffmpeg … overlay` on an exported still.
5. Import it into Premiere on **V5**, above the grade.

**Learned:**
- **Placement is per shot.** The same y that sat clear on the blue Durga landed "2026" on the gold Durga's crown. Choose y from the frame it sits on.
- The `catalog` search finds blocks (e.g. `tracking-in`), so reuse them before hand-building.
- HyperFrames' usage allowance reads as "unknown" on this machine (unsupported auth), so don't guess it.
- **Not yet verified:** the Premiere import of the alpha MOV. Confirm on the first real use: transparency, and that the clip lines up on V5.

## 2. Text behind the subject (local, free)
**Use for:** one hero word passing *behind* the idol or person, e.g. "DURGA" behind the crown. It's a signature moment, at most once or twice per reel.

**How:** `scripts/text_behind.py <clip> --in <s> --dur <s> --text WORD --y <top px> [--x-shift] [--size] -o projects/<reel>/renders/behind/<shot>`.
- It cuts the subject out with HyperFrames' `remove-background` (CPU, about 4 frames/s), stacks the footage, then the glowing word, then the cut-out, and writes ProRes 422 HQ plus a compare strip. It also runs `frame_scan.py`, so any matte flicker gets flagged.
- Place the baked clip on V1 in place of the original shot, **before** colour. It's part of the image now, so it gets graded like the shot. That's intended, because the word lives *in* the scene.

**Where it works** (my-reel tests):

| Shot | Result |
|---|---|
| Idol or person, medium or close-up, contrasting background (blue Durga) | ✅ clean; stable over handheld; 0 scan flags |
| Wide shot, small subject | ⚠️ works, but little is occluded |
| Busy, ornate full-frame close-up (gold Durga) | ❌ the matte turns to mush |

**Limits:**
- The word is fixed to the screen, so only use it on **steady holds** (`motion_holds.py`).
- The model is trained on people, so check every new subject type on a still first. Running `remove-background` on a single `.png` takes seconds.

## 3. AI-generated video (OpenRouter → Google Veo 3.1 Lite or Gemini Omni 1.2 Flash, no audio)
**Claude makes no frames.** Claude (Fable 5.2 included: "Text and images → text", checked 2026-11-10) plans the shot, writes the prompt, picks the anchor stills and checks every frame of the draft. The frames come from a paid video model through `gen_video.py`.

**The bad-footage ladder** (director, 2026-11-10). When a moment's footage is missing or bad, go down this list and stop at the first step that works. Record the steps tried in the brief's AI row:
1. **Fix it locally, free:**
   - shake: Premiere Warp Stabilizer, measured with `shake_report.py`;
   - dropped frames or a jump under about 1 s: After Effects Pixel Motion or Timewarp (`ae_roundtrip.py` `time_remap` `"blend": "pixel"`, `after-effects.md`);
   - noise: AE denoise;
   - soft focus: crop tighter, but only within the 70 % width floor (effects-playbook §B).
2. **Another take** of the same moment from the director's pool.
3. **Free stock**, video and photos, when the director allows stock for the reel (below).
4. **A code-built shot** (HyperFrames, simple 3D) when the moment can be graphic.
5. **A paid AI shot from stills**: Veo 3.1 Lite for a new shot, Gemini Omni for the frames *between* two good stills.

**Policy** (director, 2026-10-18; widened 2026-11-10):
- **Only as the ladder's last step:** for a shot the director's footage can't provide, or one whose footage and free stock are unusable after the free fixes.
- **When the director has allowed stock for the reel, search free stock video *and photos* before proposing an AI shot.** A real photo with a slow push (`conform_clip.py --push 1.06`) can carry a line. Record both searches in the brief's AI row. Kolkata spent $0.64 on an AI tram while Unsplash had about 200 real ones, and the director picked a photo.
- **May show the reel's subjects** (the people, the idol) since 2026-11-10; before that the rule was never. When it does, the label is mandatory, the reviewer checks the faces (below), and real shots of the same person are cut around it, never replaced by it wholesale.
- Every generated shot is listed in `brief.md` as **"AI-generated"**, with its prompt, why it's needed and its cost. The director approves it at **Checkpoint 1**, and approves the chosen draft before its final.
- **No raw footage is ever sent.** At most one or two stills from the director's footage go up as first or last frames, to anchor the look. Everything else (selects, motion, QA, cut-outs, graphics) runs locally and free; the reviewer sees only contact sheets.

**Cost structure** (`studio/ai-budget.json`; `scripts/gen_video.py` enforces it before sending anything):

| | Settings | Cost |
|---|---|---|
| **draft** (default) | 720p · 4 s · no audio · Veo 3.1 Lite | ≈ $0.12 |
| **final** | 1080p · 8 s · no audio · Veo 3.1 Lite | ≈ $0.40 |
| per shot | at most 3 drafts + 1 final | ≈ $0.76 |
| **omni** (`--model omni`) | 3–15 s, a first and/or last still; fills the frames **between** two stills | 720p ≈ $0.07/s, 1080p (upscaled) ≈ $0.10/s; **sound is always billed** (4 s draft ≈ $0.28, 8 s final ≈ $0.83) |
| per reel | at most **$4**, **4 final shots**, **24 s** of generated footage (and keep it under 25 % of the runtime) | |
| per month | at most **$20** (about 4 reels with AI shots) | |

- Audio is **off** by default: reels use the director's music, and audio costs about 60 % more on Lite. Omni has no silent price, so its estimate includes sound; `conform_clip.py` strips any sound it returns.
- A negative prompt goes to Veo as a parameter. Omni takes none, so `gen_video.py` adds it to the prompt as "Avoid: …".
- Prices are read **live** from OpenRouter on every run.
- The ledger (`studio/ledger/ai-spend.jsonl`) records the **actual** charged cost that OpenRouter reports per job.
- Failed generations aren't charged and don't count.

**How:**
1. Pick a still from the director's footage that the shot should continue from (optional, but it cuts retries). Export it with `ffmpeg -ss <t> -i <clip> -frames:v 1 still.png`.
2. Write the prompt with the `film-emulation-prompts` skill.
   - **The camera is cinematic**: shallow depth of field matched to the reel's real shots, an angle and lens with a reason, one steady move (director, 2026-11-11).
   - **The colour is ungraded**: no film stocks, grades, grain or halation, since the reel's V3 look and V4 grain grade the AI shot like every clip.
   - The skill also gives the `--negative` list and the draft check.
   Dry run: `./.venv/bin/python scripts/gen_video.py --reel <reel> --shot <name> --why "<why footage can't>" --prompt "<prompt>" --negative "<avoid>" [--first-frame still.png]`. It prints the cost and every cap, and spends nothing.
3. Put the shot and its draft cost in the brief, and get the director's yes. Run the draft with `--yes`.
4. Check the draft's numbers against its anchor (`film-emulation-prompts`, "Check the draft"), then show it. On a yes, run the final: `--mode final --yes`.
5. The file lands in `projects/<reel>/renders/gen/<shot>_<mode>_<time>.mp4`, with a `.json` sidecar (prompt, cost, the "AI-generated" label).

**Gaps between two good frames:** export the last good frame before the bad stretch and the first good one after it, and pass both (`--model omni --first-frame a.png --last-frame b.png`, 3 s or more; Veo takes both too, at 4, 6 or 8 s). Then conform it and retime it to the gap. A gap under about 1 s goes to After Effects instead (ladder step 1): free, and it doesn't invent new content.

**No fallback provider since v0.10.0.** The Gemini API's Veo `-preview` models were shut down on 2026-10-22. Google's replacement on that API is Omni, which needs a `GEMINI_API_KEY` and is untested here. If OpenRouter is down, wait or ask HQ.

**Higgsfield (MCP): connected in v0.10.3, tested once on C047 (below).** The director asked for it on 2026-11-11, to compare with Omni on gap fills.
- It's in `.mcp.json` as Higgsfield's official server, `https://mcp.higgsfield.ai/mcp`. Sign in with `/mcp`; it needs a paid Higgsfield plan. Tools appear as `mcp__higgsfield__*`.
- **Every Higgsfield tool call asks the director.** A `permissions.ask` rule and the `.claude/hooks/ask_paid_ai.py` hook enforce this, even for calls that spend nothing. The permission prompt is the director's yes. Never answer it for them, and never ask a peer session to.
- **It spends Higgsfield credits, which `gen_video.py` and `ai-spend.jsonl` don't count.** Name the shot, model and expected credits in the brief before the first call.
- **Caps (director, 2026-11-11): 90 credits per reel and 450 credits per calendar month** for the whole studio, HQ tests included. These are on top of the OpenRouter dollar caps. The 4 shots and 24 s per reel count both providers together.
  - Before each paid job, add its `get_cost` price to the reel's total and the month's total in `studio/ledger/higgsfield-credits.jsonl`. If either would go over its cap, stop and ask the director.
  - After the job, append one line to that file (append only, never edit past lines): `time`, `reel`, `shot`, `model`, `job`, `credits`, `balance_after`, `output`. Log it in `project.md` too.
  - Count from this file, not from Higgsfield's `transactions`. The account's history also holds the director's own Higgsfield use.
- The rest of this section still applies:
  - the last step of the ladder;
  - stills only;
  - subjects allowed, never proof;
  - the label;
  - draft before final;
  - the `film-emulation-prompts` block.
- Use it only when the brief names it. For a gap fill on Higgsfield, use Kling 3.0 pro (test below); Seedance 2.0 and Cinema Studio 4.0 don't hold the end frame.
- **Price a job before running it:** call `generate_video` with `params.get_cost: true`, and keep `balance` before and after. The `get_cost` call submits no job; this was verified on 2026-11-11, when the balance stayed 4246.49 and no transaction or generation appeared.

  Prices measured on 2026-11-11 (4 s, 16:9, no stills passed). For the three models in the C047 test, `get_cost` with both stills gave the same price, and the balance dropped by exactly that:

  | Model | Settings | Credits | Notes |
  |---|---|---|---|
  | Veo 3.1 Lite | `generate_audio: false` | 6 | 1080p accepted but not confirmed |
  | Kling 3.0 | `mode: pro`, `sound: off` | 7 | |
  | Omni 1.2 Flash | 720p | 9 | no audio switch |
  | Omni 1.2 Flash | 1080p | 13 | no audio switch |
  | Seedance 2.0 | 1080p, `std` | 48 | |
  | Cinema Studio 4.0 | 1080p, `t2v` or `omni_reference` mode | 64 | only `omni_reference` takes stills |

  The dollar value of a credit depends on the director's plan (`max`) and is unconfirmed, so Higgsfield caps are in credits. At an assumed $0.044 per credit, 90 credits is about $4 and 450 about $20.

- **Gap-fill test on Higgsfield (HQ, 2026-11-11, 119 credits, director approved).** The same C047 stills, prompt and 4 s as the Omni test below, run on Fable 5.2 through the MCP. The balance went from 4246.49 to 4127.49 (`projects/_hqtest/renders/gen/hf_c047_*`, `cmp_c047_splice_kling3_0.json`; measured with `projects/_hqtest/tools/hf_compare.py`).

  | | Kling 3.0 pro (7 cr) | Seedance 2.0 1080p std (48 cr) | Cinema Studio 4.0 1080p (64 cr) | Omni + camera block (OpenRouter, $0.42) |
  |---|---|---|---|---|
  | First frame vs still A (0–255; camera 2.4) | **3.4** | 12.2 | 14.5 | 4.2 |
  | Last frame vs still B (camera 2.4) | **4.3**, at 4.00 s | 37.4: ends on another view | 29.9: ends on another street | 6.9, at 3.96 s |
  | Biggest frame step (camera 0.012) | 0.019 | 0.047 | **0.149: a hard cut at 2.54 s** | 0.016 |
  | Saturation (camera 0.354) | 0.375 | 0.345 | 0.398 | 0.290 |
  | Content | **invents a masked motorbike rider** passing close on the left, 2.3–2.9 s; driver faces forward | new people close on the left; a red "19" sign appears | cuts to an unrelated street; the driver's shirt changes colour | nothing invented near the camera |

  - **Kling 3.0 pro is the best gap fill measured so far**, and the cheapest Higgsfield model tested. Spliced into the real take like Omni (`gap_fill_splice.py`, sigma 1.0, 3-frame dissolves), it used all 4.00 s, and the seams measured 0.012 in and 0.009 out, against the camera's 0.009 frame step. Omni's were 0.012 and 0.011. Its one fault is the invented rider, even though the prompt said "No new vehicles or people close to the auto" and the "Avoid:" list named them. Wording didn't prevent it, so check every Kling draft for invented people and vehicles near the camera, and re-roll one that has them (7 credits). This rests on one test.
  - **Seedance 2.0 and Cinema Studio 4.0 treat the stills as references, not as first and last frames.** They don't land on still B, so they aren't gap-fill models.
  - **Cinema Studio 4.0 needs `mode: "omni_reference"` to take stills.** The default `t2v` mode refuses them with a 422, which isn't charged. `get_cost` doesn't check the mode.
  - None of the three has a negative-prompt parameter. Append " Avoid: " and the negative list to the prompt.
  - Output: 1920×1080, 24 fps, 4.04 s, no audio. Kling and Seedance return H.264, and Cinema Studio returns HEVC. `conform_clip.py` retimes and re-encodes them.
  - Stills uploaded with `media_upload` stay in the Higgsfield account.

**Facts:**
- 9:16 is supported, at 4, 6 or 8 s.
- Every Veo clip has Google's **SynthID** AI watermark (Omni: assumed the same, not verified).
- **Gap-fill test, Veo vs Omni (HQ, 2026-11-11, $0.40, director approved).** Both models got the same first and last stills, 4 s apart, from Diwali C047: an auto driver from the back seat at night, with the auto rolling forward. The real 4 s between the stills was the ground truth (`projects/_hqtest/renders/gen/cmp_c047_*`).

  | | Veo 3.1 Lite ($0.12) | Gemini Omni 1.2 Flash ($0.28) |
  |---|---|---|
  | First frame vs still A (0–255) | 2.5, same as the camera | 4.1 |
  | Lands on still B | ends 8.1 off; closest at 3.68 s | ends 9.4 off; closest at 3.68 s |
  | Motion | smooth: biggest frame step 0.022, against the camera's 0.012 | **pops** at 3.36 s: one frame step of 0.106 (9×) as it snaps toward still B |
  | Content | **invents traffic**: a white car, and a man on a red motorbike with his face visible, passing beside the auto | keeps the street close to the real one, but **turns the driver's head into profile** despite "Avoid: the driver's face", and moves his hands |

  - **Round 2: Omni with the cinematic camera block** (`film-emulation-prompts`), at 1080p, 4 s, for $0.42. It came out best of the three:
    - **no pop** (biggest frame step 0.017);
    - lands on still B at 3.96 s;
    - the driver faces forward throughout;
    - nothing invented near the camera;
    - the street falls off softly.

    **The camera block fixed what the plain prompt broke.** "The motion stays smooth and continuous right to the last frame" plus naming what stays sharp removed the end snap and the head turn.
  - **Pick:** Omni with the camera block for gap fills on OpenRouter; Veo Lite for cheap first drafts of a new idea. Kling 3.0 pro on Higgsfield landed closer (above), within its credit caps. This rests on one test, so re-check it on the next reel.
  - **Round 3, depth-aware clarity:**
    - the AI fill's background was blurred (sigma 2.4) until its detail matched the real bokeh (0.0061 against 0.0056);
    - its near plane was softened (sigma 0.8) until it matched the real near plane after clarity (0.0141 against 0.0132);
    - the masks come from the real depth map at the same moment (the interior is fixed to the camera).

    The AI stretch's separation went from 1.18 to 2.30, against the real parts' 2.36. Effects-playbook §B; `projects/_hqtest/tools/depth_clarity.py`.
  - **An AI fill comes out crisper and paler than the director's camera.** Omni was 1.4× sharper (Laplacian 0.107 against 0.075) and 10 % less saturated. Before Premiere:
    - soften it to the camera's measured sharpness (`gblur` sigma 1.0 here);
    - match saturation and colour;
    - dissolve 3 frames at each seam.

    The seams then measured 0.012 and 0.011, against the camera's 0.009 frame step. The scratch tools that did this are `projects/_hqtest/tools/gap_fill_splice.py` and `gap_fill_compare.py`; `scripts/gap_fill.py` is in the v0.14 tools backlog.
  - **Omni always returns sound** (AAC; OpenRouter refuses `generate_audio: false` with a 400 that isn't charged). `gen_video.py` asks for it, and `conform_clip.py` strips it.
  - Neither model landed exactly on its last still. **Never cut straight from a gap-fill's last frame into the real shot**: cut at the frame closest to the still, or dissolve 2–4 frames.
- OpenRouter's video generation isn't eligible for zero data retention: providers keep outputs briefly.
- Google direct deletes videos after 2 days.
- Typical generation time is 30 s to a few minutes.

**Verified (2026-10-18, first real call, $0.12):**
- OpenRouter charged exactly the estimate.
- The output was 9:16 (720×1280), exactly 4.0 s, with **no audio track** (audio off is honoured).
- A `data:` URL first frame works: output frame 0 matched our C027 still (mean difference 0.6 on 0–255).
- The motion was a smooth push; `frame_scan.py` found 0 flags.
- **Veo outputs 24 fps.** Conform it to the reel's rate on import (`set_override_frame_rate`, as for 24 fps camera clips), or the sequence will repeat frames.
- Veo may "clean up" small details from the first frame: in the test it dropped a phone in the corner. Check the draft against the source still.

**Rules for using an AI shot** (also in each playbook's AI section):
- **Never proof.** No fake crowds, results, screens, dashboards or people saying things. An AI shot can set a scene, bridge one or repair one; it can never show something that didn't happen.
- **Never two in a row**, and at most about one a minute. Cut AI shots between real footage.
- **The exact scene the moment needs**, 2–5 s on screen. Use the best stretch, not the whole clip.
- **Check the draft against its source still** before asking for the final (Veo drops small details: see above). Look at every frame of the draft's contact sheet, not just the first.
- **Label it.** It's "AI-generated" in the brief and in `project.md`. At posting, **turn on Instagram's AI info label**: Veo clips carry Google's SynthID watermark, so Instagram may detect them anyway. A reel that AI only *edited*, from real footage, gets the caption's AI-credit line and **no** label (`instagram-strategy.md`).

**Conform before it goes in Premiere** (`scripts/conform_clip.py`; local, free):
```
./.venv/bin/python scripts/conform_clip.py projects/<reel>/renders/gen/<shot>_final_<time>.mp4 \
    -o projects/<reel>/renders/gen/<shot>_conformed.mov --fps 25 --start 0.5 --match <source still>
```
- Retimes frame for frame to the reel's rate (Veo's 24 → 25 plays 4 % fast, so every frame plays once) instead of the sequence repeating frames.
- `--start 0.5` skips the model's settle-in at the start of the clip.
- Scales and crops to 1080×1920, strips audio, writes ProRes 422 HQ with BT.709 tags.
- `--match <still>` pulls the clip's colour toward the director's footage (a mean/std transfer at `--strength 0.5`, written as a `.cube`), so the grade starts close.
- The same tool conforms stock clips, and turns a still into a slow push-in (`--push 1.06`).
- Check `<out>_sheet.png` (first, middle and last frames beside the match still).

**Then:** primary-correct and match the conformed shot like any other clip, and run it through the review gate like everything else.

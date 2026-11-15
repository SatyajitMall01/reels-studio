# Playbook: creator-explainer

**For:** someone talking to camera: explainers, tips, stories, opinions, with captions, graphics and cutaways (reel type `talking-head`; the spoken stretches of a `hybrid`).
**Status: untested in this studio.** It's adapted from the WeAreNoCode "YouTube Editor" skill (Nishant Chahar's editing system, built on 16:9 YouTube, kept as a read-only reference in `assets/reference-kits/WeAreNoCode-YouTube-Editor/`). The numbers come from his notes on real videos, converted to 9:16 Instagram Reels in Premiere. **The first talking-head reel is this playbook's pilot**: log every rule that doesn't fit as a CR.

## Pace and structure
- **The first 3 seconds give a specific reason to stay**, which the reel pays off. One main open loop.
- **Keep the last take of every line.** Honour spoken markers ("cut that", "take two", "let me redo"); the marker and the line before it go.
- **Dead air:** none over 0.25 s (CLAUDE.md §4b, stricter than his 0.40 s); a deliberate pause only where the brief says so.
- **Cuts are checked by the audio, not the transcript.** A word clipped at a cut edge passes a transcript check. That's his most important finding, and v0.7.0 will add an audio cut-audit tool.
- **About 6 overlay moments per 37 s** in the hook stretch. A card holds 3–7 s; past 7 s it needs internal motion (a count-up, staggered items).

## Camera and motion
- **Zoom anchored to the top of the frame**, so a centre zoom never crops the head.
- **Punch-in on emphasis** (the number, the promise, the punchline): 118–125 % over 0.30–0.35 s, ease-out. These emphasis zooms are this playbook's one standing entry on the brief's effect list (effects-playbook §0): list them once, with their count. On night or noisy footage, use cuts instead of zooms.
- **Slow creep across a thought:** 110–112 % over 5–10 s, released at the next cut.
- **Snap back to 100 % at every cut;** never carry a zoom across a cut.
- **Limits:** 1080p source up to 112 %; 4K source up to 150 %. The base framing still shows ≥ 80 % of the camera width (effects-playbook §B); these zooms are named moves on top of it.
- **Budget:** 3–5 camera moves per 40 s hook. Jump cuts stay plain by default; dress one only when the energy changes (a pivot, a joke landing), at most one per 10 s.

## Type and graphics
- **Captions:** word-exact on the kept words, 2–4 words a line, inside the safe zone (CLAUDE.md §3). Hero type 88–110 px at 1080×1920; caption block about 280–320 px above the bottom, clear of the Instagram buttons.
- **A card never covers the face.** Measure where the face sits per shot and put cards opposite it. If the copy won't fit, make it a lower line rather than shrinking the card.
- **One hero element at a time.** Enter in 0.4 s (ease-out), exit in 0.35 s; no bounces, no 3D flips, no animated blur.
- **Lists aren't panels:** each item becomes its own beat (pills beside the head, one animation per number).
- **If the frame already shows it, don't say it again on screen.**
- **Style:** the director profile's type style (DIN Condensed Bold, cream/gold), not his glass cards and cyan. Only his *rules* carry over, not his look.

## Transitions
- **Hard cuts.** Cutaways sit on jump cuts, to hide them. No flash cuts.

## Sound
- **Silence is the default; every sound needs a visible cause.** A pop when a logo lands, a click on an on-screen click, typing only during real typing. Nothing "for energy".
- **Never a whoosh or swish under text or a card.** Text arrives on motion, not on a sweep. That's the most common mistake in his notes.
- **One or two sounds per hook.** Eight in a 38 s hook was "way too busy".
- **Prepare every SFX** with `sfx_prep.py`, and place it by its transient, within 2 frames of its cause.
- **Music:** some tension under the hook, then a low bed ducked about 16 dB under the voice in the hook and about 19 dB in the body. The voice is the reference.
- **Mixed version:** −14 LUFS ± 2, true peak ≤ −1 dBTP (`verify_render.py`).

## Colour and texture
- Camera-true, clean natural skin first (effects-playbook §A0–A1). A look only if the director picks one (§A3); little or no grain.

## AI shots
- His rule: **AI shots star the creator or nobody**, show the exact scene the sentence describes, last 2–5 s, and are **never proof** (no fake dashboards, results or crowds). At most about one a minute, never two in a row. Also `motion-and-ai.md` §3.

## QA thresholds for this style (review gate)
- No clipped words at any cut: once the audio cut audit exists, run it and fix to 0 issues.
- No pause over 0.25 s unless the brief marks it.
- No card or caption over the face, in any frame.
- No sound without a visible cause; no whoosh under text.

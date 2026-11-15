#!/usr/bin/env python3
"""Pregate: the scripted checks that run before the LLM review gate (review-gate.md step 2). Minutes, no tokens.

In the first five reels the gate ran 59 times and failed 47, at about 200k tokens a run. Most FAILs were things a
script can see. This runs them first, and the reviewer is only called on a clean pregate:

  1. verify_render.py   the file: codec, profile, bitrate, size, fps, tags, black/frozen frames, loudness   FAIL → stop
                        (black inside a fade or end-card span is allowed)
  2. frame_scan.py      every frame: blur dips, frozen runs, luma jumps, black/white frames.
                        A flag inside a --designed span is expected ONLY if the span's type expects that flag
                        (v0.10.2: a step-print expects holds, not blur; an end card black and freeze). Any other
                        flag  FAIL → stop (look at it, then fix it, or type the span and say why in project.md)
  2b. motion_audit.py   camera shake per shot (the frame's outer ring, so a moving subject isn't counted):
                        a step-print whose held images jump > 4 px                                         FAIL → stop
                        camera jerk p95 > 6 or a jump > 8 px  → REVIEW: the reviewer must judge that shot on its
                        full-rate strip. The editor can't waive it (CR gate-missed-glitch).
  2c. quality_probe.py  per shot against the director's saved references (studio/reference-targets.json, v0.12):
                        grain/noise above the FAIL line                                                    FAIL → stop
                        (replace or re-frame the shot; --allow-noise <shot> only after the director accepts it)
                        noise over the WARN line, busy motion, flicker, repeated frames or jumps inside a shot → WARN,
                        and the shot gets a full-rate strip for the reviewer
  3. camera_fidelity.py each shot against its camera file: brightness, colour, crush, burn, framing         FAIL → stop
                        (skipped with --no-fidelity, or when the map has no camera clips)
  3b. sfx_sync.py       every sound effect found in the export's own audio (its file's waveform, GCC-PHAT): missing,
                        or more than 2 frames off its plan                                                FAIL → stop
                        weak match, level off the plan, or under the mix in every band → WARN: listen at that time.
                        Runs when the --map EDL has an `audio` list with effects, or with --sfx-cues; with earshot
                        installed it also draws sfx/sound_sheet.png (frames, events, spectrogram, loudness) for the reviewer.
  4. render_diff.py     with --reviewed: what changed since the last version that PASSED the gate, so the review can
                        be focused. Not merely the previous export: after an unreviewed in-between version the
                        scope would miss changes (kolkata v8 → v8b missed the title). --prev is the old name.
  5. watch.py           2 fps contact sheets for the reviewer (only when 1–3 pass)
  5b. strips            every frame (the sequence's fps) of the hook (0–3 s), of every designed span and of every
                        REVIEW shot, in strips/. 2 fps sheets can't show an 8 Hz jerk; these can.
A check that crashes or leaves no output counts as a FAIL. Old outputs in -o are cleared first.

Writes into -o: shots.json (from the map, for the gate), <export>_VERIFY.md, scan.json, fidelity/, diff.json, watch/
and PREGATE.md, which says PASS/FAIL and the review scope. Exit 1 on FAIL.

Usage (from the studio root):
  ./.venv/bin/python scripts/pregate.py projects/<reel>/renders/exports/<reel>_v4.mp4 \
      --map projects/<reel>/analysis/map_v4.json -o projects/<reel>/analysis/pregate_v4 \
      --fps 25 --expect 29.84 --designed 0-1.56:step-print 27.3-29.84:end-card [--window 0,505,1080,810] \
      [--reviewed projects/<reel>/renders/exports/<reel>_v3.mp4 --reviewed-map projects/<reel>/analysis/map_v3.json] \
      [--allow 01_C010] [--allow-noise 05_C044] [--exclude-band 0.72,0.82] [--look] [--profile ig-quiet] [--min-mbps 12] \
      [--sfx-cues projects/<reel>/analysis/sfx_cues_v4.json]
--designed takes typed spans in seconds of reel time, T0-T1:type. Types and the scan flags each one expects:
  fade (black, luma_jump) · end-card (black, frozen, luma_jump, blur_dip, white) · title (frozen, blur_dip, luma_jump)
  step-print (frozen; plus the hold-shift check) · flash (luma_jump, white, blur_dip) · transition (blur_dip, luma_jump)
  freeze (frozen). An untyped span allows black only, and pregate says so.
--window x,y,w,h: the picture's window in the export (a 4:3 or 4:5 window), for the motion audit.
The map is camera_fidelity.py's shot map (name, start, end, clip, src_in, rate), or the EDL preview_edl.py renders;
shots without a clip are fine. For an offline preview, pass --profile ig-quiet: its audio isn't loudness-normalised.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
sys.path.insert(0, str(HERE))
from media_info import fps_of  # noqa: E402

# Which frame_scan flags each type of designed span expects (v0.10.2). An untyped span allows black only.
SPAN_FLAGS = {
    "fade": {"black", "luma_jump"},
    "end-card": {"black", "frozen", "luma_jump", "blur_dip", "white"},
    "title": {"frozen", "blur_dip", "luma_jump"},
    "step-print": {"frozen"},
    "flash": {"luma_jump", "white", "blur_dip"},
    "transition": {"blur_dip", "luma_jump"},
    "freeze": {"frozen"},
    "untyped": {"black"},
}


def run(args: list[str]) -> tuple[int, str]:
    p = subprocess.run([PY, *args], capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def last_line(txt: str) -> str:
    lines = [ln for ln in txt.splitlines() if ln.strip()]
    return lines[-1][-300:] if lines else "no output"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("export", type=Path)
    ap.add_argument("--map", type=Path, required=True)
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--reviewed", "--prev", dest="prev", type=Path,
                    help="the last export that PASSED the review gate (not just the previous export)")
    ap.add_argument("--reviewed-map", "--prev-map", dest="prev_map", type=Path,
                    help="that version's map, to tell a moved cut from a changed shot")
    ap.add_argument("--fps", type=float)
    ap.add_argument("--expect", type=float, help="expected duration, s")
    ap.add_argument("--profile", choices=["mix", "ig-quiet"], default="mix")
    ap.add_argument("--min-mbps", type=float, default=12.0)
    ap.add_argument("--designed", nargs="*", default=[], metavar="T0-T1:type",
                    help="typed spans (s) where some scan flags are intended: fade, end-card, title, step-print, flash, transition, freeze")
    ap.add_argument("--window", help="x,y,w,h of the picture in the export, for the motion audit (default the whole frame)")
    ap.add_argument("--allow", nargs="*", default=[], help="shots whose fidelity FAILs are deliberate (in the brief)")
    ap.add_argument("--allow-noise", nargs="*", default=[], help="shots whose grain/noise FAIL the director accepted "
                    "(quality_probe --allow; note it in project.md)")
    ap.add_argument("--exclude-band", action="append", default=[], metavar="Y0,Y1")
    ap.add_argument("--look", action="store_true", help="a creative look is on (camera_fidelity --look)")
    ap.add_argument("--no-fidelity", action="store_true")
    ap.add_argument("--sfx-cues", type=Path, help="the sound effects as placed, when the --map has no EDL audio list: "
                                                    "[{id, file, start, in, dur, gain_db}] (sfx_sync.py)")
    a = ap.parse_args()

    if not a.export.exists():
        sys.exit(f"No export {a.export}")
    out = a.out
    out.mkdir(parents=True, exist_ok=True)
    for old in ("scan.json", "diff.json", "PREGATE.md", "shots.json", "motion.json", "strips.json", "quality.json", "QUALITY.md"):
        (out / old).unlink(missing_ok=True)
    for old in ("fidelity", "watch", "strips", "sfx"):
        shutil.rmtree(out / old, ignore_errors=True)
    smap = json.loads(a.map.read_text())
    smap = smap["shots"] if isinstance(smap, dict) else smap         # an EDL (preview_edl.py) or a plain map
    shots = [[s["name"], s["start"], s["end"]] if isinstance(s, dict) else list(s) for s in smap]
    (out / "shots.json").write_text(json.dumps(shots, indent=1))
    designed, untyped = [], []
    for span in a.designed:
        times, _, kind = span.partition(":")
        t0, t1 = (float(x) for x in times.split("-"))
        kind = kind.strip().lower() or "untyped"
        if kind not in SPAN_FLAGS:
            sys.exit(f"--designed {span}: unknown type {kind!r} (types: {', '.join(k for k in SPAN_FLAGS if k != 'untyped')})")
        if kind == "untyped":
            untyped.append(span)
        designed.append((t0, t1, kind))
    black_ok = [f"{t0:g}-{t1:g}" for t0, t1, kind in designed if "black" in SPAN_FLAGS[kind]]
    seq_fps = a.fps or fps_of(a.export)
    rows: list[tuple[str, str, str]] = []
    hard_fail = False

    # 1. the file
    args = [str(HERE / "verify_render.py"), str(a.export), "--profile", a.profile, "--min-mbps", str(a.min_mbps), "--out", str(out)]
    if black_ok:
        args += ["--allow-black", *black_ok]
    if a.fps:
        args += ["--fps", str(a.fps)]
    if a.expect:
        args += ["--expect", str(a.expect)]
    rc, txt = run(args)
    fails = [ln.strip() for ln in txt.splitlines() if ln.startswith("FAIL")]
    rows.append(("FAIL" if rc else "PASS", "verify_render", "; ".join(fails) or (last_line(txt) if rc else "all file checks pass")))
    hard_fail |= rc != 0

    # 2. every frame
    rc, txt = run([str(HERE / "frame_scan.py"), str(a.export), "-o", str(out / "scan.json"), "--shots", str(out / "shots.json")])
    if rc or not (out / "scan.json").exists():
        rows.append(("FAIL", "frame_scan", f"didn't run: {last_line(txt)}"))
        hard_fail = True
    else:
        flags = json.loads((out / "scan.json").read_text())["flags"]
        def expected(f):
            return any(t0 - 0.05 <= f["t0"] and f["t1"] <= t1 + 0.05 and f["type"] in SPAN_FLAGS[kind] for t0, t1, kind in designed)
        loose = [f for f in flags if not expected(f)]
        detail = "; ".join(f"{f['type']} {f['shot']} {f['t0']}–{f['t1']} s ({f['value']})" for f in loose)
        if loose and untyped:
            detail += f" · untyped span(s) {', '.join(untyped)} allow black only: give each a type (fade, end-card, …)"
        rows.append(("FAIL" if loose else "PASS", "frame_scan",
                     detail or f"{len(flags)} flag(s), each one expected by its span's type"))
        hard_fail |= bool(loose)

    # 2b. camera motion: step-print holds (FAIL) and shake over the limits (REVIEW, on full-rate strips)
    review_shots: list[tuple[str, float, float]] = []
    args = [str(HERE / "motion_audit.py"), str(a.export), "--shots", str(out / "shots.json"), "-o", str(out / "motion.json"),
            "--fps", f"{seq_fps:g}"]
    steps = [f"{t0:g}-{t1:g}" for t0, t1, kind in designed if kind == "step-print"]
    if steps:
        args += ["--step-print", *steps]
    if a.window:
        args += ["--window", a.window]
    rc, txt = run(args)
    if not (out / "motion.json").exists():
        rows.append(("FAIL", "motion_audit", f"didn't run: {last_line(txt)}"))
        hard_fail = True
    else:
        mo = json.loads((out / "motion.json").read_text())["shots"]
        bad = [m for m in mo if m["verdict"] == "FAIL"]
        review_shots = [(m["shot"], m["t"][0], m["t"][1]) for m in mo if m["verdict"] == "REVIEW"]
        if bad:
            rows.append(("FAIL", "motion_audit", "; ".join(f"{m['shot']}: {m['why']}" for m in bad)))
        rows.append(("REVIEW" if review_shots else "PASS", "motion_audit",
                     ("; ".join(f"{m['shot']}: {m['why']}" for m in mo if m["verdict"] == "REVIEW")
                      + " → the reviewer judges these on strips/ (not waivable)") if review_shots
                     else f"{len(mo)} shots within the motion limits" + (f", {len(steps)} step-print(s) steady" if steps else "")))
        hard_fail |= bool(bad)

    # 2c. picture quality against the director's references: grain FAILs, the rest WARN with a strip
    quality_shots: list[tuple[str, float, float]] = []
    args = [str(HERE / "quality_probe.py"), str(a.export), "--shots", str(out / "shots.json"), "-o", str(out / "quality.json")]
    if designed:
        args += ["--designed", *[f"{t0:g}-{t1:g}" for t0, t1, _ in designed]]
    if a.allow_noise:
        args += ["--allow", *a.allow_noise]
    if a.window:
        args += ["--window", a.window]
    rc, txt = run(args)
    if not (out / "quality.json").exists():
        rows.append(("FAIL", "quality_probe", f"didn't run: {last_line(txt)}"))
        hard_fail = True
    else:
        q = json.loads((out / "quality.json").read_text())
        bad = [x for x in q["shots"] if x["verdict"] == "FAIL"]
        warn = [x for x in q["shots"] if x["verdict"] == "WARN"]
        quality_shots = [(x["shot"], float(x["t"][0]), float(x["t"][1])) for x in warn]
        head = f"noise {q['reel_temporal_noise']} · motion {q['reel_motion']} (references {q['targets']['temporal_noise']} · {q['targets']['motion']})"
        if bad:
            rows.append(("FAIL", "quality_probe", head + "; " + "; ".join(f"{x['shot']}: {x['why']}" for x in bad)))
        if warn:
            rows.append(("WARN", "quality_probe", head + "; " + "; ".join(f"{x['shot']}: {x['why']}" for x in warn)
                         + " → strips for the reviewer; see QUALITY.md"))
        elif not bad:
            rows.append(("PASS", "quality_probe", head + f"; {len(q['shots'])} shots within the reference targets"))
        hard_fail |= bool(bad)

    # 3. against the camera
    has_clips = any(isinstance(s, dict) and s.get("clip") for s in smap)
    if a.no_fidelity or not has_clips:
        rows.append(("SKIP", "camera_fidelity", "--no-fidelity" if a.no_fidelity else "no camera clips in the map"))
    else:
        args = [str(HERE / "camera_fidelity.py"), str(a.export), "--map", str(a.map), "-o", str(out / "fidelity")]
        if a.allow:
            args += ["--allow", *a.allow]
        if a.look:
            args.append("--look")
        for band in a.exclude_band:
            args += ["--exclude-band", band]
        rc, txt = run(args)
        fj = out / "fidelity" / "fidelity.json"
        if not fj.exists():
            rows.append(("FAIL", "camera_fidelity", f"didn't run: {last_line(txt)}"))
            hard_fail = True
        else:
            rep = json.loads(fj.read_text())
            bad = [n for n, v in rep["shots"].items() if v.get("verdict") == "FAIL"]
            allowed = [n for n, v in rep["shots"].items() if v.get("verdict") == "ALLOWED"]
            detail = ("FAIL on " + ", ".join(bad)) if bad else "every shot within the camera bands"
            if allowed:
                detail += f" (allowed: {', '.join(allowed)})"
            rows.append(("FAIL" if bad or rc else "PASS", "camera_fidelity", detail + "; see fidelity/FIDELITY.md for WARNs"))
            hard_fail |= bool(bad) or rc != 0

    # 3b. the sound effects, in the export's own audio
    sfx_args = None
    if a.sfx_cues:
        sfx_args = ["--cues", str(a.sfx_cues)]
    elif isinstance(json.loads(a.map.read_text()), dict) and json.loads(a.map.read_text()).get("audio"):
        sfx_args = ["--edl", str(a.map)]
    if sfx_args is None:
        rows.append(("SKIP", "sfx_sync", "no sound-effect list (an EDL --map with `audio`, or --sfx-cues)"))
    else:
        rc, txt = run([str(HERE / "sfx_sync.py"), str(a.export), *sfx_args, "-o", str(out / "sfx"), "--fps", f"{seq_fps:g}",
                       "--sheet"])
        sj = out / "sfx" / "sfx_sync.json"
        if not (out / "sfx" / "SFX_SYNC.md").exists():
            rows.append(("FAIL", "sfx_sync", f"didn't run: {last_line(txt)}"))
            hard_fail = True
        elif not sj.exists():
            rows.append(("SKIP", "sfx_sync", "the list has no sound effects (music and guides are skipped)"))
        else:
            rep = json.loads(sj.read_text())
            bad = [x for x in rep["sounds"] if x["verdict"] == "FAIL"]
            warn = [x for x in rep["sounds"] if x["verdict"] == "WARN"]
            detail = "; ".join(f"{x['id']}: {x['why']}" for x in bad + warn) or \
                f"{len(rep['sounds'])} effect(s) found, each within 2 frames of its plan"
            rows.append(("FAIL" if bad else "WARN" if warn else "PASS", "sfx_sync",
                         detail + (" → listen at those times (sfx/SFX_SYNC.md)" if warn and not bad else "")))
            hard_fail |= bool(bad)

    # 4. what changed
    scope = "full review (first review of this cut)"
    changed: list[str] = []
    if a.prev:
        if not a.prev_map:
            rows.append(("INFO", "render_diff", "no --reviewed-map, so a moved cut can't be ruled out: full review"))
        args = [str(HERE / "render_diff.py"), str(a.prev), str(a.export), "-o", str(out / "diff.json"), "--shots", str(a.map)]
        if a.prev_map:
            args += ["--prev-shots", str(a.prev_map)]
        rc, txt = run(args)
        if rc or not (out / "diff.json").exists():
            rows.append(("FAIL", "render_diff", f"didn't run: {last_line(txt)}"))
            hard_fail = True
        else:
            d = json.loads((out / "diff.json").read_text())
            scope, changed = d["scope"], d["changed_shots"]
            spans = ", ".join(f"{s['t0']}–{s['t1']} s" for s in d["changed_spans"])
            what = spans or ("different length" if d["frames"][0] != d["frames"][1] else "no picture change")
            rows.append(("INFO", "render_diff", f"{d['structure']} structure, audio {'identical' if d['audio_identical'] else 'changed'}; {what}"))

    # 5. sheets for the reviewer
    if not hard_fail:
        rc, txt = run([str(HERE / "watch.py"), str(a.export), "-o", str(out / "watch"), "--fps", "2", "--shots", str(out / "shots.json")])
        rows.append(("PASS" if rc == 0 else "FAIL", "watch", "contact sheets in watch/" if rc == 0 else last_line(txt)))
        hard_fail |= rc != 0
        # 5b. every frame where 2 fps can't see: the hook, the designed spans, the REVIEW shots
        dur = max(float(s[2]) for s in shots) if shots else 3.0
        spans = [["hook_0-3s", 0.0, min(3.0, dur)]] + [[f"designed_{kind}_{t0:g}-{t1:g}", t0, t1] for t0, t1, kind in designed] \
            + [[f"review_{n}", t0, t1] for n, t0, t1 in review_shots] \
            + [[f"quality_{n}", t0, t1] for n, t0, t1 in quality_shots if n not in {r[0] for r in review_shots}]
        (out / "strips.json").write_text(json.dumps(spans, indent=1))
        rc, txt = run([str(HERE / "watch.py"), str(a.export), "-o", str(out / "strips"), "--fps", f"{seq_fps:g}",
                       "--shots", str(out / "strips.json"), "--per-sheet", "40", "--cols", "8", "--tile", "216"]
                      + (["--crop", a.window] if a.window else []))
        rows.append(("PASS" if rc == 0 else "FAIL", "strips", f"{len(spans)} full-rate strip(s) in strips/ ({seq_fps:g} fps)"
                     if rc == 0 else last_line(txt)))
        hard_fail |= rc != 0

    verdict = "FAIL" if hard_fail else "PASS"
    if not hard_fail and review_shots:
        scope += f"; full-rate verdicts needed on {len(review_shots)} REVIEW shot(s)"
    md = [f"# Pregate: {a.export.name}", "", f"**{verdict}**" + ("" if hard_fail else f" · review scope: **{scope}**"
          + (f" ({', '.join(changed)})" if changed and scope.startswith("focused") else "")), "",
          "| Check | Result | Detail |", "|---|---|---|"]
    md += [f"| {c} | {r} | {d} |" for r, c, d in rows]
    md += ["", "Fix every FAIL before calling the reviewer. On PASS, give the reviewer this folder: `shots.json`, `scan.json`, "
           "`motion.json`, `QUALITY.md`, `watch/index.md`, **`strips/index.md` (every frame of the hook, the designed spans and the REVIEW "
           "shots: the reviewer must give each a verdict)**, `fidelity/FIDELITY.md` + `fidelity/fidelity_sheet.jpg`, and "
           "`diff.json` for a focused review, plus `sfx/SFX_SYNC.md` and `sfx/sound_sheet.png` when the reel has sound effects."]
    (out / "PREGATE.md").write_text("\n".join(md) + "\n")
    for r, c, d in rows:
        print(f"{r:5s} {c:16s} {d}")
    print(f"\n{verdict} · {out / 'PREGATE.md'}" + ("" if hard_fail else f" · {scope}"))
    sys.exit(1 if hard_fail else 0)


if __name__ == "__main__":
    main()

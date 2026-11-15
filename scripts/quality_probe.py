#!/usr/bin/env python3
"""Per-shot picture quality against the director's saved references: grain, busyness, flicker, cadence (v0.12).

The 2026-11-15 diagnosis (studio/reviews/quality-diagnosis-2026-11-15.md) found the director's "glitchy, flickering,
unnatural, grainy" came from noise, camera motion and treatment that no existing check measured. This measures, for
every frame (luma at 540x960, inside --window when the picture sits in a window):
  temporal noise   frame-to-frame change in flat 16x16 blocks after removing any whole-frame brightness shift:
                   grain or noise "boiling". Punch-ins, high ISO and added grain raise it.
  motion           mean frame-to-frame change: how busy the camera and subject are.
  flicker          whole-frame brightness shift minus its 5-frame average (fades cancel, pulses stay): its RMS and peak.
  cadence          repeated frames (a conform or interpretation fault) and jumps inside a shot (dropped frames, steps).
Each shot gets PASS / WARN / FAIL against studio/reference-targets.json (the Reel Concepts medians and thresholds).
Only noise can FAIL; motion, flicker and cadence WARN, and the reviewer looks at those shots.
A shot in --allow (the director accepted it, noted in project.md) is reported but never FAILs.
Spans in --designed (T0-T1, reel seconds) skip the cadence and flicker flags: a step-print or a fade is meant to do that.

Usage:
  ./.venv/bin/python scripts/quality_probe.py <export.mp4> --shots shots.json -o quality.json [--window x,y,w,h]
      [--designed 0-1.56 27.3-29.84] [--allow 05_C044]
  ./.venv/bin/python scripts/quality_probe.py <camera_clip.mov> --whole -o cam.json     (one span: is a source already noisy?)
shots.json: [[name, start, end], ...] (pregate writes it from the map). Writes the JSON report plus QUALITY.md beside it.
Exit 1 when any shot FAILs.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ROOT / "studio" / "reference-targets.json"
W = 540


def probe(p: Path) -> tuple[int, int, float, float]:
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,avg_frame_rate:format=duration", "-of", "json", str(p)],
                       capture_output=True, text=True).stdout
    d = json.loads(o or "{}")
    s = d["streams"][0]
    n, m = s["avg_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), float(n) / float(m or 1), float(d["format"]["duration"])


def frames(p: Path, window: str | None, w: int, h: int):
    vf = []
    if window:
        x, y, ww, hh = (int(float(v)) for v in window.split(","))
        vf.append(f"crop={ww}:{hh}:{x}:{y}")
        w, h = ww, hh
    oh = max(16, int(round(h * W / w / 16)) * 16)
    vf.append(f"scale={W}:{oh}:flags=area,format=gray")
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(p), "-vf", ",".join(vf), "-f", "rawvideo", "-"],
                          stdout=subprocess.PIPE)
    size = W * oh
    while True:
        b = pr.stdout.read(size)
        if len(b) < size:
            break
        yield np.frombuffer(b, np.uint8).reshape(oh, W).astype(np.float32)
    pr.wait()


def per_frame(p: Path, window: str | None):
    w, h, fps, _ = probe(p)
    D, G, TN = [0.0], [0.0], [np.nan]
    prev = None
    for f in frames(p, window, w, h):
        hh, ww = (f.shape[0] // 16) * 16, (f.shape[1] // 16) * 16
        f = f[:hh, :ww]
        if prev is not None:
            df = f - prev
            D.append(float(np.abs(df[::4, ::4]).mean()))
            m = np.abs(df) < 12
            g = float(df[m].mean()) if m.mean() > 0.2 else 0.0
            G.append(g)
            flat = f.reshape(hh // 16, 16, ww // 16, 16).std(axis=(1, 3)) < 3.0
            bt = np.abs(df - g).reshape(hh // 16, 16, ww // 16, 16).mean(axis=(1, 3))
            TN.append(float(np.median(bt[flat])) if flat.sum() > 20 else np.nan)
        prev = f
    return fps, np.array(D[: len(G)]), np.array(G), np.array(TN)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("--shots", type=Path, help="[[name, start, end], ...]")
    ap.add_argument("--whole", action="store_true", help="treat the whole file as one shot (camera clips)")
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--window", help="x,y,w,h of the picture in the frame")
    ap.add_argument("--designed", nargs="*", default=[], metavar="T0-T1", help="designed spans: no cadence/flicker flags")
    ap.add_argument("--allow", nargs="*", default=[], help="shots the director accepted: reported, never FAIL")
    a = ap.parse_args()
    if not a.video.exists():
        sys.exit(f"No video {a.video}")
    tg = json.loads(TARGETS.read_text())
    th = tg["thresholds"]
    fps, D, G, TN = per_frame(a.video, a.window)
    n = len(D)
    if a.whole or not a.shots:
        shots = [["whole", 0.0, n / fps]]
    else:
        shots = [list(s)[:3] if not isinstance(s, dict) else [s["name"], s["start"], s["end"]]
                 for s in json.loads(a.shots.read_text())]
    designed = []
    for span in a.designed:
        t0, t1 = (float(x) for x in span.split(":")[0].split("-"))
        designed.append((t0, t1))

    def in_designed(t: float) -> bool:
        return any(t0 - 0.05 <= t <= t1 + 0.05 for t0, t1 in designed)

    res = G - np.convolve(G, np.ones(5) / 5, mode="same")
    report = []
    for name, s0, s1 in shots:
        i0, i1 = int(round(float(s0) * fps)) + 2, int(round(float(s1) * fps)) - 1   # skip the cut and its neighbour
        if i1 - i0 < 4:
            report.append(dict(shot=name, t=[s0, s1], verdict="PASS", why="too short to measure", frames=max(0, i1 - i0)))
            continue
        d, tn, r = D[i0:i1], TN[i0:i1], res[i0 + 2:i1 - 2] if i1 - i0 > 8 else res[i0:i1]
        # Noise only on still frames: camera or subject motion reads as noise in this measure (a daylight ISO 39
        # walking shot read 1.29). Too few still frames → not measured, and the motion check speaks for the shot.
        still = (d <= th["temporal_noise"]["still_motion"]) & np.isfinite(tn)
        tnoise = float(np.median(tn[still])) if still.sum() >= max(6, 0.25 * len(d)) else None
        motion = float(np.median(d))
        rms = float(np.sqrt(np.mean(r ** 2))) if len(r) else 0.0
        pk_i = int(np.argmax(np.abs(r))) if len(r) else 0
        peak = float(abs(r[pk_i])) if len(r) else 0.0
        peak_t = round((i0 + (2 if i1 - i0 > 8 else 0) + pk_i) / fps, 2)
        reps, jumps = [], []
        for t in range(i0, i1):
            lo, hi = max(i0, t - 6), min(i1, t + 7)
            nb = np.median(np.r_[D[lo:t], D[t + 1:hi]]) if hi - lo > 2 else 0.0
            ts = round(t / fps, 2)
            if in_designed(ts):
                continue
            if D[t] < 0.25 and nb > 1.5:
                reps.append(ts)
            if D[t] > max(4.0, 3 * nb):
                jumps.append(ts)
        verdict, why = "PASS", []
        if tnoise is not None and tnoise > th["temporal_noise"]["fail"]:
            verdict = "WARN" if name in a.allow else "FAIL"
            why.append(f"grain/noise {tnoise:.2f} > {th['temporal_noise']['fail']} (references' median "
                       f"{tg['reference_medians']['temporal_noise']})" + (" — allowed by the director" if name in a.allow else ""))
        elif tnoise is not None and tnoise > th["temporal_noise"]["warn"]:
            verdict = "WARN"
            why.append(f"grain/noise {tnoise:.2f} > {th['temporal_noise']['warn']}")
        elif tnoise is None:
            why.append("noise not measured: too few still frames")
        if motion > th["motion"]["warn"]:
            verdict = "WARN" if verdict == "PASS" else verdict
            why.append(f"busy: motion {motion:.1f} > {th['motion']['warn']} (references' median {tg['reference_medians']['motion']})")
        mid_designed = in_designed((float(s0) + float(s1)) / 2)
        if not mid_designed and (peak > th["flicker_peak"]["warn"] or rms > th["flicker_rms"]["warn"]):
            verdict = "WARN" if verdict == "PASS" else verdict
            why.append(f"flicker: peak {peak:.1f} at {peak_t} s, rms {rms:.2f}")
        if reps:
            verdict = "WARN" if verdict == "PASS" else verdict
            why.append(f"{len(reps)} repeated frame(s) at {reps[:6]} s (conform?)")
        if jumps:
            verdict = "WARN" if verdict == "PASS" else verdict
            why.append(f"{len(jumps)} jump(s) inside the shot at {jumps[:6]} s")
        report.append(dict(shot=name, t=[s0, s1], verdict=verdict, why="; ".join(why) or "within the reference targets",
                           temporal_noise=None if tnoise is None else round(tnoise, 3), motion=round(motion, 2),
                           flicker_rms=round(rms, 3), flicker_peak=round(peak, 2), repeats=reps, jumps=jumps))
    nz = [s["temporal_noise"] for s in report if s.get("temporal_noise") is not None]
    mo = [s["motion"] for s in report if "motion" in s]
    summary = dict(video=str(a.video), fps=round(fps, 3), frames=n,
                   reel_temporal_noise=round(float(np.median(nz)), 3) if nz else None,
                   reel_motion=round(float(np.median(mo)), 2) if mo else None,
                   targets=tg["reference_medians"], shots=report)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=1))
    md = [f"# Quality probe: {a.video.name}", "",
          f"Reel median: noise **{summary['reel_temporal_noise']}** (references {tg['reference_medians']['temporal_noise']}), "
          f"motion **{summary['reel_motion']}** (references {tg['reference_medians']['motion']}). "
          "Targets and thresholds: `studio/reference-targets.json`; why: effects-playbook §0.", "",
          "| Shot | Time | Noise | Motion | Flicker peak | Verdict | Why |", "|---|---|---|---|---|---|---|"]
    for s in report:
        md.append(f"| {s['shot']} | {float(s['t'][0]):.2f}–{float(s['t'][1]):.2f} | {s.get('temporal_noise')} | {s.get('motion')} | "
                  f"{s.get('flicker_peak')} | {s['verdict']} | {s['why']} |")
    (a.out.parent / "QUALITY.md").write_text("\n".join(md) + "\n")
    fails = [s for s in report if s["verdict"] == "FAIL"]
    warns = [s for s in report if s["verdict"] == "WARN"]
    for s in fails + warns:
        print(f"{s['verdict']} {s['shot']}: {s['why']}")
    print(f"{'FAIL' if fails else 'WARN' if warns else 'PASS'} · noise {summary['reel_temporal_noise']} · "
          f"motion {summary['reel_motion']} · {len(fails)} FAIL, {len(warns)} WARN of {len(report)} shots · {a.out}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Camera fidelity: each shot of a render against its own camera file, at the same framing (studio grading default, v0.8).

The director judges a reel against what the camera recorded ("not that bad in quality the raw videos ... the final renders are
horrible"; "over processed instead of looking HD"). This finds, for one mid-frame per shot, the camera frame and the exact
framing the render shows (time ±--slack s, scale and offset by edge matching), rebuilds the camera image at that framing with
no grade, and compares:

  luma     render mean vs camera.          FAIL if more than 0.03 darker (plus what near-black taken to black explains);
           WARN if lifted more than 0.10 (check for burn). A night shot (camera mean < 0.25) WARNs when lifted more than
           0.03: the v0.12.1 night grade test found lifts multiply the grain (×1.1–3.4, more after Instagram's encode)
  sat      saturation ratio render/camera, on camera tones above 0.15 (a black point recolours the toe by design).
           PASS within ±5 %, WARN within ±10 %, else FAIL
  hue      midtone hue shift (when the camera's midtones carry colour). PASS ≤ 3°, WARN ≤ 6°, else FAIL
  crushed  % pixels with luma < 0.03.      FAIL if more than 2 points above what the camera recorded near-black (< 0.07):
           the deepest shadows may go black (the night rule), shadow detail above that may not
  clip255  % pixels with any channel at 255 (burn). FAIL above max(camera's own, 2 %)
  whites   p98 vs camera.                  WARN if pulled more than 0.03 below a camera that doesn't clip
  width    % of the widest framing the clip allows in 9:16 (its full width for vertical clips; ~32 % of a landscape
           clip's width is the widest there). PASS ≥ 80 %, WARN ≥ 70 %, else FAIL (effects-playbook §B)
  detail   Laplacian energy ratio render/camera, reported (low = smeared or over-denoised, high = over-sharpened or grain)

Absolute brightness targets are only reported (reel mean luma), never failed: absolute floors burnt night shots on the
goddess reel (v9c). Deliberate deviations go in --allow, by shot name, and are listed as ALLOWED. With a creative look on
the V3 layer (effects-playbook §A3, director's pick), --look reports saturation and hue shifts as WARN; brightness, crush,
burn and framing still FAIL.

Input: a shot map, a JSON list with one object per shot, in reel time (or an EDL object whose "shots" are these rows,
scripts/preview_edl.py; its other keys are ignored here):
  {"name": "05_C051", "start": 8.40, "end": 10.20, "clip": "projects/<reel>/raw/b-roll/A001_..._C051.mov",
   "src_in": 4.00, "rate": 0.553}
  src_in  camera seconds (the camera file's own clock) at the shot's first frame
  rate    camera seconds per reel second: 1.0 normally; the speed for slow motion (0.5 = half speed); for a clip conformed by
          interpretation, × interpreted fps / native fps (a 30 fps clip interpreted at 25: 25/30). Default 1.0
From a Premiere read-back: src_in = trackItem.inPoint.seconds × speed × interpreted_fps / native_fps (on a speed-changed clip
the DOM's in/out are source ÷ speed). Approximate values are fine: the match searches ±--slack seconds.
Shots without "clip" (cards, graphics, AI shots) are listed and skipped. Run from the studio root: relative clip paths resolve
from there. A clip used twice gets a "#2" suffix. A shot whose clip is missing, whose frame is past the render's end, or whose
framing can't be found or matches weakly (NCC < 0.35) FAILs: fix the map, or --allow it with a reason. A slow-mo shot
swapped for an After Effects render still points at the camera file, with rate = the speed.

Writes fidelity.json, FIDELITY.md, fidelity_sheet.jpg (camera whole frame | camera at the render's framing | render, phone size)
and, with --crops, fidelity_crops.jpg (100 % crops of the most detailed region). Exit 1 if any shot FAILs (not allowed).

Usage:
  ./.venv/bin/python scripts/camera_fidelity.py renders/masters/<reel>_v3_master.mov --map projects/<reel>/analysis/map_v3.json \
      -o projects/<reel>/analysis/fidelity_v3 [--allow 12_C017] [--exclude-band 0.72,0.82] [--crops]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

W_OUT, H_OUT = 1080, 1920
# swscale's default YUV→RGB reads about 0.007 darker and ~1 point more "crushed" than exact rounding (v0.9 finding)
EXACT = "accurate_rnd+full_chroma_int"
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)


# ---------- decoding ----------
def probe(path: Path) -> dict:
    """Display size (after the rotation flag), native fps, duration."""
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,avg_frame_rate,r_frame_rate:stream_side_data=rotation:stream_tags=rotate:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    s = d["streams"][0]
    rot = 0
    for sd in s.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(float(sd["rotation"]))
    rot = rot or int(float((s.get("tags") or {}).get("rotate", 0)))
    w, h = int(s["width"]), int(s["height"])
    if abs(rot) % 180 == 90:
        w, h = h, w
    num, den = (s.get("avg_frame_rate") or s.get("r_frame_rate") or "0/1").split("/")
    fps = float(num) / float(den) if float(den) else 0.0
    return {"w": w, "h": h, "fps": fps, "duration": float(d.get("format", {}).get("duration", 0) or 0)}


def decode(path: Path, t: float, n: int, size: tuple[int, int], scale: tuple[int, int] | None = None,
           as_uint8: bool = False) -> np.ndarray:
    """n frames from t (accurate input seek), autorotated; optionally area-scaled. Returns (n, h, w, 3) float32 0..1
    (uint8 with as_uint8, to keep a search window small in memory). Fewer frames come back past the clip's end."""
    w, h = scale or size
    vf = f"scale={w}:{h}:flags=area+{EXACT},format=rgb24" if scale else f"scale=flags=bicubic+{EXACT},format=rgb24"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(t, 0):.4f}", "-i", str(path), "-an", "-frames:v", str(n),
                          "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    return fr if as_uint8 else fr.astype(np.float32) / 255


def render_frames(path: Path, idx: list[int], size: tuple[int, int]) -> dict[int, np.ndarray]:
    """Exact frames by frame number, one decode pass (no seconds × fps rounding). Frames past the end are missing."""
    if not idx:
        return {}
    sel = "+".join(f"eq(n\\,{i})" for i in sorted(set(idx)))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-an", "-vf", f"select={sel},scale=flags=bicubic+{EXACT},format=rgb24", "-fps_mode", "passthrough",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    w, h = size
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).astype(np.float32) / 255
    return dict(zip(sorted(set(idx)), fr))       # zip stops at the frames that exist


# ---------- image helpers ----------
def gray(x):
    return x @ LUMA


def resize(x, w, h):
    return np.asarray(Image.fromarray((np.clip(x, 0, 1) * 255 + .5).astype(np.uint8)).resize((w, h), Image.LANCZOS), np.float32) / 255


def edges(g):
    g = ndimage.gaussian_filter(g, 1.0)
    return np.hypot(ndimage.sobel(g, 0), ndimage.sobel(g, 1))


def phase_corr(big, small):
    """Offset (dy, dx) of `small` inside `big` (both 2-D)."""
    pad = np.zeros_like(big)
    pad[:small.shape[0], :small.shape[1]] = small - small.mean()
    F = np.fft.rfft2(big - big.mean()) * np.conj(np.fft.rfft2(pad))
    r = np.fft.irfft2(F / (np.abs(F) + 1e-6), s=big.shape)
    dy, dx = np.unravel_index(np.argmax(r), r.shape)
    return int(dy), int(dx)


def ncc(a, b):
    a, b = a - a.mean(), b - b.mean()
    return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-9))


def place(src_edges_fn, Fq, k, q, sw, sh):
    """Best offset and NCC of the render edge map Fq inside the source resized by k (output px per source px) at 1/q."""
    w, h = round(sw * k / q), round(sh * k / q)
    if w < Fq.shape[1] or h < Fq.shape[0]:
        return None
    B = src_edges_fn(w, h)
    dy, dx = phase_corr(B, Fq)
    if dy + Fq.shape[0] > h or dx + Fq.shape[1] > w:
        return None
    return ncc(B[dy:dy + Fq.shape[0], dx:dx + Fq.shape[1]], Fq), dy, dx


# ---------- matching ----------
def match(F: np.ndarray, frames: np.ndarray, half: float, sw: int, sh: int):
    """F: render frame 1080×1920. frames: camera frames (uint8) decoded at `half` of full size. Returns (ncc, frame idx, k,
    y0, x0) with k in output px per full-size source px and (y0, x0) the render's top-left in the source resized by k,
    or None when nothing fits."""
    if len(frames) == 0:
        return None
    kmin = max(W_OUT / sw, H_OUT / sh)
    ks = kmin / np.geomspace(1.0, 0.35, 19)          # shown width 100 % → 35 %
    best = None
    for q, idxs, kk in ((8, range(0, len(frames), 2), ks), (4, None, None)):
        if idxs is None:
            if best is None:
                return None
            _, i0, k0, _, _ = best
            idxs = range(max(0, i0 - 2), min(len(frames), i0 + 3))
            kk = k0 * np.geomspace(0.94, 1.06, 9)
            best = None
        Fq = edges(gray(resize(F, W_OUT // q, H_OUT // q)))
        for i in idxs:
            src = frames[i].astype(np.float32) / 255
            for k in kk:
                r = place(lambda w, h: edges(gray(resize(src, w, h))), Fq, k, q, sw, sh)
                if r and (best is None or r[0] > best[0]):
                    best = (r[0], i, float(k), r[1] * q, r[2] * q)
    return best


def refine(F: np.ndarray, S: np.ndarray, k: float, y0: int, x0: int):
    """Full-resolution refine of scale (±1.5 %) and offset (±8 px) on edge maps."""
    sh, sw = S.shape[:2]
    Fg = edges(gray(F))
    top = None
    for k2 in k * np.linspace(0.985, 1.015, 13):
        w, h = round(sw * k2), round(sh * k2)
        if w < W_OUT or h < H_OUT:
            continue
        B = edges(gray(resize(S, w, h)))
        for dy in range(-8, 9, 2):
            for dx in range(-8, 9, 2):
                yy, xx = int(round(y0 * k2 / k)) + dy, int(round(x0 * k2 / k)) + dx
                if yy < 0 or xx < 0 or yy + H_OUT > h or xx + W_OUT > w:
                    continue
                c = ncc(B[yy:yy + H_OUT:4, xx:xx + W_OUT:4], Fg[::4, ::4])
                if top is None or c > top[0]:
                    top = (c, float(k2), yy, xx)
    return top


# ---------- measurements ----------
NEAR_BLACK = 0.07     # camera luma below this may go to black in the grade (v0.12.1 night rule)
NIGHT = 0.25          # a shot whose camera mean luma is below this is a night shot: not brightened (effects-playbook §A0)
SAT_FLOOR = 0.15      # saturation is compared on camera tones above this: a black point changes the toe's colour, by design


def stats(x: np.ndarray, mask: np.ndarray, visible: np.ndarray | None = None) -> dict:
    """visible: the pixels the camera shows above SAT_FLOOR. Saturation is measured there, so shadows taken toward black
    (allowed, the night rule) don't count as a colour change."""
    y = gray(x)
    ym = y[mask]
    mx, mn = x.max(-1), x.min(-1)
    sat = np.where(mx > 1e-3, (mx - mn) / np.maximum(mx, 1e-3), 0)
    v = (mask if visible is None else visible) & (mx > 0.1)
    mid = mask & (y > 0.2) & (y < 0.6)
    hue, chroma = None, 0.0
    if mid.sum() > 500:
        c = x[mid].mean(0)
        cmx, cmn = float(c.max()), float(c.min())
        chroma = cmx - cmn
        if chroma > 1e-6:
            if cmx == c[0]:
                hue = 60 * (((c[1] - c[2]) / chroma) % 6)
            elif cmx == c[1]:
                hue = 60 * ((c[2] - c[0]) / chroma + 2)
            else:
                hue = 60 * ((c[0] - c[1]) / chroma + 4)
    lap = ndimage.laplace(ndimage.gaussian_filter(y, 0.6))
    return {"luma": round(float(ym.mean()), 3), "p02": round(float(np.percentile(ym, 2)), 3), "p98": round(float(np.percentile(ym, 98)), 3),
            "sat": round(float(sat[v].mean()) if v.any() else 0.0, 3), "hue": None if hue is None else round(float(hue), 1),
            "mid_chroma": round(chroma, 3), "crushed_%": round(float((ym < 0.03).mean() * 100), 2),
            "near_black_%": round(float((ym < NEAR_BLACK).mean() * 100), 2),
            "clip255_%": round(float((mx[mask] >= 254.5 / 255).mean() * 100), 2), "detail": round(float(np.var(lap[mask]) * 1e4), 2)}


def judge(cam: dict, ren: dict, width: float, look: bool = False) -> list[tuple[str, str, str]]:
    """(level, check, detail) rows; level PASS/WARN/FAIL. look: a chosen creative look, so colour shifts are WARN."""
    rows = []
    blown = cam["clip255_%"] > 2.0      # the camera burnt highlights: pulling them back darkens the frame on purpose
    night = cam["luma"] < NIGHT
    d = ren["luma"] - cam["luma"]
    dc = ren["crushed_%"] - cam["crushed_%"]
    # near-black taken to black darkens the mean by at most NEAR_BLACK per pixel: that much darkening is allowed
    dark_tol = 0.03 + max(0.0, dc) / 100 * NEAR_BLACK
    if d < -dark_tol:
        lv, why = ("WARN" if blown else "FAIL"), (", camera highlights blown" if blown else "")
    elif night and d > 0.03:
        lv, why = "WARN", ": a night shot brightened; a lift multiplies the grain, keep the camera's exposure (§A0)"
    else:
        lv, why = ("WARN" if d > 0.10 else "PASS"), ""
    rows.append((lv, "luma", f"{ren['luma']:.3f} vs camera {cam['luma']:.3f} ({d:+.3f})" + why))
    r = ren["sat"] / max(cam["sat"], 1e-3)
    rows.append(("PASS" if abs(r - 1) <= 0.05 else "WARN" if abs(r - 1) <= 0.10 or look else "FAIL", "sat", f"{ren['sat']:.3f} vs {cam['sat']:.3f} (×{r:.2f})"))
    if cam["hue"] is not None and ren["hue"] is not None and cam["mid_chroma"] >= 0.03:
        dh = (ren["hue"] - cam["hue"] + 180) % 360 - 180
        hv = "PASS" if abs(dh) <= 3 else "WARN" if abs(dh) <= 6 or blown or look else "FAIL"
        rows.append((hv, "hue", f"{ren['hue']:.1f}° vs {cam['hue']:.1f}° ({dh:+.1f}°); a deliberate cast fix goes in --allow"))
    lim_c = max(cam["crushed_%"], cam["near_black_%"]) + 2.0     # only what the camera recorded near-black may go black (+2: grain at the edge)
    rows.append(("FAIL" if ren["crushed_%"] > lim_c else "PASS", "crushed",
                 f"{ren['crushed_%']:.1f} % vs camera {cam['crushed_%']:.1f} % (near-black {cam['near_black_%']:.1f} %, "
                 f"limit {lim_c:.1f} %)"))
    lim = max(cam["clip255_%"], 2.0)
    rows.append(("FAIL" if ren["clip255_%"] > lim else "PASS", "clip255", f"{ren['clip255_%']:.2f} % (limit {lim:.2f} %)"))
    if cam["clip255_%"] < 1.0 and ren["p98"] < cam["p98"] - 0.03:
        rows.append(("WARN", "whites", f"p98 {ren['p98']:.3f} vs camera {cam['p98']:.3f}"))
    rows.append(("PASS" if width >= 80 else "WARN" if width >= 70 else "FAIL", "width",
                 f"{width:.0f} % of the widest framing this clip allows in 9:16"))
    dr = ren["detail"] / max(cam["detail"], 1e-3)
    rows.append(("INFO", "detail", f"×{dr:.2f} of the camera's at this framing"))
    return rows


# ---------- sheets ----------
def sheet(rows, tw, th, path, font):
    ncol = len(rows[0][1])
    im = Image.new("RGB", (tw * ncol, 34 + (th + 30) * len(rows)), (14, 14, 14))
    d = ImageDraw.Draw(im)
    for kk, (lab, _) in enumerate(rows[0][1]):
        d.text((kk * tw + 6, 6), lab, font=font, fill=(240, 210, 80))
    for rr, (nm, cols) in enumerate(rows):
        y = 34 + rr * (th + 30)
        d.text((6, y + 2), nm, font=font, fill=(255, 255, 255))
        for kk, (_, x) in enumerate(cols):
            im.paste(Image.fromarray((np.clip(x, 0, 1) * 255 + .5).astype(np.uint8)).resize((tw, th), Image.LANCZOS), (kk * tw, y + 28))
    im.save(path, quality=90)


def load_font(size):
    for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path, help="the export or master (1080×1920)")
    ap.add_argument("--map", type=Path, required=True, help="shot map JSON (see above)")
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--allow", nargs="*", default=[], help="shot names whose FAILs are deliberate (recorded in the brief)")
    ap.add_argument("--exclude-band", action="append", default=[], metavar="Y0,Y1",
                    help="leave a horizontal band out of the stats, as fractions of the height (e.g. subtitles 0.72,0.82)")
    ap.add_argument("--look", action="store_true", help="a creative look is on (§A3): colour shifts WARN instead of FAIL")
    ap.add_argument("--at", type=float, default=0.5, help="where in each shot to sample, 0..1 (default the middle)")
    ap.add_argument("--slack", type=float, default=0.4, help="time search either side of the mapped camera time, s")
    ap.add_argument("--crops", action="store_true", help="also write 100 %% crops of the most detailed region")
    a = ap.parse_args()

    a.out.mkdir(parents=True, exist_ok=True)
    shots = json.loads(a.map.read_text())
    shots = shots["shots"] if isinstance(shots, dict) else shots      # an EDL (preview_edl.py) or a plain map
    rp = probe(a.render)
    if (rp["w"], rp["h"]) != (W_OUT, H_OUT):
        sys.exit(f"render is {rp['w']}×{rp['h']}, expected {W_OUT}×{H_OUT}")
    fps = rp["fps"]
    mask = np.ones((H_OUT, W_OUT), bool)
    for band in a.exclude_band:
        y0, y1 = (float(v) for v in band.split(","))
        mask[int(y0 * H_OUT):int(y1 * H_OUT)] = False

    seen: dict[str, int] = {}
    for s in shots:                                   # unique names, so a clip used twice keeps both rows
        seen[s["name"]] = seen.get(s["name"], 0) + 1
        if seen[s["name"]] > 1:
            s["name"] = f"{s['name']}#{seen[s['name']]}"
    picks = {i: int(round((s["start"] + a.at * (s["end"] - s["start"])) * fps)) for i, s in enumerate(shots) if s.get("clip")}
    R = render_frames(a.render, list(picks.values()), (W_OUT, H_OUT))
    font = load_font(22)
    report, phone, crops = {"render": str(a.render), "fps": fps, "shots": {}}, [], []
    lumas = []
    def fail(name: str, why: str) -> None:
        v = "ALLOWED" if name in a.allow else "FAIL"
        report["shots"][name] = {"verdict": v, "checks": [{"level": "FAIL", "check": "match", "detail": why}]}
        print(f"{name:14s} {v:7s} {why}")

    for si, s in enumerate(shots):
        name = s["name"]
        if not s.get("clip"):
            report["shots"][name] = {"skipped": "no camera clip in the map"}
            print(f"{name:14s} skipped (no clip)")
            continue
        clip = Path(s["clip"])
        if not clip.exists():
            fail(name, f"camera clip not found: {clip} (paths are relative to where the script runs: the studio root)")
            continue
        cp = probe(clip)
        sw, sh = cp["w"], cp["h"]
        n = picks[si]
        if n not in R:
            fail(name, f"render frame {n} is past the render's end: check the map's start/end")
            continue
        F = R[n]
        t_reel = n / fps
        t_cam = s.get("src_in", 0.0) + (t_reel - s["start"]) * s.get("rate", 1.0)
        nf = max(1, int(round(2 * a.slack * cp["fps"]))) + 1
        t0 = max(0.0, t_cam - a.slack)
        half = 0.5
        small = decode(clip, t0, nf, (sw, sh), (int(sw * half) // 2 * 2, int(sh * half) // 2 * 2), as_uint8=True)
        best = match(F, small, half, sw, sh)
        del small
        if best is None:
            fail(name, f"no framing found near camera {t_cam:.2f} s: check the map's clip, src_in and rate")
            continue
        c0, i, k, y0, x0 = best
        t_found = t0 + i / cp["fps"]
        S = decode(clip, t_found, 1, (sw, sh))[0]
        top = refine(F, S, k, y0, x0)
        c, k, y0, x0 = top if top else (c0, k, y0, x0)
        w, h = round(sw * k), round(sh * k)
        ideal = resize(S, w, h)[y0:y0 + H_OUT, x0:x0 + W_OUT]
        width = 100 * W_OUT / w                                   # % of the camera's width shown
        width_max = 100 * W_OUT / (sw * max(W_OUT / sw, H_OUT / sh))   # the widest 9:16 framing (100 % for vertical clips)
        visible = mask & (gray(ideal) >= SAT_FLOOR)
        cam, ren = stats(ideal, mask, visible), stats(F, mask, visible)
        rows = judge(cam, ren, 100 * width / width_max, a.look)
        if c < 0.35:
            rows.append(("FAIL", "match", f"weak match (NCC {c:.2f}): the comparison isn't reliable. Fix the map's clip, src_in "
                                          "or rate, or --allow the shot with a reason"))
        allowed = name in a.allow
        worst = "FAIL" if any(r[0] == "FAIL" for r in rows) else "WARN" if any(r[0] == "WARN" for r in rows) else "PASS"
        verdict = "ALLOWED" if worst == "FAIL" and allowed else worst
        lumas.append(ren["luma"])
        report["shots"][name] = {"verdict": verdict, "render_frame": n, "camera_s": round(t_found, 3), "match_ncc": round(c, 3),
                                 "width_shown_%": round(width, 1), "width_of_widest_%": round(100 * width / width_max, 1),
                                 "camera": cam, "render": ren,
                                 "checks": [{"level": l, "check": ch, "detail": dt} for l, ch, dt in rows]}
        print(f"{name:14s} {verdict:7s} ncc {c:.2f}  width {width:4.0f} %  " +
              "  ".join(f"{ch} {l}" for l, ch, _ in rows if l in ("FAIL", "WARN")))
        full = resize(S, int(round(sw * W_OUT / max(sw, sh * W_OUT / H_OUT))), int(round(sh * W_OUT / max(sw, sh * W_OUT / H_OUT))))
        canvas = np.zeros((H_OUT, W_OUT, 3), np.float32)
        fy, fx = (H_OUT - full.shape[0]) // 2, (W_OUT - full.shape[1]) // 2
        canvas[max(fy, 0):max(fy, 0) + min(full.shape[0], H_OUT), max(fx, 0):max(fx, 0) + min(full.shape[1], W_OUT)] = \
            full[:min(full.shape[0], H_OUT), :min(full.shape[1], W_OUT)]
        phone.append((f"{name}  {verdict}", [("camera, whole frame", canvas), ("camera, render's framing", ideal), ("render", F)]))
        if a.crops:
            e = ndimage.uniform_filter(edges(gray(F)), 360)[180:-180, 180:-180]
            cy, cx = np.unravel_index(np.argmax(e), e.shape)
            cy, cx = cy + 180, cx + 180
            sl = (slice(cy - 180, cy + 180), slice(cx - 180, cx + 180))
            src = S[int((y0 + cy - 180) / k):int((y0 + cy + 180) / k), int((x0 + cx - 180) / k):int((x0 + cx + 180) / k)]
            crops.append((name, [("camera, source pixels", resize(src, 360, 360)), ("camera, render's framing", ideal[sl]), ("render", F[sl])]))

    verdicts = [v.get("verdict") for v in report["shots"].values() if "verdict" in v]
    if not verdicts:
        print("no camera shots in the map: nothing compared")
    report["reel_mean_luma"] = round(float(np.mean(lumas)), 3) if lumas else None
    report["verdict"] = "FAIL" if "FAIL" in verdicts else "WARN" if "WARN" in verdicts else "PASS"
    (a.out / "fidelity.json").write_text(json.dumps(report, indent=1))
    md = [f"# Camera fidelity: {a.render.name}", "", f"**Verdict: {report['verdict']}** · reel mean luma {report['reel_mean_luma']} "
          "(reported only; shots are judged against their own camera file)", "",
          "| Shot | Verdict | Width (of widest) | Luma (cam → render) | Sat × | Hue Δ | Crushed % | Clip255 % | Findings |", "|---|---|---|---|---|---|---|---|---|"]
    for nm, v in report["shots"].items():
        if "verdict" not in v:
            md.append(f"| {nm} | – | | | | | | | {v['skipped']} |")
            continue
        if "camera" not in v:
            md.append(f"| {nm} | {v['verdict']} | | | | | | | {v['checks'][0]['detail']} |")
            continue
        cm, rn = v["camera"], v["render"]
        dh = "" if cm["hue"] is None or rn["hue"] is None else f"{(rn['hue'] - cm['hue'] + 180) % 360 - 180:+.1f}°"
        fnd = "; ".join(f"{c['check']} {c['level']}: {c['detail']}" for c in v["checks"] if c["level"] in ("FAIL", "WARN"))
        md.append(f"| {nm} | {v['verdict']} | {v['width_of_widest_%']:.0f} % | {cm['luma']:.3f} → {rn['luma']:.3f} | "
                  f"{rn['sat'] / max(cm['sat'], 1e-3):.2f} | {dh} | {cm['crushed_%']:.1f} → {rn['crushed_%']:.1f} | "
                  f"{cm['clip255_%']:.2f} → {rn['clip255_%']:.2f} | {fnd} |")
    md += ["", "Sheet: `fidelity_sheet.jpg` (camera whole frame | camera at the render's framing | render)."]
    (a.out / "FIDELITY.md").write_text("\n".join(md) + "\n")
    if phone:
        sheet(phone, 270, 480, a.out / "fidelity_sheet.jpg", font)
    if crops:
        sheet(crops, 360, 360, a.out / "fidelity_crops.jpg", font)
    print(f"\n{report['verdict']} · {a.out / 'FIDELITY.md'}")
    sys.exit(1 if report["verdict"] == "FAIL" else 0)


if __name__ == "__main__":
    main()

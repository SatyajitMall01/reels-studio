#!/usr/bin/env python3
"""Controlled noise comparison: the SAME picture areas in every variant.
Blocks are chosen on the camera variant (B): 16x16 at 540x960, flat (std < 4) and dark-to-mid (mean 6-90 of 255).
In those blocks, for A / B / C: spatial grain (std of a 5-point high-pass) and boil (frame-to-frame change minus
the block's mean change), as medians, plus the ratio to B. Also split by the camera tone: deep (6-30) and mid-dark (30-90)."""
import json, os, subprocess, sys
import numpy as np

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renders", "nightgrade")
CLIPS = ["C027", "C017", "C044"]
VARS = ["A_posted", "B_camera", "C_dark"]


def read(path):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", "scale=540:960:flags=area,format=gray",
                        "-f", "rawvideo", "-"], capture_output=True).stdout
    n = len(b) // (540 * 960)
    return np.frombuffer(b[:n * 540 * 960], np.uint8).reshape(n, 960, 540).astype(np.float32)


def blocks(x):
    h, w = x.shape[-2:]
    return x[..., : h // 16 * 16, : w // 16 * 16].reshape(*x.shape[:-2], h // 16, 16, w // 16, 16)


def stats(stack, masks):
    hp = stack - (np.roll(stack, 1, 1) + np.roll(stack, -1, 1) + np.roll(stack, 1, 2) + np.roll(stack, -1, 2) + stack) / 5
    g = blocks(hp).std(axis=(2, 4))                                 # n, by, bx
    d = blocks(stack[1:] - stack[:-1])
    b = np.abs(d - d.mean(axis=(2, 4), keepdims=True)).mean(axis=(2, 4))
    out = {}
    for name, m in masks.items():
        out[name] = dict(grain=round(float(np.median(g[m])), 3), boil=round(float(np.median(b[m[1:] & m[:-1]])), 3),
                         blocks=int(m.sum()))
    return out


def main(tag):
    res = {}
    for c in CLIPS:
        st = {k: read(f"{D}/{c}_{k}{tag}") for k in VARS}
        n = min(len(s) for s in st.values())
        st = {k: s[:n] for k, s in st.items()}
        B = blocks(st["B_camera"])
        mean, sd = B.mean(axis=(2, 4)), B.std(axis=(2, 4))
        flat = sd < 4
        masks = {"all_dark": flat & (mean > 6) & (mean < 90), "deep": flat & (mean > 6) & (mean <= 30),
                 "mid_dark": flat & (mean > 30) & (mean < 90)}
        res[c] = {k: stats(st[k], masks) for k in VARS}
        for m in masks:
            b0 = res[c]["B_camera"][m]
            for k in VARS:
                r = res[c][k][m]
                r["grain_x"] = round(r["grain"] / b0["grain"], 2) if b0["grain"] else None
                r["boil_x"] = round(r["boil"] / b0["boil"], 2) if b0["boil"] else None
    return res


if __name__ == "__main__":
    out = {"export": main(".mp4"), "ig_sim": main("_ig.webm")}
    json.dump(out, open(f"{D}/results_controlled.json", "w"), indent=1)
    for where, r in out.items():
        print("==", where)
        for c, v in r.items():
            for m in ("all_dark", "deep", "mid_dark"):
                print(f"  {c} {m:8s} " + "  ".join(
                    f"{k[0]} grain {v[k][m]['grain']} (x{v[k][m]['grain_x']}) boil {v[k][m]['boil']} (x{v[k][m]['boil_x']})"
                    for k in VARS) + f"  n={v['B_camera'][m]['blocks']}")

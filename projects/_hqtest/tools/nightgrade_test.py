#!/usr/bin/env python3
"""Night-grade test: does lifting dark night shots (Goddess v9e grade) raise the noise people see?

For each clip, the same 3 s of camera frames are rendered three ways at 1080x1920:
  A  posted   - the Goddess v9e lift, emulated: exposure in linear light + Shadows bump + highlight shoulder,
                with the exposure calibrated so the mean luma matches the posted master's measured mean
  B  camera   - the camera file as recorded, no lift
  C  dark     - camera tones kept (never brightened), deepest shadows crushed to black (black point 0.035)
Each variant is encoded like an export (x264 CRF 16), then like Instagram's basic tier (VP9 ~3 Mb/s, 1080p).
Measured on both, luma at 540x960: spatial noise and temporal change in flat dark blocks, mean luma, p02,
8x8 blocking in the darks.
"""
import json, os, subprocess, sys
import numpy as np

ROOT = os.path.expanduser("~/Documents/reels-studio/") + "projects/we-never-treated-her-like-a-goddess/raw/b-roll"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renders", "nightgrade")
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1920
# clip, start s, posted mean luma (project.md v9d measurements), Lumetri values in the posted grade
CLIPS = [
    ("C027", "A001_10211941_C027.mov", 3.0, 0.313, dict(E=2.0, S=45, Hi=-60)),
    ("C017", "A001_10192144_C017.mov", 9.0, 0.214, dict(E=1.6, S=30, Hi=-60)),
    ("C044", "A001_10212045_C044.mov", 10.0, 0.323, dict(E=0.9, S=0, Hi=-35)),
]
DUR = 3.0


def luma(rgb):
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def lift(v, e, s, hi):
    l = np.power(np.clip(v, 0, 1), 2.4) * (2.0 ** e)
    x = np.power(l, 1 / 2.4)
    k = 0.75 + 0.1 * (1 + hi / 100)                       # stronger highlight pull -> lower shoulder start
    y = np.where(x < k, x, k + (1 - k) * np.tanh((x - k) / (1 - k)))
    y = y + (s / 100) * 0.6 * y * (1 - y) ** 3            # Shadows bump, largest around 0.25
    return np.clip(y, 0, 1)


def dark(v, g):
    # the reference look: camera tones kept, deepest shadows crushed to black (black point 0.035), never lifted
    y = np.clip(v * g, 0, 1)
    b = 0.035
    return np.clip((y - b) / (1 - b), 0, 1)


def frames(path, ss):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss), "-t", str(DUR), "-i", path,
           "-vf", f"scale={W}:{H}:flags=area:in_color_matrix=bt709:in_range=tv,format=rgb24", "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32) / 255.0
    p.wait()


def fps_of(path):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=avg_frame_rate",
                        "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip().split("\n")[0].split(",")[0]
    a, b = o.split("/")
    return float(a) / float(b)


def encoder(dst, fps):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", f"{fps:.4f}", "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                             "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-color_primaries", "bt709",
                             "-color_trc", "bt709", "-colorspace", "bt709", dst], stdin=subprocess.PIPE)


def ig_sim(src, dst):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-c:v", "libvpx-vp9", "-b:v", "3M", "-maxrate", "3.5M",
                    "-bufsize", "6M", "-deadline", "good", "-cpu-used", "4", "-row-mt", "1", "-an", dst], check=True)


def read_luma(path):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", "scale=540:960:flags=area,format=gray",
                        "-f", "rawvideo", "-"], capture_output=True).stdout
    n = len(b) // (540 * 960)
    return np.frombuffer(b[:n * 540 * 960], np.uint8).reshape(n, 960, 540).astype(np.float32)


def measure(path):
    a = read_luma(path)
    n, h, w = a.shape
    B = lambda x: x[: h // 16 * 16, : w // 16 * 16].reshape(h // 16, 16, w // 16, 16)
    sn, tn = [], []
    for i in range(n):
        f = a[i]
        blk = B(f)
        flat = (blk.std(axis=(1, 3)) < 4) & (blk.mean(axis=(1, 3)) < 90) & (blk.mean(axis=(1, 3)) > 6)
        hp = f - (np.roll(f, 1, 0) + np.roll(f, -1, 0) + np.roll(f, 1, 1) + np.roll(f, -1, 1) + f) / 5
        if flat.sum() > 20:
            sn.append(float(np.median(B(hp).std(axis=(1, 3))[flat])))
        if i:
            d = B(f - a[i - 1])
            r = np.abs(d - d.mean(axis=(1, 3), keepdims=True)).mean(axis=(1, 3))
            if flat.sum() > 20:
                tn.append(float(np.median(r[flat])))
    dx = np.abs(np.diff(a, axis=2))
    cols = np.arange(1, w)
    darkmask = a[:, :, 1:] < 60
    blk_ratio = float(dx[:, :, cols % 8 == 0][darkmask[:, :, cols % 8 == 0]].mean() /
                      dx[:, :, cols % 8 != 0][darkmask[:, :, cols % 8 != 0]].mean())
    return dict(spatial_noise=round(float(np.median(sn)), 3) if sn else None,
                temporal_flat=round(float(np.median(tn)), 3) if tn else None,
                luma=round(float(a.mean()) / 255, 3), p02=round(float(np.percentile(a, 2)) / 255, 3),
                dark_block=round(blk_ratio, 3), flat_frames=len(sn))


def main():
    res = {}
    for name, fn, ss, target, g in CLIPS:
        path = f"{ROOT}/{fn}"
        fps = fps_of(path)
        mid = None
        for i, fr in enumerate(frames(path, ss + DUR / 2)):
            mid = fr
            break
        lo, hi = -1.0, 5.0                                   # calibrate exposure to the posted mean luma
        for _ in range(30):
            e = (lo + hi) / 2
            if luma(lift(mid, e, g["S"], g["Hi"])).mean() < target:
                lo = e
            else:
                hi = e
        e_cal = round((lo + hi) / 2, 2)
        p995 = float(np.percentile(luma(mid), 99.5))
        gain = min(1.0 / max(p995, 1e-3) * 0.95, 1.0) if p995 > 0.95 else 0.95 / max(p995, 1e-3)
        gain = min(gain, 1.0)                                 # never brighten: expose for the lights at most down
        encs = {k: encoder(f"{OUT}/{name}_{k}.mp4", fps) for k in ("A_posted", "B_camera", "C_dark")}
        for fr in frames(path, ss):
            for k, img in (("A_posted", lift(fr, e_cal, g["S"], g["Hi"])), ("B_camera", fr), ("C_dark", dark(fr, gain))):
                encs[k].stdin.write((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        for p in encs.values():
            p.stdin.close(); p.wait()
        res[name] = dict(lumetri=g, exposure_calibrated=e_cal, camera_p995=round(p995, 3), dark_gain=round(gain, 3))
        for k in ("A_posted", "B_camera", "C_dark"):
            ig_sim(f"{OUT}/{name}_{k}.mp4", f"{OUT}/{name}_{k}_ig.webm")
            res[name][k] = dict(export=measure(f"{OUT}/{name}_{k}.mp4"), ig=measure(f"{OUT}/{name}_{k}_ig.webm"))
        print(json.dumps({name: res[name]}), flush=True)
    json.dump(res, open(f"{OUT}/results.json", "w"), indent=1)


if __name__ == "__main__":
    main()

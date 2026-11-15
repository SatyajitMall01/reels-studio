#!/usr/bin/env python3
"""Phone comparison of the night-grade test: each clip as Instagram's basic tier would serve it (VP9 sim),
A posted lift -> B camera -> C dark, 3 s each with a label; plus a still sheet with 1:1 dark-area crops."""
import json, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renders", "nightgrade")
CLIPS = ["C027", "C017", "C044"]
VAR = [("A_posted", "A  as posted: night lifted"), ("B_camera", "B  camera, no lift"), ("C_dark", "C  lights exposed, shadows dark")]
W, H = 1080, 1920


def font(sz):
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def label_png(text, sub, path):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([60, 250, W - 60, 420], fill=(0, 0, 0, 170))
    d.text((90, 270), text, font=font(54), fill=(255, 255, 255, 255))
    d.text((90, 350), sub, font=font(38), fill=(255, 210, 90, 255))
    im.save(path)


def frame(path, t):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", path, "-frames:v", "1", "-vf",
                        f"scale={W}:{H}:in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24", "-f", "rawvideo", "-"],
                       capture_output=True).stdout
    return np.frombuffer(b, np.uint8).reshape(H, W, 3)


def main():
    res = json.load(open(f"{D}/results_controlled.json"))["ig_sim"]
    segs = []
    for c in CLIPS:
        for k, txt in VAR:
            m = res[c][k]["all_dark"]
            png = f"{D}/lbl_{c}_{k}.png"
            label_png(txt, f"{c}  dark areas vs camera: grain x{m['grain_x']}  boil x{m['boil_x']}", png)
            seg = f"{D}/seg_{c}_{k}.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{D}/{c}_{k}_ig.webm", "-i", png, "-filter_complex",
                            "[0:v]fps=25,format=yuv420p[v];[v][1:v]overlay=0:0:format=auto,format=yuv420p", "-t", "3",
                            "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-color_primaries", "bt709",
                            "-color_trc", "bt709", "-colorspace", "bt709", "-an", seg], check=True)
            segs.append(seg)
    lst = f"{D}/segs.txt"
    open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    f"{D}/night_grade_test_phone.mp4"], check=True)

    # still sheet: per clip, A|B|C at phone scale, then 1:1 crops of the darkest textured area
    tw, th, cs = 360, 640, 360
    sheet = Image.new("RGB", (3 * tw, len(CLIPS) * (th + cs + 50)), (0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for r, c in enumerate(CLIPS):
        frames = [frame(f"{D}/{c}_{k}_ig.webm", 1.5) for k, _ in VAR]
        L = 0.2126 * frames[1][..., 0] + 0.7152 * frames[1][..., 1] + 0.0722 * frames[1][..., 2]
        best, by, bx = 1e9, 0, 0
        for y in range(200, H - cs - 200, 60):
            for x in range(0, W - cs, 60):
                m = L[y:y + cs, x:x + cs].mean()
                if 25 < m < 70 and abs(m - 45) < best:
                    best, by, bx = abs(m - 45), y, x
        y0 = r * (th + cs + 50)
        for i, (k, txt) in enumerate(VAR):
            sheet.paste(Image.fromarray(frames[i]).resize((tw, th), Image.LANCZOS), (i * tw, y0 + 40))
            sheet.paste(Image.fromarray(frames[i][by:by + cs, bx:bx + cs]), (i * tw, y0 + 40 + th))
            d.text((i * tw + 8, y0 + 8), f"{c}  {txt.split(':')[0][:28]}", font=font(22), fill=(255, 255, 255))
    sheet.save(f"{D}/night_grade_test_sheet.jpg", quality=92)
    print(f"{D}/night_grade_test_phone.mp4\n{D}/night_grade_test_sheet.jpg")


if __name__ == "__main__":
    main()

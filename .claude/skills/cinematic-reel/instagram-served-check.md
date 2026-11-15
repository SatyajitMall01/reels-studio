# Checking a reel as Instagram serves it (v0.12)

The export isn't what people watch. Instagram re-encodes every reel, and **how well depends on the reel's expected watch time**: popular reels get an advanced, per-title ladder (and the most popular an AV1 copy), while a small account's reel gets a basic encode ([Meta, 2023](https://engineering.fb.com/2023/02/21/video-engineering/av1-codec-facebook-instagram-reels/)).

Measured on 2026-11-15 (`studio/reviews/quality-diagnosis-2026-11-15.md`):

| Reel | What Instagram served |
|---|---|
| Kolkata | only `dash_baseline_1_v1`: H.264 baseline, 720p, 1.39 Mb/s, from our 11.2 Mb/s upload; 8×8 blocking +20–28 % in the darks |
| Goddess, Pujo | `vp9-basic-gen2` 1080p at 2.8–3.2 Mb/s, keeping 83–95 % of the export's detail |
| Most references | `r2evevp9 … q20–q90` (the advanced ladder) |

Run this **after the director posts**, read-only, in Claude in Chrome (the director's signed-in browser), on the reel's page `https://www.instagram.com/<handle>/reel/<code>/`. Record the results in `project.md`.

**Instagram's CSP blocks `eval`.** Pass each snippet to `javascript_tool` as it is. Don't store code and eval it later.

## 1. The encode tier, resolution and bitrate
The snippet plays the reel muted, seeks to the end so the last segment loads, then reads each video request's `efg` tag and the largest byte requested:

```js
await new Promise(r=>setTimeout(r,4000));
const v=[...document.querySelectorAll('video')].sort((a,b)=>b.clientHeight-a.clientHeight)[0];
v.muted=true; await v.play().catch(()=>{}); await new Promise(r=>setTimeout(r,3000));
v.currentTime=v.duration-0.6; await new Promise(r=>setTimeout(r,5000));
const out={};
for(const e of performance.getEntriesByType('resource')){ if(!/\.mp4/.test(e.name)) continue;
  const u=new URL(e.name); let tag='';
  try{ tag=JSON.parse(atob(decodeURIComponent(u.searchParams.get('efg')).replace(/-/g,'+').replace(/_/g,'/'))).vencode_tag||''; }catch(x){}
  if(!/clips/.test(tag)) continue;
  const k=tag.replace(/[^A-Za-z0-9_.\-]/g,' '); out[k]=Math.max(out[k]||0,+u.searchParams.get('byteend')||0); }
JSON.stringify({w:v.videoWidth,h:v.videoHeight,d:v.duration,
  tiers:Object.fromEntries(Object.entries(out).map(([k,b])=>[k,{MB:+(b/1e6).toFixed(2),mbps:+(b*8/v.duration/1e6).toFixed(2)}]))})
```

How to read the tags:

| Tag | Tier |
|---|---|
| `dash_baseline_1_v1` | the lowest: H.264 baseline, one 720p rung |
| `vp9-basic-gen2_<res>` | basic VP9, a few resolutions |
| `r2evevp9-r1gen2vp9_q<N>` | advanced, per-title (q20–q90) |

A rung's bitrate is only right once that rung has loaded to the end. The browser picks rungs by bandwidth.

## 2. Detail kept against our export
In the browser, measure frames at fixed times:

```js
await new Promise(r=>setTimeout(r,4000));
const v=[...document.querySelectorAll('video')].sort((a,b)=>b.clientHeight-a.clientHeight)[0];
v.muted=true; await v.play().catch(()=>{}); await new Promise(r=>setTimeout(r,6000)); v.pause();
const W=v.videoWidth,H=v.videoHeight, c=document.createElement('canvas'); c.width=W; c.height=H;
const x=c.getContext('2d',{willReadFrequently:true}), res={W,H,frames:[]};
for(const t of [3,8,13,18,23]){ v.currentTime=t; await new Promise(r=>{v.addEventListener('seeked',r,{once:true}); setTimeout(r,5000);});
  await new Promise(r=>setTimeout(r,400)); x.drawImage(v,0,0,W,H); const d=x.getImageData(0,0,W,H).data;
  const L=new Float32Array(W*H); for(let i=0,j=0;i<d.length;i+=4,j++) L[j]=0.2126*d[i]+0.7152*d[i+1]+0.0722*d[i+2];
  let g=0,n=0,bd=0,bn=0,nd=0,nn=0,m=0;
  for(let y=1;y<H;y++) for(let xx=1;xx<W;xx++){ const k=y*W+xx, dx=Math.abs(L[k]-L[k-1]); g+=dx+Math.abs(L[k]-L[k-W]); n++; if(xx%8==0){bd+=dx;bn++;} else {nd+=dx;nn++;} }
  for(let j=0;j<W*H;j++) m+=L[j];
  res.frames.push({t:+v.currentTime.toFixed(3),luma:+(m/(W*H)).toFixed(2),detail:+(g/n).toFixed(3),block:+((bd/bn)/(nd/nn)).toFixed(3)}); }
JSON.stringify(res)
```

Then measure the same times on our export, at the served size (`W,H`; prefix the scale with `720:1280:flags=bicubic:` for a 720p rung), with the same maths:

```python
import subprocess, numpy as np
def detail(path, t, W=1080, H=1920):
    b = subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",path,"-frames:v","1","-vf",
        f"scale={W}:{H}:in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24","-f","rawvideo","-"],
        capture_output=True).stdout
    a = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32)
    L = 0.2126*a[...,0] + 0.7152*a[...,1] + 0.0722*a[...,2]
    dx = np.abs(np.diff(L, axis=1))[1:, :]; dy = np.abs(np.diff(L, axis=0))[:, 1:]
    cols = np.arange(1, W)
    return dict(luma=L.mean(), detail=(dx+dy).mean(), block=dx[:, cols%8==0].mean()/dx[:, cols%8!=0].mean())
```

Lumas should agree within about 1. If they don't, the frames aren't aligned.

What to report:
- **detail kept** = served ÷ export. Below 0.85 on several frames is a visible softening.
- **block**: above about 1.15 is visible 8×8 blocking. Our exports sit at about 1.0.

## 3. The audio plays
**The director checks this by ear**, unmuted, on the phone. Claude can't hear through iPhone Mirroring or the browser.
- The line under the handle is **not evidence**. Goddess reads "Audio unavailable" ("This audio is no longer available" when tapped), yet its voiceover plays (director, 2026-11-15). HQ wrongly reported it silent from the label.
- If the director hears silence on a reel that borrowed another creator's audio ("Use audio", CLAUDE.md §4c), the reel needs new audio or a repost. Never post the guide-baked `_mix`: it holds someone else's audio.

## 4. On the phone (optional)
The iPhone app may get a different rung from the browser. Use iPhone Mirroring (`ig-posting-reality.md`) to watch the reel with the director. Mirroring's own stream is compressed, so judge on the phone itself, not on mirror screenshots.

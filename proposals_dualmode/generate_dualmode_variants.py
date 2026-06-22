from __future__ import annotations
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

ROOT = Path("/sessions/clever-gallant-knuth/mnt/Secvier_ImageAssets")
SRC = ROOT / "svg2png"
OUT = Path("/sessions/clever-gallant-knuth/mnt/outputs/proposals")
RES = 512
SIZES = [512, 128]

SAMPLES = [SRC/"alphanum"/"char_A.png", SRC/"alphanum"/"char_R.png",
           SRC/"alphanum"/"char_5.png", SRC/"alphanum"/"char_8.png",
           SRC/"suits"/"spade.png", SRC/"suits"/"heart.png",
           SRC/"suits"/"diamond.png", SRC/"suits"/"club.png"]

def V(**k): return k
VARIANTS = {
 "jisetsu": V(label="磁雪", kind="outer", w_out=13,
   body=(246,243,236,255), grad=None, outline=(28,24,19,255)),
 "shitsuboku": V(label="漆墨", kind="outer", w_out=13,
   body=(20,17,13,255), grad=None, outline=(232,220,190,255)),
 "suigyoku": V(label="翠玉", kind="double", w_halo=11, w_key=7,
   grad=((46,196,122,255),(12,104,62,255)), body=None,
   keyline=(8,40,24,255), halo=(242,248,243,255)),
 "sakin": V(label="砂金", kind="double", w_halo=11, w_key=7,
   grad=((244,208,104,255),(180,126,30,255)), body=None,
   keyline=(58,38,6,255), halo=(247,239,214,255)),
}

def load_mask(path):
    im = Image.open(path).convert("L").resize((RES,RES), Image.LANCZOS)
    return 1.0 - np.asarray(im, dtype=np.float32)/255.0

def sdf_from_mask(mask):
    solid = mask >= 0.5
    return distance_transform_edt(~solid) - distance_transform_edt(solid)

def region_alpha(sdf, t, aa=1.1):
    return np.clip((t - sdf)/aa + 0.5, 0.0, 1.0)

def vgrad(top, bottom, mask):
    ys = np.where(mask.max(axis=1) > 0.05)[0]
    y0,y1 = (ys.min(), ys.max()) if len(ys) else (0, RES-1)
    t = np.clip((np.arange(RES)-y0)/max(1,(y1-y0)), 0, 1)
    rgb = (np.array(top[:3])[None,:]*(1-t)[:,None] + np.array(bottom[:3])[None,:]*t[:,None])
    return np.repeat(rgb[:,None,:], RES, axis=1)

def over(dst, color_rgb, alpha):
    a = alpha[...,None]
    dst[...,:3] = color_rgb*a + dst[...,:3]*(1-a)
    dst[...,3:4] = a + dst[...,3:4]*(1-a)
    return dst

def render(mask, spec):
    sdf = sdf_from_mask(mask)
    c = np.zeros((RES,RES,4), dtype=np.float32)
    if spec["kind"] == "outer":
        w = spec["w_out"]
        over(c, np.array(spec["outline"][:3],dtype=np.float32), region_alpha(sdf, w))
        over(c, np.array(spec["body"][:3],dtype=np.float32)[None,None,:], region_alpha(sdf, 0.0))
    else:
        wh,wk = spec["w_halo"], spec["w_key"]
        body = vgrad(*spec["grad"], mask) if spec["grad"] else np.array(spec["body"][:3],dtype=np.float32)[None,None,:]
        over(c, np.array(spec["halo"][:3],dtype=np.float32), region_alpha(sdf, wh))
        over(c, np.array(spec["keyline"][:3],dtype=np.float32), region_alpha(sdf, 0.0))
        over(c, body, region_alpha(sdf, -wk))
    out = np.empty_like(c)
    out[...,:3] = c[...,:3]          # RGB は既に 0-255
    out[...,3] = c[...,3]*255        # alpha のみ 0-1 -> 0-255
    return Image.fromarray(np.clip(out,0,255).astype(np.uint8), "RGBA")

def main():
    for key in VARIANTS:
        for sz in SIZES:
            (OUT/key/f"{sz}").mkdir(parents=True, exist_ok=True)
    for path in SAMPLES:
        mask = load_mask(path); stem = path.stem
        for key, spec in VARIANTS.items():
            img = render(mask, spec)
            for sz in SIZES:
                out = img.resize((sz,sz), Image.LANCZOS) if sz!=RES else img
                out.save(OUT/key/f"{sz}"/f"{stem}.png")
        print("rendered", stem)
    print("DONE ->", OUT)

if __name__ == "__main__":
    main()

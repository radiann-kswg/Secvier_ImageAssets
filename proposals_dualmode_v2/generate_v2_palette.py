"""既存配色対応版：alphanum 5バリアント + suits 4色（両モード透過PNG）。"""
from __future__ import annotations
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

ROOT = Path("/sessions/clever-gallant-knuth/mnt/Secvier_ImageAssets")
SRC = ROOT / "svg2png"
OUT = Path("/sessions/clever-gallant-knuth/mnt/outputs/proposals2")
RES = 512
SIZES = [512, 128]

ALNUM_SAMPLES = ["char_A","char_R","char_5","char_8"]
SUIT_SAMPLES = ["spade","heart","diamond","club"]

# ── alphanum: 既存 dist/alphanum 5バリアントの配色に対応 ──
# grad=(top,bottom) ボディ宝石グラデ / key=内側キーライン / halo=外側ハロー
def V(**k): return k
ALNUM = {
 "seiyuu":   V(label="星幽", grad=((178,150,255),(86,104,196)),  key=(10,10,32),  halo=(238,226,185)),
 "suigyoku": V(label="翠玉", grad=((128,224,164),(38,140,76)),   key=(4,24,12),   halo=(214,248,220)),
 "kougyoku": V(label="紅玉", grad=((244,94,120),(185,20,48)),    key=(18,2,8),    halo=(255,228,208)),
 # 白磁=白ボディ→明色面で消えぬよう外縁を濃茶、内側に金（磁器の金縁）
 "hakuji":   V(label="白磁", grad=((250,247,240),(232,224,206)), key=(150,128,88), halo=(54,42,26)),
 "sakin":    V(label="砂金", grad=((226,178,64),(184,138,28)),   key=(44,26,6),   halo=(245,232,190)),
}
# ── suits: dist/cards の4色デック配色に対応 ──
SUITS = {
 "spade":   V(label="♠青", grad=((124,110,226),(72,96,192)),  key=(0,0,26),  halo=(236,238,250)),
 "heart":   V(label="♥赤", grad=((242,74,98),(168,0,48)),     key=(12,0,4),  halo=(255,224,224)),
 "diamond": V(label="♦金", grad=((230,182,70),(168,120,24)),  key=(40,26,0), halo=(250,238,200)),
 "club":    V(label="♣緑", grad=((96,192,120),(24,120,72)),   key=(4,26,14), halo=(226,246,232)),
}
W_HALO, W_KEY = 11, 7

def load_mask(p):
    im = Image.open(p).convert("L").resize((RES,RES), Image.LANCZOS)
    return 1.0 - np.asarray(im, dtype=np.float32)/255.0

def sdf(mask):
    s = mask >= 0.5
    return distance_transform_edt(~s) - distance_transform_edt(s)

def ra(d, t, aa=1.1):
    return np.clip((t-d)/aa + 0.5, 0, 1)

def vgrad(top, bottom, mask):
    ys = np.where(mask.max(axis=1) > 0.05)[0]
    y0,y1 = (ys.min(), ys.max()) if len(ys) else (0, RES-1)
    t = np.clip((np.arange(RES)-y0)/max(1,(y1-y0)), 0, 1)
    rgb = np.array(top)[None,:]*(1-t)[:,None] + np.array(bottom)[None,:]*t[:,None]
    return np.repeat(rgb[:,None,:], RES, axis=1)

def over(dst, col, a):
    a = a[...,None]
    dst[...,:3] = col*a + dst[...,:3]*(1-a)
    dst[...,3:4] = a + dst[...,3:4]*(1-a)

def render(mask, spec):
    d = sdf(mask)
    c = np.zeros((RES,RES,4), dtype=np.float32)
    body = vgrad(spec["grad"][0], spec["grad"][1], mask)
    over(c, np.array(spec["halo"],dtype=np.float32), ra(d, W_HALO))
    over(c, np.array(spec["key"],dtype=np.float32),  ra(d, 0.0))
    over(c, body, ra(d, -W_KEY))
    out = np.empty_like(c); out[...,:3]=c[...,:3]; out[...,3]=c[...,3]*255
    return Image.fromarray(np.clip(out,0,255).astype(np.uint8), "RGBA")

def run(group, table, stems, subdir):
    for key in table:
        for sz in SIZES:
            (OUT/subdir/key/f"{sz}").mkdir(parents=True, exist_ok=True)
    for stem in stems:
        src = SRC/("alphanum" if group=="alnum" else "suits")/f"{stem}.png"
        mask = load_mask(src)
        for key, spec in table.items():
            img = render(mask, spec)
            for sz in SIZES:
                o = img.resize((sz,sz), Image.LANCZOS) if sz!=RES else img
                o.save(OUT/subdir/key/f"{sz}"/f"{stem}.png")
        print(group, stem, "done")

if __name__ == "__main__":
    run("alnum", ALNUM, ALNUM_SAMPLES, "alphanum")
    run("suit",  SUITS, SUIT_SAMPLES, "suits")
    print("ALL ->", OUT)

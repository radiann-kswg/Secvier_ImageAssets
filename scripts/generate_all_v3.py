"""
Secvier ImageAssets — 英数字 + ダイス全絵文字 一括生成 v3
（自己完結スクリプト: 外部モジュールに非依存）

バリアント 5種:
  seiyuu   / 星幽  — 深夜宇宙・神秘
  suigyoku / 翠玉  — 深翠宝石・森の叡智
  kougyoku / 紅玉  — 紅玉石・情熱の焔       ← 新規
  hakuji   / 白磁  — 白磁器・清廉・極限美
  sakin    / 砂金  — 羊皮紙・黄金文書        ← 新規

出力:
  dist/alphanum/{variant}/char_{X}.png         36枚/variant × 5 = 180枚
  dist/dice/{variant}/dice_{type}_{face}.png   70枚/variant × 5 = 350枚
  dist/dice/{variant}/dice_type_{type}.png      7枚/variant × 5 =  35枚
  合計 565枚
"""
from __future__ import annotations
import math
from pathlib import Path
from typing import NamedTuple
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.parent
FONT_PATH = ROOT / "assets" / "fonts" / "Secvier.otf"
DIST = ROOT / "dist"
SIZE = 128
C = SIZE // 2

# ════════════════════════════════════════════
# バリアント定義
# ════════════════════════════════════════════
class V(NamedTuple):
    key: str; label: str
    bg: tuple; text: tuple; border: tuple
    accent: tuple; sfill: tuple; sline: tuple

VARIANTS: list[V] = [
    V("seiyuu",   "星幽",
      (10,10,26,255),    (238,226,185,255), (90,108,195,255),
      (175,148,255,255), (22,22,58,255),    (120,100,230,255)),
    V("suigyoku", "翠玉",
      (4,18,10,255),     (210,248,218,255), (38,140,76,255),
      (100,210,140,255), (8,36,18,255),     (56,168,104,255)),
    V("kougyoku", "紅玉",
      (14,2,6,255),      (255,228,208,255), (185,20,48,255),
      (240,80,105,255),  (30,4,12,255),     (210,32,65,255)),
    V("hakuji",   "白磁",
      (248,244,236,255), (22,18,14,255),    (150,128,88,255),
      (110,88,52,255),   (232,224,208,255), (140,118,78,255)),
    V("sakin",    "砂金",
      (245,232,190,255), (44,26,6,255),     (188,142,30,255),
      (218,168,42,255),  (235,215,168,255), (178,132,22,255)),
]

# ════════════════════════════════════════════
# 共通ヘルパー
# ════════════════════════════════════════════
def lf(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)

def poly(cx, cy, r, n, rot=0):
    pts = []
    for i in range(n):
        a = math.radians(rot + i*360/n) - math.pi/2
        pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    return pts

# ════════════════════════════════════════════
# フレーム
# ════════════════════════════════════════════
def frame(draw: ImageDraw.ImageDraw, v: V):
    m = 4
    if v.key == "seiyuu":
        draw.rounded_rectangle([m,m,SIZE-m-1,SIZE-m-1], radius=8,
                               outline=v.border, width=2)
        for cx,cy in [(m+2,m+2),(SIZE-m-3,m+2),(m+2,SIZE-m-3),(SIZE-m-3,SIZE-m-3)]:
            draw.polygon(poly(cx,cy,4,4,45), fill=v.accent)

    elif v.key == "suigyoku":
        draw.rounded_rectangle([m,m,SIZE-m-1,SIZE-m-1], radius=6,
                               outline=v.border, width=2)
        for (cx,cy),rot in [((m+2,m+2),0),((SIZE-m-3,m+2),0),
                            ((m+2,SIZE-m-3),180),((SIZE-m-3,SIZE-m-3),180)]:
            draw.polygon(poly(cx,cy,5,3,rot), fill=v.accent)

    elif v.key == "kougyoku":
        draw.rounded_rectangle([m,m,SIZE-m-1,SIZE-m-1], radius=10,
                               outline=v.border, width=2)
        cr = 4
        for cx,cy in [(m+3,m+3),(SIZE-m-4,m+3),(m+3,SIZE-m-4),(SIZE-m-4,SIZE-m-4)]:
            draw.ellipse([cx-cr,cy-cr,cx+cr,cy+cr], fill=v.accent)

    elif v.key == "hakuji":
        draw.rectangle([3,3,SIZE-4,SIZE-4], outline=v.border, width=1)
        draw.rectangle([7,7,SIZE-8,SIZE-8], outline=v.border, width=1)
        sq = 3
        for cx,cy in [(3,3),(SIZE-4,3),(3,SIZE-4),(SIZE-4,SIZE-4)]:
            draw.rectangle([cx-sq,cy-sq,cx+sq,cy+sq], fill=v.accent)

    else:  # sakin
        draw.rectangle([m,m,SIZE-m-1,SIZE-m-1], outline=v.border, width=2)
        arm = 7
        for cx,cy in [(m+1,m+1),(SIZE-m-2,m+1),(m+1,SIZE-m-2),(SIZE-m-2,SIZE-m-2)]:
            draw.line([(cx,cy),(cx+arm,cy+arm)], fill=v.accent, width=2)
            draw.line([(cx+arm,cy),(cx,cy+arm)], fill=v.accent, width=2)

def base(v: V):
    img = Image.new("RGBA", (SIZE,SIZE), v.bg)
    draw = ImageDraw.Draw(img)
    frame(draw, v)
    return img, draw

# ════════════════════════════════════════════
# ダイス形状
# ════════════════════════════════════════════
FACE_R = C - 24   # 出目用（小）
TYPE_R = C - 10   # 種別用（大）

def shape_pts(shape: str, r: float):
    if shape == "tri":
        return poly(C,C,r,3)
    if shape == "dia":
        hh,hw = r, int(r*0.70)
        return [(C,C-hh),(C+hw,C),(C,C+hh),(C-hw,C)]
    if shape == "kite":
        sy = C - int(r*0.44); sx = int(r*0.80)
        return [(C,C-r),(C+sx,sy),(C,C+r),(C-sx,sy)]
    if shape == "penta":
        return poly(C,C,r,5)
    if shape == "d20":
        # 12角形で丸みを帯びた D20 シルエット
        return poly(C,C,r,12)
    return []

def draw_d6_sq(draw, r, v: V):
    pad = int(C - r*0.707)
    draw.rounded_rectangle([pad,pad,SIZE-pad-1,SIZE-pad-1],
                           radius=6, fill=v.sfill, outline=v.sline, width=2)

def draw_shape_bg(draw, shape: str, r: float, v: V):
    pts = shape_pts(shape, r)
    if not pts: return
    draw.polygon(pts, fill=v.sfill, outline=v.sline, width=2)
    if shape == "d20":
        # 内接三角形 + 中点三角形
        tri = poly(C,C,r*0.78,3)
        draw.polygon(tri, fill=None, outline=v.sline, width=1)
        mid = [((tri[i][0]+tri[(i+1)%3][0])/2,
                (tri[i][1]+tri[(i+1)%3][1])/2) for i in range(3)]
        draw.polygon(mid, fill=None, outline=v.sline, width=1)

# ════════════════════════════════════════════
# D6 pip
# ════════════════════════════════════════════
L,R = C-23, C+23
T,M,B = C-23, C, C+23
PIPS = {
    1:[(M,M)], 2:[(L,T),(R,B)], 3:[(R,T),(M,M),(L,B)],
    4:[(L,T),(R,T),(L,B),(R,B)], 5:[(L,T),(R,T),(M,M),(L,B),(R,B)],
    6:[(L,T),(R,T),(L,M),(R,M),(L,B),(R,B)],
}
PR = 10

# ════════════════════════════════════════════
# 英数字
# ════════════════════════════════════════════
ALPHANUM = [(ch,f"char_{ch}") for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"]

def gen_alphanum(v: V, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    font = lf(96)
    for ch, stem in ALPHANUM:
        img, draw = base(v)
        draw.text((C, C+4), ch, font=font, fill=v.text, anchor="mm")
        img.save(out/f"{stem}.png","PNG",optimize=True)
    return len(ALPHANUM)

# ════════════════════════════════════════════
# ダイス出目
# ════════════════════════════════════════════
def fsz(t):  # face font size
    n=len(t); return 86 if n==1 else (66 if n==2 else 52)

def tsz(t):  # type label size
    return 54 if len(t)<=2 else 42

def save_die_face(img, out: Path, stem: str):
    out.mkdir(parents=True, exist_ok=True)
    img.save(out/f"{stem}.png","PNG",optimize=True)

def gen_dice(v: V, out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    count = 0

    # ── D4 (三角形, 1–4)
    for f in range(1,5):
        img,draw = base(v)
        draw_shape_bg(draw,"tri",FACE_R,v)
        draw.text((C,C+10),str(f),font=lf(fsz(str(f))),fill=v.text,anchor="mm")
        save_die_face(img, out, f"dice_d4_{f}"); count+=1

    # ── D6 pip (1–6)
    for f in range(1,7):
        img,draw = base(v)
        draw_d6_sq(draw,FACE_R,v)
        for px,py in PIPS[f]:
            draw.ellipse([px-PR,py-PR,px+PR,py+PR],fill=v.text)
        save_die_face(img, out, f"dice_d6_{f}"); count+=1

    # ── D8 (縦長ダイヤ, 1–8)
    for f in range(1,9):
        img,draw = base(v)
        draw_shape_bg(draw,"dia",FACE_R,v)
        draw.text((C,C),str(f),font=lf(fsz(str(f))),fill=v.text,anchor="mm")
        save_die_face(img, out, f"dice_d8_{f}"); count+=1

    # ── D10 (カイト, 0–9)
    for f in range(0,10):
        img,draw = base(v)
        draw_shape_bg(draw,"kite",FACE_R,v)
        draw.text((C,C),str(f),font=lf(fsz(str(f))),fill=v.text,anchor="mm")
        save_die_face(img, out, f"dice_d10_{f}"); count+=1

    # ── D% テンズテン (カイト, 00–90)
    for t in range(0,10):
        s=f"{t*10:02d}"
        img,draw = base(v)
        draw_shape_bg(draw,"kite",FACE_R,v)
        draw.text((C,C),s,font=lf(fsz(s)),fill=v.text,anchor="mm")
        save_die_face(img, out, f"dice_d10p_{s}"); count+=1

    # ── D12 (五角形, 1–12) — 2桁出目(10–12)に合わせ全面 size=66
    for f in range(1,13):
        img,draw = base(v)
        draw_shape_bg(draw,"penta",FACE_R,v)
        draw.text((C,C),str(f),font=lf(66),fill=v.text,anchor="mm")
        save_die_face(img, out, f"dice_d12_{f}"); count+=1

    # ── D20 (12角形+内三角, 1–20) — 2桁出目(10–20)に合わせ全面 size=66
    for f in range(1,21):
        s=str(f)
        img,draw = base(v)
        draw_shape_bg(draw,"d20",FACE_R,v)
        draw.text((C,C),s,font=lf(66),fill=v.text,anchor="mm")
        save_die_face(img, out, f"dice_d20_{f}"); count+=1

    # ── 種別アイコン
    type_defs = [
        ("dice_type_d4",  "tri",   "D4"),
        ("dice_type_d6",  "sq",    "D6"),
        ("dice_type_d8",  "dia",   "D8"),
        ("dice_type_d10", "kite",  "D10"),
        ("dice_type_d10p","kite",  "D00"),
        ("dice_type_d12", "penta", "D12"),
        ("dice_type_d20", "d20",   "D20"),
    ]
    for stem, shape, label in type_defs:
        img,draw = base(v)
        if shape == "sq":
            draw_d6_sq(draw, TYPE_R, v)
        else:
            draw_shape_bg(draw, shape, TYPE_R, v)
        oy = 12 if shape=="tri" else 0
        draw.text((C,C+oy),label,font=lf(tsz(label)),fill=v.text,anchor="mm")
        img.save(out/f"{stem}.png","PNG",optimize=True)
        count += 1

    return count

# ════════════════════════════════════════════
# メイン
# ════════════════════════════════════════════
def main():
    grand = 0
    for v in VARIANTS:
        a_dir = DIST/"alphanum"/v.key
        d_dir = DIST/"dice"/v.key
        na = gen_alphanum(v, a_dir)
        nd = gen_dice(v, d_dir)
        print(f"  {v.label:4} ({v.key:10}): alphanum {na}枚  dice {nd}枚")
        grand += na + nd
    print(f"\n✓ 合計 {grand} 枚")

if __name__ == "__main__":
    main()

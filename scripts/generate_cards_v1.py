"""
Secvier ImageAssets — トランプ絵文字 バリアント案3種 生成 v1
（自己完結スクリプト）

バリアント案:
  A: seiyuu_c  / 星幽   — 深夜宇宙・神秘タロット (dark)
  B: hakuji_c  / 白磁   — 白磁清廉・古典トランプ  (light)
  C: sakin_c   / 砂金   — 羊皮紙・黄金写本        (warm)

各バリアント: 52枚 + ジョーカー2枚 + スートマーク4枚 = 58枚
合計: 58 × 3 = 174枚

出力: dist/cards/{variant}/card_{suit}_{rank}.png
             dist/cards/{variant}/card_joker_{1,2}.png
             dist/cards/{variant}/card_suit_{S,H,D,C}.png
"""
from __future__ import annotations
import math
from pathlib import Path
from typing import NamedTuple
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.parent
FONT_PATH = ROOT / "assets" / "fonts" / "Secvier.otf"
DIST = ROOT / "dist" / "cards"
SIZE = 128
CX = SIZE // 2  # 64

# ────────────────────────────────────────────
# カードの寸法
# ────────────────────────────────────────────
CX1, CY1 = 9, 3       # card top-left
CX2, CY2 = 119, 125   # card bottom-right
CARD_R = 9             # corner radius

# ────────────────────────────────────────────
# バリアント定義
# ────────────────────────────────────────────
class CV(NamedTuple):
    key: str
    label: str
    outer_bg: tuple   # canvas background
    card_bg: tuple    # card face fill
    card_border: tuple
    accent: tuple     # corner ornament color
    rank_col: tuple   # rank/text color
    red_suit: tuple   # ♥♦
    blk_suit: tuple   # ♠♣
    skin: tuple       # face-card character skin
    robe: tuple       # robe / garment
    trim: tuple       # crown / trim / highlight

PROPOSALS: list[CV] = [
    # ── A: 星幽 (深夜宇宙・タロット) ────────────────
    CV("seiyuu_c", "星幽",
       outer_bg=(10,10,26,255),
       card_bg=(18,16,42,255),
       card_border=(90,108,195,255),
       accent=(175,148,255,255),
       rank_col=(238,226,185,255),
       red_suit=(210,65,95,255),
       blk_suit=(120,100,230,255),
       skin=(220,210,188,255),
       robe=(48,38,110,255),
       trim=(175,148,255,255)),

    # ── B: 白磁 (清廉・古典トランプ) ────────────────
    CV("hakuji_c", "白磁",
       outer_bg=(210,205,195,255),
       card_bg=(248,244,236,255),
       card_border=(150,128,88,255),
       accent=(110,88,52,255),
       rank_col=(22,18,14,255),
       red_suit=(175,30,38,255),
       blk_suit=(22,18,14,255),
       skin=(245,228,208,255),
       robe=(90,68,36,255),
       trim=(150,128,88,255)),

    # ── C: 砂金 (羊皮紙・黄金写本) ──────────────────
    CV("sakin_c", "砂金",
       outer_bg=(188,142,30,255),
       card_bg=(245,232,190,255),
       card_border=(188,142,30,255),
       accent=(218,168,42,255),
       rank_col=(44,26,6,255),
       red_suit=(148,22,34,255),
       blk_suit=(44,26,6,255),
       skin=(230,205,158,255),
       robe=(80,46,10,255),
       trim=(188,142,30,255)),
]

# ────────────────────────────────────────────
# フォント
# ────────────────────────────────────────────
def lf(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)

# ────────────────────────────────────────────
# スートの色取得
# ────────────────────────────────────────────
def sc(suit: str, cv: CV) -> tuple:
    return cv.red_suit if suit in ('H', 'D') else cv.blk_suit

# ────────────────────────────────────────────
# スート描画関数
# ────────────────────────────────────────────
def draw_heart(draw, cx, cy, r, color):
    r = max(3, int(r))
    hh = max(2, int(r * 0.55))
    # Two upper circles
    draw.ellipse([cx-r, cy-hh, cx, cy+hh], fill=color)
    draw.ellipse([cx, cy-hh, cx+r, cy+hh], fill=color)
    # Bottom point
    draw.polygon([(cx-r, cy+hh//2), (cx+r, cy+hh//2), (cx, cy+r+hh//2)], fill=color)

def draw_diamond(draw, cx, cy, r, color):
    rw = max(2, int(r * 0.65))
    draw.polygon([(cx, cy-r), (cx+rw, cy), (cx, cy+r), (cx-rw, cy)], fill=color)

def draw_spade(draw, cx, cy, r, color):
    r = max(3, int(r))
    # Top point + two lower circles
    tip_y = cy - int(r * 0.5)
    body_r = int(r * 0.55)
    draw.polygon([(cx-r, tip_y+body_r), (cx+r, tip_y+body_r), (cx, cy-r)], fill=color)
    draw.ellipse([cx-r, tip_y, cx-r+body_r*2, tip_y+body_r*2], fill=color)
    draw.ellipse([cx+r-body_r*2, tip_y, cx+r, tip_y+body_r*2], fill=color)
    # Stem
    sw = max(2, r//5)
    draw.rectangle([cx-sw, cy+int(r*0.4), cx+sw, cy+r], fill=color)
    draw.ellipse([cx-r//2, cy+r-r//5, cx+r//2, cy+r+r//5], fill=color)

def draw_club(draw, cx, cy, r, color):
    r = max(3, int(r))
    cr = max(2, int(r * 0.52))
    draw.ellipse([cx-cr, cy-r, cx+cr, cy-r+cr*2], fill=color)        # top
    draw.ellipse([cx-r, cy-cr, cx-r+cr*2, cy-cr+cr*2], fill=color)   # left
    draw.ellipse([cx+r-cr*2, cy-cr, cx+r, cy-cr+cr*2], fill=color)   # right
    # Fill center gap
    draw.polygon([(cx-cr, cy-cr), (cx+cr, cy-cr), (cx+cr, cy+cr//2), (cx-cr, cy+cr//2)], fill=color)
    # Stem
    sw = max(2, r//5)
    draw.rectangle([cx-sw, cy+cr, cx+sw, cy+r], fill=color)
    draw.ellipse([cx-r//2, cy+r-r//5, cx+r//2, cy+r+r//5], fill=color)

SUIT_FN = {'S': draw_spade, 'H': draw_heart, 'D': draw_diamond, 'C': draw_club}

# ────────────────────────────────────────────
# カードベース
# ────────────────────────────────────────────
def make_card(cv: CV) -> tuple:
    img = Image.new("RGBA", (SIZE, SIZE), cv.outer_bg)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([CX1, CY1, CX2, CY2], radius=CARD_R,
                           fill=cv.card_bg, outline=cv.card_border, width=2)
    return img, draw

# ────────────────────────────────────────────
# コーナーインデックス（ランク＋ミニスート）
# ────────────────────────────────────────────
def make_corner_index(rank: str, suit: str, cv: CV) -> Image.Image:
    """小コーナー画像 (24×32 RGBA)。"""
    w, h = 24, 32
    ci = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(ci)
    fsize = 13 if len(rank) == 1 else 10
    cd.text((w//2, 1), rank, font=lf(fsize), fill=cv.rank_col, anchor="mt")
    SUIT_FN[suit](cd, w//2, 25, 6, sc(suit, cv))
    return ci

def paste_corners(img: Image.Image, rank: str, suit: str, cv: CV):
    ci = make_corner_index(rank, suit, cv)
    # Top-left
    img.paste(ci, (CX1+3, CY1+2), ci)
    # Bottom-right (rotated 180°)
    ci_rot = ci.rotate(180)
    img.paste(ci_rot, (CX2-3-ci.width, CY2-2-ci.height), ci_rot)

# ────────────────────────────────────────────
# フレーム装飾（バリアント別コーナー）
# ────────────────────────────────────────────
def poly(cx, cy, r, n, rot=0):
    pts = []
    for i in range(n):
        a = math.radians(rot + i*360/n) - math.pi/2
        pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    return pts

def draw_card_frame(draw, cv: CV):
    m = 4
    if cv.key == "seiyuu_c":
        for cx, cy in [(CX1+4, CY1+4), (CX2-4, CY1+4),
                       (CX1+4, CY2-4), (CX2-4, CY2-4)]:
            draw.polygon(poly(cx, cy, 4, 4, 45), fill=cv.accent)
    elif cv.key == "hakuji_c":
        draw.rectangle([CX1+4, CY1+4, CX2-4, CY2-4],
                       outline=cv.accent, width=1)
        for cx, cy in [(CX1+4, CY1+4), (CX2-4, CY1+4),
                       (CX1+4, CY2-4), (CX2-4, CY2-4)]:
            s = 3
            draw.rectangle([cx-s, cy-s, cx+s, cy+s], fill=cv.accent)
    else:  # sakin_c
        arm = 6
        for cx, cy in [(CX1+4, CY1+4), (CX2-4, CY1+4),
                       (CX1+4, CY2-4), (CX2-4, CY2-4)]:
            draw.line([(cx, cy), (cx+arm, cy+arm)], fill=cv.accent, width=2)
            draw.line([(cx+arm, cy), (cx, cy+arm)], fill=cv.accent, width=2)

# ────────────────────────────────────────────
# ピップ座標定義
# ────────────────────────────────────────────
# pip area: x from 30 to 98, y from 36 to 94 (within card face)
PL, PM_X, PR = 34, 64, 94
PT, PB = 40, 92
PM_Y = (PT + PB) // 2   # 66
PUM = PT + (PM_Y - PT) * 2 // 5   # upper-mid ≈ 51
PLM = PM_Y + (PB - PM_Y) * 3 // 5  # lower-mid ≈ 80

PIP_LAYOUTS: dict[str, list[tuple[int, int]]] = {
    '2':  [(PM_X, PT+4),  (PM_X, PB-4)],
    '3':  [(PM_X, PT+4),  (PM_X, PM_Y), (PM_X, PB-4)],
    '4':  [(PL, PT+4),   (PR, PT+4),   (PL, PB-4),   (PR, PB-4)],
    '5':  [(PL, PT+4),   (PR, PT+4),   (PM_X, PM_Y), (PL, PB-4), (PR, PB-4)],
    '6':  [(PL, PT+4),   (PR, PT+4),   (PL, PM_Y),   (PR, PM_Y), (PL, PB-4), (PR, PB-4)],
    '7':  [(PL, PT+4),   (PR, PT+4),   (PM_X, PUM),  (PL, PM_Y), (PR, PM_Y), (PL, PB-4), (PR, PB-4)],
    '8':  [(PL, PT+4),   (PR, PT+4),   (PM_X, PUM),  (PL, PM_Y), (PR, PM_Y),
           (PM_X, PLM),  (PL, PB-4),   (PR, PB-4)],
    '9':  [(PL, PT+4),   (PR, PT+4),   (PL, PUM),    (PR, PUM),  (PM_X, PM_Y),
           (PL, PLM),    (PR, PLM),    (PL, PB-4),   (PR, PB-4)],
    '10': [(PL, PT+4),   (PR, PT+4),   (PM_X, PT+14),(PL, PUM),  (PR, PUM),
           (PL, PLM),    (PR, PLM),    (PM_X, PB-14),(PL, PB-4), (PR, PB-4)],
}

# ────────────────────────────────────────────
# ピップカード描画
# ────────────────────────────────────────────
def draw_pip_card(draw, rank: str, suit: str, cv: CV):
    color = sc(suit, cv)
    if rank == 'A':
        SUIT_FN[suit](draw, CX, 66, 24, color)
    else:
        pr = 5
        for px, py in PIP_LAYOUTS.get(rank, []):
            SUIT_FN[suit](draw, px, py, pr, color)

# ────────────────────────────────────────────
# コートカード（J/Q/K）キャラクター描画
# ────────────────────────────────────────────
def draw_face_card(draw, rank: str, suit: str, cv: CV):
    color = sc(suit, cv)
    cx = CX

    # ── ローブ（体）──────────────────────────
    robe_top = 68
    robe_bot = CY2 - 8
    rw_top, rw_bot = 22, 30
    draw.polygon([
        (cx - rw_top, robe_top), (cx + rw_top, robe_top),
        (cx + rw_bot, robe_bot), (cx - rw_bot, robe_bot),
    ], fill=cv.robe, outline=cv.trim)

    # ローブのスートシンボル
    SUIT_FN[suit](draw, cx, (robe_top + robe_bot) // 2, 12, color)

    # ── 顔 (頭) ────────────────────────────────
    head_cy = 51
    head_r  = 14
    draw.ellipse([cx-head_r, head_cy-head_r, cx+head_r, head_cy+head_r],
                 fill=cv.skin, outline=cv.trim)

    # 目
    for ex in (cx-5, cx+5):
        draw.ellipse([ex-2, head_cy-3, ex+2, head_cy+1], fill=cv.rank_col)

    # 口 (弧)
    draw.arc([cx-5, head_cy+2, cx+5, head_cy+8], 0, 180, fill=cv.rank_col, width=1)

    # 首/えり
    draw.polygon([
        (cx-6, head_cy+head_r), (cx+6, head_cy+head_r),
        (cx+8, robe_top),       (cx-8, robe_top),
    ], fill=cv.skin, outline=cv.trim)

    # ── 王冠/帽子 (ランク別) ─────────────────────
    hat_base_y = head_cy - head_r

    if rank == 'K':
        # 5 point crown
        crown_base = hat_base_y + 2
        pts = [
            (cx - 14, crown_base),
            (cx - 14, crown_base - 7),
            (cx - 7,  crown_base - 3),
            (cx,      crown_base - 12),
            (cx + 7,  crown_base - 3),
            (cx + 14, crown_base - 7),
            (cx + 14, crown_base),
        ]
        draw.polygon(pts, fill=cv.trim, outline=color)
        # Crown gems
        for gx, gy in [(cx-12, crown_base-6), (cx, crown_base-10), (cx+12, crown_base-6)]:
            draw.ellipse([gx-3, gy-3, gx+3, gy+3], fill=color)

    elif rank == 'Q':
        # Tiara arc
        ta_y = hat_base_y - 1
        draw.arc([cx-14, ta_y-10, cx+14, ta_y+4], 195, 345, fill=cv.trim, width=3)
        # Pearl dots on tiara
        for gx, gy in [(cx-11, ta_y-4), (cx-5, ta_y-8),
                       (cx,    ta_y-9), (cx+5, ta_y-8), (cx+11, ta_y-4)]:
            draw.ellipse([gx-2, gy-2, gx+2, gy+2], fill=color)
        # Side hair
        for dx in (-1, 1):
            hx0 = cx + dx * head_r - 5
            hx1 = cx + dx * (head_r + 7) + 5
            if hx0 > hx1:
                hx0, hx1 = hx1, hx0
            draw.ellipse([hx0, head_cy, hx1, head_cy + 18], fill=cv.robe)

    elif rank == 'J':
        # Bi-color jester hat
        hat_pts = [
            (cx-14, hat_base_y+2),
            (cx-6,  hat_base_y-8),
            (cx,    hat_base_y-2),
            (cx+6,  hat_base_y-8),
            (cx+14, hat_base_y+2),
        ]
        half_l = hat_pts[:3] + [(cx, hat_base_y+2)]
        half_r = [(cx, hat_base_y+2)] + hat_pts[2:]
        draw.polygon(half_l, fill=cv.trim, outline=color)
        draw.polygon(half_r, fill=color,   outline=cv.trim)
        # Bell tips
        for bx, by, bc in [(cx-6, hat_base_y-8, color), (cx+6, hat_base_y-8, cv.trim)]:
            draw.ellipse([bx-3, by-3, bx+3, by+3], fill=bc)

    # ── 肩ライン ──────────────────────────────
    draw.line([(cx-rw_top, robe_top), (cx+rw_top, robe_top)], fill=cv.trim, width=2)

# ────────────────────────────────────────────
# ジョーカー描画
# ────────────────────────────────────────────
def draw_joker(draw, variant: int, cv: CV):
    """variant=0 → red joker, variant=1 → black/alt joker."""
    j_color  = cv.red_suit if variant == 0 else cv.blk_suit
    alt_col  = cv.accent

    # JOKER ラベル (上部)
    draw.text((CX, CY1+10), "JOKER", font=lf(11), fill=cv.rank_col, anchor="mt")

    cx = CX
    # ── ジェスターの体 ──────────────────────
    body_top = 68
    body_bot = CY2 - 10
    bw = 24
    draw.polygon([
        (cx-bw, body_top), (cx+bw, body_top),
        (cx+bw+8, body_bot), (cx-bw-8, body_bot),
    ], fill=j_color, outline=alt_col)

    # ひし形ダイヤパターン on robe
    for i in range(3):
        dy = body_top + 8 + i * 18
        dc = alt_col if i % 2 == 0 else j_color
        draw.polygon([(cx, dy), (cx+9, dy+9), (cx, dy+18), (cx-9, dy+9)], fill=dc)

    # ── 頭 ─────────────────────────────────
    head_cy = 50
    head_r  = 13
    draw.ellipse([cx-head_r, head_cy-head_r, cx+head_r, head_cy+head_r],
                 fill=cv.skin, outline=alt_col)

    # 目 (おどけた表情)
    for ex, ey in [(cx-5, head_cy-2), (cx+5, head_cy-2)]:
        draw.ellipse([ex-3, ey-3, ex+3, ey+3], fill=cv.rank_col)
    # 大きな笑顔
    draw.arc([cx-7, head_cy+2, cx+7, head_cy+9], 0, 180, fill=cv.rank_col, width=2)

    # 首
    draw.polygon([
        (cx-5, head_cy+head_r), (cx+5, head_cy+head_r),
        (cx+7, body_top), (cx-7, body_top),
    ], fill=cv.skin, outline=alt_col)

    # ── 3点ジェスター帽子 ──────────────────
    hat_base_y = head_cy - head_r
    bell_r = 4
    # Left tip (alt color)
    draw.polygon([(cx-14, hat_base_y+2), (cx-22, hat_base_y-12), (cx-3, hat_base_y-4)],
                 fill=alt_col, outline=j_color)
    draw.ellipse([cx-22-bell_r, hat_base_y-12-bell_r,
                  cx-22+bell_r, hat_base_y-12+bell_r], fill=j_color)
    # Center tip (j_color)
    draw.polygon([(cx-3, hat_base_y-4), (cx, hat_base_y-16), (cx+3, hat_base_y-4)],
                 fill=j_color, outline=alt_col)
    draw.ellipse([cx-bell_r, hat_base_y-16-bell_r,
                  cx+bell_r, hat_base_y-16+bell_r], fill=alt_col)
    # Right tip (alt color)
    draw.polygon([(cx+3, hat_base_y-4), (cx+22, hat_base_y-12), (cx+14, hat_base_y+2)],
                 fill=alt_col, outline=j_color)
    draw.ellipse([cx+22-bell_r, hat_base_y-12-bell_r,
                  cx+22+bell_r, hat_base_y-12+bell_r], fill=j_color)
    # Hat band
    draw.polygon([
        (cx-14, hat_base_y+2), (cx+14, hat_base_y+2),
        (cx+head_r-2, hat_base_y+6), (cx-head_r+2, hat_base_y+6),
    ], fill=j_color if variant==1 else alt_col, outline=alt_col if variant==1 else j_color)

# ────────────────────────────────────────────
# スートマーク絵文字（単体）
# ────────────────────────────────────────────
def gen_suit_emoji(cv: CV, out: Path):
    """4種のスートマーク単体絵文字を生成。"""
    # outer bg を dice/alphanum と同じフレーム枠で描画
    for suit_key, is_red in [('S', False), ('H', True), ('D', True), ('C', False)]:
        img = Image.new("RGBA", (SIZE, SIZE), cv.outer_bg)
        draw = ImageDraw.Draw(img)
        # シンプルな枠線（カード外枠を流用）
        draw.rounded_rectangle([4, 4, SIZE-5, SIZE-5], radius=8,
                               fill=cv.card_bg, outline=cv.card_border, width=2)
        # フレーム装飾
        draw_card_frame(draw, cv)
        # 大きなスートマーク
        color = cv.red_suit if is_red else cv.blk_suit
        SUIT_FN[suit_key](draw, CX, CX, 26, color)
        img.save(out / f"card_suit_{suit_key}.png", "PNG", optimize=True)

# ────────────────────────────────────────────
# 全生成
# ────────────────────────────────────────────
SUITS = [('S','Spade'), ('H','Heart'), ('D','Diamond'), ('C','Club')]
RANKS = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']

def generate_proposal(cv: CV) -> int:
    out = DIST / cv.key
    out.mkdir(parents=True, exist_ok=True)
    count = 0

    for suit_key, _ in SUITS:
        for rank in RANKS:
            img, draw = make_card(cv)
            draw_card_frame(draw, cv)
            paste_corners(img, rank, suit_key, cv)

            if rank in ('J', 'Q', 'K'):
                draw_face_card(draw, rank, suit_key, cv)
            else:
                draw_pip_card(draw, rank, suit_key, cv)

            img.save(out / f"card_{suit_key}_{rank}.png", "PNG", optimize=True)
            count += 1

    # Jokers
    for i in range(2):
        img, draw = make_card(cv)
        draw_card_frame(draw, cv)
        draw_joker(draw, i, cv)
        img.save(out / f"card_joker_{i+1}.png", "PNG", optimize=True)
        count += 1

    # Suit mark emoji
    gen_suit_emoji(cv, out)
    count += 4

    return count

def main():
    total = 0
    for cv in PROPOSALS:
        n = generate_proposal(cv)
        print(f"  {cv.label} ({cv.key}): {n}枚")
        total += n
    print(f"\n✓ 合計 {total}枚")

if __name__ == "__main__":
    main()

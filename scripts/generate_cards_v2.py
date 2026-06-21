"""
Secvier ImageAssets — トランプ絵文字 v2
白磁ベース・スート別バリアント配色 + Noto Sans Symbols2 コートカード

スート→バリアント対応:
  ♠ Spades   → seiyuu  (星幽: 深夜宇宙, 深紫)
  ♥ Hearts   → kougyoku (紅玉: 紅玉石, 深紅)
  ♦ Diamonds → sakin    (砂金: 羊皮紙, 黄金)
  ♣ Clubs    → suigyoku (翠玉: 深翠, 翠緑)

生成:
  4スート × 14ランク (A,2~10,J,C,Q,K) = 56枚
  ジョーカー 2枚 (黒: seiyuu, 赤: kougyoku)
  スート単体絵文字 4枚
  合計 62枚

出力: dist/cards/hakuji_c/card_{suit}_{rank}.png
             dist/cards/hakuji_c/card_joker_black.png
             dist/cards/hakuji_c/card_joker_red.png
             dist/cards/hakuji_c/card_suit_{S,H,D,C}.png
"""
from __future__ import annotations
import io
import math
import re
import sys
from pathlib import Path
from typing import NamedTuple

import fitz  # PyMuPDF

from PIL import Image, ImageDraw, ImageFont

# ════════════════════════════════════════════
# パス
# ════════════════════════════════════════════
ROOT      = Path(__file__).parent.parent
FONT_PATH = ROOT / "assets" / "fonts" / "Secvier.otf"
SUIT_DIR  = ROOT / "src" / "suits"
NOTO_DIR  = ROOT / "src" / "noto_cards"
DIST      = ROOT / "dist" / "cards" / "hakuji_c"
SIZE      = 128
CX        = SIZE // 2  # 64

# カード矩形
CX1, CY1 = 9,   3
CX2, CY2 = 119, 125
CARD_R    = 9

# ════════════════════════════════════════════
# バリアント定義（generate_all_v3.py から流用）
# ════════════════════════════════════════════
class V(NamedTuple):
    key:    str; label:  str
    bg:     tuple; text:   tuple; border: tuple
    accent: tuple; sfill:  tuple; sline:  tuple

VARIANTS: dict[str, V] = {
    v.key: v for v in [
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
}

# スート→バリアントキー対応
SUIT_VARIANT: dict[str, str] = {
    'S': 'seiyuu',
    'H': 'kougyoku',
    'D': 'sakin',
    'C': 'suigyoku',
}
SUIT_FILE: dict[str, str] = {
    'S': 'spade',
    'H': 'heart',
    'D': 'diamond',
    'C': 'club',
}
SUIT_OLD_FILL: dict[str, str] = {
    'S': '#1A1A1A',
    'H': '#CC1111',
    'D': '#CC1111',
    'C': '#1A1A1A',
}

# ════════════════════════════════════════════
# フォント
# ════════════════════════════════════════════
def lf(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)

# ════════════════════════════════════════════
# SVGスートマーク描画
# ════════════════════════════════════════════
# 72×72 正規化座標 (generate_cards.py の SUIT_PATHS と同一)
SUIT_PATHS: dict[str, str] = {
    'S': "M36,0 L27,9 L9,27 L0,45 L18,63 L27,63 L36,54 L45,63 L54,63 L72,45 L63,27 L45,9 Z M27,72 L45,72 L36,54 Z",
    'H': "M36,72 L27,54 L9,36 L0,27 L0,9 L18,0 L27,0 L36,9 L45,0 L54,0 L72,9 L72,27 L63,36 L45,54 Z",
    'D': "M36,0 L27,18 L18,27 L0,36 L18,45 L27,54 L36,72 L45,54 L54,45 L72,36 L54,27 L45,18 Z",
    'C': "M18,27 L18,9 L27,0 L45,0 L54,9 L54,27 L36,45 Z M27,63 L9,63 L0,54 L0,36 L9,27 L18,27 L36,54 Z M45,63 L63,63 L72,54 L72,36 L63,27 L54,27 L36,54 Z M27,72 L45,72 L36,54 Z",
}

def _parse_path_polys(d: str) -> list[list[tuple[float, float]]]:
    """M/L/Z のみで構成される SVG path d 属性 → ポリゴン点列リスト。"""
    polys: list[list[tuple[float, float]]] = []
    current: list[tuple[float, float]] = []
    tokens = re.findall(r'[MmLlZz]|[-+]?[0-9]*\.?[0-9]+', d)
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ('M', 'm', 'L', 'l'):
            i += 1
        elif t in ('Z', 'z'):
            if current:
                polys.append(current[:])
                current = []
            i += 1
        else:
            if i + 1 < len(tokens) and re.match(r'^[-+]?[0-9]*\.?[0-9]+$', tokens[i + 1]):
                current.append((float(t), float(tokens[i + 1])))
                i += 2
            else:
                i += 1
    if current:
        polys.append(current)
    return polys

def color_hex(c: tuple) -> str:
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"

def render_suit_svg(suit: str, size: int, color: tuple) -> Image.Image:
    """Pillowポリゴン描画でスートマークを生成（SVGライブラリ不要）。"""
    scale = size / 72.0
    polys = _parse_path_polys(SUIT_PATHS[suit])
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    fill_color = color[:3] + (255,)
    for pts in polys:
        scaled = [(x * scale, y * scale) for x, y in pts]
        if len(scaled) >= 3:
            draw.polygon(scaled, fill=fill_color)
    return img

# ════════════════════════════════════════════
# Notoコートカード SVG レンダリング
# ════════════════════════════════════════════
RANK_NAME: dict[str, str] = {
    'J': 'JACK', 'C': 'KNIGHT', 'Q': 'QUEEN', 'K': 'KING',
}
SUIT_NAME: dict[str, str] = {
    'S': 'SPADES', 'H': 'HEARTS', 'D': 'DIAMONDS', 'C': 'CLUBS',
}
JOKER_FILE: dict[str, str] = {
    'black': 'PLAYING CARD BLACK JOKER',
    'red':   'PLAYING CARD RED JOKER',
}

def render_noto_svg(svg_path: Path, out_w: int, out_h: int,
                    crop_frac: float = 0.0) -> Image.Image | None:
    """
    Noto SVGをPyMuPDF(fitz)でout_w×out_hにレンダリング。
    crop_frac>0 なら四辺を比率分クロップしてリサイズ。
    失敗時はNone。
    """
    if not svg_path.exists() or svg_path.stat().st_size < 200:
        return None
    try:
        render_w = int(out_w / (1 - 2 * crop_frac)) if crop_frac > 0 else out_w
        render_h = int(out_h / (1 - 2 * crop_frac)) if crop_frac > 0 else out_h
        svg_bytes = svg_path.read_bytes()
        doc  = fitz.open(stream=svg_bytes, filetype="svg")
        page = doc[0]
        sx   = render_w / page.rect.width
        sy   = render_h / page.rect.height
        pix  = page.get_pixmap(matrix=fitz.Matrix(sx, sy), alpha=True)
        full = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGBA")
        if crop_frac > 0:
            fw, fh   = full.size
            cx_off   = int(fw * crop_frac)
            cy_off   = int(fh * crop_frac)
            full     = full.crop((cx_off, cy_off, fw - cx_off, fh - cy_off))
            full     = full.resize((out_w, out_h), Image.LANCZOS)
        return full
    except Exception as e:
        print(f"  fitz error for {svg_path.name}: {e}", file=sys.stderr)
        return None

# ════════════════════════════════════════════
# フレーム（generate_all_v3.py の frame() 相当）
# ────────────────────────────────────────────
# カード外縁フレーム（128×128ルートに適用）
# ════════════════════════════════════════════
def poly(cx: float, cy: float, r: float, n: int, rot: float = 0):
    pts = []
    for i in range(n):
        a = math.radians(rot + i * 360 / n) - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def draw_outer_frame(draw: ImageDraw.ImageDraw, v: V):
    """128×128キャンバス外縁にバリアント別デコレーション。"""
    m = 4
    if v.key == "seiyuu":
        draw.rounded_rectangle([m, m, SIZE-m-1, SIZE-m-1],
                                radius=8, outline=v.border, width=2)
        for cx, cy in [(m+2,m+2),(SIZE-m-3,m+2),(m+2,SIZE-m-3),(SIZE-m-3,SIZE-m-3)]:
            draw.polygon(poly(cx, cy, 4, 4, 45), fill=v.accent)

    elif v.key == "suigyoku":
        draw.rounded_rectangle([m, m, SIZE-m-1, SIZE-m-1],
                                radius=6, outline=v.border, width=2)
        for (cx, cy), rot in [((m+2,m+2),0),((SIZE-m-3,m+2),0),
                               ((m+2,SIZE-m-3),180),((SIZE-m-3,SIZE-m-3),180)]:
            draw.polygon(poly(cx, cy, 5, 3, rot), fill=v.accent)

    elif v.key == "kougyoku":
        draw.rounded_rectangle([m, m, SIZE-m-1, SIZE-m-1],
                                radius=10, outline=v.border, width=2)
        cr = 4
        for cx, cy in [(m+3,m+3),(SIZE-m-4,m+3),(m+3,SIZE-m-4),(SIZE-m-4,SIZE-m-4)]:
            draw.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=v.accent)

    elif v.key == "hakuji":
        draw.rectangle([3, 3, SIZE-4, SIZE-4], outline=v.border, width=1)
        draw.rectangle([7, 7, SIZE-8, SIZE-8], outline=v.border, width=1)
        sq = 3
        for cx, cy in [(3,3),(SIZE-4,3),(3,SIZE-4),(SIZE-4,SIZE-4)]:
            draw.rectangle([cx-sq, cy-sq, cx+sq, cy+sq], fill=v.accent)

    else:  # sakin
        draw.rectangle([m, m, SIZE-m-1, SIZE-m-1], outline=v.border, width=2)
        arm = 7
        for cx, cy in [(m+1,m+1),(SIZE-m-2,m+1),(m+1,SIZE-m-2),(SIZE-m-2,SIZE-m-2)]:
            draw.line([(cx,cy),(cx+arm,cy+arm)], fill=v.accent, width=2)
            draw.line([(cx+arm,cy),(cx,cy+arm)], fill=v.accent, width=2)

# ════════════════════════════════════════════
# カードフレームデコレーション（カード矩形内縁）
# ════════════════════════════════════════════
def draw_card_frame(draw: ImageDraw.ImageDraw, v: V):
    """カード矩形の内側コーナーにバリアント別小デコ。"""
    # カード内側コーナー座標
    corners = [
        (CX1+6, CY1+6), (CX2-6, CY1+6),
        (CX1+6, CY2-6), (CX2-6, CY2-6),
    ]
    if v.key == "seiyuu":
        for cx, cy in corners:
            draw.polygon(poly(cx, cy, 3, 4, 45), fill=v.accent)
    elif v.key == "suigyoku":
        for (cx, cy), rot in zip(corners, [0, 0, 180, 180]):
            draw.polygon(poly(cx, cy, 3, 3, rot), fill=v.accent)
    elif v.key == "kougyoku":
        cr = 3
        for cx, cy in corners:
            draw.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=v.accent)
    elif v.key == "hakuji":
        draw.rectangle([CX1+5, CY1+5, CX2-5, CY2-5], outline=v.accent, width=1)
        sq = 2
        for cx, cy in corners:
            draw.rectangle([cx-sq, cy-sq, cx+sq, cy+sq], fill=v.accent)
    else:  # sakin
        arm = 5
        for cx, cy in corners:
            draw.line([(cx, cy), (cx+arm, cy+arm)], fill=v.accent, width=1)
            draw.line([(cx+arm, cy), (cx, cy+arm)], fill=v.accent, width=1)

# ════════════════════════════════════════════
# カードベース生成
# ════════════════════════════════════════════
CARD_BG = (255, 253, 248, 255)   # クリーム白（全スート共通カード面）

def make_card_base(v: V) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    """128×128 カードキャンバス + カード矩形。"""
    img  = Image.new("RGBA", (SIZE, SIZE), v.bg)
    draw = ImageDraw.Draw(img)
    # 外縁フレーム
    draw_outer_frame(draw, v)
    # カード面（白/クリーム）
    draw.rounded_rectangle(
        [CX1, CY1, CX2, CY2], radius=CARD_R,
        fill=CARD_BG, outline=v.border, width=2,
    )
    # カード面内縁デコ
    draw_card_frame(draw, v)
    return img, draw

# ════════════════════════════════════════════
# コーナーインデックス（ランク + 小スートマーク）
# ════════════════════════════════════════════
def make_corner(rank: str, suit: str, v: V) -> Image.Image:
    """22×30 RGBA コーナーインデックス画像。"""
    W, H  = 22, 30
    ci    = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd    = ImageDraw.Draw(ci)
    fsize = 14 if len(rank) == 1 else 11
    # ランク文字
    cd.text((W//2, 1), rank, font=lf(fsize), fill=v.border[:3]+(255,), anchor="mt")
    # 小スートマーク（12×12）
    pip_col = v.sline[:3] + (255,)
    pip_img = render_suit_svg(suit, 12, pip_col)
    ci.alpha_composite(pip_img, (W//2 - 6, H - 13))
    return ci

def paste_corners(img: Image.Image, rank: str, suit: str, v: V):
    ci = make_corner(rank, suit, v)
    # 左上
    img.alpha_composite(ci, (CX1 + 2, CY1 + 2))
    # 右下（180°回転）
    ci_rot = ci.rotate(180)
    img.alpha_composite(ci_rot, (CX2 - 2 - ci.width, CY2 - 2 - ci.height))

# ════════════════════════════════════════════
# ピップレイアウト
# ════════════════════════════════════════════
# カード面内ピップ領域
PL, PM_X, PR = 34, CX, 94
PT, PB       = 40, 90
PM_Y         = (PT + PB) // 2
PUM          = PT + (PM_Y - PT) * 2 // 5
PLM          = PM_Y + (PB - PM_Y) * 3 // 5

PIP_POSITIONS: dict[str, list[tuple[int, int]]] = {
    '2':  [(PM_X, PT+2),  (PM_X, PB-2)],
    '3':  [(PM_X, PT+2),  (PM_X, PM_Y), (PM_X, PB-2)],
    '4':  [(PL, PT+2),   (PR, PT+2),   (PL, PB-2),   (PR, PB-2)],
    '5':  [(PL, PT+2),   (PR, PT+2),   (PM_X, PM_Y), (PL, PB-2), (PR, PB-2)],
    '6':  [(PL, PT+2),   (PR, PT+2),   (PL, PM_Y),   (PR, PM_Y), (PL, PB-2), (PR, PB-2)],
    '7':  [(PL, PT+2),   (PR, PT+2),   (PM_X, PUM),  (PL, PM_Y), (PR, PM_Y), (PL, PB-2), (PR, PB-2)],
    '8':  [(PL, PT+2),   (PR, PT+2),   (PM_X, PUM),  (PL, PM_Y), (PR, PM_Y),
           (PM_X, PLM),  (PL, PB-2),   (PR, PB-2)],
    '9':  [(PL, PT+2),   (PR, PT+2),   (PL, PUM),    (PR, PUM),  (PM_X, PM_Y),
           (PL, PLM),    (PR, PLM),    (PL, PB-2),   (PR, PB-2)],
    '10': [(PL, PT+2),   (PR, PT+2),   (PM_X, PT+12),(PL, PUM),  (PR, PUM),
           (PL, PLM),    (PR, PLM),    (PM_X, PB-12),(PL, PB-2), (PR, PB-2)],
}

def draw_pips(img: Image.Image, rank: str, suit: str, v: V):
    """数字カードのピップを配置。"""
    pip_col = v.sline[:3] + (255,)
    if rank == 'A':
        # エース: 大きなスートマーク中央
        pip_sz = 44
        pip_img = render_suit_svg(suit, pip_sz, pip_col)
        img.alpha_composite(pip_img, (CX - pip_sz//2, 65 - pip_sz//2))
    else:
        pip_sz = 14
        pip_img = render_suit_svg(suit, pip_sz, pip_col)
        for px, py in PIP_POSITIONS.get(rank, []):
            img.alpha_composite(pip_img, (px - pip_sz//2, py - pip_sz//2))

# ════════════════════════════════════════════
# コートカード（J/C/Q/K）
# ════════════════════════════════════════════
FACE_AREA_W = 84   # コートカード図柄幅
FACE_AREA_H = 78   # コートカード図柄高
FACE_X      = CX - FACE_AREA_W // 2  # 22
FACE_Y      = 32                       # 図柄上端

def draw_face_card(img: Image.Image, draw: ImageDraw.ImageDraw,
                   rank: str, suit: str, v: V):
    """Noto SVGを使用。利用不可の場合はフォールバック表示。"""
    svg_name = f"PLAYING CARD {RANK_NAME[rank]} OF {SUIT_NAME[suit]}.svg"
    svg_path = NOTO_DIR / svg_name

    noto_img = render_noto_svg(svg_path, FACE_AREA_W, FACE_AREA_H, crop_frac=0.08)
    if noto_img is not None:
        img.alpha_composite(noto_img, (FACE_X, FACE_Y))
    else:
        # フォールバック: ランク文字を大きく表示
        pip_col = v.sline[:3] + (255,)
        draw.text((CX, 68), rank, font=lf(52), fill=pip_col, anchor="mm")
        # 小スート4隅
        sm = 10
        sm_img = render_suit_svg(suit, sm, pip_col)
        for ox, oy in [(FACE_X, FACE_Y), (FACE_X+FACE_AREA_W-sm, FACE_Y),
                       (FACE_X, FACE_Y+FACE_AREA_H-sm),
                       (FACE_X+FACE_AREA_W-sm, FACE_Y+FACE_AREA_H-sm)]:
            img.alpha_composite(sm_img, (ox, oy))

# ════════════════════════════════════════════
# ジョーカーカード
# ════════════════════════════════════════════
def make_joker_card(color: str) -> Image.Image:
    """color = 'black' or 'red'."""
    v_key = 'seiyuu' if color == 'black' else 'kougyoku'
    v     = VARIANTS[v_key]
    img, draw = make_card_base(v)

    pip_col = v.sline[:3] + (255,)

    # Noto SVG ジョーカー
    svg_path = NOTO_DIR / f"{JOKER_FILE[color]}.svg"
    noto_img = render_noto_svg(svg_path, FACE_AREA_W, FACE_AREA_H + 16, crop_frac=0.06)
    if noto_img is not None:
        img.alpha_composite(noto_img, (FACE_X, FACE_Y - 4))
    else:
        # フォールバック: "JOKER" テキスト + スート4個
        draw.text((CX, 62), "JOKER", font=lf(16), fill=pip_col, anchor="mm")
        sm = 16
        for suit, ox, oy in [('S',CX-22,72),('H',CX+6,72),('D',CX-22,90),('C',CX+6,90)]:
            sm_v  = VARIANTS[SUIT_VARIANT[suit]]
            sm_col = sm_v.sline[:3] + (255,)
            sm_img = render_suit_svg(suit, sm, sm_col)
            img.alpha_composite(sm_img, (ox, oy))

    # コーナー "JK" ラベル + スート4個
    ci_w, ci_h = 22, 30
    ci = Image.new("RGBA", (ci_w, ci_h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(ci)
    cd.text((ci_w//2, 1), "JK", font=lf(11), fill=pip_col, anchor="mt")
    # 4スートを小さく並べる
    mini = 6
    suits_row = ['S','H','D','C']
    for i, s in enumerate(suits_row):
        sc_col = VARIANTS[SUIT_VARIANT[s]].sline[:3] + (255,)
        si     = render_suit_svg(s, mini, sc_col)
        ox     = (i % 2) * (mini + 1)
        oy     = ci_h - mini * 2 - 2 + (i // 2) * (mini + 1)
        ci.alpha_composite(si, (ox, oy))
    img.alpha_composite(ci, (CX1 + 2, CY1 + 2))
    img.alpha_composite(ci.rotate(180), (CX2 - 2 - ci_w, CY2 - 2 - ci_h))

    return img

# ════════════════════════════════════════════
# スート単体絵文字（バリアントフレーム付き）
# ════════════════════════════════════════════
def make_suit_mark_emoji(suit: str) -> Image.Image:
    """スートに対応したバリアントフレームで128×128スートマーク絵文字。"""
    v    = VARIANTS[SUIT_VARIANT[suit]]
    img  = Image.new("RGBA", (SIZE, SIZE), v.bg)
    draw = ImageDraw.Draw(img)
    draw_outer_frame(draw, v)

    # 大きなスートマーク（中央）
    mark_sz  = 72
    mark_col = v.sline[:3] + (255,)
    mark_img = render_suit_svg(suit, mark_sz, mark_col)
    img.alpha_composite(mark_img, (CX - mark_sz//2, CX - mark_sz//2))
    return img

# ════════════════════════════════════════════
# メイン
# ════════════════════════════════════════════
RANKS_NUM  = ['A','2','3','4','5','6','7','8','9','10']
RANKS_FACE = ['J','C','Q','K']
SUITS      = ['S','H','D','C']

def main():
    DIST.mkdir(parents=True, exist_ok=True)

    # 古いバリアントディレクトリは手動削除してください
    # (dist/cards/seiyuu_c/, dist/cards/sakin_c/)

    total = 0

    # ── 数字カード ──────────────────────────
    for suit in SUITS:
        v = VARIANTS[SUIT_VARIANT[suit]]
        for rank in RANKS_NUM:
            img, draw = make_card_base(v)
            draw_pips(img, rank, suit, v)
            paste_corners(img, rank, suit, v)
            out = DIST / f"card_{suit}_{rank}.png"
            img.save(out)
            total += 1
    print(f"  数字カード: {len(SUITS) * len(RANKS_NUM)} 枚")

    # ── コートカード ────────────────────────
    for suit in SUITS:
        v = VARIANTS[SUIT_VARIANT[suit]]
        for rank in RANKS_FACE:
            img, draw = make_card_base(v)
            draw_face_card(img, draw, rank, suit, v)
            paste_corners(img, rank, suit, v)
            out = DIST / f"card_{suit}_{rank}.png"
            img.save(out)
            total += 1
    print(f"  コートカード: {len(SUITS) * len(RANKS_FACE)} 枚")

    # ── ジョーカー ──────────────────────────
    for color in ['black', 'red']:
        img = make_joker_card(color)
        out = DIST / f"card_joker_{color}.png"
        img.save(out)
        total += 1
    print(f"  ジョーカー: 2 枚")

    # ── スート単体絵文字 ─────────────────────
    for suit in SUITS:
        img = make_suit_mark_emoji(suit)
        out = DIST / f"card_suit_{suit}.png"
        img.save(out)
        total += 1
    print(f"  スート絵文字: {len(SUITS)} 枚")

    print(f"\n[OK] 合計 {total} 枚 → dist/cards/hakuji_c/")


if __name__ == "__main__":
    main()

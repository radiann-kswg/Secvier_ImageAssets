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

出力: dist/cards/card_{suit}_{rank}.png
             dist/cards/card_joker_black.png
             dist/cards/card_joker_red.png
             dist/cards/card_suit_{S,H,D,C}.png
"""
from __future__ import annotations
import io
import math
import re
import sys
from pathlib import Path
from typing import NamedTuple

import fitz        # PyMuPDF
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ════════════════════════════════════════════
# パス
# ════════════════════════════════════════════
ROOT      = Path(__file__).parent.parent
FONT_PATH = ROOT / "assets" / "fonts" / "Secvier.otf"
SUIT_DIR  = ROOT / "src" / "suits"
NOTO_DIR   = ROOT / "src" / "noto_cards"
NOTO_CACHE = ROOT / "src" / "noto_cache"   # bindfs 回避用キャッシュ
NOTO_SVG   = ROOT / "src" / "noto_svg"     # 追加キャッシュ

def get_noto_path(name: str) -> Path:
    """noto_svg → noto_cache → noto_cards の順で有効なSVGを探す。"""
    for d in (NOTO_SVG, NOTO_CACHE, NOTO_DIR):
        p = d / name
        if p.exists() and p.stat().st_size > 200:
            return p
    return NOTO_DIR / name  # フォールバック（0バイトでも返す）
DIST      = ROOT / "dist" / "cards"
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

_NOTO_ZOOM     = 1.4   # 拡大倍率: ZOOMレンダー後クロップで余白を狭める
_NOTO_CORNER_W = 30    # 最終画像コーナー余白幅 (Secvierラベル26px + 4px)
_NOTO_CORNER_H = 44    # 最終画像コーナー余白高 (Secvierラベル38px + 6px)

def render_noto_figure(svg_path: Path, v: V,
                       out_w: int, out_h: int) -> Image.Image | None:
    """
    Noto コートカード SVG から人物図柄を抽出し、バリアント配色で着色。
    処理:
      1. 3倍サイズで高解像度レンダリング
      2. 外縁カード枠を透過化（上下左右 6%）
      3. コーナーインデックス（ランク+スート）を消去（左上・右下 30%×28%）
      4. 残ピクセル（人物図）をバリアントの sline カラーに着色
      5. out_w × out_h にリサイズ
    """
    if not svg_path.exists() or svg_path.stat().st_size < 200:
        return None
    try:
        zoom     = _NOTO_ZOOM
        render_w = int(out_w * zoom)
        render_h = int(out_h * zoom)

        scale_up = 3
        rw, rh   = render_w * scale_up, render_h * scale_up

        svg_bytes = svg_path.read_bytes()
        doc  = fitz.open(stream=svg_bytes, filetype="svg")
        page = doc[0]
        sx   = rw / page.rect.width
        sy   = rh / page.rect.height
        pix  = page.get_pixmap(matrix=fitz.Matrix(sx, sy), alpha=True)
        img  = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGBA")
        arr  = np.array(img, dtype=np.uint8)

        # ① 外縁カード枠を透過（上下左右 6%）
        bx = int(rw * 0.06)
        by = int(rh * 0.06)
        arr[:by, :, 3] = 0
        arr[rh - by:, :, 3] = 0
        arr[:, :bx, 3] = 0
        arr[:, rw - bx:, 3] = 0

        # ② Noto コーナーインデックス消去（SVG内 36%W×46%H のコーナー矩形）
        cx_px = int(rw * 0.36)
        cy_px = int(rh * 0.46)
        arr[:cy_px, :cx_px, 3] = 0
        arr[rh - cy_px:, rw - cx_px:, 3] = 0

        # ③ 残ピクセルをスート sline カラーに着色
        pip_r, pip_g, pip_b = v.sline[:3]
        dark_mask = arr[:, :, 3] > 10
        arr[dark_mask, 0] = pip_r
        arr[dark_mask, 1] = pip_g
        arr[dark_mask, 2] = pip_b

        result = Image.fromarray(arr, 'RGBA')
        result = result.resize((render_w, render_h), Image.LANCZOS)

        # ④ クロップ: コーナー余白が _NOTO_CORNER_W × _NOTO_CORNER_H になるよう offset
        cx_face = int(render_w * 0.36)
        cy_face = int(render_h * 0.46)
        ox = max(0, cx_face - _NOTO_CORNER_W)
        oy = max(0, cy_face - _NOTO_CORNER_H)
        result = result.crop((ox, oy, ox + out_w, oy + out_h))

        return result
    except Exception as e:
        print(f"  noto_figure error for {svg_path.name}: {e}", file=sys.stderr)
        return None


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
    """26×38 RGBA コーナーインデックス画像（数字大きめ）。"""
    W, H  = 26, 38
    ci    = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd    = ImageDraw.Draw(ci)
    fsize = 19 if len(rank) == 1 else 15   # ← 数字サイズ拡大
    # ランク文字
    cd.text((W//2, 0), rank, font=lf(fsize), fill=v.border[:3]+(255,), anchor="mt")
    # 小スートマーク（15×15）
    pip_col = v.sline[:3] + (255,)
    pip_img = render_suit_svg(suit, 15, pip_col)
    ci.alpha_composite(pip_img, (W//2 - 7, H - 16))
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
PL, PM_X, PR = 46, CX, 82          # 横幅を狭める（旧: 34, 64, 94）
PT, PB       = 36, 108
PM_Y         = (PT + PB) // 2   # 72
PUM          = PT + (PM_Y - PT) * 2 // 5   # 50
PLM          = PM_Y + (PB - PM_Y) * 3 // 5  # 93

PIP_POSITIONS: dict[str, list[tuple[int, int]]] = {
    '2':  [(PM_X, PT+2),  (PM_X, PB-2)],
    '3':  [(PM_X, PT+2),  (PM_X, PM_Y), (PM_X, PB-2)],
    '4':  [(PL, PT+2),   (PR, PT+2),   (PL, PB-2),   (PR, PB-2)],
    '5':  [(PL, PT+2),   (PR, PT+2),   (PM_X, PM_Y), (PL, PB-2), (PR, PB-2)],
    '6':  [(PL, PT+2),   (PR, PT+2),   (PL, PM_Y),   (PR, PM_Y), (PL, PB-2), (PR, PB-2)],
    '7':  [(PL, PT+2),   (PR, PT+2),   (PM_X, PUM),  (PL, PM_Y), (PR, PM_Y), (PL, PB-2), (PR, PB-2)],
    '8':  [(PL, PT+2),   (PR, PT+2),   (PM_X, PUM),  (PL, PM_Y), (PR, PM_Y),
           (PM_X, PLM),  (PL, PB-2),   (PR, PB-2)],
    # 9/10: 左右列を縦方向均等4段配置（PT=36, PB=108, 間隔24px）
    '9':  [(PL, 36), (PR, 36), (PL, 60), (PR, 60), (PM_X, PM_Y),
           (PL, 84), (PR, 84), (PL, 108),(PR, 108)],
    '10': [(PL, 36), (PR, 36), (PM_X, 48),(PL, 60), (PR, 60),
           (PL, 84), (PR, 84), (PM_X, 96),(PL, 108),(PR, 108)],
}

def draw_pips(img: Image.Image, rank: str, suit: str, v: V):
    """数字カードのピップを配置。"""
    pip_col = v.sline[:3] + (255,)
    if rank == 'A':
        # エース: 大きなスートマーク中央（拡大）
        pip_sz = 52
        pip_img = render_suit_svg(suit, pip_sz, pip_col)
        img.alpha_composite(pip_img, (CX - pip_sz//2, 62 - pip_sz//2))
    else:
        pip_sz = 16
        pip_img = render_suit_svg(suit, pip_sz, pip_col)
        for px, py in PIP_POSITIONS.get(rank, []):
            img.alpha_composite(pip_img, (px - pip_sz//2, py - pip_sz//2))

# ════════════════════════════════════════════
# コートカード（J/C/Q/K）
# ════════════════════════════════════════════
FACE_AREA_W = 110  # コートカード図柄幅 = カード面全幅
FACE_AREA_H = 122  # コートカード図柄高 = カード面全高
FACE_X      = CX1  # = 9
FACE_Y      = CY1  # = 3

def draw_face_card(img: Image.Image, draw: ImageDraw.ImageDraw,
                   rank: str, suit: str, v: V):
    """Noto SVGから人物図柄を抽出・着色して配置。利用不可の場合はフォールバック。"""
    # HEARTS KNIGHT: 頭部が破綻するため CLUBS KNIGHT SVG を代替流用（着色はHeartsのまま）
    figure_suit = 'C' if (rank == 'C' and suit == 'H') else suit
    svg_name = f"PLAYING CARD {RANK_NAME[rank]} OF {SUIT_NAME[figure_suit]}.svg"
    svg_path = get_noto_path(svg_name)

    noto_img = render_noto_figure(svg_path, v, FACE_AREA_W, FACE_AREA_H)
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

    # Noto SVG ジョーカー（人物図柄抽出・バリアント着色）
    svg_path = get_noto_path(f"{JOKER_FILE[color]}.svg")
    noto_img = render_noto_figure(svg_path, v, FACE_AREA_W, FACE_AREA_H + 10)
    if noto_img is not None:
        img.alpha_composite(noto_img, (FACE_X, FACE_Y - 2))
    else:
        # フォールバック: "JOKER" テキスト + スート4個
        draw.text((CX, 62), "JOKER", font=lf(16), fill=pip_col, anchor="mm")
        sm = 16
        for suit, ox, oy in [('S',CX-22,72),('H',CX+6,72),('D',CX-22,90),('C',CX+6,90)]:
            sm_v  = VARIANTS[SUIT_VARIANT[suit]]
            sm_col = sm_v.sline[:3] + (255,)
            sm_img = render_suit_svg(suit, sm, sm_col)
            img.alpha_composite(sm_img, (ox, oy))

    # コーナー "JOKER" 横書きラベル（数字カードのランク文字と同様の扱い）
    ci_w, ci_h = 26, 20
    ci = Image.new("RGBA", (ci_w, ci_h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(ci)
    cd.text((ci_w // 2, 1), "JOKER", font=lf(8), fill=pip_col, anchor="mt")
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

    print(f"\n[OK] 合計 {total} 枚 → dist/cards/")


if __name__ == "__main__":
    main()

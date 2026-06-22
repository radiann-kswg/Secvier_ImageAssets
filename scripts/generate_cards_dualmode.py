"""
Secvier ImageAssets — トランプ絵文字 デュアルモード版（Discord / Misskey）

カード描画範囲のアスペクト比を 4:5 縦長に統一し、プラットフォーム別に出力する。

  Discord  : 256×256 正方形キャンバス。4:5カードを中央に配置し、
             左右端それぞれ約25pxを透過させる（カードは上下いっぱい）。
  Misskey  : 256×320 キャンバス。4:5カードがキャンバス全面を占める。

主な仕様（generate_cards_v2.py からの変更点）:
  * 全キャンバスを 4:5 縦長へ再設計（マスタ 768×960 を SS=3 で描画 → 各出力へ縮小）
  * スートピップ／Notoコート図柄をカード中央へ対称配置（間隔は保持）
  * JOKER文字は縦方向に90°回転（頭文字Jが上端/下端）
  * Notoコート図柄はカード内側にフィットさせ、隅インデックス部のみを
    クリアして Secvier フォントの番号・スートを収める（図柄欠けを最小化）
  * 左上・右下の番号＋スートはカード四隅基準で位置・大きさ一定

出力:
  dist/cards/discord/card_{suit}_{rank}.png        (256×256)
  dist/cards/discord/card_joker_{black|red}.png
  dist/cards/discord/card_suit_{S,H,D,C}.png
  dist/cards/misskey/card_{...}.png                (256×320)

著作権者: RadianN_kswg / ラジアン（柏木主税） / ライセンス: CC BY 4.0
"""
from __future__ import annotations

import io
import math
import re
import sys
from pathlib import Path
from typing import NamedTuple

import fitz  # PyMuPDF
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

# ════════════════════════════════════════════
# パス
# ════════════════════════════════════════════
ROOT = Path(__file__).resolve().parent.parent
FONT_PATH = ROOT / "assets" / "fonts" / "Secvier.otf"
NOTO_DIR = ROOT / "src" / "noto_cards"
NOTO_CACHE = ROOT / "src" / "noto_cache"
NOTO_SVG = ROOT / "src" / "noto_svg"
DIST = ROOT / "dist" / "cards"


def get_noto_path(name: str) -> Path:
    for d in (NOTO_SVG, NOTO_CACHE, NOTO_DIR):
        p = d / name
        if p.exists() and p.stat().st_size > 200:
            return p
    return NOTO_DIR / name


# ════════════════════════════════════════════
# 出力サイズ / 4:5 マスタ
# ════════════════════════════════════════════
# Misskey 最終サイズ = 4:5 カードそのもの
MK_W, MK_H = 256, 320
# Discord 正方形キャンバス
DC = 256
# Discord 内のカード領域（高さいっぱい・幅は 4:5、左右に約25px透過）
DC_CARD_H = DC                      # 256（上下いっぱい）
DC_CARD_W = round(DC * 4 / 5)       # 205（4:5）
DC_MARGIN_X = (DC - DC_CARD_W) // 2  # ≈25（左右透過）

# マスタ（スーパーサンプリング）
SS = 3
MW, MH = MK_W * SS, MK_H * SS        # 768 × 960

# ── マスタ座標系は「256×320 ベース値 × SS」で表現する ──
def u(v: float) -> int:
    """ベース(256×320)座標 → マスタ座標。"""
    return int(round(v * SS))


# カード矩形（ベース 256×320, 中心 = (128,160)）
CX0, CY0, CX1, CY1 = 15, 12, 241, 308
CARD_CX = (CX0 + CX1) / 2            # 128
CARD_CY = (CY0 + CY1) / 2            # 160
CARD_R = 16

# ════════════════════════════════════════════
# バリアント定義
# ════════════════════════════════════════════
class V(NamedTuple):
    key: str; label: str
    bg: tuple; text: tuple; border: tuple
    accent: tuple; sfill: tuple; sline: tuple


VARIANTS: dict[str, V] = {
    v.key: v for v in [
        V("seiyuu", "星幽",
          (10, 10, 26, 255), (238, 226, 185, 255), (90, 108, 195, 255),
          (175, 148, 255, 255), (22, 22, 58, 255), (120, 100, 230, 255)),
        V("suigyoku", "翠玉",
          (4, 18, 10, 255), (210, 248, 218, 255), (38, 140, 76, 255),
          (100, 210, 140, 255), (8, 36, 18, 255), (56, 168, 104, 255)),
        V("kougyoku", "紅玉",
          (14, 2, 6, 255), (255, 228, 208, 255), (185, 20, 48, 255),
          (240, 80, 105, 255), (30, 4, 12, 255), (210, 32, 65, 255)),
        V("hakuji", "白磁",
          (248, 244, 236, 255), (22, 18, 14, 255), (150, 128, 88, 255),
          (110, 88, 52, 255), (232, 224, 208, 255), (140, 118, 78, 255)),
        V("sakin", "砂金",
          (245, 232, 190, 255), (44, 26, 6, 255), (188, 142, 30, 255),
          (218, 168, 42, 255), (235, 215, 168, 255), (178, 132, 22, 255)),
    ]
}

SUIT_VARIANT = {'S': 'seiyuu', 'H': 'kougyoku', 'D': 'sakin', 'C': 'suigyoku'}
CARD_BG = (255, 253, 248, 255)       # クリーム白カード面

# ════════════════════════════════════════════
# フォント
# ════════════════════════════════════════════
def lf(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)


# ════════════════════════════════════════════
# スートマーク（ポリゴン描画）
# ════════════════════════════════════════════
SUIT_PATHS: dict[str, str] = {
    'S': "M36,0 L27,9 L9,27 L0,45 L18,63 L27,63 L36,54 L45,63 L54,63 L72,45 L63,27 L45,9 Z M27,72 L45,72 L36,54 Z",
    'H': "M36,72 L27,54 L9,36 L0,27 L0,9 L18,0 L27,0 L36,9 L45,0 L54,0 L72,9 L72,27 L63,36 L45,54 Z",
    'D': "M36,0 L27,18 L18,27 L0,36 L18,45 L27,54 L36,72 L45,54 L54,45 L72,36 L54,27 L45,18 Z",
    'C': "M18,27 L18,9 L27,0 L45,0 L54,9 L54,27 L36,45 Z M27,63 L9,63 L0,54 L0,36 L9,27 L18,27 L36,54 Z M45,63 L63,63 L72,54 L72,36 L63,27 L54,27 L36,54 Z M27,72 L45,72 L36,54 Z",
}


def _parse_path_polys(d: str) -> list[list[tuple[float, float]]]:
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
                polys.append(current[:]); current = []
            i += 1
        else:
            if i + 1 < len(tokens) and re.match(r'^[-+]?[0-9]*\.?[0-9]+$', tokens[i + 1]):
                current.append((float(t), float(tokens[i + 1]))); i += 2
            else:
                i += 1
    if current:
        polys.append(current)
    return polys


def render_suit(suit: str, size: int, color: tuple) -> Image.Image:
    """スートマークを size×size の RGBA で描画。"""
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
# Noto コート図柄の抽出・着色
# ════════════════════════════════════════════
RANK_NAME = {'J': 'JACK', 'C': 'KNIGHT', 'Q': 'QUEEN', 'K': 'KING'}
SUIT_NAME = {'S': 'SPADES', 'H': 'HEARTS', 'D': 'DIAMONDS', 'C': 'CLUBS'}
JOKER_FILE = {'black': 'PLAYING CARD BLACK JOKER', 'red': 'PLAYING CARD RED JOKER'}


# コート図柄の固定クロップ枠（Noto canvas に対する比率）。
# 全コートカードを同一寸法・同一位置に揃えるためタイトクロップではなく固定枠を使う。
COURT_CROP = (0.05, 0.045, 0.95, 0.955)  # (x0, y0, x1, y1) 比率


def render_noto_clean(svg_name: str, color: tuple, *, strip_index: bool,
                      target_h: int, tight_crop: bool = True) -> Image.Image | None:
    """
    Noto コートカード SVG を高解像度でレンダリングし:
      1. 外縁カード枠を透過化
      2. (strip_index) Noto 内包の隅インデックスを透過化
      3. 残ピクセルを color に着色
      4. tight_crop=True なら alpha bbox でタイトクロップ、
         False なら COURT_CROP の固定枠でクロップ（寸法を揃える）
    高さ target_h(px) 基準でレンダリングして返す。
    """
    svg_path = get_noto_path(svg_name)
    if not svg_path.exists() or svg_path.stat().st_size < 200:
        return None
    try:
        doc = fitz.open(stream=svg_path.read_bytes(), filetype="svg")
        page = doc[0]
        # target_h を基準にレンダリング解像度を決定
        sy = target_h / page.rect.height
        sx = sy
        pix = page.get_pixmap(matrix=fitz.Matrix(sx, sy), alpha=True)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGBA")
        arr = np.array(img, dtype=np.uint8)
        h, w = arr.shape[:2]

        # ① 外縁カード枠を透過（上下左右 5%）
        bx, by = int(w * 0.05), int(h * 0.05)
        arr[:by, :, 3] = 0
        arr[h - by:, :, 3] = 0
        arr[:, :bx, 3] = 0
        arr[:, w - bx:, 3] = 0

        # ② Noto 内包の隅インデックス（ランク文字＋スート記号）を透過。
        #    記号は文字の下にあり縦に長いため、文字+記号を完全に覆う範囲を消す。
        #    （各ランクの図柄はスート間で共通で、スートは記号でのみ区別されるため、
        #     記号を除去し Secvier 側インデックスで正しいスートを表現する）
        if strip_index:
            ix, iy = int(w * 0.24), int(h * 0.25)
            arr[:iy, :ix, 3] = 0
            arr[h - iy:, w - ix:, 3] = 0

        # ③ 着色
        r, g, b = color[:3]
        mask = arr[:, :, 3] > 12
        if not mask.any():
            return None
        arr[mask, 0] = r; arr[mask, 1] = g; arr[mask, 2] = b

        # ④ クロップ
        if tight_crop:
            ys, xs = np.where(mask)
            y0, y1 = ys.min(), ys.max()
            x0, x1 = xs.min(), xs.max()
        else:
            fx0, fy0, fx1, fy1 = COURT_CROP
            x0, y0 = int(w * fx0), int(h * fy0)
            x1, y1 = int(w * fx1), int(h * fy1)
        cropped = Image.fromarray(arr[y0:y1 + 1, x0:x1 + 1], "RGBA")
        return cropped
    except Exception as e:
        print(f"  noto error {svg_name}: {e}", file=sys.stderr)
        return None


# ════════════════════════════════════════════
# コート図柄のスート記号修正（誤ったダイヤ図柄 → 正しいスートへ）
# ────────────────────────────────────────────
# 一部のソースSVG（♣J・♠C・♥C・♠Q・♥Q）は中身がダイヤ図柄になっている
# （♥C はさらに頭部が破損している）。各ランクの肖像はスート間で共通で、
# スートは図柄内の「ダイヤ記号」でのみ異なるため、クリーンなダイヤ図柄
# (OF DIAMONDS)を土台にし、図柄内の充填された菱形(ダイヤ)だけを検出して
# 目的スート記号へスタンプし直す。（単一ソースを土台にするため肖像は乱れない）
# ════════════════════════════════════════════
# (rank_letter, suit_letter): ソースが誤っており修正が必要なコートカード
WRONG_COURT: set[tuple[str, str]] = {
    ('J', 'C'),  # ♣ジャック
    ('C', 'S'),  # ♠ナイト
    ('C', 'H'),  # ♥ナイト（ソースが頭部破損＋ダイヤ胴体）
    ('Q', 'S'),  # ♠クィーン
    ('Q', 'H'),  # ♥クィーン
}


def _suit_bitmap(suit: str, size: int, flip: bool) -> np.ndarray:
    """スートマークのブールビットマップ（AA付き高解像 → 縮小）。"""
    ss = 4
    big = render_suit(suit, size * ss, (0, 0, 0, 255))
    big = big.resize((size, size), Image.LANCZOS)
    arr = np.array(big)[:, :, 3] > 110
    if flip:
        arr = arr[::-1, ::-1]
    return arr


def _stamp(canvas: np.ndarray, bm: np.ndarray, cx: float, cy: float):
    H, W = canvas.shape
    bh, bw = bm.shape
    x = int(round(cx - bw / 2)); y = int(round(cy - bh / 2))
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + bw), min(H, y + bh)
    if x1 <= x0 or y1 <= y0:
        return
    canvas[y0:y1, x0:x1] |= bm[y0 - y:y1 - y, x0 - x:x1 - x]


def render_court_fixed(rank_name: str, suit: str, color: tuple,
                       target_h: int) -> Image.Image | None:
    """OF DIAMONDS 図柄を土台に、胴部のダイヤ記号のみを suit へ置換して着色。"""
    try:
        path = get_noto_path(f"PLAYING CARD {rank_name} OF DIAMONDS.svg")
        if not path.exists() or path.stat().st_size < 200:
            return None
        doc = fitz.open(stream=path.read_bytes(), filetype="svg")
        page = doc[0]
        s = target_h / page.rect.height
        pix = page.get_pixmap(matrix=fitz.Matrix(s, s), alpha=True)
        base = np.array(Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGBA"))[:, :, 3] > 60
        base = base.copy()
        h, w = base.shape

        # 充填された菱形（ダイヤ）を侵食で抽出（細線は消え、塗り面のみ残る）
        it = max(2, round(h * 0.005))
        er = ndimage.binary_erosion(base, iterations=it)
        lab, n = ndimage.label(er)
        out = base.copy()
        for i in range(1, n + 1):
            ys, xs = np.where(lab == i)
            x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
            bw, bh = x1 - x0 + 1, y1 - y0 + 1
            fill = len(xs) / (bw * bh)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            # ダイヤ判定: 小〜中サイズ・塗り率約0.5・概ね正方アスペクト
            if not (0.025 * w < bw < 0.16 * w and 0.025 * h < bh < 0.13 * h
                    and 0.40 < fill < 0.72 and 0.55 < bw / bh < 1.7):
                continue
            # 隅インデックス領域はスキップ（Secvier 側で描画）
            if (cx < 0.30 * w and cy < 0.28 * h) or (cx > 0.70 * w and cy > 0.72 * h):
                continue
            # 元のダイヤを消去（侵食コアを膨張して塗り面ごと除去）
            core = ndimage.binary_dilation(lab == i, iterations=it + 2)
            out &= ~core
            flip = cy > h / 2
            sz = max(4, int(max(bw, bh) * 1.0))
            _stamp(out, _suit_bitmap(suit, sz, flip), cx, cy)

        # 隅インデックスを除去（Secvier に置換）
        iy, ix = int(h * 0.25), int(w * 0.24)
        out[:iy, :ix] = False
        out[h - iy:, w - ix:] = False

        if not out.any():
            return None
        arr = np.zeros((h, w, 4), np.uint8)
        r, g, b = color[:3]
        arr[out, 0] = r; arr[out, 1] = g; arr[out, 2] = b
        arr[out, 3] = 255
        # 直接ソース版と同一の固定枠でクロップ（全コートカードで寸法を統一）
        fx0, fy0, fx1, fy1 = COURT_CROP
        x0, y0 = int(w * fx0), int(h * fy0)
        x1, y1 = int(w * fx1), int(h * fy1)
        return Image.fromarray(arr[y0:y1 + 1, x0:x1 + 1], "RGBA")
    except Exception as e:
        print(f"  court fix error {rank_name} {suit}: {e}", file=sys.stderr)
        return None


# ════════════════════════════════════════════
# カードベース（bg + 外枠 + クリーム面）
# ════════════════════════════════════════════
def poly(cx: float, cy: float, r: float, n: int, rot: float = 0):
    pts = []
    for i in range(n):
        a = math.radians(rot + i * 360 / n) - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_outer_frame(draw: ImageDraw.ImageDraw, v: V):
    """マスタ全面の外縁デコ（4辺 + 四隅）。"""
    m = u(6)
    W, H = MW, MH
    if v.key == "seiyuu":
        draw.rounded_rectangle([m, m, W - m - 1, H - m - 1], radius=u(10),
                               outline=v.border, width=u(2))
        for cx, cy in [(m + u(3), m + u(3)), (W - m - u(3), m + u(3)),
                       (m + u(3), H - m - u(3)), (W - m - u(3), H - m - u(3))]:
            draw.polygon(poly(cx, cy, u(5), 4, 45), fill=v.accent)
    elif v.key == "suigyoku":
        draw.rounded_rectangle([m, m, W - m - 1, H - m - 1], radius=u(8),
                               outline=v.border, width=u(2))
        for (cx, cy), rot in [((m + u(3), m + u(3)), 0), ((W - m - u(3), m + u(3)), 0),
                              ((m + u(3), H - m - u(3)), 180), ((W - m - u(3), H - m - u(3)), 180)]:
            draw.polygon(poly(cx, cy, u(6), 3, rot), fill=v.accent)
    elif v.key == "kougyoku":
        draw.rounded_rectangle([m, m, W - m - 1, H - m - 1], radius=u(12),
                               outline=v.border, width=u(2))
        cr = u(5)
        for cx, cy in [(m + u(4), m + u(4)), (W - m - u(4), m + u(4)),
                       (m + u(4), H - m - u(4)), (W - m - u(4), H - m - u(4))]:
            draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=v.accent)
    elif v.key == "hakuji":
        draw.rectangle([u(4), u(4), W - u(5), H - u(5)], outline=v.border, width=u(1))
        draw.rectangle([u(8), u(8), W - u(9), H - u(9)], outline=v.border, width=u(1))
    else:  # sakin
        draw.rectangle([m, m, W - m - 1, H - m - 1], outline=v.border, width=u(2))
        arm = u(8)
        for cx, cy in [(m + u(1), m + u(1)), (W - m - u(2), m + u(1)),
                       (m + u(1), H - m - u(2)), (W - m - u(2), H - m - u(2))]:
            draw.line([(cx, cy), (cx + arm, cy + arm)], fill=v.accent, width=u(2))
            draw.line([(cx + arm, cy), (cx, cy + arm)], fill=v.accent, width=u(2))


def make_card_base(v: V) -> Image.Image:
    img = Image.new("RGBA", (MW, MH), v.bg)
    draw = ImageDraw.Draw(img)
    draw_outer_frame(draw, v)
    draw.rounded_rectangle([u(CX0), u(CY0), u(CX1), u(CY1)], radius=u(CARD_R),
                           fill=CARD_BG, outline=v.border, width=u(2))
    return img


# ════════════════════════════════════════════
# コーナーインデックス（番号 + スート） — 四隅基準で一定
# ════════════════════════════════════════════
# ベース(256×320)でのコーナーセル定義
LBL_INSET = 7          # カード枠からの内側余白
LBL_W = 42             # セル幅
LBL_RANK_FS = 34       # ランク文字サイズ（1文字）
LBL_RANK_FS2 = 25      # ランク文字サイズ（"10"）
LBL_PIP = 22           # スートマークサイズ
LBL_GAP = 2            # 文字とスートの間


def make_corner(rank: str, suit: str, v: V) -> Image.Image:
    """マスタ解像度のコーナーインデックス画像（番号 + スート）を返す。"""
    cell_w = u(LBL_W)
    rank_fs = u(LBL_RANK_FS if len(rank) == 1 else LBL_RANK_FS2)
    pip = u(LBL_PIP)
    gap = u(LBL_GAP)
    # 高さ = ランク文字 + gap + pip（おおよそ）
    cell_h = rank_fs + gap + pip + u(4)
    ci = Image.new("RGBA", (cell_w, cell_h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(ci)
    cd.text((cell_w // 2, 0), rank, font=lf(rank_fs),
            fill=v.border[:3] + (255,), anchor="mt")
    pip_img = render_suit(suit, pip, v.sline[:3] + (255,))
    ci.alpha_composite(pip_img, ((cell_w - pip) // 2, rank_fs + gap))
    return ci


def paste_corners(img: Image.Image, rank: str, suit: str, v: V,
                  *, patch: bool = False):
    """左上 + 右下(180°) にコーナーインデックスを配置（四隅基準・一定）。"""
    ci = make_corner(rank, suit, v)
    inset = u(LBL_INSET)
    tlx, tly = u(CX0) + inset, u(CY0) + inset
    brx, bry = u(CX1) - inset - ci.width, u(CY1) - inset - ci.height
    if patch:
        # 図柄背後にクリームの小パッチを敷いて視認性を確保
        _patch_behind(img, tlx, tly, ci.width, ci.height, v)
        _patch_behind(img, brx, bry, ci.width, ci.height, v)
    img.alpha_composite(ci, (tlx, tly))
    img.alpha_composite(ci.rotate(180), (brx, bry))


def _patch_behind(img: Image.Image, x: int, y: int, w: int, h: int, v: V):
    pad = u(3)
    patch = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    pd = ImageDraw.Draw(patch)
    pd.rounded_rectangle([0, 0, w + 2 * pad - 1, h + 2 * pad - 1],
                         radius=u(5), fill=CARD_BG)
    img.alpha_composite(patch, (x - pad, y - pad))


# ════════════════════════════════════════════
# 数字カードのピップ配置（中心対称 → 自動的に中央）
# ════════════════════════════════════════════
# ベース座標（中心 128,160 に対称）
_PL, _PM, _PR = 86, 128, 170
_PT, _PB = 74, 246
_PM_Y = (_PT + _PB) // 2  # 160
_P_UPPER = _PT + (_PM_Y - _PT) // 2   # 117
_P_LOWER = _PM_Y + (_PB - _PM_Y) // 2  # 203
# 9/10 用 4 行（中心対称）
_R4 = [74, 132, 188, 246]

PIP_POSITIONS: dict[str, list[tuple[int, int]]] = {
    '2': [(_PM, _PT), (_PM, _PB)],
    '3': [(_PM, _PT), (_PM, _PM_Y), (_PM, _PB)],
    '4': [(_PL, _PT), (_PR, _PT), (_PL, _PB), (_PR, _PB)],
    '5': [(_PL, _PT), (_PR, _PT), (_PM, _PM_Y), (_PL, _PB), (_PR, _PB)],
    '6': [(_PL, _PT), (_PR, _PT), (_PL, _PM_Y), (_PR, _PM_Y), (_PL, _PB), (_PR, _PB)],
    '7': [(_PL, _PT), (_PR, _PT), (_PM, _P_UPPER), (_PL, _PM_Y), (_PR, _PM_Y),
          (_PL, _PB), (_PR, _PB)],
    '8': [(_PL, _PT), (_PR, _PT), (_PM, _P_UPPER), (_PL, _PM_Y), (_PR, _PM_Y),
          (_PM, _P_LOWER), (_PL, _PB), (_PR, _PB)],
    '9': [(_PL, _R4[0]), (_PR, _R4[0]), (_PL, _R4[1]), (_PR, _R4[1]),
          (_PM, _PM_Y),
          (_PL, _R4[2]), (_PR, _R4[2]), (_PL, _R4[3]), (_PR, _R4[3])],
    '10': [(_PL, _R4[0]), (_PR, _R4[0]), (_PM, 103), (_PL, _R4[1]), (_PR, _R4[1]),
           (_PL, _R4[2]), (_PR, _R4[2]), (_PM, 217), (_PL, _R4[3]), (_PR, _R4[3])],
}

PIP_SIZE = 30   # 数字カードのスートサイズ（ベース）
ACE_SIZE = 104  # エース中央スートサイズ（ベース）


def draw_pips(img: Image.Image, rank: str, suit: str, v: V):
    pip_col = v.sline[:3] + (255,)
    if rank == 'A':
        sz = u(ACE_SIZE)
        pip = render_suit(suit, sz, pip_col)
        img.alpha_composite(pip, (u(CARD_CX) - sz // 2, u(CARD_CY) - sz // 2))
    else:
        sz = u(PIP_SIZE)
        pip = render_suit(suit, sz, pip_col)
        for px, py in PIP_POSITIONS.get(rank, []):
            img.alpha_composite(pip, (u(px) - sz // 2, u(py) - sz // 2))


# ════════════════════════════════════════════
# コートカード（J/C/Q/K）
# ════════════════════════════════════════════
# 図柄フィット領域（カード内側、コーナー余白あり）
FACE_PAD_X = 14
FACE_PAD_Y = 16


def draw_face_card(img: Image.Image, rank: str, suit: str, v: V):
    avail_w = u(CX1 - CX0 - 2 * FACE_PAD_X)
    avail_h = u(CY1 - CY0 - 2 * FACE_PAD_Y)
    # 全コートカード共通: クリーンなダイヤ図柄を土台に、図柄内の記号を
    # Secvier のマークグリフへ置換して描画（ランクごとに統一された肖像 +
    # 正しいスートの Secvier マーク。全16枚で図柄・サイズ・記号様式が揃う）
    fig = render_court_fixed(RANK_NAME[rank], suit, v.sline, avail_h)
    if fig is None:
        # フォールバック: 大きなランク文字
        d = ImageDraw.Draw(img)
        d.text((u(CARD_CX), u(CARD_CY)), rank, font=lf(u(96)),
               fill=v.sline[:3] + (255,), anchor="mm")
    else:
        # avail_w / avail_h に収まるよう縮小（縦横比保持）
        fw, fh = fig.size
        scale = min(avail_w / fw, avail_h / fh)
        nw, nh = max(1, int(fw * scale)), max(1, int(fh * scale))
        fig = fig.resize((nw, nh), Image.LANCZOS)
        # カード中央に配置
        ox = u(CARD_CX) - nw // 2
        oy = u(CARD_CY) - nh // 2
        img.alpha_composite(fig, (ox, oy))
    # コーナーインデックス（背後にクリームパッチ）
    paste_corners(img, rank, suit, v, patch=True)


# ════════════════════════════════════════════
# ジョーカー
# ════════════════════════════════════════════
def make_joker(color: str) -> Image.Image:
    v = VARIANTS['seiyuu' if color == 'black' else 'kougyoku']
    img = make_card_base(v)
    avail_w = u(CX1 - CX0 - 2 * FACE_PAD_X)
    avail_h = u(CY1 - CY0 - 2 * FACE_PAD_Y)
    fig = render_noto_clean(f"{JOKER_FILE[color]}.svg", v.sline,
                            strip_index=False, target_h=avail_h)
    if fig is not None:
        fw, fh = fig.size
        scale = min(avail_w / fw, avail_h / fh)
        nw, nh = max(1, int(fw * scale)), max(1, int(fh * scale))
        fig = fig.resize((nw, nh), Image.LANCZOS)
        img.alpha_composite(fig, (u(CARD_CX) - nw // 2, u(CARD_CY) - nh // 2))
    # 縦書き "JOKER"（90°回転, 頭文字Jが上端/下端）
    _paste_joker_label(img, v)
    return img


def _paste_joker_label(img: Image.Image, v: V):
    """JOKER を縦方向(90°回転)で左上(J上端)・右下(J下端)に配置。"""
    fs = u(17)
    pip_col = v.sline[:3] + (255,)
    # 横書き "JOKER" を生成
    font = lf(fs)
    tmp = Image.new("RGBA", (u(LBL_W) * 4, fs + u(6)), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.text((2, 0), "JOKER", font=font, fill=pip_col, anchor="lt")
    bbox = tmp.getbbox()
    label = tmp.crop(bbox)
    # 90°時計回り回転 → 頭文字Jが上端、下へ読む
    label_tl = label.rotate(-90, expand=True)
    inset = u(LBL_INSET)
    # 左上: J が上端に来るよう、左上隅へ
    tlx, tly = u(CX0) + inset, u(CY0) + inset
    _patch_strip(img, tlx, tly, label_tl.width, label_tl.height, v)
    img.alpha_composite(label_tl, (tlx, tly))
    # 右下: 180°回転 → J が下端
    label_br = label_tl.rotate(180, expand=True)
    brx = u(CX1) - inset - label_br.width
    bry = u(CY1) - inset - label_br.height
    _patch_strip(img, brx, bry, label_br.width, label_br.height, v)
    img.alpha_composite(label_br, (brx, bry))


def _patch_strip(img: Image.Image, x: int, y: int, w: int, h: int, v: V):
    pad = u(2)
    patch = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    pd = ImageDraw.Draw(patch)
    pd.rounded_rectangle([0, 0, w + 2 * pad - 1, h + 2 * pad - 1],
                         radius=u(4), fill=CARD_BG)
    img.alpha_composite(patch, (x - pad, y - pad))


# ════════════════════════════════════════════
# スート単体絵文字
# ════════════════════════════════════════════
# ♥単体カードは♦と同様に明色背景（赤マーク）にする
HEART_LIGHT = V("kougyoku", "紅玉",
                (248, 238, 236, 255), (44, 14, 18, 255), (185, 20, 48, 255),
                (240, 80, 105, 255), (235, 210, 210, 255), (200, 28, 60, 255))


def make_suit_emoji(suit: str) -> Image.Image:
    v = HEART_LIGHT if suit == 'H' else VARIANTS[SUIT_VARIANT[suit]]
    img = Image.new("RGBA", (MW, MH), v.bg)
    draw = ImageDraw.Draw(img)
    draw_outer_frame(draw, v)
    sz = u(150)
    mark = render_suit(suit, sz, v.sline[:3] + (255,))
    img.alpha_composite(mark, (u(128) - sz // 2, u(160) - sz // 2))
    return img


# ════════════════════════════════════════════
# マスタ → プラットフォーム出力
# ════════════════════════════════════════════
def export_platforms(master: Image.Image, stem: str):
    """master(4:5, MW×MH) を Discord / Misskey 出力へ。"""
    # Misskey: 256×320 にそのまま縮小
    mk = master.resize((MK_W, MK_H), Image.LANCZOS)
    (DIST / "misskey").mkdir(parents=True, exist_ok=True)
    mk.save(DIST / "misskey" / f"{stem}.png")

    # Discord: 256×256 正方形, カードを 205×256 で中央(左右約25px透過)
    card = master.resize((DC_CARD_W, DC_CARD_H), Image.LANCZOS)
    canvas = Image.new("RGBA", (DC, DC), (0, 0, 0, 0))
    canvas.alpha_composite(card, (DC_MARGIN_X, 0))
    (DIST / "discord").mkdir(parents=True, exist_ok=True)
    canvas.save(DIST / "discord" / f"{stem}.png")


# ════════════════════════════════════════════
# メイン
# ════════════════════════════════════════════
RANKS_NUM = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10']
RANKS_FACE = ['J', 'C', 'Q', 'K']
SUITS = ['S', 'H', 'D', 'C']


def main():
    DIST.mkdir(parents=True, exist_ok=True)
    total = 0

    for suit in SUITS:
        v = VARIANTS[SUIT_VARIANT[suit]]
        for rank in RANKS_NUM:
            img = make_card_base(v)
            draw_pips(img, rank, suit, v)
            paste_corners(img, rank, suit, v)
            export_platforms(img, f"card_{suit}_{rank}")
            total += 1
    print(f"  数字カード: {len(SUITS) * len(RANKS_NUM)} 枚")

    for suit in SUITS:
        v = VARIANTS[SUIT_VARIANT[suit]]
        for rank in RANKS_FACE:
            img = make_card_base(v)
            draw_face_card(img, rank, suit, v)
            export_platforms(img, f"card_{suit}_{rank}")
            total += 1
    print(f"  コートカード: {len(SUITS) * len(RANKS_FACE)} 枚")

    for color in ['black', 'red']:
        img = make_joker(color)
        export_platforms(img, f"card_joker_{color}")
        total += 1
    print(f"  ジョーカー: 2 枚")

    for suit in SUITS:
        img = make_suit_emoji(suit)
        export_platforms(img, f"card_suit_{suit}")
        total += 1
    print(f"  スート絵文字: {len(SUITS)} 枚")

    print(f"\n[OK] 合計 {total} 種 × 2プラットフォーム → {DIST}/discord, {DIST}/misskey")


if __name__ == "__main__":
    main()

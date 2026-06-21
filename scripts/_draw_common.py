"""
描画共通関数（フレーム・ベースキャンバス）
"""
from __future__ import annotations
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from _variants import Variant

ROOT = Path(__file__).parent.parent
FONT_PATH = ROOT / "assets" / "fonts" / "Secvier.otf"
SIZE = 128
C = SIZE // 2


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)


def polygon_pts(
    cx: float, cy: float, r: float, n: int, rotation_deg: float = 0,
) -> list[tuple[float, float]]:
    pts = []
    for i in range(n):
        a = math.radians(rotation_deg + i * 360 / n) - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ────────────────────────────────────────────
# フレーム描画（バリアント別）
# ────────────────────────────────────────────
def draw_frame(draw: ImageDraw.ImageDraw, v: Variant) -> None:
    m = 4

    if v.key == "seiyuu":
        # 角丸ボーダー + 四隅に小ダイヤ
        draw.rounded_rectangle(
            [m, m, SIZE - m - 1, SIZE - m - 1],
            radius=8, outline=v.border, width=2,
        )
        for cx, cy in [(m+2, m+2), (SIZE-m-3, m+2),
                       (m+2, SIZE-m-3), (SIZE-m-3, SIZE-m-3)]:
            pts = polygon_pts(cx, cy, 4, 4, rotation_deg=45)
            draw.polygon(pts, fill=v.accent)

    elif v.key == "suigyoku":
        # 角丸ボーダー + 四隅に宝石カット（逆三角）
        draw.rounded_rectangle(
            [m, m, SIZE - m - 1, SIZE - m - 1],
            radius=6, outline=v.border, width=2,
        )
        gem_r = 5
        for (cx, cy), rot in [
            ((m+2, m+2), 0), ((SIZE-m-3, m+2), 0),
            ((m+2, SIZE-m-3), 180), ((SIZE-m-3, SIZE-m-3), 180),
        ]:
            pts = polygon_pts(cx, cy, gem_r, 3, rotation_deg=rot)
            draw.polygon(pts, fill=v.accent)

    elif v.key == "kougyoku":
        # 角丸ボーダー + 四隅に小円（ルビーカボション）
        draw.rounded_rectangle(
            [m, m, SIZE - m - 1, SIZE - m - 1],
            radius=10, outline=v.border, width=2,
        )
        cr = 4
        for cx, cy in [(m+3, m+3), (SIZE-m-4, m+3),
                       (m+3, SIZE-m-4), (SIZE-m-4, SIZE-m-4)]:
            draw.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=v.accent)

    elif v.key == "hakuji":
        # 二重細線 + 四隅に小正方形
        draw.rectangle([3, 3, SIZE-4, SIZE-4], outline=v.border, width=1)
        draw.rectangle([7, 7, SIZE-8, SIZE-8], outline=v.border, width=1)
        sq = 3
        for cx, cy in [(3, 3), (SIZE-4, 3), (3, SIZE-4), (SIZE-4, SIZE-4)]:
            draw.rectangle([cx-sq, cy-sq, cx+sq, cy+sq], fill=v.accent)

    else:  # sakin
        # 一重太線 + 四隅に対角スラッシュ（金の封印/装飾帯）
        draw.rectangle([m, m, SIZE-m-1, SIZE-m-1], outline=v.border, width=2)
        arm = 7
        for cx, cy in [(m+1, m+1), (SIZE-m-2, m+1),
                       (m+1, SIZE-m-2), (SIZE-m-2, SIZE-m-2)]:
            draw.line([(cx, cy), (cx+arm, cy+arm)], fill=v.accent, width=2)
            draw.line([(cx+arm, cy), (cx, cy+arm)], fill=v.accent, width=2)


def make_base(v: Variant) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (SIZE, SIZE), v.bg)
    draw = ImageDraw.Draw(img)
    draw_frame(draw, v)
    return img, draw

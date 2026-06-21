"""
Secvier ImageAssets — ダイス出目絵文字 & ダイス種絵文字 PNG 生成 (v3)

改善点 (v3):
  - D20: 12角形(十二角形) + 内部三角線 で丸みを帯びたアイコソ感
  - バリアント 5種対応 (seiyuu / suigyoku / kougyoku / hakuji / sakin)

出目  70面 × 5バリアント = 350 枚
種別   7種 × 5バリアント =  35 枚
合計                        385 枚
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _draw_common import C, SIZE, load_font, polygon_pts, make_base
from _variants import VARIANTS, Variant

DIST = Path(__file__).parent.parent / "dist"

# ────────────────────────────────────────────
# 形状サイズ
# ────────────────────────────────────────────
FACE_SHAPE_R = C - 24   # 出目用: 形状小さめ、文字が少しはみ出る
TYPE_SHAPE_R = C - 10   # 種別用: 形状を大きく


# ────────────────────────────────────────────
# ダイス形状頂点
# ────────────────────────────────────────────
def get_shape_pts(shape: str, r: float) -> list[tuple[float, float]]:
    if shape == "tri":      # D4
        return polygon_pts(C, C, r, 3)
    if shape == "sq":       # D6 (角丸は別途)
        return polygon_pts(C, C, r, 4, rotation_deg=45)
    if shape == "dia":      # D8: 縦長ダイヤ
        hh, hw = r, int(r * 0.70)
        return [(C, C-hh), (C+hw, C), (C, C+hh), (C-hw, C)]
    if shape == "kite":     # D10: 細長いカイト
        side_y = C - int(r * 0.44)
        side_x = int(r * 0.80)
        return [(C, C-r), (C+side_x, side_y), (C, C+r), (C-side_x, side_y)]
    if shape == "penta":    # D12: 正五角形
        return polygon_pts(C, C, r, 5)
    if shape == "d20":      # D20: 12角形（丸みを帯びたアイコソ）
        return polygon_pts(C, C, r, 12)
    return []


def draw_d6_bg(draw: ImageDraw.ImageDraw, r: float, v: Variant) -> None:
    """D6 の角丸正方形背景。"""
    pad = int(C - r * 0.707)
    draw.rounded_rectangle(
        [pad, pad, SIZE-pad-1, SIZE-pad-1],
        radius=6, fill=v.shape_fill, outline=v.shape_line, width=2,
    )


def draw_poly_bg(
    draw: ImageDraw.ImageDraw, shape: str, r: float, v: Variant,
) -> None:
    """多面体ダイスの形状背景。"""
    pts = get_shape_pts(shape, r)
    if not pts:
        return
    draw.polygon(pts, fill=v.shape_fill, outline=v.shape_line, width=2)

    # D20: 12角形の中に内接三角形 + 中点三角形を描いてアイコソ感を出す
    if shape == "d20":
        inner_r = r * 0.78
        tri = polygon_pts(C, C, inner_r, 3)
        # 内接三角形
        draw.polygon(tri, fill=None, outline=v.shape_line, width=1)
        # 中点三角形 (メジアル三角形)
        mid = [
            ((tri[i][0] + tri[(i+1)%3][0]) / 2,
             (tri[i][1] + tri[(i+1)%3][1]) / 2)
            for i in range(3)
        ]
        draw.polygon(mid, fill=None, outline=v.shape_line, width=1)


# ────────────────────────────────────────────
# D6 pip 配置
# ────────────────────────────────────────────
_L, _R = C - 23, C + 23
_T, _M, _B = C - 23, C, C + 23

PIP_POSITIONS: dict[int, list[tuple[int, int]]] = {
    1: [(_M, _M)],
    2: [(_L, _T), (_R, _B)],
    3: [(_R, _T), (_M, _M), (_L, _B)],
    4: [(_L, _T), (_R, _T), (_L, _B), (_R, _B)],
    5: [(_L, _T), (_R, _T), (_M, _M), (_L, _B), (_R, _B)],
    6: [(_L, _T), (_R, _T), (_L, _M), (_R, _M), (_L, _B), (_R, _B)],
}
PIP_R = 10


# ────────────────────────────────────────────
# フォントサイズ
# ────────────────────────────────────────────
def face_font_size(text: str) -> int:
    n = len(text)
    if n == 1: return 86
    if n == 2: return 66
    return 52


def type_label_size(text: str) -> int:
    n = len(text)
    if n <= 2: return 54
    return 42


# ────────────────────────────────────────────
# 出目レンダリング
# ────────────────────────────────────────────
def render_d6_face(face: int, v: Variant, out_dir: Path) -> None:
    img, draw = make_base(v)
    draw_d6_bg(draw, FACE_SHAPE_R, v)
    for px, py in PIP_POSITIONS[face]:
        draw.ellipse([px-PIP_R, py-PIP_R, px+PIP_R, py+PIP_R], fill=v.text)
    out_dir.mkdir(parents=True, exist_ok=True)
    img.save(out_dir / f"dice_d6_{face}.png", "PNG", optimize=True)


def render_poly_face(
    die_key: str, shape: str, face_str: str,
    v: Variant, out_dir: Path,
) -> None:
    img, draw = make_base(v)
    draw_poly_bg(draw, shape, FACE_SHAPE_R, v)

    font = load_font(face_font_size(face_str))
    # 三角形 (D4) は重心オフセット、D20(12角形)はオフセット不要
    offset_y = 10 if shape == "tri" else 0
    draw.text((C, C + offset_y), face_str, font=font, fill=v.text, anchor="mm")

    out_dir.mkdir(parents=True, exist_ok=True)
    img.save(out_dir / f"{die_key}_{face_str}.png", "PNG", optimize=True)


# ────────────────────────────────────────────
# 種別レンダリング
# ────────────────────────────────────────────
def render_type_d6(v: Variant, out_dir: Path) -> None:
    img, draw = make_base(v)
    draw_d6_bg(draw, TYPE_SHAPE_R, v)
    font = load_font(type_label_size("D6"))
    draw.text((C, C), "D6", font=font, fill=v.text, anchor="mm")
    out_dir.mkdir(parents=True, exist_ok=True)
    img.save(out_dir / "dice_type_d6.png", "PNG", optimize=True)


def render_type_poly(
    file_stem: str, shape: str, label: str,
    v: Variant, out_dir: Path,
) -> None:
    img, draw = make_base(v)
    draw_poly_bg(draw, shape, TYPE_SHAPE_R, v)
    font = load_font(type_label_size(label))
    offset_y = 12 if shape == "tri" else 0
    draw.text((C, C + offset_y), label, font=font, fill=v.text, anchor="mm")
    out_dir.mkdir(parents=True, exist_ok=True)
    img.save(out_dir / f"{file_stem}.png", "PNG", optimize=True)


# ────────────────────────────────────────────
# 全生成
# ────────────────────────────────────────────
def generate_for_variant(v: Variant) -> int:
    out = DIST / "dice" / v.key
    out.mkdir(parents=True, exist_ok=True)
    count = 0

    # 出目
    for f in range(1, 5):
        render_poly_face("dice_d4", "tri", str(f), v, out);  count += 1
    for f in range(1, 7):
        render_d6_face(f, v, out);  count += 1
    for f in range(1, 9):
        render_poly_face("dice_d8", "dia", str(f), v, out);  count += 1
    for f in range(0, 10):
        render_poly_face("dice_d10",  "kite", str(f), v, out);  count += 1
    for t in range(0, 10):
        render_poly_face("dice_d10p", "kite", f"{t*10:02d}", v, out);  count += 1
    for f in range(1, 13):
        render_poly_face("dice_d12", "penta", str(f), v, out);  count += 1
    for f in range(1, 21):
        render_poly_face("dice_d20", "d20",   str(f), v, out);  count += 1

    # 種別
    render_type_poly("dice_type_d4",   "tri",   "D4",  v, out)
    render_type_d6(v, out)
    render_type_poly("dice_type_d8",   "dia",   "D8",  v, out)
    render_type_poly("dice_type_d10",  "kite",  "D10", v, out)
    render_type_poly("dice_type_d10p", "kite",  "D00", v, out)
    render_type_poly("dice_type_d12",  "penta", "D12", v, out)
    render_type_poly("dice_type_d20",  "d20",   "D20", v, out)
    count += 7

    return count


def main() -> None:
    total = 0
    for v in VARIANTS:
        n = generate_for_variant(v)
        print(f"  {v.label} ({v.key}): {n} 枚")
        total += n
    print(f"\n✓ 合計 {total} 枚")


if __name__ == "__main__":
    main()

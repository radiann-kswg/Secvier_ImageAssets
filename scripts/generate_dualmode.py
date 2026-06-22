"""ライト/ダーク両モード対応 透過PNG（二重縁取り）バリアント生成.

`svg2png/` の「黒字・白背景」グリフPNGからアルファマスクを抽出し、
SDF(符号付き距離場)で外ハロー＋内キーライン＋宝石ボディの二重縁取りを付与する。
背景を持たない単体グリフでも、縁取りによりライト・ダーク両モードで視認可能。

出力:
    dist/alphanum_dualmode/{variant}/char_{X}_{size}.png   （A–Z / 0–9 × 6バリアント）
    dist/suits_dualmode/{suit}_{color}_{size}.png          （♠♥♦♣ × 指定2配色）

著作権者: RadianN_kswg / ラジアン（柏木主税） / ライセンス: CC BY 4.0
"""
from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "svg2png"
DIST = ROOT / "dist"
RES = 512                 # 作業解像度（マスク基準）
SIZES = (512, 128)        # 出力サイズ（高解像 / 標準絵文字）
W_HALO = 11               # 外ハロー幅（512px基準, px）
W_KEY = 7                 # 内キーライン幅（512px基準, px）
AA = 1.1                  # 境界アンチエイリアス幅


class Scheme(NamedTuple):
    """二重縁取りの配色定義（全て 0-255 の RGB）。"""

    label: str
    grad_top: tuple[int, int, int]
    grad_bottom: tuple[int, int, int]
    keyline: tuple[int, int, int]
    halo: tuple[int, int, int]


# ── alphanum 6バリアント（既存 dist/alphanum 配色に対応 + 黒磁） ──
ALPHANUM: dict[str, Scheme] = {
    "seiyuu":   Scheme("星幽", (178, 150, 255), (86, 104, 196), (10, 10, 32),  (238, 226, 185)),
    "suigyoku": Scheme("翠玉", (128, 224, 164), (38, 140, 76),  (4, 24, 12),   (214, 248, 220)),
    "kougyoku": Scheme("紅玉", (244, 94, 120),  (185, 20, 48),  (18, 2, 8),    (255, 228, 208)),
    "hakuji":   Scheme("白磁", (250, 247, 240), (232, 224, 206), (150, 128, 88), (54, 42, 26)),
    "sakin":    Scheme("砂金", (226, 178, 64),  (184, 138, 28), (44, 26, 6),   (245, 232, 190)),
    # 白磁の色反転（黒文字ボディ・金縁は踏襲）
    "kokuji":   Scheme("黒磁", (44, 40, 34),    (18, 15, 12),   (150, 128, 88), (240, 232, 212)),
}

# ── suits：スートごとの指定2配色のみ（♠青/黒 ♥赤/白 ♦黄/白 ♣緑/黒） ──
# 有彩色は dist/cards の4色デック配色に対応。
_MONO_BLACK = Scheme("黒", (44, 40, 34), (16, 14, 12), (8, 7, 6), (238, 236, 232))
_MONO_WHITE = Scheme("白", (250, 247, 240), (232, 226, 210), (150, 140, 120), (52, 44, 34))
SUITS: dict[str, dict[str, Scheme]] = {
    "spade": {
        "blue":  Scheme("青", (124, 110, 226), (72, 96, 192), (0, 0, 26), (236, 238, 250)),
        "black": _MONO_BLACK,
    },
    "heart": {
        "red":   Scheme("赤", (242, 74, 98), (168, 0, 48), (12, 0, 4), (255, 224, 224)),
        "white": _MONO_WHITE,
    },
    "diamond": {
        "yellow": Scheme("黄", (230, 182, 70), (168, 120, 24), (40, 26, 0), (250, 238, 200)),
        "white":  _MONO_WHITE,
    },
    "club": {
        "green": Scheme("緑", (96, 192, 120), (24, 120, 72), (4, 26, 14), (226, 246, 232)),
        "black": _MONO_BLACK,
    },
}


def load_mask(path: Path) -> np.ndarray:
    """黒字・白背景PNG → グリフ被覆率 [0,1]（アンチエイリアス保持）。"""
    im = Image.open(path).convert("L").resize((RES, RES), Image.LANCZOS)
    return 1.0 - np.asarray(im, dtype=np.float32) / 255.0


def signed_distance(mask: np.ndarray) -> np.ndarray:
    """符号付き距離場：グリフ外で正、内で負（px）。"""
    solid = mask >= 0.5
    return distance_transform_edt(~solid) - distance_transform_edt(solid)


def region_alpha(sdf: np.ndarray, t: float) -> np.ndarray:
    """{sdf <= t} 領域のアンチエイリアス被覆率 [0,1]。"""
    return np.clip((t - sdf) / AA + 0.5, 0.0, 1.0)


def vertical_gradient(top: tuple, bottom: tuple, mask: np.ndarray) -> np.ndarray:
    """グリフのbbox範囲で上→下の縦グラデRGBを生成（H,W,3）。"""
    ys = np.where(mask.max(axis=1) > 0.05)[0]
    y0, y1 = (int(ys.min()), int(ys.max())) if len(ys) else (0, RES - 1)
    t = np.clip((np.arange(RES) - y0) / max(1, (y1 - y0)), 0.0, 1.0)
    rgb = np.array(top)[None, :] * (1 - t)[:, None] + np.array(bottom)[None, :] * t[:, None]
    return np.repeat(rgb[:, None, :], RES, axis=1)


def _over(dst: np.ndarray, color: np.ndarray, alpha: np.ndarray) -> None:
    """dst(RGBA float, RGBは0-255 / Aは0-1) に color を alpha 合成（in-place）。"""
    a = alpha[..., None]
    dst[..., :3] = color * a + dst[..., :3] * (1 - a)
    dst[..., 3:4] = a + dst[..., 3:4] * (1 - a)


def render(mask: np.ndarray, s: Scheme) -> Image.Image:
    """二重縁取りグリフを透過RGBAで描画する。"""
    sdf = signed_distance(mask)
    canvas = np.zeros((RES, RES, 4), dtype=np.float32)
    body = vertical_gradient(s.grad_top, s.grad_bottom, mask)
    _over(canvas, np.array(s.halo, dtype=np.float32), region_alpha(sdf, W_HALO))     # 外ハロー
    _over(canvas, np.array(s.keyline, dtype=np.float32), region_alpha(sdf, 0.0))     # 内キーライン
    _over(canvas, body, region_alpha(sdf, -W_KEY))                                   # 宝石ボディ
    out = np.empty_like(canvas)
    out[..., :3] = canvas[..., :3]          # RGB は既に 0-255
    out[..., 3] = canvas[..., 3] * 255.0    # alpha のみ 0-1 -> 0-255
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def _save_all_sizes(img: Image.Image, out_dir: Path, stem: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for sz in SIZES:
        scaled = img.resize((sz, sz), Image.LANCZOS) if sz != RES else img
        scaled.save(out_dir / f"{stem}_{sz}.png")


def build_alphanum() -> int:
    count = 0
    sources = sorted((SRC / "alphanum").glob("char_*.png"))
    for variant, scheme in ALPHANUM.items():
        out_dir = DIST / "alphanum_dualmode" / variant
        for src in sources:
            img = render(load_mask(src), scheme)
            _save_all_sizes(img, out_dir, src.stem)
            count += 1
    return count


def build_suits() -> int:
    count = 0
    out_dir = DIST / "suits_dualmode"
    for suit, colorways in SUITS.items():
        src = SRC / "suits" / f"{suit}.png"
        mask = load_mask(src)
        for color, scheme in colorways.items():
            img = render(mask, scheme)
            _save_all_sizes(img, out_dir, f"{suit}_{color}")
            count += 1
    return count


def main() -> None:
    a = build_alphanum()
    s = build_suits()
    print(f"alphanum: {a} glyph-variants, suits: {s} colorways  (× {len(SIZES)} sizes)")
    print(f"-> {DIST / 'alphanum_dualmode'}")
    print(f"-> {DIST / 'suits_dualmode'}")


if __name__ == "__main__":
    main()

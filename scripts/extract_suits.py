"""Secvierフォント収録のスートグリフをアウトライン化SVGとして抽出する。

Secvier v0.1-beta が収録するトランプスート（♠ U+2660 / ♥ U+2665 /
♦ U+2666 / ♣ U+2663）を、フォント依存なしの純粋な <path> SVGとして
src/suits/ に出力する。extract_glyphs.py の英数字版に相当し、グリフの
アウトライン化ロジックを共有する。

これらSVGは svg2png/suits/ の黒字マスクを経て
dist/suits_dualmode/（独立スートマーク絵文字）の土台になる。
※トランプ札面のスートpipは各カード生成スクリプト内蔵のSUIT_PATHSを使用する
  （札レイアウトに最適化された別表現）。本スクリプトは独立スートマーク専用。

出力:
    src/suits/spade.svg
    src/suits/heart.svg
    src/suits/diamond.svg
    src/suits/club.svg

使い方:
    python scripts/extract_suits.py
    python scripts/extract_suits.py --viewbox 512 --scale 0.78
"""
from __future__ import annotations

import sys
from pathlib import Path

import click
from fontTools import ttLib
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen

sys.path.insert(0, str(Path(__file__).parent))

ROOT     = Path(__file__).parent.parent
FONT_PATH = ROOT / "assets" / "fonts" / "Secvier.otf"
OUT_DIR  = ROOT / "src" / "suits"
VIEWBOX  = 512
# viewBox内のスート描画サイズ（px）。余白 = (512-SUIT_PX)/2。
# 英数字は em基準・ベースライン揃えだが、スートは記号のため実bbox基準で天地中央に配置する。
SUIT_PX  = 400

# スート名 → Unicodeコードポイント
SUITS: dict[str, int] = {
    "spade":   0x2660,
    "heart":   0x2665,
    "diamond": 0x2666,
    "club":    0x2663,
}


def suit_svg_centered(
    glyph_name: str,
    glyph_set: object,
    viewbox: int,
    suit_px: int,
    title: str,
) -> str | None:
    """スートグリフを実バウンディングボックス基準で天地・左右中央に配置したSVGを返す。

    英数字（ベースライン揃え）と異なり、記号は視覚的中心を揃えたいため、
    グリフのbboxをviewBox中央に等倍配置する。
    """
    pen = SVGPathPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    path_data = pen.getCommands()
    if not path_data.strip():
        return None

    bp = BoundsPen(glyph_set)
    glyph_set[glyph_name].draw(bp)
    if bp.bounds is None:
        return None
    x_min, y_min, x_max, y_max = bp.bounds
    gw = x_max - x_min
    gh = y_max - y_min
    scale = suit_px / max(gw, gh)  # 長辺を suit_px に合わせる

    # フォント座標(Y上)→SVG座標(Y下)。bbox中心を viewBox中心へ。
    cx_glyph = (x_min + x_max) / 2
    cy_glyph = (y_min + y_max) / 2
    tx = viewbox / 2 - scale * cx_glyph
    ty = viewbox / 2 + scale * cy_glyph  # Y反転ぶん符号を +

    transform = f"matrix({scale:.6f},0,0,{-scale:.6f},{tx:.3f},{ty:.3f})"

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg"\n'
        f'     viewBox="0 0 {viewbox} {viewbox}"\n'
        f'     width="{viewbox}" height="{viewbox}">\n'
        f'  <title>{title}</title>\n'
        f'  <g transform="{transform}">\n'
        f'    <path d="{path_data}" fill="#000000"/>\n'
        '  </g>\n'
        '</svg>\n'
    )


def extract_all(
    font_path: Path = FONT_PATH,
    out_dir: Path = OUT_DIR,
    viewbox: int = VIEWBOX,
    suit_px: int = SUIT_PX,
) -> list[Path]:
    """全4スートのアウトライン化SVG（天地中央）を out_dir に出力する。

    Args:
        font_path: Secvier OTFファイルのパス
        out_dir:   出力ディレクトリ
        viewbox:   SVG viewBoxサイズ（正方形）
        suit_px:   viewBox内のスート描画サイズ（長辺px）

    Returns:
        生成したSVGファイルのパスリスト
    """
    tt = ttLib.TTFont(str(font_path))
    glyph_set = tt.getGlyphSet()
    cmap      = tt.getBestCmap()

    out_dir.mkdir(parents=True, exist_ok=True)
    produced: list[Path] = []

    for suit, codepoint in SUITS.items():
        if codepoint not in cmap:
            print(f"  SKIP: {suit} (U+{codepoint:04X}) — cmapに未登録")
            continue

        glyph_name = cmap[codepoint]
        svg = suit_svg_centered(
            glyph_name, glyph_set, viewbox, suit_px,
            f"Secvier suit {suit}",
        )
        if svg is None:
            print(f"  SKIP: {suit} — パスデータなし（空グリフ）")
            continue

        out_path = out_dir / f"{suit}.svg"
        out_path.write_text(svg, encoding="utf-8")
        produced.append(out_path)
        print(f"  OK: {out_path.name}  (glyph={glyph_name!r})")

    return produced


@click.command()
@click.option(
    "--font", "font_path",
    default=str(FONT_PATH),
    show_default=True,
    help="Secvier OTFファイルのパス",
)
@click.option(
    "--out-dir",
    default=str(OUT_DIR),
    show_default=True,
    help="SVG出力ディレクトリ",
)
@click.option(
    "--viewbox",
    default=VIEWBOX,
    show_default=True,
    help="SVG viewBoxサイズ（px、正方形）",
)
@click.option(
    "--size",
    "suit_px",
    default=SUIT_PX,
    show_default=True,
    help="viewBox内のスート描画サイズ（長辺px）",
)
def main(font_path: str, out_dir: str, viewbox: int, suit_px: int) -> None:
    """Secvierフォント収録スートグリフの単体SVGを生成します（4枚, 天地中央）。"""
    fp = Path(font_path)
    od = Path(out_dir)
    print(f"フォント : {fp}")
    print(f"出力先   : {od}")
    print(f"viewBox  : {viewbox}x{viewbox}  /  スートサイズ: {suit_px}px")
    print()

    paths = extract_all(fp, od, viewbox, suit_px)
    print(f"\n完了: {len(paths)} スートを出力しました")


if __name__ == "__main__":
    main()

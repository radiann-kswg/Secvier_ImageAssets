"""Secvierフォントのグリフをアウトライン化SVGとして抽出する。

fontToolsのSVGPathPenを使い、フォントに依存しない純粋なSVGパス（<path d="...">）を
src/alphanum/ に出力する。生成SVGは外部フォント参照を一切持たない。

対象グリフ: A–Z / 0–9（Secvier v0.0-alphaが収録する36グリフ）

使い方:
    python scripts/extract_glyphs.py
    python scripts/extract_glyphs.py --viewbox 256
    python scripts/extract_glyphs.py --out-dir src/alphanum
"""
from __future__ import annotations

from pathlib import Path

import click
from fontTools import ttLib
from fontTools.pens.svgPathPen import SVGPathPen

FONT_PATH = Path(__file__).parent.parent / "assets" / "fonts" / "Secvier.otf"
OUT_DIR   = Path(__file__).parent.parent / "src" / "alphanum"
VIEWBOX   = 512

ALPHA_CHARS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
DIGIT_CHARS = list("0123456789")
ALL_CHARS   = ALPHA_CHARS + DIGIT_CHARS


def char_to_stem(char: str) -> str:
    """文字からファイル名ステム（拡張子なし）を生成する。"""
    return f"char_{char}"


def extract_glyph_svg(
    glyph_name: str,
    glyph_set: object,
    hmtx_metrics: dict[str, tuple[int, int]],
    ascender: int,
    upm: int,
    viewbox: int,
    title: str,
) -> str | None:
    """1グリフのアウトライン化SVG文字列を生成する。

    Args:
        glyph_name: フォント内グリフ名（例: 'A', 'zero'）
        glyph_set:  fontTools glyphSet オブジェクト
        hmtx_metrics: {グリフ名: (advanceWidth, lsb)} のマップ
        ascender:   フォントのアセンダー高さ（フォントユニット）
        upm:        Units Per Em
        viewbox:    出力SVGのviewBoxサイズ（正方形）
        title:      SVG <title> 要素のテキスト

    Returns:
        SVG文字列、またはパスデータが空の場合は None
    """
    pen = SVGPathPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    path_data: str = pen.getCommands()

    if not path_data.strip():
        return None  # space等の空グリフはスキップ

    advance_width, _ = hmtx_metrics.get(glyph_name, (upm, 0))

    # フォント座標系（Y上方向）→ SVG座標系（Y下方向）の変換
    # 変換行列: matrix(sx, 0, 0, -sx, tx, ty)
    #   sx = viewbox / upm  （スケール）
    #   ty = ascender * sx  （ベースライン位置をY軸に反映）
    #   tx = グリフを水平中央揃えするオフセット
    scale = viewbox / upm
    glyph_width_px = advance_width * scale
    tx = (viewbox - glyph_width_px) / 2
    ty = ascender * scale

    transform = (
        f"matrix({scale:.6f},0,0,{-scale:.6f},{tx:.3f},{ty:.3f})"
    )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg"\n'
        f'     viewBox="0 0 {viewbox} {viewbox}"\n'
        f'     width="{viewbox}" height="{viewbox}">\n'
        f'  <title>{title}</title>\n'
        f'  <g transform="{transform}">\n'
        f'    <path d="{path_data}" fill="#000000"/>\n'
        "  </g>\n"
        "</svg>\n"
    )


def extract_all(
    font_path: Path = FONT_PATH,
    out_dir: Path = OUT_DIR,
    viewbox: int = VIEWBOX,
) -> list[Path]:
    """全対象グリフのアウトライン化SVGを out_dir に出力する。

    Args:
        font_path: Secvier OTFファイルのパス
        out_dir:   出力ディレクトリ
        viewbox:   SVG viewBoxサイズ（px）

    Returns:
        生成したSVGファイルのパスリスト
    """
    tt = ttLib.TTFont(str(font_path))
    glyph_set    = tt.getGlyphSet()
    cmap         = tt.getBestCmap()
    hmtx_metrics: dict[str, tuple[int, int]] = tt["hmtx"].metrics
    upm: int     = tt["head"].unitsPerEm

    # アセンダー取得（OS/2 優先、なければ hhea）
    try:
        ascender: int = tt["OS/2"].sTypoAscender
    except (KeyError, AttributeError):
        ascender = tt["hhea"].ascender

    out_dir.mkdir(parents=True, exist_ok=True)
    produced: list[Path] = []

    for char in ALL_CHARS:
        codepoint = ord(char)
        if codepoint not in cmap:
            print(f"  SKIP: '{char}' (U+{codepoint:04X}) — cmapに未登録")
            continue

        glyph_name = cmap[codepoint]
        stem  = char_to_stem(char)
        title = f"Secvier {char}"

        svg = extract_glyph_svg(
            glyph_name, glyph_set, hmtx_metrics,
            ascender, upm, viewbox, title,
        )

        if svg is None:
            print(f"  SKIP: '{char}' — パスデータなし（空グリフ）")
            continue

        out_path = out_dir / f"{stem}.svg"
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
def main(font_path: str, out_dir: str, viewbox: int) -> None:
    """SecvierフォントからA-Z/0-9のアウトライン化SVGを生成します。"""
    fp  = Path(font_path)
    od  = Path(out_dir)

    print(f"フォント : {fp}")
    print(f"出力先   : {od}")
    print(f"viewBox  : {viewbox}x{viewbox}")
    print()

    paths = extract_all(fp, od, viewbox)

    print(f"\n完了: {len(paths)} グリフを出力しました")


if __name__ == "__main__":
    main()

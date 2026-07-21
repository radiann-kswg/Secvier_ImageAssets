"""Secvierフォントのグリフをアウトライン化SVGとして抽出する。

fontToolsのSVGPathPenを使い、フォントに依存しない純粋なSVGパス（<path d="...">）を
src/alphanum/（英数字）または src/alphanum_greek/（ギリシャ大文字）に出力する。
生成SVGは外部フォント参照を一切持たない。

対象グリフ:
    latin: A–Z / 0–9（36グリフ）
    greek: Α–Ω（ギリシャ大文字24グリフ, Secvier v0.1-beta で収録）

使い方:
    python scripts/extract_glyphs.py                    # 英数字 → src/alphanum/
    python scripts/extract_glyphs.py --charset greek    # ギリシャ大文字 → src/alphanum_greek/
    python scripts/extract_glyphs.py --viewbox 256
    python scripts/extract_glyphs.py --out-dir src/alphanum
"""
from __future__ import annotations

from pathlib import Path

import click
from fontTools import ttLib
from fontTools.pens.svgPathPen import SVGPathPen

ROOT      = Path(__file__).parent.parent
FONT_PATH = ROOT / "assets" / "fonts" / "Secvier.otf"
OUT_DIR   = ROOT / "src" / "alphanum"
GREEK_DIR = ROOT / "src" / "alphanum_greek"
VIEWBOX   = 512

ALPHA_CHARS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
DIGIT_CHARS = list("0123456789")
ALL_CHARS   = ALPHA_CHARS + DIGIT_CHARS

# ギリシャ大文字（U+0391–U+03A9）。ファイル名はローマ字表記のステムを使う
# （Α等のマルチバイト文字をファイル名に用いないため）。
GREEK_UPPER: dict[str, str] = {
    "Α": "Alpha",   "Β": "Beta",    "Γ": "Gamma",   "Δ": "Delta",
    "Ε": "Epsilon", "Ζ": "Zeta",    "Η": "Eta",     "Θ": "Theta",
    "Ι": "Iota",    "Κ": "Kappa",   "Λ": "Lambda",  "Μ": "Mu",
    "Ν": "Nu",      "Ξ": "Xi",      "Ο": "Omicron", "Π": "Pi",
    "Ρ": "Rho",     "Σ": "Sigma",   "Τ": "Tau",     "Υ": "Upsilon",
    "Φ": "Phi",     "Χ": "Chi",     "Ψ": "Psi",     "Ω": "Omega",
}

# charset名 → (対象文字→ステム名 の並び, 既定出力ディレクトリ)
CHARSETS: dict[str, tuple[list[tuple[str, str]], Path]] = {
    "latin": ([(ch, ch) for ch in ALL_CHARS], OUT_DIR),
    "greek": (list(GREEK_UPPER.items()), GREEK_DIR),
}


def char_to_stem(name: str) -> str:
    """ステム名からファイル名ステム（拡張子なし）を生成する。"""
    return f"char_{name}"


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
    out_dir: Path | None = None,
    viewbox: int = VIEWBOX,
    charset: str = "latin",
) -> list[Path]:
    """指定charsetの全対象グリフのアウトライン化SVGを out_dir に出力する。

    Args:
        font_path: Secvier OTFファイルのパス
        out_dir:   出力ディレクトリ（Noneでcharset既定を使用）
        viewbox:   SVG viewBoxサイズ（px）
        charset:   文字セット（'latin' または 'greek'）

    Returns:
        生成したSVGファイルのパスリスト
    """
    targets, default_dir = CHARSETS[charset]
    out_dir = out_dir or default_dir

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

    for char, name in targets:
        codepoint = ord(char)
        if codepoint not in cmap:
            print(f"  SKIP: '{char}' (U+{codepoint:04X}) — cmapに未登録")
            continue

        glyph_name = cmap[codepoint]
        stem  = char_to_stem(name)
        title = f"Secvier {name}"

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
    "--charset",
    type=click.Choice(list(CHARSETS.keys())),
    default="latin",
    show_default=True,
    help="抽出する文字セット（latin=英数字36 / greek=ギリシャ大文字24）",
)
@click.option(
    "--out-dir",
    default=None,
    help="SVG出力ディレクトリ（未指定でcharset既定: latin→src/alphanum, greek→src/alphanum_greek）",
)
@click.option(
    "--viewbox",
    default=VIEWBOX,
    show_default=True,
    help="SVG viewBoxサイズ（px、正方形）",
)
def main(font_path: str, charset: str, out_dir: str | None, viewbox: int) -> None:
    """Secvierフォントから英数字/ギリシャ大文字のアウトライン化SVGを生成します。"""
    fp = Path(font_path)
    od = Path(out_dir) if out_dir else None

    print(f"フォント : {fp}")
    print(f"文字セット: {charset}")
    print(f"出力先   : {od or CHARSETS[charset][1]}")
    print(f"viewBox  : {viewbox}x{viewbox}")
    print()

    paths = extract_all(fp, od, viewbox, charset)

    print(f"\n完了: {len(paths)} グリフを出力しました")


if __name__ == "__main__":
    main()

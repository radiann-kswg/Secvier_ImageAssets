"""Secvierスートグリフをアウトライン化SVGとして抽出する。

generate_cards.py が保持する SUIT_PATHS（72×72正規化済みパス）を使い、
512×512 の純粋な <path> SVGを src/cards/ に出力する。
フォント依存なし。extract_glyphs.py の英数字版に相当する。

出力:
    src/cards/suit_spade.svg
    src/cards/suit_heart.svg
    src/cards/suit_diamond.svg
    src/cards/suit_club.svg

使い方:
    python scripts/extract_suits.py
    python scripts/extract_suits.py --size 400 --out-dir src/cards
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

# generate_cards.py から SUIT_PATHS / SUIT_COLORS を再利用
sys.path.insert(0, str(Path(__file__).parent))
from generate_cards import SUIT_PATHS, SUIT_COLORS

OUT_DIR  = Path(__file__).parent.parent / "src" / "cards"
VIEWBOX  = 512
SUIT_PX  = 400  # viewBox内のスートサイズ（px）。余白 = (512-400)/2 = 56px


def suit_svg(suit: str, viewbox: int = VIEWBOX, suit_px: int = SUIT_PX) -> str:
    """1スートのアウトライン化SVG文字列を返す。

    Args:
        suit:     スート名（spade / heart / diamond / club）
        viewbox:  SVGのviewBoxサイズ（正方形）
        suit_px:  スートシンボルの描画サイズ（px）

    Returns:
        SVG文字列
    """
    scale  = suit_px / 72            # 72×72 → suit_px×suit_px
    offset = (viewbox - suit_px) / 2  # 中央揃えオフセット
    color  = SUIT_COLORS[suit]
    path_d = SUIT_PATHS[suit]

    transform = (
        f"matrix({scale:.6f},0,0,{scale:.6f},{offset:.3f},{offset:.3f})"
    )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg"\n'
        f'     viewBox="0 0 {viewbox} {viewbox}"\n'
        f'     width="{viewbox}" height="{viewbox}">\n'
        f'  <title>Secvier suit {suit}</title>\n'
        f'  <g transform="{transform}">\n'
        f'    <path d="{path_d}" fill="{color}"/>\n'
        '  </g>\n'
        '</svg>\n'
    )


def extract_all(
    out_dir: Path = OUT_DIR,
    viewbox: int = VIEWBOX,
    suit_px: int = SUIT_PX,
) -> list[Path]:
    """全4スートのSVGを out_dir に出力する。

    Returns:
        生成したSVGファイルのパスリスト
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    produced: list[Path] = []

    for suit in SUIT_PATHS:
        svg      = suit_svg(suit, viewbox, suit_px)
        out_path = out_dir / f"suit_{suit}.svg"
        out_path.write_text(svg, encoding="utf-8")
        produced.append(out_path)
        print(f"  OK: {out_path.name}")

    return produced


@click.command()
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
    help="viewBox内のスート描画サイズ（px）",
)
def main(out_dir: str, viewbox: int, suit_px: int) -> None:
    """Secvierスートグリフの単体SVGを生成します（4枚）。"""
    od = Path(out_dir)
    print(f"出力先  : {od}")
    print(f"viewBox : {viewbox}x{viewbox}  /  スートサイズ: {suit_px}px")
    print()

    paths = extract_all(od, viewbox, suit_px)
    print(f"\n完了: {len(paths)} スートを出力しました")


if __name__ == "__main__":
    main()

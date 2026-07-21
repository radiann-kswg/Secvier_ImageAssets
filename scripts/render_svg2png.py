"""アウトライン化SVG → 黒字・白背景マスクPNG（svg2png/）を再現生成する。

extract_glyphs.py / extract_suits.py が出力した src/ 配下のSVG（黒fill・透過背景）を、
白背景に合成した装飾なしPNGとして svg2png/ に書き出す。
このPNGは generate_dualmode.py がアルファマスク（グリフ被覆率）として読み込み、
二重縁取りの宝石バリアントを描画するための土台になる。

従来 svg2png/ の中身は手動生成だったが、本スクリプトによりパイプラインを再現可能にした。

対応カテゴリ:
    src/alphanum/       → svg2png/alphanum/        （char_A.png 〜 char_9.png, 36枚）
    src/alphanum_greek/ → svg2png/alphanum_greek/  （char_Alpha.png 〜 char_Omega.png, 24枚）
    src/suits/          → svg2png/suits/           （spade/heart/diamond/club.png, 4枚）

使い方:
    python scripts/render_svg2png.py                 # 全カテゴリ
    python scripts/render_svg2png.py --category greek
    python scripts/render_svg2png.py --res 512
"""
from __future__ import annotations

from pathlib import Path

import cairosvg
import click

ROOT = Path(__file__).parent.parent
SRC = ROOT / "src"
DST = ROOT / "svg2png"
RES = 512  # 出力解像度（マスク基準）。generate_dualmode の RES と一致させる

# カテゴリ名 → (入力SVGディレクトリ, 出力PNGディレクトリ)
CATEGORIES: dict[str, tuple[Path, Path]] = {
    "alphanum": (SRC / "alphanum",       DST / "alphanum"),
    "greek":    (SRC / "alphanum_greek", DST / "alphanum_greek"),
    "suits":    (SRC / "suits",          DST / "suits"),
}


def render_category(name: str, res: int = RES) -> int:
    """1カテゴリのSVG群を白背景マスクPNGに変換する。

    Args:
        name: カテゴリ名（alphanum / greek / suits）
        res:  出力解像度（px、正方形）

    Returns:
        生成したPNGの枚数
    """
    src_dir, out_dir = CATEGORIES[name]
    if not src_dir.exists():
        print(f"  WARN: {src_dir} が存在しません — スキップ")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    svgs = sorted(src_dir.glob("*.svg"))
    for svg in svgs:
        out_path = out_dir / f"{svg.stem}.png"
        cairosvg.svg2png(
            bytestring=svg.read_bytes(),
            write_to=str(out_path),
            output_width=res,
            output_height=res,
            background_color="white",  # 透過部分を白で塗り、黒字マスクに
        )
    print(f"  [{name}] {len(svgs)}枚 → {out_dir}")
    return len(svgs)


@click.command()
@click.option(
    "--category", "-c",
    type=click.Choice(list(CATEGORIES.keys()) + ["all"]),
    default="all",
    show_default=True,
    help="変換するカテゴリ",
)
@click.option(
    "--res",
    default=RES,
    show_default=True,
    help="出力解像度（px、正方形）",
)
def main(category: str, res: int) -> None:
    """src/ のアウトラインSVGを svg2png/ の白背景マスクPNGに変換します。"""
    targets = list(CATEGORIES.keys()) if category == "all" else [category]
    total = 0
    for cat in targets:
        total += render_category(cat, res)
    print(f"\n完了: 合計 {total} 枚を svg2png/ に出力しました")


if __name__ == "__main__":
    main()

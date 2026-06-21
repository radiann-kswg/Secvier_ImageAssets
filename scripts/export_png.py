"""SVGファイルをPNG（72px / 512px）に変換して dist/ に出力する。"""
from __future__ import annotations

from pathlib import Path

import cairosvg
from PIL import Image

DIST_DIR = Path(__file__).parent.parent / "dist"
SIZES = {
    "72": 72,
    "512": 512,
}


def svg_to_png(
    svg_path: Path,
    category: str,
    filename_stem: str,
    sizes: dict[str, int] = SIZES,
) -> list[Path]:
    """SVGを指定サイズのPNGに変換する。

    Args:
        svg_path: 変換元SVGファイル
        category: 出力カテゴリ（cards/dice/mahjong/alphanum）
        filename_stem: ファイル名（拡張子・サイズサフィックスなし）
        sizes: {サフィックス: ピクセル数} の辞書

    Returns:
        生成したPNGファイルのパスリスト
    """
    svg_data = svg_path.read_bytes()
    outputs: list[Path] = []

    for suffix, px in sizes.items():
        out_dir = DIST_DIR / category
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{filename_stem}_{suffix}.png"

        png_data = cairosvg.svg2png(
            bytestring=svg_data,
            output_width=px,
            output_height=px,
        )

        # Pillowで品質確認・保存
        from io import BytesIO
        img = Image.open(BytesIO(png_data)).convert("RGBA")
        img.save(str(out_path), "PNG", optimize=True)
        outputs.append(out_path)
        print(f"  Exported: {out_path} ({px}px)")

    return outputs


def export_category(category: str) -> None:
    """src/{category}/ 内の全SVGをPNGに変換する。

    Args:
        category: カテゴリ名（cards/dice/mahjong/alphanum）
    """
    src_dir = Path(__file__).parent.parent / "src" / category
    if not src_dir.exists():
        print(f"Warning: {src_dir} が存在しません")
        return

    svgs = sorted(src_dir.glob("*.svg"))
    print(f"[{category}] {len(svgs)}件のSVGを変換中...")
    for svg in svgs:
        svg_to_png(svg, category, svg.stem)
    print(f"[{category}] 完了")


if __name__ == "__main__":
    # 動作確認: alphanumカテゴリ
    export_category("alphanum")

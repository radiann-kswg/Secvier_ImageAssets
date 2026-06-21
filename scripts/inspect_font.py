"""Secvierフォントのグリフ情報を検査し、docs/glyph_map.txt に出力する。"""
from __future__ import annotations

from pathlib import Path

from fontTools import ttLib

FONT_PATH = Path(__file__).parent.parent / "assets" / "fonts" / "Secvier.otf"
OUTPUT_PATH = Path(__file__).parent.parent / "docs" / "glyph_map.txt"


def inspect_font(font_path: Path = FONT_PATH, output: Path = OUTPUT_PATH) -> None:
    """フォントを読み込み、グリフ名・Unicodeマッピングを出力する。

    Args:
        font_path: OTFフォントファイルのパス
        output: 出力テキストファイルのパス
    """
    tt = ttLib.TTFont(str(font_path))

    cmap = tt.getBestCmap()
    glyph_set = tt.getGlyphSet()

    lines: list[str] = [
        f"# Secvier Glyph Map",
        f"# Font: {font_path.name}",
        f"# Total glyphs: {len(glyph_set)}",
        f"# Unicode mapped glyphs: {len(cmap) if cmap else 0}",
        "",
        "## Unicode → Glyph Name",
        "",
    ]

    if cmap:
        for codepoint in sorted(cmap.keys()):
            glyph_name = cmap[codepoint]
            char = chr(codepoint)
            lines.append(
                f"U+{codepoint:04X}  {char!r:6}  {glyph_name}"
            )

    lines += [
        "",
        "## All Glyph Names",
        "",
    ]
    for name in sorted(glyph_set.keys()):
        lines.append(f"  {name}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Glyph map written to: {output}")
    print(f"  Total glyphs: {len(glyph_set)}")
    if cmap:
        print(f"  Unicode mapped: {len(cmap)}")


if __name__ == "__main__":
    inspect_font()

"""Secvierフォントのグリフからアウトライン化SVGを生成する。

フォント内のグリフパスを取得し、外部フォント依存なしのSVGとして書き出す。
生成SVGは src/{category}/ に配置される。
"""
from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional

FONT_PATH = Path(__file__).parent.parent / "assets" / "fonts" / "Secvier.otf"
SRC_DIR = Path(__file__).parent.parent / "src"
VIEWBOX_SIZE = 512


def font_b64(font_path: Path = FONT_PATH) -> str:
    """フォントファイルをBase64エンコードして返す。"""
    return base64.b64encode(font_path.read_bytes()).decode("ascii")


def make_svg_with_font(
    char: str,
    label: Optional[str] = None,
    font_size: int = 400,
    viewbox: int = VIEWBOX_SIZE,
    fg_color: str = "#000000",
    bg_color: Optional[str] = None,
) -> str:
    """Secvierフォントを埋め込んだSVG文字列を生成する。

    Args:
        char: レンダリングする文字
        label: SVGタイトル（省略時はchar）
        font_size: フォントサイズ（px）
        viewbox: viewBoxサイズ（正方形）
        fg_color: 文字色
        bg_color: 背景色（Noneで透過）

    Returns:
        SVG文字列
    """
    b64 = font_b64()
    title = label or char
    cx = viewbox // 2
    cy = viewbox // 2

    bg_rect = (
        f'  <rect width="{viewbox}" height="{viewbox}" fill="{bg_color}"/>\n'
        if bg_color
        else ""
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {viewbox} {viewbox}"
     width="{viewbox}" height="{viewbox}">
  <title>{title}</title>
  <defs>
    <style>
      @font-face {{
        font-family: 'Secvier';
        src: url('data:font/otf;base64,{b64}') format('opentype');
      }}
    </style>
  </defs>
{bg_rect}  <text
    x="{cx}"
    y="{cy + font_size // 3}"
    font-family="Secvier"
    font-size="{font_size}"
    text-anchor="middle"
    fill="{fg_color}"
  >{char}</text>
</svg>"""


def render_char(
    char: str,
    category: str,
    filename_stem: str,
    **kwargs,
) -> Path:
    """1文字分のSVGを src/{category}/ に書き出す。

    Args:
        char: レンダリングする文字
        category: 出力カテゴリ（cards/dice/mahjong/alphanum）
        filename_stem: ファイル名（拡張子なし）
        **kwargs: make_svg_with_font に渡すオプション

    Returns:
        書き出したSVGファイルのパス
    """
    out_dir = SRC_DIR / category
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{filename_stem}.svg"
    svg = make_svg_with_font(char, **kwargs)
    out_path.write_text(svg, encoding="utf-8")
    return out_path


if __name__ == "__main__":
    # 動作確認: 英字Aをレンダリング
    path = render_char("A", "alphanum", "char_A", label="Secvier A")
    print(f"Rendered: {path}")

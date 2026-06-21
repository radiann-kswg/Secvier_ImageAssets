"""Secvierスートグリフを使ったトランプカードSVGを生成する。

スートパスは _original-fonts/f-skt Secvier.svg の polygon 座標を
72×72座標系に正規化して埋め込んでいる。
値テキスト（A/2-10/J/Q/K）は Secvier.otf を Base64 埋め込みで使用。
出力先: src/cards/card_{suit}_{value}.svg (512×512)

使い方:
    python scripts/generate_cards.py
    python scripts/generate_cards.py --dry-run
"""
from __future__ import annotations

import base64
from pathlib import Path

import click

FONT_PATH    = Path(__file__).parent.parent / "assets" / "fonts" / "Secvier.otf"
OUT_DIR      = Path(__file__).parent.parent / "src" / "cards"
VIEWBOX: int = 512

# ── スートパス ────────────────────────────────────────────────────────────────
# _original-fonts/f-skt Secvier.svg の <polygon> 座標を
# 各スートの bounding box (72×72) 原点に正規化した <path d> 文字列。
#
# ♦ : polygon points="153 432 ..." → subtract (117, 432)
# ♥ : polygon points="297 504 ..." → subtract (261, 432)
# ♠ : <g> body "153 576 ..." + stem "144 648 ..." → subtract (117, 576)
# ♣ : <g> 4 polygons → subtract (261, 576)
SUIT_PATHS: dict[str, str] = {
    "diamond": (
        "M36,0 L27,18 L18,27 L0,36 L18,45 L27,54 L36,72 "
        "L45,54 L54,45 L72,36 L54,27 L45,18 Z"
    ),
    "heart": (
        "M36,72 L27,54 L9,36 L0,27 L0,9 L18,0 L27,0 L36,9 "
        "L45,0 L54,0 L72,9 L72,27 L63,36 L45,54 Z"
    ),
    "spade": (
        # body
        "M36,0 L27,9 L9,27 L0,45 L18,63 L27,63 L36,54 "
        "L45,63 L54,63 L72,45 L63,27 L45,9 Z "
        # stem
        "M27,72 L45,72 L36,54 Z"
    ),
    "club": (
        # top lobe
        "M18,27 L18,9 L27,0 L45,0 L54,9 L54,27 L36,45 Z "
        # left lobe
        "M27,63 L9,63 L0,54 L0,36 L9,27 L18,27 L36,54 Z "
        # right lobe
        "M45,63 L63,63 L72,54 L72,36 L63,27 L54,27 L36,54 Z "
        # stem
        "M27,72 L45,72 L36,54 Z"
    ),
}

SUIT_COLORS: dict[str, str] = {
    "spade":   "#1A1A1A",
    "heart":   "#CC1111",
    "diamond": "#CC1111",
    "club":    "#1A1A1A",
}

SUITS  = ["spade", "heart", "diamond", "club"]
VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

# カードレイアウト定数
_MARGIN      = 28
_FONT_LG     = 80   # 値テキスト（A/J/Q/K/2-9）
_FONT_10     = 58   # "10" は2文字なので小さめ
_CORNER_SUIT = 52   # コーナースートサイズ(px)
_CENTER_SUIT = 224  # センタースートサイズ(px)
_BORDER_R    = 36   # カード角丸半径


# ── ヘルパー ───────────────────────────────────────────────────────────────────

def _font_b64(font_path: Path = FONT_PATH) -> str:
    """フォントファイルをBase64エンコードして返す。"""
    return base64.b64encode(font_path.read_bytes()).decode("ascii")


def _suit_path_el(suit: str, x: float, y: float, size: float) -> str:
    """スートシンボルの <path> 要素文字列を返す（72×72→size にスケール）。"""
    scale  = size / 72
    color  = SUIT_COLORS[suit]
    path_d = SUIT_PATHS[suit]
    return (
        f'<path d="{path_d}" fill="{color}" '
        f'transform="translate({x:.2f},{y:.2f}) scale({scale:.5f})"/>'
    )


def _font_style(b64: str) -> str:
    return (
        "<style>\n"
        "  @font-face {\n"
        "    font-family: 'Secvier';\n"
        f"    src: url('data:font/otf;base64,{b64}') format('opentype');\n"
        "  }\n"
        "</style>"
    )


# ── SVG 生成 ───────────────────────────────────────────────────────────────────

def card_svg(suit: str, value: str, b64: str) -> str:
    """通常カード1枚のSVG文字列を生成する。"""
    color     = SUIT_COLORS[suit]
    font_size = _FONT_10 if value == "10" else _FONT_LG
    half      = VIEWBOX / 2

    # 上左コーナー: 値テキストのベースライン
    vx = _MARGIN + 10
    vy = _MARGIN + font_size

    # 上左コーナー: スートの左上座標
    sx = _MARGIN + 6
    sy = vy + 6

    # センタースートの左上座標
    ctr = (VIEWBOX - _CENTER_SUIT) / 2

    # 上左コーナー要素
    value_tl = (
        f'<text x="{vx}" y="{vy}" '
        f'font-family="Secvier" font-size="{font_size}" '
        f'fill="{color}" text-anchor="start">{value}</text>'
    )
    suit_tl = _suit_path_el(suit, sx, sy, _CORNER_SUIT)

    # 下右コーナー（180°回転）
    rot = f'transform="rotate(180,{half},{half})"'
    value_br = f'<g {rot}>{value_tl}</g>'
    suit_br  = f'<g {rot}>{suit_tl}</g>'

    # センタースート
    suit_ctr = _suit_path_el(suit, ctr, ctr, _CENTER_SUIT)

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg"\n'
        f'     viewBox="0 0 {VIEWBOX} {VIEWBOX}"\n'
        f'     width="{VIEWBOX}" height="{VIEWBOX}">\n'
        f'  <title>Secvier {value} of {suit}</title>\n'
        f'  <defs>{_font_style(b64)}</defs>\n'
        f'  <rect width="{VIEWBOX}" height="{VIEWBOX}" rx="{_BORDER_R}"\n'
        f'        fill="#FAFAFA" stroke="#C8C8C8" stroke-width="4"/>\n'
        f'  {suit_ctr}\n'
        f'  {value_tl}\n'
        f'  {suit_tl}\n'
        f'  {value_br}\n'
        f'  {suit_br}\n'
        '</svg>\n'
    )


def joker_svg(joker_type: str, b64: str) -> str:
    """ジョーカーカードのSVG文字列を生成する。"""
    color = "#1A1A1A" if joker_type == "black" else "#CC1111"
    half  = VIEWBOX / 2

    # "J" 上・"K" 下を中央に大きく配置
    jy = half - 20
    ky = half + 120

    # コーナー "J"
    cx  = _MARGIN + 10
    cy  = _MARGIN + _FONT_LG
    rot = f'transform="rotate(180,{half},{half})"'

    corner = (
        f'<text x="{cx}" y="{cy}" '
        f'font-family="Secvier" font-size="{_FONT_LG}" '
        f'fill="{color}" text-anchor="start">J</text>'
    )

    # 4スートを十字配置（センター装飾）
    s = 64  # 各スートのサイズ
    suits_deco = "\n".join([
        _suit_path_el("spade",   half - s / 2, half - s - 10, s),
        _suit_path_el("heart",   half - s / 2, half + 10,      s),
        _suit_path_el("diamond", half - s - 10, half - s / 2,  s),
        _suit_path_el("club",    half + 10,     half - s / 2,  s),
    ])

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg"\n'
        f'     viewBox="0 0 {VIEWBOX} {VIEWBOX}"\n'
        f'     width="{VIEWBOX}" height="{VIEWBOX}">\n'
        f'  <title>Secvier Joker {joker_type}</title>\n'
        f'  <defs>{_font_style(b64)}</defs>\n'
        f'  <rect width="{VIEWBOX}" height="{VIEWBOX}" rx="{_BORDER_R}"\n'
        f'        fill="#FAFAFA" stroke="#C8C8C8" stroke-width="4"/>\n'
        f'  {suits_deco}\n'
        f'  <text x="{half}" y="{jy}"\n'
        f'    font-family="Secvier" font-size="100"\n'
        f'    text-anchor="middle" fill="{color}">J</text>\n'
        f'  <text x="{half}" y="{ky}"\n'
        f'    font-family="Secvier" font-size="100"\n'
        f'    text-anchor="middle" fill="{color}">K</text>\n'
        f'  {corner}\n'
        f'  <g {rot}>{corner}</g>\n'
        '</svg>\n'
    )


# ── メイン ────────────────────────────────────────────────────────────────────

@click.command()
@click.option("--dry-run", is_flag=True, help="ファイルを生成せず内容を表示")
def main(dry_run: bool) -> None:
    """Secvierスートグリフを使ったトランプカードSVGを生成します（54枚）。"""
    if dry_run:
        total = len(SUITS) * len(VALUES) + 2
        for suit in SUITS:
            for value in VALUES:
                print(f"  DRY-RUN: card_{suit}_{value}.svg")
        print("  DRY-RUN: card_joker_black.svg")
        print("  DRY-RUN: card_joker_red.svg")
        print(f"\n（dry-run: {total}枚 — ファイルは生成されていません）")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    b64 = _font_b64()
    count = 0

    for suit in SUITS:
        for value in VALUES:
            stem = f"card_{suit}_{value}"
            svg  = card_svg(suit, value, b64)
            path = OUT_DIR / f"{stem}.svg"
            path.write_text(svg, encoding="utf-8")
            print(f"  OK: {path.name}")
            count += 1

    for jtype in ("black", "red"):
        svg  = joker_svg(jtype, b64)
        path = OUT_DIR / f"card_joker_{jtype}.svg"
        path.write_text(svg, encoding="utf-8")
        print(f"  OK: {path.name}")
        count += 1

    print(f"\n完了: {count}枚 -> {OUT_DIR}")


if __name__ == "__main__":
    main()

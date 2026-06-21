"""Secvier ImageAssets 一括ビルドスクリプト。

使い方:
  python scripts/build.py                    # 全カテゴリ
  python scripts/build.py --category cards   # 特定カテゴリ
  python scripts/build.py --dry-run          # 実行内容の確認のみ
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

# scriptsディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from render_svg import render_char, SRC_DIR
from export_png import export_category

# ----------------------------------------------------------------
# 絵文字定義
# ----------------------------------------------------------------

# トランプ: {filename_stem: (char, label)}
SUITS = {
    "spade":   ("♠", "スペード"),
    "heart":   ("♥", "ハート"),
    "diamond": ("♦", "ダイヤ"),
    "club":    ("♣", "クラブ"),
}
VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

CARDS: dict[str, tuple[str, str]] = {}
for suit_key, (suit_char, suit_label) in SUITS.items():
    for value in VALUES:
        stem = f"card_{suit_key}_{value}"
        CARDS[stem] = (f"{suit_char}{value}", f"{suit_label}{value}")
CARDS["card_joker_black"] = ("🃏", "ジョーカー（黒）")
CARDS["card_joker_red"]   = ("🃏", "ジョーカー（赤）")

# ダイス: {filename_stem: (char, label)}
DICE: dict[str, tuple[str, str]] = {
    "dice_d4_1":  ("⛆", "D4-1"),  # ← Secvierフォントのグリフに合わせて後で更新
    "dice_d6_1":  ("⚀", "D6-1"),
    "dice_d6_2":  ("⚁", "D6-2"),
    "dice_d6_3":  ("⚂", "D6-3"),
    "dice_d6_4":  ("⚃", "D6-4"),
    "dice_d6_5":  ("⚄", "D6-5"),
    "dice_d6_6":  ("⚅", "D6-6"),
}
# D4, D8, D10, D10tens, D12, D20 の面定義は inspect_font.py 実行後に確定させること

# 麻雀牌
MAHJONG: dict[str, tuple[str, str]] = {}
# 萬子 1–9
for i in range(1, 10):
    MAHJONG[f"mj_man_{i}"] = (f"{i}万", f"萬子{i}")
# 筒子 1–9
for i in range(1, 10):
    MAHJONG[f"mj_pin_{i}"] = (f"{i}筒", f"筒子{i}")
# 索子 1–9
for i in range(1, 10):
    MAHJONG[f"mj_sou_{i}"] = (f"{i}索", f"索子{i}")
# 字牌
CHAR_TILES = {
    "east":  ("東", "東"),
    "south": ("南", "南"),
    "west":  ("西", "西"),
    "north": ("北", "北"),
    "chun":  ("中", "中（チュン）"),
    "hatsu": ("發", "發（ハツ）"),
    "haku":  ("白", "白（ハク）"),
}
for key, (char, label) in CHAR_TILES.items():
    MAHJONG[f"mj_char_{key}"] = (char, label)

# 英数字
ALPHANUM: dict[str, tuple[str, str]] = {}
for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    ALPHANUM[f"char_{ch}"] = (ch, f"英字 {ch}")
for d in "0123456789":
    ALPHANUM[f"char_{d}"] = (d, f"数字 {d}")

CATEGORIES: dict[str, dict[str, tuple[str, str]]] = {
    "cards":    CARDS,
    "dice":     DICE,
    "mahjong":  MAHJONG,
    "alphanum": ALPHANUM,
}

# ----------------------------------------------------------------
# ビルド処理
# ----------------------------------------------------------------

def build_category(category: str, dry_run: bool = False) -> None:
    """指定カテゴリのSVGを生成し、PNGに変換する。"""
    items = CATEGORIES.get(category, {})
    print(f"\n=== [{category}] {len(items)}枚 ===")
    if dry_run:
        for stem, (char, label) in items.items():
            print(f"  DRY-RUN: {stem}  ({char})  {label}")
        return

    # SVG生成
    for stem, (char, label) in items.items():
        path = render_char(char, category, stem, label=label)
        print(f"  SVG: {path.name}")

    # PNG変換
    export_category(category)


@click.command()
@click.option(
    "--category", "-c",
    type=click.Choice(list(CATEGORIES.keys()) + ["all"]),
    default="all",
    show_default=True,
    help="ビルドするカテゴリ",
)
@click.option("--dry-run", is_flag=True, help="実際には生成せず内容を表示")
def main(category: str, dry_run: bool) -> None:
    """Secvier絵文字アセットをビルドします。"""
    targets = list(CATEGORIES.keys()) if category == "all" else [category]
    for cat in targets:
        build_category(cat, dry_run=dry_run)

    if not dry_run:
        print("\n✓ ビルド完了")
    else:
        print("\n（dry-runモード：ファイルは生成されていません）")


if __name__ == "__main__":
    main()

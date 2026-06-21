"""
Secvier ImageAssets — Discord/Misskey カスタム絵文字 PNG 生成
3 デザインバリアント × 英数字(36枚) = 108 枚

デザインコンセプト (100BeautiesLab_CreationsDB 傾向):
  A: 星幽   (seiyuu)   ── 深夜の宇宙・星座・神秘的で静謐な美
  B: 白磁   (hakuji)   ── 白磁器・清廉・極限まで削ぎ落とされた美意識
  C: 翠玉   (suigyoku) ── 深翠・宝石・森の叡智 (v2: kouya を廃止して新設)

出力先: dist/alphanum/{seiyuu,hakuji,suigyoku}/
サイズ: 128×128 px PNG (Discord/Misskey 標準絵文字)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _draw_common import C, SIZE, load_font, make_base
from _variants import VARIANTS, Variant

DIST = Path(__file__).parent.parent / "dist"

ALPHANUM_CHARS: list[tuple[str, str]] = (
    [(ch, f"char_{ch}") for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"] +
    [(d,  f"char_{d}")  for d in "0123456789"]
)


def render_alphanum(char: str, stem: str, v: Variant, out_dir: Path) -> None:
    img, draw = make_base(v)
    font = load_font(96)   # より大きく
    draw.text((C, C + 4), char, font=font, fill=v.text, anchor="mm")
    out_dir.mkdir(parents=True, exist_ok=True)
    img.save(out_dir / f"{stem}.png", "PNG", optimize=True)


def main() -> None:
    total = 0
    for v in VARIANTS:
        out_dir = DIST / "alphanum" / v.key
        for char, stem in ALPHANUM_CHARS:
            render_alphanum(char, stem, v, out_dir)
        print(f"  {v.label} ({v.key}): {len(ALPHANUM_CHARS)} 枚 → dist/alphanum/{v.key}/")
        total += len(ALPHANUM_CHARS)
    print(f"\n✓ 英数字 合計 {total} 枚")


if __name__ == "__main__":
    main()

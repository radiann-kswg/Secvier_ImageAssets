"""
バリアント定義（全スクリプト共通）

  seiyuu   : 星幽 — 深夜宇宙・星座・神秘
  hakuji   : 白磁 — 白磁器・清廉・極限美
  suigyoku : 翠玉 — 深翠・宝石・森の叡智
  kougyoku : 紅玉 — 紅玉石・情熱・焔の叡智   (seiyuu/suigyoku の暗色宝石系を踏襲)
  sakin    : 砂金 — 砂金・羊皮紙・黄金文書    (hakuji の淡色清廉系を踏襲)
"""
from __future__ import annotations
from typing import NamedTuple


class Variant(NamedTuple):
    key: str
    label: str
    bg: tuple[int, int, int, int]
    text: tuple[int, int, int, int]
    border: tuple[int, int, int, int]
    accent: tuple[int, int, int, int]
    shape_fill: tuple[int, int, int, int]
    shape_line: tuple[int, int, int, int]


VARIANTS: list[Variant] = [
    # ── 暗色系 ───────────────────────────────────────────────
    Variant(
        key="seiyuu", label="星幽",
        bg=(10, 10, 26, 255),
        text=(238, 226, 185, 255),
        border=(90, 108, 195, 255),
        accent=(175, 148, 255, 255),
        shape_fill=(22, 22, 58, 255),
        shape_line=(120, 100, 230, 255),
    ),
    Variant(
        key="suigyoku", label="翠玉",
        bg=(4, 18, 10, 255),
        text=(210, 248, 218, 255),
        border=(38, 140, 76, 255),
        accent=(100, 210, 140, 255),
        shape_fill=(8, 36, 18, 255),
        shape_line=(56, 168, 104, 255),
    ),
    Variant(
        key="kougyoku", label="紅玉",
        bg=(14, 2, 6, 255),           # 深紅玉黒
        text=(255, 228, 208, 255),    # 温かみのある白
        border=(185, 20, 48, 255),    # 紅玉色
        accent=(240, 80, 105, 255),   # 鮮やかな紅
        shape_fill=(30, 4, 12, 255),  # 濃紅
        shape_line=(210, 32, 65, 255),# 明紅
    ),
    # ── 淡色系 ───────────────────────────────────────────────
    Variant(
        key="hakuji", label="白磁",
        bg=(248, 244, 236, 255),
        text=(22, 18, 14, 255),
        border=(150, 128, 88, 255),
        accent=(110, 88, 52, 255),
        shape_fill=(232, 224, 208, 255),
        shape_line=(140, 118, 78, 255),
    ),
    Variant(
        key="sakin", label="砂金",
        bg=(245, 232, 190, 255),      # 羊皮紙
        text=(44, 26, 6, 255),        # 深セピア
        border=(188, 142, 30, 255),   # 金
        accent=(218, 168, 42, 255),   # 明金
        shape_fill=(235, 215, 168, 255),  # 薄金
        shape_line=(178, 132, 22, 255),   # 濃金
    ),
]

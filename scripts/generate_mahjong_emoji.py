#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""generate_mahjong_emoji.py — 麻雀牌 SVG から Discord / Misskey 用 PNG を生成し、
Misskey 一括インポート用 zip を出力する。

入力:  src/mahjong/mj_*.svg（5:7）
出力:
  dist/mahjong/discord/{stem}.png   … 256×256（牌を中央配置・余白透過）Discord 用
  dist/mahjong/misskey/{stem}.png   … 256×358（5:7・透過）Misskey 用
  _exported-dist/secvier-mahjong-misskey-{timestamp}.zip … Misskey 一括インポート

依存: cairosvg, Pillow
著作権者: RadianN_kswg / ラジアン（柏木主税） / CC BY 4.0
"""
from __future__ import annotations

import io
import json
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import cairosvg
from PIL import Image

ROOT = Path(__file__).parent.parent
SRC = ROOT / "src" / "mahjong"
DIST = ROOT / "dist" / "mahjong"
OUTPUT_DIR = ROOT / "_exported-dist"

LICENSE = ("CC BY 4.0 RadianN_kswg / ラジアン（柏木主税） "
           "https://github.com/radiann-kswg/Secvier_ImageAssets")

# Misskey/Discord 出力サイズ
MK_W, MK_H = 256, 358          # 5:7 透過（Misskey）
DC = 256                       # Discord 正方
DC_TILE_H = 248                # Discord 内に収める牌の高さ

CAT = "Secvier/05.麻雀牌"

WIND = {
    "east": ("東", ["east", "ton", "東", "wind"]),
    "south": ("南", ["south", "nan", "南", "wind"]),
    "west": ("西", ["west", "shaa", "西", "wind"]),
    "north": ("北", ["north", "pei", "北", "wind"]),
}
DRAGON = {
    "hatsu": ("發", ["hatsu", "green", "發", "dragon"]),
    "chun": ("中", ["chun", "red", "中", "dragon"]),
    "haku": ("白", ["haku", "white", "白", "dragon"]),
}
SEASON = {
    "spring": ("春", ["spring", "春", "season"]),
    "summer": ("夏", ["summer", "夏", "season"]),
    "autumn": ("秋", ["autumn", "秋", "season"]),
    "winter": ("冬", ["winter", "冬", "season"]),
}


def classify(stem: str) -> tuple[str, list[str]]:
    """stem からカテゴリとエイリアスを返す。"""
    p = stem.split("_")  # mj_man_1 / mj_man_5_red / mj_char_east / mj_season_spring
    kind = p[1]
    if kind in ("man", "pin", "sou"):
        suitjp = {"man": "萬子", "pin": "筒子", "sou": "索子"}[kind]
        suiten = {"man": "manzu", "pin": "pinzu", "sou": "souzu"}[kind]
        n = p[2]
        if len(p) >= 4 and p[3] == "red":     # 赤ドラ
            return (CAT + "/赤ドラ",
                    ["akadora", "red5", "赤ドラ", kind, suiten, suitjp, n])
        return (CAT + "/" + suitjp, [n, kind, suiten, suitjp, f"{kind}{n}", f"{n}{kind}"])
    if kind == "char":
        key = p[2]
        if key in WIND:
            return (CAT + "/字牌", WIND[key][1] + ["honor"])
        if key in DRAGON:
            return (CAT + "/字牌", DRAGON[key][1] + ["honor"])
        return (CAT + "/字牌", [key, "honor"])
    if kind == "season":
        key = p[2]
        return (CAT + "/季節牌", SEASON.get(key, (key, [key]))[1])
    return (CAT, [stem])


def render(svg_path: Path) -> Image.Image:
    """SVG を高解像 RGBA で描画。"""
    png = cairosvg.svg2png(url=str(svg_path), output_width=720, output_height=1008)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def make_misskey(img: Image.Image) -> Image.Image:
    return img.resize((MK_W, MK_H), Image.LANCZOS)


def make_discord(img: Image.Image) -> Image.Image:
    h = DC_TILE_H
    w = round(h * img.width / img.height)
    tile = img.resize((w, h), Image.LANCZOS)
    canvas = Image.new("RGBA", (DC, DC), (0, 0, 0, 0))
    canvas.alpha_composite(tile, ((DC - w) // 2, (DC - h) // 2))
    return canvas


def meta_entry(file_name: str, name: str, category: str, aliases: list[str]) -> dict:
    # 重複除去（順序維持）
    seen, al = set(), []
    for a in aliases:
        if a not in seen:
            seen.add(a)
            al.append(a)
    return {
        "fileName": file_name,
        "downloaded": True,
        "emoji": {
            "id": uuid.uuid4().hex[:16],
            "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "name": name,
            "host": None,
            "category": category,
            "originalUrl": "",
            "publicUrl": "",
            "uri": None,
            "type": "image/png",
            "aliases": al,
            "license": LICENSE,
            "localOnly": False,
            "isSensitive": False,
            "roleIdsThatCanBeUsedThisEmojiAsReaction": [],
        },
    }


def main() -> None:
    dc_dir = DIST / "discord"
    mk_dir = DIST / "misskey"
    dc_dir.mkdir(parents=True, exist_ok=True)
    mk_dir.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    entries: list[tuple[Path, str, dict]] = []
    svgs = sorted(SRC.glob("mj_*.svg"))
    for svg in svgs:
        stem = svg.stem                      # mj_man_1
        img = render(svg)
        make_discord(img).save(dc_dir / f"{stem}.png")
        mk_png = mk_dir / f"{stem}.png"
        make_misskey(img).save(mk_png)
        name = "sv_" + stem                  # sv_mj_man_1
        category, aliases = classify(stem)
        entries.append((mk_png, f"{name}.png", meta_entry(f"{name}.png", name, category, aliases)))

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    zip_path = OUTPUT_DIR / f"secvier-mahjong-misskey-{timestamp}.zip"
    now_jst = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT+0900 (JST)")
    meta = {
        "metaVersion": 2,
        "host": "radiann6631.net",
        "exportedAt": now_jst,
        "emojis": [e for _, _, e in entries],
    }
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED) as zf:
        for src_path, zip_name, _ in entries:
            zf.write(src_path, zip_name)
        zf.writestr("meta.json", json.dumps(meta, ensure_ascii=False, indent=2))

    print("Discord PNG : %d -> %s" % (len(svgs), dc_dir))
    print("Misskey PNG : %d -> %s" % (len(svgs), mk_dir))
    print("Misskey zip : %s (%d emojis)" % (zip_path.name, len(entries)))
    by_cat: dict[str, int] = {}
    for _, _, e in entries:
        c = e["emoji"]["category"]
        by_cat[c] = by_cat.get(c, 0) + 1
    for c in sorted(by_cat):
        print("  %s: %d" % (c, by_cat[c]))


if __name__ == "__main__":
    main()

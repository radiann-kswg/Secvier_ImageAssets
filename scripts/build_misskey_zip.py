"""Misskey一括インポート用zipファイルを生成するスクリプト。

dist/cards/misskey/, dist/alphanum_dualmode/, dist/suits_dualmode/, dist/dice/ から
Misskey互換 meta.json 付きのzipアーカイブを作成します。

出力: _exported-dist/secvier-misskey-{timestamp}.zip
"""
from __future__ import annotations

import json
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
DIST = ROOT / "dist"
OUTPUT_DIR = ROOT / "_exported-dist"

LICENSE = "CC BY 4.0 RadianN_kswg / ラジアン（柏木主税） https://github.com/radiann-kswg/Secvier_ImageAssets"

VARIANT_NAMES: dict[str, str] = {
    "seiyuu": "星幽",
    "suigyoku": "翠玉",
    "kougyoku": "紅玉",
    "hakuji": "白磁",
    "kokuji": "黒磁",
    "sakin": "砂金",
}

SUIT_LABELS: dict[str, str] = {
    "S": "spade",
    "H": "heart",
    "D": "diamond",
    "C": "club",
}

RANK_ALIASES: dict[str, list[str]] = {
    "A": ["ace"],
    "J": ["jack"],
    "C": ["knight"],
    "Q": ["queen"],
    "K": ["king"],
}


def _make_entry(file_name: str, name: str, category: str, aliases: list[str]) -> dict:
    """meta.json 用の絵文字エントリを生成する。"""
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
            "aliases": aliases,
            "license": LICENSE,
            "localOnly": False,
            "isSensitive": False,
            "roleIdsThatCanBeUsedThisEmojiAsReaction": [],
        },
    }


def _collect_cards() -> list[tuple[Path, str, dict]]:
    """dist/cards/misskey/*.png のエントリを収集する。"""
    src_dir = DIST / "cards" / "misskey"
    entries: list[tuple[Path, str, dict]] = []

    for png in sorted(src_dir.glob("*.png")):
        stem = png.stem
        zip_name = f"sv_{stem}.png"
        emoji_name = f"sv_{stem}"

        if "suit" in stem:
            # card_suit_C → スートマーク
            suit_key = stem.split("_")[-1]
            suit_label = SUIT_LABELS.get(suit_key, suit_key.lower())
            category = "Secvier/01.トランプ/スートマーク"
            aliases = [suit_label, suit_key.lower()]
        elif "joker" in stem:
            color = stem.split("_")[-1]
            category = "Secvier/01.トランプ/ジョーカー"
            aliases = ["joker", color]
        else:
            # card_C_10, card_H_A など
            parts = stem.split("_")  # ['card', 'C', '10']
            suit_key = parts[1]
            rank = parts[2]
            suit_label = SUIT_LABELS.get(suit_key, suit_key.lower())
            category = "Secvier/01.トランプ"
            aliases = [rank, suit_label, f"{suit_label}_{rank}"]
            aliases += RANK_ALIASES.get(rank, [])

        entries.append((png, zip_name, _make_entry(zip_name, emoji_name, category, aliases)))

    return entries


def _collect_alphanum() -> list[tuple[Path, str, dict]]:
    """dist/alphanum_dualmode/{variant}/char_*_128.png のエントリを収集する。"""
    entries: list[tuple[Path, str, dict]] = []

    for variant in sorted(VARIANT_NAMES):
        variant_dir = DIST / "alphanum_dualmode" / variant
        if not variant_dir.exists():
            continue
        vname = VARIANT_NAMES[variant]
        category = f"Secvier/02.英数字_{vname}"

        for png in sorted(variant_dir.glob("char_*_128.png")):
            char = png.stem.split("_")[1]  # char_A_128 → A
            zip_name = f"sv_{variant}_{char}.png"
            emoji_name = f"sv_{variant}_{char}"
            aliases = [char, char.lower(), variant, vname]
            entries.append((png, zip_name, _make_entry(zip_name, emoji_name, category, aliases)))

    return entries


def _collect_dice() -> list[tuple[Path, str, dict]]:
    """dist/dice/{variant}/*.png のエントリを収集する。"""
    entries: list[tuple[Path, str, dict]] = []

    for variant_dir in sorted((DIST / "dice").iterdir()):
        if not variant_dir.is_dir():
            continue
        variant = variant_dir.name
        vname = VARIANT_NAMES.get(variant, variant)
        category = f"Secvier/04.ダイス_{vname}"

        for png in sorted(variant_dir.glob("dice_*.png")):
            stem = png.stem  # e.g. dice_d6_3, dice_type_d4, dice_d10p_90
            suffix = stem[len("dice_"):]  # d6_3 / type_d4 / d10p_90
            zip_name = f"sv_dice_{variant}_{suffix}.png"
            emoji_name = f"sv_dice_{variant}_{suffix}"

            # エイリアス生成
            parts = suffix.split("_")  # ['d6', '3'] / ['type', 'd4'] / ['d10p', '90']
            dice_type = parts[0]  # d6 / type / d10p
            aliases = [dice_type, variant, vname]
            if len(parts) >= 2:
                aliases.append(parts[1])  # 出目値 or サブキー

            entries.append((png, zip_name, _make_entry(zip_name, emoji_name, category, aliases)))

    return entries


def _collect_suits() -> list[tuple[Path, str, dict]]:
    """dist/suits_dualmode/*_128.png のエントリを収集する。"""
    entries: list[tuple[Path, str, dict]] = []
    category = "Secvier/03.スートマーク"

    for png in sorted((DIST / "suits_dualmode").glob("*_128.png")):
        parts = png.stem.split("_")  # spade_blue_128 → ['spade', 'blue', '128']
        suit, color = parts[0], parts[1]
        zip_name = f"sv_suit_{suit}_{color}.png"
        emoji_name = f"sv_suit_{suit}_{color}"
        aliases = [suit, color]
        entries.append((png, zip_name, _make_entry(zip_name, emoji_name, category, aliases)))

    return entries


def _collect_mahjong() -> list[tuple[Path, str, dict]]:
    """dist/mahjong/misskey/mj_*.png のエントリを収集する。"""
    entries: list[tuple[Path, str, dict]] = []
    src_dir = DIST / "mahjong" / "misskey"
    suitjp = {"man": "萬子", "pin": "筒子", "sou": "索子"}
    cat = "Secvier/05.麻雀牌"
    for png in sorted(src_dir.glob("mj_*.png")):
        stem = png.stem
        name = f"sv_{stem}"
        zip_name = f"{name}.png"
        parts = stem.split("_")
        kind = parts[1]
        if kind in suitjp:
            n = parts[2]
            if len(parts) >= 4 and parts[3] == "red":
                category = cat + "/赤ドラ"
                aliases = ["akadora", "red5", "赤ドラ", kind, n]
            else:
                category = cat + "/" + suitjp[kind]
                aliases = [n, kind, suitjp[kind]]
        elif kind == "char":
            category = cat + "/字牌"
            aliases = [parts[2], "honor"]
        elif kind == "season":
            category = cat + "/季節牌"
            aliases = [parts[2], "season"]
        else:
            category = cat
            aliases = [stem]
        entries.append((png, zip_name, _make_entry(zip_name, name, category, aliases)))
    return entries


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    all_entries: list[tuple[Path, str, dict]] = []
    all_entries += _collect_cards()
    all_entries += _collect_alphanum()
    all_entries += _collect_dice()
    all_entries += _collect_suits()
    all_entries += _collect_mahjong()

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    zip_path = OUTPUT_DIR / f"secvier-misskey-{timestamp}.zip"

    now_jst = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT+0900 (JST)")
    meta: dict = {
        "metaVersion": 2,
        "host": "radiann6631.net",
        "exportedAt": now_jst,
        "emojis": [entry for _, _, entry in all_entries],
    }

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED) as zf:
        for src_path, zip_name, _ in all_entries:
            zf.write(src_path, zip_name)
        zf.writestr("meta.json", json.dumps(meta, ensure_ascii=False, indent=2))

    print(f"Created: {zip_path.name}")
    print(f"Total: {len(all_entries)} emojis")
    by_cat: dict[str, int] = {}
    for _, _, e in all_entries:
        cat = e["emoji"]["category"]
        by_cat[cat] = by_cat.get(cat, 0) + 1
    for cat in sorted(by_cat):
        print(f"  {cat}: {by_cat[cat]}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_category_previews.py — 絵文字カテゴリ別のプレビュー画像を生成する。

カテゴリ（英数字 / ダイス / トランプ / 麻雀牌）ごとに:
  docs/previews/{cat}_proto.png … 図柄一覧（全デザインのコンタクトシート）
  docs/previews/{cat}_emoji.png … 絵文字サンプル（暗背景＝Discord/ダーク, 明背景＝Misskey/ライト）

入力は dist/ 配下の生成済み PNG。依存: Pillow
"""
from __future__ import annotations
import glob
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.parent
DIST = ROOT / "dist"
OUT = ROOT / "docs" / "previews"

DARK = (54, 57, 63)       # Discord ダーク相当
LIGHT = (244, 244, 246)   # Misskey ライト相当
PANEL = (60, 62, 70)
TXT = (225, 225, 225)
TXT_D = (60, 60, 60)

VAR = {"seiyuu": "星幽", "suigyoku": "翠玉", "kougyoku": "紅玉",
       "hakuji": "白磁", "kokuji": "黒磁", "sakin": "砂金"}


def load(p, cell):
    im = Image.open(p).convert("RGBA")
    im.thumbnail((cell, cell), Image.LANCZOS)
    return im


def contact(paths, cols, cell, bg, label_fn=None, pad=8, lab=14, title=None):
    """paths を cols 列で並べたコンタクトシート画像を返す。"""
    n = len(paths)
    rows = (n + cols - 1) // cols
    th = 22 if title else 0
    tcol = TXT if bg in (PANEL, DARK) else TXT_D
    W = cols * (cell + pad) + pad
    H = th + rows * (cell + pad + lab) + pad
    s = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(s)
    if title:
        d.text((pad, 5), title, fill=tcol)
    for i, p in enumerate(paths):
        im = load(p, cell)
        r, c = divmod(i, cols)
        x = pad + c * (cell + pad) + (cell - im.width) // 2
        y = th + pad + r * (cell + pad + lab) + (cell - im.height) // 2
        s.paste(im, (x, y), im)
        if label_fn:
            d.text((pad + c * (cell + pad), th + pad + r * (cell + pad + lab) + cell + 1),
                   label_fn(p), fill=tcol)
    return s


def emoji_strip(dark_paths, light_paths, cell=132, labels=None):
    """暗背景・明背景の2段サンプル帯。"""
    def row(paths, bg):
        pad = 14
        W = len(paths) * (cell + pad) + pad
        H = cell + pad * 2 + 16
        s = Image.new("RGB", (W, H), bg)
        d = ImageDraw.Draw(s)
        tcol = TXT if bg == DARK else TXT_D
        for i, p in enumerate(paths):
            im = load(p, cell)
            x = pad + i * (cell + pad) + (cell - im.width) // 2
            y = pad + (cell - im.height) // 2
            s.paste(im, (x, y), im)
            if labels:
                d.text((pad + i * (cell + pad), H - 15), labels[i], fill=tcol)
        return s
    a = row(dark_paths, DARK)
    b = row(light_paths, LIGHT)
    s = Image.new("RGB", (max(a.width, b.width), a.height + b.height + 6), (28, 28, 30))
    s.paste(a, (0, 0))
    s.paste(b, (0, a.height + 6))
    return s


def stack_v(imgs, bg=(28, 28, 30), gap=8):
    W = max(i.width for i in imgs)
    H = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    s = Image.new("RGB", (W, H), bg)
    y = 0
    for im in imgs:
        s.paste(im, (0, y))
        y += im.height + gap
    return s


def first(globpat):
    g = sorted(glob.glob(globpat))
    return g[0] if g else None


# ─────────────────────────────────────────────────────────
def build_cards():
    mk = sorted(glob.glob(str(DIST / "cards" / "misskey" / "*.png")))
    proto = contact(mk, 9, 120, PANEL,
                    label_fn=lambda p: Path(p).stem.replace("card_", ""))
    proto.save(OUT / "cards_proto.png")
    samp = ["card_S_A", "card_H_10", "card_D_K", "card_C_7",
            "card_S_J", "card_H_Q", "card_joker_red", "card_suit_S"]
    dk = [str(DIST / "cards" / "discord" / f"{s}.png") for s in samp]
    lt = [str(DIST / "cards" / "misskey" / f"{s}.png") for s in samp]
    dk = [p for p in dk if os.path.exists(p)]
    lt = [p for p in lt if os.path.exists(p)]
    emoji_strip(dk, lt, labels=[Path(p).stem.replace("card_", "") for p in lt]).save(
        OUT / "cards_emoji.png")


def build_mahjong():
    mk = sorted(glob.glob(str(DIST / "mahjong" / "misskey" / "*.png")))
    proto = contact(mk, 9, 120, PANEL,
                    label_fn=lambda p: Path(p).stem.replace("mj_", ""))
    proto.save(OUT / "mahjong_proto.png")
    samp = ["mj_man_5", "mj_pin_9", "mj_sou_1", "mj_sou_8", "mj_char_east",
            "mj_char_chun", "mj_season_spring", "mj_man_5_red"]
    dk = [str(DIST / "mahjong" / "discord" / f"{s}.png") for s in samp]
    lt = [str(DIST / "mahjong" / "misskey" / f"{s}.png") for s in samp]
    emoji_strip(dk, lt, labels=[s.replace("mj_", "") for s in samp]).save(
        OUT / "mahjong_emoji.png")


CHARS = [str(c) for c in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"]


def build_alphanum():
    blocks = []
    for v in VAR:
        paths = []
        for ch in CHARS:
            p = DIST / "alphanum_dualmode" / v / f"char_{ch}_128.png"
            if p.exists():
                paths.append(str(p))
        if not paths:
            continue
        blk = contact(paths, 6, 84, PANEL,
                      label_fn=lambda p: Path(p).stem.split("_")[1],
                      title=f"{v}  {VAR[v]}")
        blocks.append(blk)
    # 2列に並べる
    cols = 2
    rows = (len(blocks) + cols - 1) // cols
    cw = max(b.width for b in blocks)
    ch = max(b.height for b in blocks)
    gap = 10
    sheet = Image.new("RGB", (cols * cw + gap * (cols + 1), rows * ch + gap * (rows + 1)),
                      (28, 28, 30))
    for i, b in enumerate(blocks):
        r, c = divmod(i, cols)
        sheet.paste(b, (gap + c * (cw + gap), gap + r * (ch + gap)))
    sheet.save(OUT / "alphanum_proto.png")
    # emoji: 各バリアントの "S" を 暗/明 で
    sample_chars = ["S", "V", "7"]
    dk, lt, labels = [], [], []
    for v in VAR:
        for ch in sample_chars:
            p = DIST / "alphanum_dualmode" / v / f"char_{ch}_128.png"
            if p.exists():
                dk.append(str(p))
                lt.append(str(p))
                labels.append(f"{ch}/{VAR[v]}")
    emoji_strip(dk, lt, cell=96, labels=labels).save(OUT / "alphanum_emoji.png")


GREEK_NAMES = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta",
               "Eta", "Theta", "Iota", "Kappa", "Lambda", "Mu",
               "Nu", "Xi", "Omicron", "Pi", "Rho", "Sigma",
               "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega"]


def build_greek():
    blocks = []
    for v in VAR:
        paths = []
        for nm in GREEK_NAMES:
            p = DIST / "alphanum_greek_dualmode" / v / f"char_{nm}_128.png"
            if p.exists():
                paths.append(str(p))
        if not paths:
            continue
        blk = contact(paths, 6, 84, PANEL,
                      label_fn=lambda p: Path(p).stem.split("_")[1],
                      title=f"{v}  {VAR[v]}")
        blocks.append(blk)
    if not blocks:
        return
    cols = 2
    rows = (len(blocks) + cols - 1) // cols
    cw = max(b.width for b in blocks)
    ch = max(b.height for b in blocks)
    gap = 10
    sheet = Image.new("RGB", (cols * cw + gap * (cols + 1), rows * ch + gap * (rows + 1)),
                      (28, 28, 30))
    for i, b in enumerate(blocks):
        r, c = divmod(i, cols)
        sheet.paste(b, (gap + c * (cw + gap), gap + r * (ch + gap)))
    sheet.save(OUT / "greek_proto.png")
    # emoji: 各バリアントの Α/Σ/Ω を 暗/明 で
    sample = ["Alpha", "Sigma", "Omega"]
    dk, lt, labels = [], [], []
    for v in VAR:
        for nm in sample:
            p = DIST / "alphanum_greek_dualmode" / v / f"char_{nm}_128.png"
            if p.exists():
                dk.append(str(p))
                lt.append(str(p))
                labels.append(f"{nm}/{VAR[v]}")
    if dk:
        emoji_strip(dk, lt, cell=96, labels=labels).save(OUT / "greek_emoji.png")


def build_dice():
    # proto: 1バリアント(seiyuu)の全出目
    seiyuu = sorted(glob.glob(str(DIST / "dice" / "seiyuu" / "*.png")))
    if not seiyuu:
        any_var = first(str(DIST / "dice" / "*"))
        seiyuu = sorted(glob.glob(os.path.join(any_var, "*.png"))) if any_var else []
    proto = contact(seiyuu, 12, 76, PANEL,
                    label_fn=lambda p: Path(p).stem.replace("dice_", ""),
                    title="ダイス（星幽 seiyuu）— 他バリアント: 翠玉/紅玉/砂金/白磁")
    proto.save(OUT / "dice_proto.png")
    # emoji: 代表的な出目を各バリアントで 暗/明
    picks = ["dice_d6_6", "dice_d20_20", "dice_d4_4", "dice_d8_8",
             "dice_d12_12", "dice_d10_5"]
    variants = list((DIST / "dice").glob("*"))
    variants = [v.name for v in variants if v.is_dir()]
    dk, lt, labels = [], [], []
    for i, pick in enumerate(picks):
        v = variants[i % len(variants)] if variants else "seiyuu"
        p = DIST / "dice" / v / f"{pick}.png"
        if p.exists():
            dk.append(str(p))
            lt.append(str(p))
            labels.append(pick.replace("dice_", "") + f"/{VAR.get(v, v)}")
    if dk:
        emoji_strip(dk, lt, cell=110, labels=labels).save(OUT / "dice_emoji.png")


HERO_ROWS = [
    ["cards/discord/card_S_A", "cards/discord/card_H_Q", "cards/discord/card_D_K",
     "cards/discord/card_C_7", "cards/discord/card_joker_red",
     "mahjong/discord/mj_man_5", "mahjong/discord/mj_pin_9",
     "mahjong/discord/mj_sou_1", "mahjong/discord/mj_char_east"],
    ["dice/seiyuu/dice_d20_20", "dice/kougyoku/dice_d6_6", "dice/suigyoku/dice_d12_12",
     "dice/sakin/dice_d10_5", "dice/hakuji/dice_d8_8",
     "alphanum_dualmode/seiyuu/char_S_128", "alphanum_dualmode/kougyoku/char_V_128",
     "alphanum_greek_dualmode/suigyoku/char_Alpha_128",
     "alphanum_greek_dualmode/sakin/char_Omega_128"],
]


def build_hero(cell: int = 128, pad: int = 14) -> None:
    """README 冒頭用の横長バナー（全カテゴリの代表絵文字）。"""
    rows = [[str(DIST / f"{n}.png") for n in r if (DIST / f"{n}.png").exists()]
            for r in HERO_ROWS]
    rows = [r for r in rows if r]
    if not rows:
        return
    cols = max(len(r) for r in rows)
    W = cols * (cell + pad) + pad
    H = len(rows) * (cell + pad) + pad
    s = Image.new("RGB", (W, H), (28, 28, 30))
    for r, paths in enumerate(rows):
        y0 = pad + r * (cell + pad)
        for c, p in enumerate(paths):
            im = load(p, cell)
            s.paste(im, (pad + c * (cell + pad) + (cell - im.width) // 2,
                         y0 + (cell - im.height) // 2), im)
    s.save(OUT / "hero.png")


GLYPHSET_BG = (28, 28, 30)
GLYPHSET_SUB = (130, 130, 138)
VAR_ORDER = ["seiyuu", "suigyoku", "kougyoku", "hakuji", "kokuji", "sakin"]


def _sections() -> list[tuple[str, list[str]]]:
    """収録一覧シートの (見出し, PNGパス列) を組み立てる。"""
    def g(pat):
        return sorted(glob.glob(str(DIST / pat)))

    def variants(pat, names):
        return [str(DIST / pat.format(v=v)) for v in names
                if (DIST / pat.format(v=v)).exists()]

    dice_v = [v for v in VAR_ORDER if (DIST / "dice" / v).is_dir()]
    an_v = [v for v in VAR_ORDER if (DIST / "alphanum_dualmode" / v).is_dir()]
    gr_v = [v for v in VAR_ORDER if (DIST / "alphanum_greek_dualmode" / v).is_dir()]
    romaji = ", ".join
    return [
        ("Playing Cards  x2 platforms (Discord 256x256 / Misskey 256x320)",
         g("cards/misskey/*.png")),
        ("Suit Marks  dual-mode (light / dark)", g("suits_dualmode/*_512.png")),
        ("Mahjong Tiles  x2 platforms", g("mahjong/misskey/*.png")),
        (f"Dice  D4-D20 + D%  [{dice_v[0] if dice_v else '-'}]",
         g(f"dice/{dice_v[0]}/*.png") if dice_v else []),
        (f"Dice variants  {romaji(dice_v)}",
         variants("dice/{v}/dice_d20_20.png", dice_v)),
        (f"Alphanumeric  A-Z 0-9  dual-mode  [{an_v[0] if an_v else '-'}]",
         g(f"alphanum_dualmode/{an_v[0]}/char_*_512.png") if an_v else []),
        (f"Alphanumeric variants  {romaji(an_v)}",
         variants("alphanum_dualmode/{v}/char_S_512.png", an_v)),
        (f"Greek  Alpha-Omega  dual-mode  [{gr_v[2] if len(gr_v) > 2 else '-'}]",
         g(f"alphanum_greek_dualmode/{gr_v[2]}/char_*_512.png") if len(gr_v) > 2 else []),
        (f"Greek variants  {romaji(gr_v)}",
         variants("alphanum_greek_dualmode/{v}/char_Omega_512.png", gr_v)),
    ]


def build_glyphset(cell: int = 54, pad: int = 24, gap: int = 7, width: int = 1240) -> None:
    """収録内容の一覧シート（カテゴリ別の全図柄＋バリアント見本）。"""
    secs = [(label, paths) for label, paths in _sections() if paths]
    if not secs:
        return
    title_f, head_f, note_f = (ImageFont.load_default(size=s) for s in (34, 20, 15))
    head_h, sec_gap = 34, 26

    def flow(sheet, draw, paths, y):
        x = pad
        for p in paths:
            im = load(p, cell)
            if x > pad and x + im.width > pad + width:
                x, y = pad, y + cell + gap
            if sheet is not None:
                sheet.paste(im, (x, y + (cell - im.height) // 2), im)
            x += im.width + gap
        return y + cell

    def render(sheet):
        draw = ImageDraw.Draw(sheet if sheet else Image.new("RGB", (1, 1)))
        y = pad
        if sheet:
            draw.text((pad, y), "Secvier  /  custom emoji set", font=title_f, fill=TXT)
            draw.text((pad, y + 42),
                      "playing cards / suit marks / mahjong tiles / dice / "
                      "alphanumeric / greek  -  gem-styled variants: "
                      + ", ".join(VAR_ORDER),  # 既定フォントは日本語不可のため romaji のみ
                      font=note_f, fill=GLYPHSET_SUB)
        y += 74
        for label, paths in secs:
            if sheet:
                draw.text((pad, y), f"{label}  {len(paths)}", font=head_f,
                          fill=GLYPHSET_SUB)
            y = flow(sheet, draw, paths, y + head_h) + sec_gap
        return y - sec_gap + pad

    height = render(None)
    sheet = Image.new("RGB", (width + pad * 2, height), GLYPHSET_BG)
    render(sheet)
    sheet.save(OUT / "glyphset.png")
    print("glyphset ->", OUT / "glyphset.png", sheet.size)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    build_cards()
    build_mahjong()
    build_alphanum()
    build_greek()
    build_dice()
    build_hero()
    build_glyphset()
    print("previews ->", OUT)
    for p in sorted(OUT.glob("*.png")):
        print("  ", p.name, Image.open(p).size)


if __name__ == "__main__":
    main()

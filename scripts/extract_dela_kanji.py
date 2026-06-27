#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""extract_dela_kanji.py — 字牌・季節牌中央用に Dela Gothic One（幾何学的・Secvier に近い字形）
の漢字アウトラインを src/noto_mahjong/kanji_{name}.svg として書き出す。

フォントは assets/fonts/delagothicone/ に同梱したサブセット(woff2)を使用。
Dela Gothic One: SIL Open Font License 1.1 (c) 2020 The Dela Gothic Project Authors。
OFL は「フォントで作成した文書」には及ばないため、出力 SVG は CC BY 4.0 で配布可。
viewBox 0 0 1000 1000・中央寄せ・fill 無し（埋め込み側で着色）。
"""
import os
import glob
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "noto_mahjong")
FONT_DIR = os.path.join(ROOT, "assets", "fonts", "delagothicone")

CHARS = {"east": "東", "south": "南", "west": "西", "north": "北",
         "chun": "中", "hatsu": "發",
         "spring": "春", "summer": "夏", "autumn": "秋", "winter": "冬"}


def build_cpmap():
    cpfile = {}
    for f in sorted(glob.glob(os.path.join(FONT_DIR, "*.woff2"))):
        try:
            cm = TTFont(f).getBestCmap()
            for cp in cm:
                cpfile.setdefault(cp, f)
        except Exception:
            pass
    return cpfile


def main():
    os.makedirs(OUT, exist_ok=True)
    cpfile = build_cpmap()
    for name, ch in CHARS.items():
        f = cpfile[ord(ch)]
        font = TTFont(f)
        gs = font.getGlyphSet()
        gname = font.getBestCmap()[ord(ch)]
        bp = BoundsPen(gs)
        gs[gname].draw(bp)
        xmin, ymin, xmax, ymax = bp.bounds
        pen = SVGPathPen(gs)
        gs[gname].draw(pen)
        d = pen.getCommands()
        box, margin = 1000.0, 80.0
        scale = (box - 2 * margin) / max(xmax - xmin, ymax - ymin)
        cx = (xmin + xmax) / 2.0
        cy = (ymin + ymax) / 2.0
        tx = box / 2.0 - cx * scale
        ty = box / 2.0 + cy * scale
        svg = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" '
               'width="1000" height="1000">\n'
               '  <title>Dela Gothic One %s (%s)</title>\n'
               '  <g transform="translate(%.3f,%.3f) scale(%.5f,%.5f)">'
               '<path d="%s"/></g>\n</svg>\n'
               % (ch, name, tx, ty, scale, -scale, d))
        with open(os.path.join(OUT, "kanji_%s.svg" % name), "w", encoding="utf-8") as fh:
            fh.write(svg)
        print("wrote kanji_%s.svg (%s)" % (name, ch))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_mahjong_proto.py — Secvier 麻雀牌 プロトタイプ SVG 生成（改訂版）

仕様（ラジアン／柏木主税 指定 / 第2回添削反映）:
  * アスペクト比 5:7、外枠はトランプ（♦）に寄せた白角丸フレーム
  * 全牌に右上・左下の隅インデックス（番号/字＋SV(萬)/I(索)/O(筒) マーク、
    左下は 180°回転）をトランプと同様に付与
  * 萬子 1-9 : 中央＝大きな数字（黒・一回り拡大）＋下段 "SV"（赤）
  * 筒子 1-9 : Secvier "O" をリメイクした回転対称コインを、忠実な配置・配色で
  * 索子 2-9 : Secvier "I" をリメイクした長さ方向対称の竹を、忠実な配置・配色で
  * 索子 1   : 中央に Noto 一索（孔雀）＋隅インデックス 1 / I
  * 風牌     : 隅＝E/S/W/N、中央＝Noto CJK 漢字（東南西北・紺）
  * 三元牌   : 發＝隅 H(右上)/T(左下)・中央 發(緑) / 中＝隅 G(右上)/B(左下)・中央 中(赤)
  * 白       : 豆腐記号なし。外枠のみ
  * 季節牌   : 中央＝Noto 季節イラスト、英単語を Joker 風に縦書きで右上・左下
  * 赤ドラ   : 伍萬・伍索・伍筒。印字を鮮やかな赤（紅玉ベースの明色）で

配色（既存バリアント由来）: 白下地 / 赤(紅玉) 緑(翠玉) 紺(星幽)
著作権者: RadianN_kswg / ラジアン（柏木主税） / CC BY 4.0
Noto 素材: Noto Emoji(Apache-2.0) / Noto Serif CJK(OFL-1.1), Google Inc.
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALNUM_DIR = os.path.join(ROOT, "src", "alphanum")
NOTO_DIR = os.path.join(ROOT, "src", "noto_mahjong")
OUT_DIR = os.path.join(ROOT, "src", "mahjong")
PARTS_DIR = os.path.join(OUT_DIR, "parts")

# ── キャンバス（5:7） ──
W, H = 360, 504
RCX, RCY = W / 2.0, H / 2.0          # 180°回転中心

# ── 配色 ──
INK_RED   = "#B81430"   # 紅玉 deep
INK_GREEN = "#218A48"   # 翠玉 deep
INK_NAVY  = "#26346F"   # 星幽寄りの紺（＝筒子の青）
INK_INK   = "#1E1E2A"   # 黒に近い字色
NODE_GRN  = "#145C34"   # 竹節（濃緑）
RED_DORA  = "#EC1B3A"   # 赤ドラ用 鮮やかな赤（紅玉を明色化）
NODE_DORA = "#9E0E26"

P_G, P_B, P_R = INK_GREEN, INK_NAVY, INK_RED   # 筒子 緑/青/赤

CREDIT = "RadianN_kswg / ラジアン（柏木主税） CC BY 4.0"

# ─────────────────────────────────────────────────────────
_glyph_cache = {}


def glyph_inner(char, color):
    if char not in _glyph_cache:
        with open(os.path.join(ALNUM_DIR, "char_%s.svg" % char), encoding="utf-8") as f:
            svg = f.read()
        m = re.search(r'(<g\s+transform="matrix[^>]*>.*?</g>)', svg, re.S)
        _glyph_cache[char] = m.group(1)
    return _glyph_cache[char].replace('fill="#000000"', 'fill="%s"' % color)


def place_glyph(char, cx, cy, size, color, sy_ratio=1.0):
    unit = glyph_inner(char, color)
    sx = size / 512.0
    syy = sx * sy_ratio
    x = cx - size / 2.0
    y = cy - (512.0 * syy) / 2.0
    return ('<g transform="translate(%.2f,%.2f) scale(%.4f,%.4f)">%s</g>'
            % (x, y, sx, syy, unit))


# ── 任意 SVG（Noto emoji / 抽出漢字）を入れ子で配置 ──
_svg_cache = {}


def embed_svg(fname, x, y, w, h, fill=None):
    if fname not in _svg_cache:
        with open(os.path.join(NOTO_DIR, fname), encoding="utf-8") as f:
            c = f.read()
        c = re.sub(r'<\?xml.*?\?>', '', c, flags=re.S)
        c = re.sub(r'<!--.*?-->', '', c, flags=re.S)
        vb = re.search(r'viewBox="([\d.\s-]+)"', c).group(1)
        inner = re.search(r'<svg[^>]*>(.*)</svg>', c, re.S).group(1).strip()
        _svg_cache[fname] = (vb, inner)
    vb, inner = _svg_cache[fname]
    nested = ('<svg xmlns:xlink="http://www.w3.org/1999/xlink" '
              'x="%.2f" y="%.2f" width="%.2f" height="%.2f" viewBox="%s">%s</svg>'
              % (x, y, w, h, vb, inner))
    if fill:
        return '<g fill="%s">%s</g>' % (fill, nested)
    return nested


# ─────────────────────────────────────────────────────────
#  Secvier 由来 最小部品
# ─────────────────────────────────────────────────────────
def place_O(cx, cy, size, color):
    """O グリフの輪の中心が正確に (cx,cy) へ来るよう配置（縦の字面オフセット補正）。"""
    return place_glyph("O", cx, cy + 0.10 * size, size, color)


def pin_coin(cx, cy, size, color):
    """O グリフ由来の回転対称コイン（輪＋同心の中心ピップ）。"""
    return (place_O(cx, cy, size, color)
            + '<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/>'
            % (cx, cy, size * 0.12, color))


def pin_one(cx, cy):
    """一筒：同心の多重リング（紺/赤/紺）。"""
    return (place_O(cx, cy, 168, P_B)
            + place_O(cx, cy, 104, P_R)
            + '<circle cx="%.2f" cy="%.2f" r="22" fill="%s"/>' % (cx, cy, P_B))


def sou_stick(cx, cy, w, h, color, node, angle=0):
    """Secvier "I"（端セリフ＝竹節）を踏襲した『長さ方向対称』の竹。
    太い竹幹＋上下のセリフ節＋中央の節帯。angle で傾ける（W/M 配置用）。"""
    def rrect(x, y, ww, hh, col):
        return ('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" fill="%s"/>'
                % (x, y, ww, hh, min(ww, hh) * 0.5, col))
    sw = w * 0.60                       # 竹幹幅
    cap = h * 0.13                      # セリフ節（上下）の高さ
    g = rrect(cx - sw / 2, cy - h / 2, sw, h, color)                 # 竹幹
    g += rrect(cx - w / 2, cy - h / 2, w, cap, color)               # 上セリフ節
    g += rrect(cx - w / 2, cy + h / 2 - cap, w, cap, color)         # 下セリフ節
    g += rrect(cx - w * 0.5, cy - h * 0.04, w, h * 0.08, node)      # 中央節帯
    if angle:
        return '<g transform="rotate(%.1f,%.2f,%.2f)">%s</g>' % (angle, cx, cy, g)
    return g


# ─────────────────────────────────────────────────────────
#  外枠 / ドキュメント
# ─────────────────────────────────────────────────────────
def frame():
    # 白牌でも視認できるよう太めの枠＋内側キーライン
    return ('<rect x="5" y="5" width="350" height="494" rx="32" '
            'fill="#FAFAFA" stroke="#AFAFAF" stroke-width="9"/>'
            '<rect x="20" y="20" width="320" height="464" rx="22" '
            'fill="none" stroke="#CFCFCF" stroke-width="4"/>')


def svg_doc(title, body):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'width="%d" height="%d">\n  <title>%s</title>\n  <desc>%s</desc>\n'
            '  %s\n  %s\n</svg>\n'
            % (W, H, W, H, title, CREDIT, frame(), body))


def rot_bl(content_at_tr):
    """右上座標で描いた内容を 180°回転して左下に置く。"""
    return '<g transform="rotate(180,%.1f,%.1f)">%s</g>' % (RCX, RCY, content_at_tr)


# ── 隅インデックス ──
def corner_number(rank, mark, color):
    tr = place_glyph(rank, 300, 84, 66, color)
    if len(mark) == 1:
        tr += place_glyph(mark, 300, 142, 54, color)
    else:                                   # "SV"
        tr += place_glyph(mark[0], 282, 144, 44, color)
        tr += place_glyph(mark[1], 318, 144, 44, color)
    return tr + rot_bl(tr)


def corner_letters(tr_letter, bl_letter, color):
    tr = place_glyph(tr_letter, 300, 96, 82, color)
    bl = rot_bl(place_glyph(bl_letter, 300, 96, 82, color))
    return tr + bl


def corner_word(word, color):
    # 横書きを90°回転して縦書きに（Joker風）。右端は上から/左端は下から読める
    n = len(word)
    step, size = 34, 34
    row = "".join(place_glyph(word[i], (i - (n - 1) / 2.0) * step, 0, size, color)
                  for i in range(n))
    tr = '<g transform="translate(330,192) rotate(90)">%s</g>' % row
    return tr + rot_bl(tr)


# ─────────────────────────────────────────────────────────
#  数牌の配置（忠実）
# ─────────────────────────────────────────────────────────
GX0, GX1, GY0, GY1 = 86, 274, 120, 388


def gp(nx, ny):
    return (GX0 + nx * (GX1 - GX0), GY0 + ny * (GY1 - GY0))


# 筒子: (nx, ny, color)
PIN = {
    2: [(.5, .18, P_B), (.5, .82, P_B)],
    3: [(.20, .16, P_B), (.5, .5, P_R), (.80, .84, P_B)],   # 紺赤紺 右肩下がり
    4: [(.28, .24, P_B), (.72, .24, P_B), (.28, .76, P_B), (.72, .76, P_B)],
    5: [(.26, .22, P_B), (.74, .22, P_B), (.5, .5, P_R),
        (.26, .78, P_B), (.74, .78, P_B)],
    6: [(.28, .17, P_B), (.72, .17, P_B), (.28, .5, P_R), (.72, .5, P_R),
        (.28, .83, P_R), (.72, .83, P_R)],
    7: [(.20, .12, P_B), (.5, .26, P_B), (.80, .40, P_B),   # 上段3つ紺 右肩下がり
        (.30, .72, P_R), (.70, .72, P_R), (.30, .92, P_R), (.70, .92, P_R)],
    8: [(.30, .11, P_B), (.70, .11, P_B), (.30, .37, P_B), (.70, .37, P_B),
        (.30, .63, P_R), (.70, .63, P_R), (.30, .89, P_R), (.70, .89, P_R)],
    9: [(.20, .18, P_B), (.5, .18, P_B), (.80, .18, P_B),
        (.20, .5, P_R), (.5, .5, P_R), (.80, .5, P_R),
        (.20, .82, P_B), (.5, .82, P_B), (.80, .82, P_B)],
}
PIN_SIZE = {2: 124, 3: 120, 4: 118, 5: 108, 6: 104, 7: 92, 8: 90, 9: 92}

# 索子: (nx, ny[, "red"])。色は基本緑、"red" 指定のみ赤。
SOU = {
    2: [(.5, .26), (.5, .74)],
    3: [(.5, .20), (.32, .76), (.68, .76)],
    4: [(.30, .26), (.70, .26), (.30, .74), (.70, .74)],
    5: [(.28, .24), (.72, .24), (.5, .5, "red"), (.28, .76), (.72, .76)],
    6: [(.30, .19), (.70, .19), (.30, .5), (.70, .5), (.30, .81), (.70, .81)],
    # 七索: 上段1本(赤) + 下段 3列×2行(緑)
    7: [(.5, .11, "red"),
        (.22, .55), (.5, .55), (.78, .55), (.22, .85), (.5, .85), (.78, .85)],
    # 九索: 3×3、中列(真ん中の縦列)は赤
    9: [(.22, .19), (.5, .19, "red"), (.78, .19),
        (.22, .5), (.5, .5, "red"), (.78, .5),
        (.22, .81), (.5, .81, "red"), (.78, .81)],
}
SOU_DIM = {2: (58, 116), 3: (50, 98), 4: (50, 98), 5: (46, 92),
           6: (42, 80), 7: (38, 64), 8: (34, 60), 9: (42, 78)}


# ─────────────────────────────────────────────────────────
#  各カテゴリ
# ─────────────────────────────────────────────────────────
def tile_man(n, dora=False):
    col_num = RED_DORA if dora else INK_INK
    col_sv = RED_DORA if dora else INK_RED
    body = [corner_number(str(n), "SV", RED_DORA if dora else INK_INK)]
    # 他カテゴリの柄サイズに合わせて全体縮小（比率・配置は維持）
    body.append(place_glyph(str(n), RCX, 206, 150, col_num))
    body.append(place_glyph("S", RCX - 42, 330, 112, col_sv))
    body.append(place_glyph("V", RCX + 42, 330, 112, col_sv))
    tag = "man %d%s" % (n, " (red dora)" if dora else "")
    return svg_doc("Secvier mahjong " + tag, "".join(body))


def tile_pin(n, dora=False):
    body = []
    icol = RED_DORA if dora else INK_INK
    body.append(corner_number(str(n), "O", icol))
    if n == 1:
        body.append(pin_one(*gp(.5, .5)))
    else:
        size = PIN_SIZE[n]
        for nx, ny, col in PIN[n]:
            cx, cy = gp(nx, ny)
            body.append(pin_coin(cx, cy, size, RED_DORA if dora else col))
    tag = "pin %d%s" % (n, " (red dora)" if dora else "")
    return svg_doc("Secvier mahjong " + tag, "".join(body))


def tile_sou(n, dora=False):
    if n == 1:
        return tile_sou_one()
    icol = RED_DORA if dora else INK_INK
    body = [corner_number(str(n), "I", icol)]
    col0 = RED_DORA if dora else INK_GREEN
    node0 = NODE_DORA if dora else NODE_GRN
    if n == 8:
        # 八索: 左右端4本=垂直 / 中の4本=より斜め。竹は四索並みに伸長
        w, h = 48, 96
        xs = (.13, .40, .60, .87)
        top_ang = (0, 28, -28, 0)
        bot_ang = (0, -28, 28, 0)
        for x, a in zip(xs, top_ang):
            cx, cy = gp(x, .27)
            body.append(sou_stick(cx, cy, w, h, col0, node0, angle=a))
        for x, a in zip(xs, bot_ang):
            cx, cy = gp(x, .73)
            body.append(sou_stick(cx, cy, w, h, col0, node0, angle=a))
    else:
        w, h = SOU_DIM[n]
        for spec in SOU[n]:
            nx, ny = spec[0], spec[1]
            is_red = dora or (len(spec) > 2 and spec[2] == "red")
            col = RED_DORA if is_red else INK_GREEN
            node = NODE_DORA if is_red else NODE_GRN
            cx, cy = gp(nx, ny)
            body.append(sou_stick(cx, cy, w, h, col, node))
    tag = "sou %d%s" % (n, " (red dora)" if dora else "")
    return svg_doc("Secvier mahjong " + tag, "".join(body))


def tile_sou_one():
    # 一索: FluffyStuff(CC0) の忠実な麻雀牌「一索」の鳥イラスト（viewBox 300x400）
    body = [corner_number("1", "I", INK_INK)]
    body.append(embed_svg("ichisou_bird_cc0.svg", 78, 100, 204, 272))
    return svg_doc("Secvier mahjong sou 1 (ichisou)", "".join(body))


def tile_wind(label, letter, kanji):
    body = [corner_letters(letter, letter, INK_NAVY)]
    body.append(embed_svg(kanji, 76, 150, 208, 208, fill=INK_NAVY))
    return svg_doc("Secvier mahjong wind %s (%s)" % (label, letter), "".join(body))


def tile_dragon(label, tr, bl, kanji, color):
    body = [corner_letters(tr, bl, color)]
    body.append(embed_svg(kanji, 76, 150, 208, 208, fill=color))
    return svg_doc("Secvier mahjong dragon %s (%s/%s)" % (label, tr, bl), "".join(body))


def tile_haku():
    return svg_doc("Secvier mahjong dragon haku (blank)", "")


SEASON = {
    # 絵柄は xhokir/riichi-mahjong-tiles の季節牌(花)CC BY 4.0。Season1-4=春夏秋冬
    "spring": ("SPRING", "kanji_spring.svg", "season1_cc_by.svg", INK_RED),
    "summer": ("SUMMER", "kanji_summer.svg", "season2_cc_by.svg", INK_GREEN),
    "autumn": ("AUTUMN", "kanji_autumn.svg", "season3_cc_by.svg", INK_RED),
    "winter": ("WINTER", "kanji_winter.svg", "season4_cc_by.svg", INK_NAVY),
}


def tile_season(key):
    # 季節イラスト（主役）＋ 季節漢字を絵柄右上に赤（中と同色）＋ Joker 風縦書き英単語
    word, kanji, noto, color = SEASON[key]
    body = [corner_word(word, color)]
    body.append(embed_svg(noto, 78, 100, 204, 272))                 # 花（一索の鳥と同位置・同サイズ）
    body.append(embed_svg(kanji, 246, 134, 72, 72, fill=INK_RED))   # 季節漢字 赤・絵柄右上
    return svg_doc("Secvier mahjong season %s (%s)" % (key, word), "".join(body))


# ─────────────────────────────────────────────────────────
#  最小部品
# ─────────────────────────────────────────────────────────
def part_doc(title, vbw, vbh, body):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'width="%d" height="%d">\n  <title>%s</title>\n  <desc>%s</desc>\n'
            '  %s\n</svg>\n' % (vbw, vbh, vbw, vbh, title, CREDIT, body))


def write_parts():
    os.makedirs(PARTS_DIR, exist_ok=True)
    with open(os.path.join(PARTS_DIR, "sou_stick.svg"), "w", encoding="utf-8") as f:
        f.write(part_doc("Secvier sou bamboo (sym., from I)", 120, 360,
                         sou_stick(60, 180, 60, 300, INK_GREEN, NODE_GRN)))
    with open(os.path.join(PARTS_DIR, "pin_coin.svg"), "w", encoding="utf-8") as f:
        f.write(part_doc("Secvier pin coin (rot.sym., from O)", 200, 200,
                         pin_coin(100, 100, 180, INK_NAVY)))
    lc = {"E": INK_NAVY, "S": INK_NAVY, "W": INK_NAVY, "N": INK_NAVY,
          "H": INK_GREEN, "T": INK_GREEN, "G": INK_RED, "B": INK_RED}
    for ch, col in lc.items():
        with open(os.path.join(PARTS_DIR, "letter_%s.svg" % ch), "w", encoding="utf-8") as f:
            f.write(part_doc("Secvier letter %s" % ch, 200, 200,
                             place_glyph(ch, 100, 100, 170, col)))


# ─────────────────────────────────────────────────────────
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    written = []

    def dump(name, content):
        with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
            f.write(content)
        written.append(name)

    for n in range(1, 10):
        dump("mj_man_%d.svg" % n, tile_man(n))
        dump("mj_pin_%d.svg" % n, tile_pin(n))
        dump("mj_sou_%d.svg" % n, tile_sou(n))

    for label, letter, kanji in [("east", "E", "kanji_east.svg"),
                                 ("south", "S", "kanji_south.svg"),
                                 ("west", "W", "kanji_west.svg"),
                                 ("north", "N", "kanji_north.svg")]:
        dump("mj_char_%s.svg" % label, tile_wind(label, letter, kanji))

    dump("mj_char_hatsu.svg", tile_dragon("hatsu", "H", "T", "kanji_hatsu.svg", INK_GREEN))
    dump("mj_char_chun.svg", tile_dragon("chun", "G", "B", "kanji_chun.svg", INK_RED))
    dump("mj_char_haku.svg", tile_haku())

    for key in ("spring", "summer", "autumn", "winter"):
        dump("mj_season_%s.svg" % key, tile_season(key))

    dump("mj_man_5_red.svg", tile_man(5, dora=True))
    dump("mj_pin_5_red.svg", tile_pin(5, dora=True))
    dump("mj_sou_5_red.svg", tile_sou(5, dora=True))

    write_parts()
    print("written %d tiles + parts" % len(written))


if __name__ == "__main__":
    main()

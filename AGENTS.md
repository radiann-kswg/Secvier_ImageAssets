# AGENTS.md — Secvier ImageAssets 共通エージェント指示書

このファイルは **Codex**、**Claude Code**、**GitHub Copilot** が共有する
Secvier リポジトリ固有指示の **唯一の正（SSOT）** です。
`CLAUDE.md` は `@AGENTS.md` の参照入口であり、詳細指示を重複記載しません。

---

## プロジェクト概要

各種SNSおよびチャットサービス（Discord・Misskeyなど）向けに、
**RadianN_kswg / ラジアン（柏木主税）による独自フォント Secvier** と
**Claude による Agent 機能**、およびその他のアセット（Noto Emoji など）によって制作された
カスタム絵文字アセット群リポジトリです。

**著作権者**: RadianN_kswg / ラジアン（柏木主税） / **ライセンス**: CC BY 4.0

| カテゴリ       | 内容                                                          | 枚数                          |
| -------------- | ------------------------------------------------------------- | ----------------------------- |
| トランプ       | ♠♥♦♣ × A,2–10,J,C,Q,K + ジョーカー黒・赤 + スート単体         | 62枚（Discord/Misskey各対応） |
| ダイス         | D4 / D6(×出目) / D8 / D10(×出目) / D%(テンズテン) / D12 / D20 | 5バリアント                   |
| 英数字         | A–Z（大文字） / 0–9（デュアルモード対応）                     | 6バリアント × 36枚            |
| ギリシャ文字   | Α–Ω（大文字, デュアルモード対応）※Secvier v0.1-beta で追加    | 6バリアント × 24枚            |
| スートマーク   | ♠♥♦♣ 透過デュアルモード版（各2色）※フォント収録グリフ由来     | 8種                           |
| 麻雀牌         | 萬子1–9 / 筒子1–9 / 索子1–9 / 字牌7枚（東南西北中發白）+ 季節牌4枚 + 赤ドラ3枚 | 41枚（Discord/Misskey各対応） |

---

## 権限・ライセンス（最優先）

- **著作権者**：RadianN_kswg / ラジアン（柏木主税）
- **ライセンス**：CC BY 4.0
- Secvierフォントのグリフは著作者の独自創作物。
  第三者フォント・商用グリフのグリフパスを流用することを**絶対に行わないこと**。
- すべての出力ファイルにクレジット属性を保持すること。
- `_original-fonts/` 内のファイルは**読み取り専用**。ビルドスクリプトから変更・削除禁止。

---

## ディレクトリ構成

```
Secvier_ImageAssets/
├── AGENTS.md                   ← 本ファイル（エージェント共通指示書）
├── CLAUDE.md                   ← Claude Code 互換入口（@AGENTS.md のみ）
├── .github/
│   └── copilot-instructions.md ← GitHub Copilot 向け補足
├── assets/
│   └── fonts/
│       ├── Secvier.otf         ← ビルド参照フォント（_original-fontsのコピー）
│       └── delagothicone/      ← Dela Gothic One サブセット（字牌・季節牌漢字用、SIL OFL 1.1）
├── src/
│   ├── alphanum/               ← 英数字 SVGソース（アウトライン化済み）
│   ├── alphanum_greek/         ← ギリシャ大文字 SVGソース（Α–Ω, アウトライン化済み）
│   ├── cards/                  ← トランプ SVGソース（v1 旧実装）
│   ├── suits/                  ← スートマーク SVG（フォント収録グリフ由来, 天地中央）
│   ├── noto_cards/             ← Noto Emoji コートカード SVG（原本、読み取り専用）
│   ├── noto_cache/             ← Noto SVG キャッシュ（bindfs 回避用）
│   ├── noto_svg/               ← Noto SVG 補完キャッシュ
│   ├── dice/                   ← ダイス SVGソース
│   ├── mahjong/                ← 麻雀牌 SVGソース（牌本体 + parts/）
│   │   └── parts/              ← 筒子コイン・索子竹・字牌文字など最小部品
│   ├── noto_mahjong/           ← 麻雀牌用 漢字・季節牌 外部SVGアセット
│   ├── ext_mahjong/            ← 外部素材（CC0/CC BY）: 一索鳥・季節牌花絵柄
│   └── templates/              ← ベーステンプレートSVG
├── dist/
│   ├── cards/
│   │   ├── discord/            ← Discord向け 256×256px トランプ PNG
│   │   └── misskey/            ← Misskey向け 256×320px トランプ PNG
│   ├── dice/{variant}/         ← ダイス PNG（バリアント別サブディレクトリ）
│   ├── alphanum/{variant}/     ← 英数字 PNG（バリアント別、通常版）
│   ├── alphanum_greek/{variant}/ ← ギリシャ大文字 PNG（バリアント別、枠付き通常版）
│   ├── alphanum_dualmode/{variant}/ ← 英数字 PNG（透過デュアルモード版）
│   ├── alphanum_greek_dualmode/{variant}/ ← ギリシャ大文字 PNG（透過デュアルモード版）
│   ├── suits_dualmode/         ← スートマーク 透過デュアルモード版
│   └── mahjong/
│       ├── discord/            ← Discord向け 256×256px 麻雀牌 PNG
│       └── misskey/            ← Misskey向け 256×320px 麻雀牌 PNG
├── svg2png/                    ← 黒字・白背景マスクPNG（render_svg2png.py が生成）
│   ├── alphanum/               ← char_{A-Z,0-9}.svg を単純PNG変換したもの
│   ├── alphanum_greek/         ← char_{Alpha–Omega}.svg を単純PNG変換したもの
│   └── suits/                  ← スートマーク SVG の単純PNG変換
├── scripts/
│   ├── generate_cards_v2.py    ← トランプ絵文字生成【現行メイン】
│   ├── generate_cards_dualmode.py ← Discord/Misskey向けトランプ生成【現行メイン】
│   ├── generate_all_v3.py      ← ダイス・英数字一括生成【現行メイン】
│   ├── generate_dualmode.py    ← 英数字・スートマーク デュアルモード生成【現行メイン】
│   ├── generate_dice_faces.py  ← ダイス出目イラスト生成
│   ├── generate_mahjong_proto.py ← 麻雀牌 SVG生成【現行メイン】
│   ├── generate_mahjong_emoji.py ← 麻雀牌 Discord/Misskey向けPNG生成【現行メイン】
│   ├── extract_dela_kanji.py   ← Dela Gothic One から字牌・季節牌漢字を抽出
│   ├── build_misskey_zip.py    ← Misskey一括インポート用zip生成
│   ├── inspect_font.py         ← グリフ検査 → docs/glyph_map.txt
│   ├── extract_glyphs.py       ← フォントアウトライン → src/alphanum/・alphanum_greek/ SVG（--charset）
│   ├── extract_suits.py        ← フォント収録スートグリフ → src/suits/ SVG（天地中央）
│   ├── render_svg2png.py       ← src SVG → svg2png/ 黒字白背景マスクPNG
│   ├── render_svg.py           ← SVG合成ユーティリティ
│   ├── export_png.py           ← SVG → PNG変換
│   └── build.py                ← 全カテゴリ一括ビルド
├── docs/
│   ├── glyph_map.txt           ← inspect_font.py が自動生成
│   ├── cards_dualmode_spec.md  ← Discord/Misskey向けトランプ仕様書
│   └── mahjong_proto_spec.md   ← 麻雀牌 SVG仕様書（外部素材ライセンスを含む）
├── proposals_dualmode/         ← デュアルモード初期デザイン提案（作業履歴）
├── proposals_dualmode_v2/      ← デュアルモード v2 デザイン提案（作業履歴）
├── _exported-dist/             ← エクスポートzip格納（.gitignore対象）
├── _original-fonts/            ← 原本（読み取り専用）
├── requirements.txt
└── LICENSE
```

---

## ファイル命名規則

| カテゴリ                   | 命名パターン                       | 例                                         |
| -------------------------- | ---------------------------------- | ------------------------------------------ |
| 英数字                     | `char_{文字}.svg`                  | `char_A.svg`, `char_0.svg`                 |
| トランプ                   | `card_{suit}_{value}.svg`          | `card_spade_A.svg`, `card_joker_black.svg` |
| ダイス                     | `dice_{type}_{face}.svg`           | `dice_d6_6.svg`                            |
| 麻雀牌                     | `mj_{suit}_{id}.svg`               | `mj_man_1.svg`, `mj_char_east.svg`         |
| PNG出力（dist）            | `{stem}_72.png` / `{stem}_512.png` | `char_A_512.png`                           |
| SVG→PNG単純変換（svg2png） | `{stem}.png`                       | `char_A.png`, `spade.png`                  |

### suit / type / id の定義値

- **トランプ suit**: `spade` `heart` `diamond` `club` `joker`
- **トランプ value**: `A` `2`–`10` `J` `Q` `K`（jokerは `black` `red`）
- **ダイス type**: `d4` `d6` `d8` `d10` `d10tens` `d12` `d20`
- **麻雀 suit**: `man`（萬子）`pin`（筒子）`sou`（索子）`char`（字牌）`season`（季節牌）
- **麻雀 char値**: `east` `south` `west` `north` `chun` `hatsu` `haku`
- **麻雀 season値**: `spring` `summer` `autumn` `winter`
- **赤ドラ**: 数牌5の赤ドラは `mj_{man,pin,sou}_5_red.svg` / `_5_red.png`

---

## 技術スタック

- **言語**: Python 3.11+
- **主要ライブラリ**:
  - `fonttools` — フォントグリフ解析・アウトライン抽出（`SVGPathPen`）
  - `cairosvg` — SVG→PNG変換
  - `Pillow` — PNG後処理・絵文字画像生成
  - `PyMuPDF` — Noto Emoji SVGの高品質レンダリング（コートカード用）
  - `numpy` — ピクセル配列操作（着色・マスク処理）
  - `scipy` — 画像ラベリング処理（デュアルモードカード生成用）
  - `svgwrite` — SVGファイル生成補助
  - `click` — CLIインターフェース
- **フォントファイル**: `assets/fonts/Secvier.otf`
- **libcairo（OS 別の注意）**: `cairosvg` が使う libcairo は pip では入らない。
  - macOS（Homebrew）: `brew install cairo`。`/opt/homebrew/lib` は dyld の既定の探索先に無いため
    `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` を渡してから実行する。
  - Windows: libcairo の DLL（例: KiCad 同梱の `cairo-2.dll`）があるディレクトリを `PATH` に足す。
- **外部アセット**:
  - `src/noto_cards/` — Noto Emoji playing card SVG（Google LLC, SIL OFL 1.1）
  - `src/ext_mahjong/` — 麻雀牌用外部素材（一索鳥 CC0、季節牌花絵柄 CC BY 4.0）
  - `src/noto_mahjong/` — 字牌・季節牌 漢字SVGキャッシュ
  - `assets/fonts/delagothicone/` — Dela Gothic One サブセット（SIL OFL 1.1）

---

## ビルドフロー

```
Secvier.otf
  │
  ├─ [検査] scripts/inspect_font.py
  │         └─ docs/glyph_map.txt
  │
  ├─ [英数字アウトライン抽出] scripts/extract_glyphs.py
  │         └─ src/alphanum/char_*.svg  （fontToolsのSVGPathPenで純粋パス出力）
  │
  ├─ [合成SVG生成] scripts/render_svg.py
  │         └─ src/{cards,dice,mahjong}/*.svg  （フォント埋め込み + SVG図形）
  │
  └─ [PNG変換] scripts/export_png.py
            └─ dist/{category}/{stem}_72.png
               dist/{category}/{stem}_512.png
```

一括実行は `python scripts/build.py`（全カテゴリ）または `--category` で個別指定。

### ビルドコマンド早見表

```bash
pip install -r requirements.txt             # 初回セットアップ
python scripts/inspect_font.py              # フォント検査 → docs/glyph_map.txt
python scripts/extract_glyphs.py            # 英数字グリフSVG抽出 → src/alphanum/
python scripts/extract_glyphs.py --charset greek  # ギリシャ大文字SVG抽出 → src/alphanum_greek/
python scripts/extract_suits.py             # フォント収録スートSVG抽出 → src/suits/
python scripts/render_svg2png.py            # src SVG → svg2png/ 黒字マスクPNG（全カテゴリ）
python scripts/build.py                     # 全カテゴリビルド
python scripts/build.py --category cards    # カテゴリ指定
python scripts/build.py --dry-run           # 実行確認（ファイル生成なし）

# Discord/Misskey向けトランプ生成 → dist/cards/discord/, dist/cards/misskey/
python scripts/generate_cards_dualmode.py

# 英数字・ギリシャ文字・スートマーク デュアルモード生成
#   → dist/alphanum_dualmode/, dist/alphanum_greek_dualmode/, dist/suits_dualmode/
python scripts/generate_dualmode.py

# 麻雀牌生成 → src/mahjong/*.svg（牌SVG） → dist/mahjong/{discord,misskey}/
python scripts/extract_dela_kanji.py    # 字牌・季節牌の漢字SVG抽出（初回・フォント更新時）
python scripts/generate_mahjong_proto.py # 牌SVGソース生成
python scripts/generate_mahjong_emoji.py # Discord/Misskey向けPNG生成

# Misskey一括インポートzip生成 → _exported-dist/secvier-misskey-{timestamp}.zip
python scripts/build_misskey_zip.py

# README掲載プレビュー生成 → docs/previews/
python scripts/build_category_previews.py
```

### README掲載プレビューの更新（必須）

`docs/previews/` の画像は README の顔であり、**収録内容が変わったら必ず作り直す**。

| ファイル                        | 役割                                             |
| ------------------------------- | ------------------------------------------------ |
| `docs/previews/hero.png`        | README 冒頭バナー（全カテゴリの代表絵文字）      |
| `docs/previews/glyphset.png`    | 収録内容一覧（カテゴリ別の全図柄＋バリアント見本）|
| `docs/previews/{cat}_*.png`     | カテゴリ別 図柄一覧／絵文字サンプル              |

- **更新トリガ**: `dist/` に図柄を追加・削除・再生成したとき、バリアントを増減したとき。
- **手順**: `python scripts/build_category_previews.py` を実行し、生成画像を目視確認して
  `dist/` の変更と**同じコミットに含める**（README とプレビューの乖離を残さない）。
- 新カテゴリを足したら `_sections()` に見出しと glob を 1 行追加する。
  見出しは Pillow 既定フォントで描画するため **ASCII のみ**（日本語は豆腐になる）。

---

## SVG制作仕様

- **viewBox**: `0 0 512 512`（正方形）
- **背景**: 透過（alpha）
- **カラーモード**: sRGB
- **フォント依存の排除**:
  - `src/alphanum/` の SVG は `extract_glyphs.py` が生成するアウトライン化済みパス
  - トランプ等の合成SVGは `render_svg.py` が生成するBase64フォント埋め込み方式
- **PNG出力サイズ**: 72px（標準絵文字）/ 512px（高解像度）
- 出力は必ず `scripts/build.py` 経由で `dist/` に配置すること（直接配置禁止）

---

## Pythonコーディング規則

- スタイル: PEP 8 準拠
- 型ヒント: 全関数に付与（`from __future__ import annotations`）
- docstring: Google スタイル（日本語可）
- エラーハンドリング: フォント読み込み・SVG変換は `try/except` でラップ

```python
# 良い例
from __future__ import annotations
from pathlib import Path

def render_glyph(char: str, output: Path, size: int = 512) -> None:
    """指定文字のグリフをPNGとして書き出す。

    Args:
        char: レンダリングする文字（Secvierフォントのグリフ）
        output: 出力PNGパス
        size: 出力サイズ（px）
    """
    ...
```

---

## コミットメッセージ規約

```
<type>(<scope>): <subject>
```

- **type**: `feat` `fix` `build` `docs` `chore` `style`
- **scope**: `cards` `dice` `mahjong` `alphanum` `scripts` `assets` `docs`
- **言語**: 日本語・英語いずれも可（混在可）

例:

```
feat(alphanum): add A-Z / 0-9 outlined SVGs from Secvier font
build(scripts): add extract_glyphs.py for SVGPathPen outline extraction
docs: update AGENTS.md with unified agent instructions
```

---

## Secvier v0.1-beta 収録グリフ（確認済み）

```
グリフ総数: 71  /  Unicodeマッピング: 176
実質収録:   A–Z（大文字、小文字も同グリフにマップ） / 0–9
            Α–Ω（ギリシャ大文字, U+0391–U+03A9） ※v0.1-betaで追加
            ♠ U+2660 / ♣ U+2663 / ♥ U+2665 / ♦ U+2666（トランプスート） ※v0.1-betaで追加
            ラテン拡張（アクセント付き, A–Z ベースグリフへマップ）
```

| カテゴリ     | フォントグリフ利用                                   | 制作アプローチ                                |
| ------------ | ---------------------------------------------------- | --------------------------------------------- |
| 英数字       | ✅ A–Z / 0–9 直接使用                                | `extract_glyphs.py` でアウトライン化          |
| ギリシャ文字 | ✅ Α–Ω 直接使用（v0.1-beta）                         | `extract_glyphs.py --charset greek`           |
| スートマーク | ✅ ♠♣♥♦ 直接使用（v0.1-beta）                        | `extract_suits.py`（天地中央でアウトライン化）|
| トランプ札面 | ✅ 値文字（A/J/Q/K/2–10）はフォント、pipは内蔵SVGパス | `generate_cards_dualmode.py` で合成           |
| ダイス       | 数字のみフォント（面デザインはSVG）                  | SVGで面ごとにデザイン                         |
| 麻雀牌       | ❌ グリフなし                                        | SVG + Dela Gothic One 漢字で牌ごとにデザイン  |

> 補足: トランプ**札面**のスートpipは各カード生成スクリプト内蔵の `SUIT_PATHS`
> （札レイアウトに最適化された72単位パス）を引き続き使用する。フォント収録スートは
> **独立スートマーク**（`dist/suits_dualmode/`, 03.スートマーク）に適用される。

フォントが更新されたら `python scripts/inspect_font.py` を再実行し
`docs/glyph_map.txt` で差分を確認すること。

---

## 絶対に行わないこと（全エージェント共通）

- `_original-fonts/` 内ファイルの変更・削除
- Secvier以外の商用フォント・第三者フォントのグリフパス流用
- `dist/` への直接ファイル配置（`scripts/build.py` 経由のみ）
- ライセンス表記（CC BY 4.0 / 著作者名）の削除・改ざん
- `assets/fonts/Secvier.otf` の上書き（差し替えはコミット履歴を残すこと）

---

## 作業開始時の共通チェック

- 新しいSVGを作る前に `src/templates/` のベーステンプレートを確認すること
- `docs/glyph_map.txt` を読んで利用可能グリフを把握してから作業すること
- Python依存の追加は `requirements.txt` に記録し、インストール手順も更新すること
- テスト実行: `python scripts/build.py --dry-run`
- `dist/` を更新したら `python scripts/build_category_previews.py` でプレビューを
  作り直し、同じコミットに含めること（→ [README掲載プレビューの更新](#readme掲載プレビューの更新必須)）

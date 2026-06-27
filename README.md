# Secvier ImageAssets

各種SNSおよびチャットサービス（Discord・Misskeyなど）向けに、**RadianN_kswg / ラジアン（柏木主税）による独自フォント Secvier** と **Claude による Agent 機能**、およびその他のアセットによって制作された、カスタム絵文字アセット群です。

> **著作権者**: RadianN_kswg / ラジアン（柏木主税）
> **ライセンス**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.ja)

---

## 収録内容

### トランプ（62枚 × 2プラットフォーム）

スートごとに異なるデザインバリアントを適用した絵文字です。Discord と Misskey の両プラットフォームに対応した出力を提供します。

| スート     | バリアント      | テーマ         |
| ---------- | --------------- | -------------- |
| ♠ スペード | 星幽 (seiyuu)   | 深夜宇宙・深紫 |
| ♥ ハート   | 紅玉 (kougyoku) | 紅玉石・深紅   |
| ♦ ダイヤ   | 砂金 (sakin)    | 羊皮紙・黄金   |
| ♣ クラブ   | 翠玉 (suigyoku) | 深翠・翠緑     |

| プラットフォーム | 出力先                  | サイズ        |
| ---------------- | ----------------------- | ------------- |
| Discord          | `dist/cards/discord/`   | 256 × 256 px  |
| Misskey          | `dist/cards/misskey/`   | 256 × 320 px  |

収録ランク: A / 2–10 / J（ジャック）/ C（ナイト）/ Q（クイーン）/ K（キング）× 4スート + ジョーカー黒・赤 + スートマーク単体 4枚

コートカード（J/C/Q/K）の人物図柄は **Noto Emoji** の SVG を使用しています（→ [クレジット](#クレジット)）。

### ダイス（5バリアント × 各種面数）

| 種別            | 内容                                |
| --------------- | ----------------------------------- |
| D4              | 4面ダイス                           |
| D6              | 6面ダイス（出目1〜6のイラスト付き） |
| D8              | 8面ダイス                           |
| D10             | 10面ダイス（出目0〜9付き）          |
| D% (テンズテン) | パーセンタイルダイス                |
| D12             | 12面ダイス                          |
| D20             | 20面ダイス                          |

バリアント: 星幽 / 翠玉 / 紅玉 / 白磁 / 砂金

### 英数字（6バリアント × 36文字）

A–Z（大文字）/ 0–9 の Secvier フォントグリフを絵文字化。各バリアント 36枚。
ライト/ダーク両モード対応の透過PNG（`dist/alphanum_dualmode/`）と、通常版（`dist/alphanum/`）を提供します。

### 麻雀牌（41枚 × 2プラットフォーム）

萬子・筒子・索子の数牌、字牌（東南西北中發白）、季節牌（春夏秋冬）、赤ドラを収録。

| カテゴリ | 内容                              | 枚数 |
| -------- | --------------------------------- | ---- |
| 萬子     | 1–9 + 赤ドラ（5m赤）             | 10   |
| 筒子     | 1–9 + 赤ドラ（5p赤）             | 10   |
| 索子     | 1–9 + 赤ドラ（5s赤）             | 10   |
| 字牌     | 東・南・西・北・中・發・白        | 7    |
| 季節牌   | 春・夏・秋・冬                    | 4    |

| プラットフォーム | 出力先                    | サイズ        |
| ---------------- | ------------------------- | ------------- |
| Discord          | `dist/mahjong/discord/`   | 256 × 256 px  |
| Misskey          | `dist/mahjong/misskey/`   | 256 × 320 px  |

- 筒子の絵柄は Secvier の「O」グリフを同心円コインとして配置（xhokir 準拠の紺×赤配色）
- 索子の絵柄は Secvier の「I」グリフを竹に見立てて配置（xhokir 準拠の緑×赤配色）
- 字牌・季節牌の漢字は **Dela Gothic One**（SIL OFL 1.1）から抽出
- 一索の鳥は **FluffyStuff**（CC0）、季節牌の花絵柄は **xhokir**（CC BY 4.0）の素材を使用
  （→ [クレジット](#クレジット)）

---

## デザインバリアント

| キー       | 名称 | テーマ                   | 対応カテゴリ              |
| ---------- | ---- | ------------------------ | ------------------------- |
| `seiyuu`   | 星幽 | 深夜紺×薄紫 — 宇宙・星幽 | トランプ♠ / ダイス / 英数字 |
| `suigyoku` | 翠玉 | 深翠×翠緑 — エメラルド   | トランプ♣ / ダイス / 英数字 |
| `kougyoku` | 紅玉 | 深紅×紅 — ルビー         | トランプ♥ / ダイス / 英数字 |
| `hakuji`   | 白磁 | 白磁×金茶 — 磁器・和風   | ダイス / 英数字            |
| `kokuji`   | 黒磁 | 黒×金縁 — 白磁の色反転   | 英数字（デュアルモード専用）|
| `sakin`    | 砂金 | 黄金×金 — 砂金・羊皮紙   | トランプ♦ / ダイス / 英数字 |

---

## ディレクトリ構成

```
Secvier_ImageAssets/
├── assets/
│   └── fonts/
│       ├── Secvier.otf              # ビルドで参照するフォント
│       └── delagothicone/           # Dela Gothic One サブセット（字牌・季節牌漢字用）
├── src/
│   ├── alphanum/                    # 英数字 SVG（アウトライン化済み）
│   ├── cards/                       # トランプ SVG（v1 旧実装）
│   ├── suits/                       # スートマーク SVG
│   ├── noto_cards/                  # Noto Emoji コートカード SVG（原本）
│   ├── noto_cache/                  # Noto SVG キャッシュ
│   ├── noto_svg/                    # Noto SVG 補完キャッシュ
│   ├── dice/                        # ダイス SVG
│   ├── mahjong/                     # 麻雀牌 SVGソース
│   │   └── parts/                   # 最小部品（筒子コイン・索子竹・字牌文字など）
│   ├── noto_mahjong/                # 字牌・季節牌 漢字SVGキャッシュ
│   ├── ext_mahjong/                 # 外部素材（一索鳥 CC0・季節牌花絵柄 CC BY 4.0）
│   └── templates/                   # ベーステンプレート
├── dist/
│   ├── cards/
│   │   ├── discord/                 # Discord向け 256×256px トランプ PNG
│   │   └── misskey/                 # Misskey向け 256×320px トランプ PNG
│   ├── dice/{variant}/              # ダイス PNG（バリアント別）
│   ├── alphanum/{variant}/          # 英数字 PNG（通常版）
│   ├── alphanum_dualmode/{variant}/ # 英数字 PNG（透過デュアルモード）
│   ├── suits_dualmode/              # スートマーク 透過デュアルモード
│   └── mahjong/
│       ├── discord/                 # Discord向け 256×256px 麻雀牌 PNG
│       └── misskey/                 # Misskey向け 256×320px 麻雀牌 PNG
├── scripts/
│   ├── generate_cards_dualmode.py   # Discord/Misskey向けトランプ生成（現行）
│   ├── generate_dualmode.py         # 英数字・スートマーク デュアルモード生成（現行）
│   ├── generate_all_v3.py           # ダイス・英数字一括生成
│   ├── generate_dice_faces.py       # ダイス出目イラスト生成
│   ├── generate_mahjong_proto.py    # 麻雀牌 SVGソース生成（現行）
│   ├── generate_mahjong_emoji.py    # 麻雀牌 Discord/Misskey向けPNG生成（現行）
│   ├── extract_dela_kanji.py        # Dela Gothic One から漢字SVG抽出
│   ├── build_misskey_zip.py         # Misskey一括インポートzip生成
│   ├── inspect_font.py              # フォントグリフ検査
│   ├── extract_glyphs.py            # Secvier → SVGアウトライン抽出
│   ├── build.py                     # 全カテゴリ一括ビルド
│   ├── export_png.py                # SVG → PNG 変換
│   └── render_svg.py                # SVG合成ユーティリティ
├── docs/
│   ├── glyph_map.txt                # inspect_font.py が自動生成
│   ├── cards_dualmode_spec.md       # Discord/Misskey向けトランプ仕様書
│   └── mahjong_proto_spec.md        # 麻雀牌 SVG仕様書（外部素材ライセンス含む）
├── _exported-dist/                  # エクスポートzip（.gitignore対象）
├── _original-fonts/                 # 原本フォント（読み取り専用）
├── requirements.txt
├── LICENSE
├── AGENTS.md                        # エージェント共通指示書
└── CLAUDE.md                        # Claude 向け補足
```

---

## セットアップ

### 必要環境

- Python 3.11+
- 依存ライブラリ（`requirements.txt` 参照）

```bash
pip install -r requirements.txt
```

### トランプ絵文字の生成

コートカード生成に **Noto Emoji の SVG ファイル**（18枚）が必要です。`src/noto_cards/` に配置してください（→ [Noto Emoji リリースページ](https://github.com/googlefonts/noto-emoji/releases)）。

```bash
# Discord/Misskey向けトランプ生成（現行） → dist/cards/discord/, dist/cards/misskey/
python scripts/generate_cards_dualmode.py
```

### ダイス・英数字の生成

```bash
# ダイス・英数字 全バリアント生成
python scripts/generate_all_v3.py

# 英数字・スートマーク デュアルモード生成（透過PNG）
# → dist/alphanum_dualmode/, dist/suits_dualmode/
python scripts/generate_dualmode.py

# 一括ビルド（dry-run確認）
python scripts/build.py --dry-run
python scripts/build.py
```

### 麻雀牌の生成

字牌・季節牌の漢字抽出スクリプトを先に実行し、次に牌SVG・PNG を生成します。

```bash
# 字牌・季節牌の漢字SVG抽出（初回、またはフォント更新時）
python scripts/extract_dela_kanji.py

# 麻雀牌 SVGソース生成 → src/mahjong/
python scripts/generate_mahjong_proto.py

# Discord/Misskey向けPNG生成 → dist/mahjong/{discord,misskey}/
python scripts/generate_mahjong_emoji.py
```

### Misskey 絵文字一括インポート

```bash
# Misskey用zip生成 → _exported-dist/secvier-misskey-{timestamp}.zip
# 収録: トランプ(62) + 英数字デュアルモード(216) + ダイス(399) + スートマーク(8) + 麻雀牌(41) = 726絵文字
python scripts/build_misskey_zip.py
```

---

## 出力仕様

| 項目                             | 仕様                              |
| -------------------------------- | --------------------------------- |
| フォーマット                     | PNG（RGBA）                       |
| トランプ（Discord）              | 256 × 256 px（カード部: 205×256） |
| トランプ（Misskey）              | 256 × 320 px                      |
| ダイス・英数字（通常版）         | 128 × 128 px                      |
| 英数字・スートマーク（dualmode） | 128 × 128 px / 512 × 512 px       |
| 麻雀牌（Discord）                | 256 × 256 px                      |
| 麻雀牌（Misskey）                | 256 × 320 px                      |
| 麻雀牌 SVGキャンバス             | 360 × 504 px（比率 5:7）          |
| 背景                             | 透過（alpha）                     |
| カラーモード                     | sRGB                              |

---

## クレジット

### フォント

**Secvier** — RadianN_kswg / ラジアン（柏木主税）による独自作字フォント。
本リポジトリの絵文字アセットはこのフォントのグリフをベースに制作されています。

### 生成ツール

**Claude（Anthropic）** — Agent 機能を使用して絵文字アセットの設計・スクリプト生成・画像生成を行っています。
本プロジェクトの制作は Claude Cowork による自律エージェント作業によって実施されました。

### コートカード人物図柄

**Noto Emoji** — Google LLC
ライセンス: [SIL Open Font License 1.1](https://scripts.sil.org/OFL)
リポジトリ: [googlefonts/noto-emoji](https://github.com/googlefonts/noto-emoji)

使用対象: Playing Card SVG（PLAYING CARD JACK/KNIGHT/QUEEN/KING OF ♠♥♦♣ および JOKER）
加工内容: コーナーインデックス除去・バリアントカラーへの着色・サイズ調整

### 麻雀牌 外部素材

**FluffyStuff / riichi-mahjong-tiles** — 一索の鳥イラスト
ライセンス: CC0（パブリックドメイン）

**xhokir / riichi-mahjong-tiles** — 季節牌の花絵柄（FluffyStuff 由来・季節牌追加版）
ライセンス: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

使用対象: `src/ext_mahjong/ichisou_bird_cc0.svg`（一索）、`src/ext_mahjong/season{1-4}_cc_by.svg`（季節牌）
加工内容: Secvier バリアント配色（紅玉・翠玉・星幽）への色置換

詳細なライセンス・帰属情報は `src/ext_mahjong/CREDITS.md` を参照してください。

### 麻雀牌 漢字フォント

**Dela Gothic One** — 字牌（東南西北中發白）および季節牌（春夏秋冬）の漢字に使用
ライセンス: [SIL Open Font License 1.1](https://scripts.sil.org/OFL)

使用対象: `assets/fonts/delagothicone/`（woff2 サブセット）
加工内容: フォントから漢字を SVG パスとして抽出（`extract_dela_kanji.py`）

---

## ライセンス

本アセット群（Secvier フォントグリフ派生部分および独自デザイン部分）は **CC BY 4.0** で公開されています。

**[Creative Commons 表示 4.0 国際](https://creativecommons.org/licenses/by/4.0/deed.ja)**

著作者：RadianN_kswg / ラジアン（柏木主税）

利用時のクレジット表記例:

```
Secvier emoji assets by RadianN_kswg / ラジアン（柏木主税）
CC BY 4.0 https://creativecommons.org/licenses/by/4.0/
Includes Noto Emoji playing card illustrations by Google LLC (SIL OFL 1.1)
Mahjong tile graphics include works by FluffyStuff (CC0) and xhokir (CC BY 4.0)
Mahjong kanji rendered with Dela Gothic One (SIL OFL 1.1)
```

> **注意**:
> - コートカードの人物図柄部分（Noto Emoji 派生）は SIL OFL 1.1 の条件に従います。
> - 麻雀牌の季節牌花絵柄（xhokir 由来）は CC BY 4.0 の条件に従います（帰属表示が必要）。
> - 一索の鳥（FluffyStuff 由来）は CC0 のため帰属表示不要ですが、上記クレジット表記を推奨します。
> 本アセットを二次配布する場合は各ライセンスの条件を確認してください。

# Secvier ImageAssets

各種SNSおよびチャットサービス（Discord・Misskeyなど）向けに、**RadianN_kswg / ラジアン（柏木主税）による独自フォント Secvier** と **Claude による Agent 機能**、およびその他のアセットによって制作された、カスタム絵文字アセット群です。

> **著作権者**: RadianN_kswg / ラジアン（扇二春・柏木主税）  
> **ライセンス**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.ja)

---

## 収録内容

### トランプ（62枚）

スートごとに異なるデザインバリアントを適用した 128×128px の絵文字です。

| スート | バリアント | テーマ |
|--------|-----------|--------|
| ♠ スペード | 星幽 (seiyuu) | 深夜宇宙・深紫 |
| ♥ ハート | 紅玉 (kougyoku) | 紅玉石・深紅 |
| ♦ ダイヤ | 砂金 (sakin) | 羊皮紙・黄金 |
| ♣ クラブ | 翠玉 (suigyoku) | 深翠・翠緑 |

収録ランク: A / 2–10 / J（ジャック）/ C（ナイト）/ Q（クイーン）/ K（キング）× 4スート + ジョーカー黒・赤 + スートマーク単体 4枚

コートカード（J/C/Q/K）の人物図柄は **Noto Emoji** の SVG を使用しています（→ [クレジット](#クレジット)）。

### ダイス（5バリアント × 各種面数）

| 種別 | 内容 |
|------|------|
| D4 | 4面ダイス |
| D6 | 6面ダイス（出目1〜6のイラスト付き） |
| D8 | 8面ダイス |
| D10 | 10面ダイス（出目0〜9付き） |
| D% (テンズテン) | パーセンタイルダイス |
| D12 | 12面ダイス |
| D20 | 20面ダイス |

バリアント: 星幽 / 翠玉 / 紅玉 / 白磁 / 砂金

### 英数字（5バリアント × 36文字）

A–Z（大文字）/ 0–9 の Secvier フォントグリフを絵文字化。各バリアント 36枚。

### 麻雀牌（予定）

萬子1–9 / 筒子1–9 / 索子1–9 / 字牌（東南西北中發白）— 実装予定

---

## デザインバリアント

| キー | 名称 | テーマ |
|------|------|--------|
| `seiyuu` | 星幽 | 深夜紺×薄紫 — 宇宙・星幽 |
| `suigyoku` | 翠玉 | 深翠×翠緑 — エメラルド |
| `kougyoku` | 紅玉 | 深紅×紅 — ルビー |
| `hakuji` | 白磁 | 白磁×金茶 — 磁器・和風 |
| `sakin` | 砂金 | 黄金×金 — 砂金・羊皮紙 |

---

## ディレクトリ構成

```
Secvier_ImageAssets/
├── assets/
│   └── fonts/
│       └── Secvier.otf          # ビルドで参照するフォント
├── src/
│   ├── alphanum/                # 英数字 SVG（アウトライン化済み）
│   ├── cards/                   # トランプ SVG（v1 旧実装）
│   ├── suits/                   # スートマーク SVG
│   ├── noto_cards/              # Noto Emoji コートカード SVG（原本）
│   ├── noto_cache/              # Noto SVG キャッシュ
│   ├── noto_svg/                # Noto SVG 補完キャッシュ
│   ├── dice/                    # ダイス SVG
│   ├── mahjong/                 # 麻雀牌 SVG（予定）
│   └── templates/               # ベーステンプレート
├── dist/
│   ├── cards/                   # トランプ PNG（128×128px）
│   │   ├── card_{S|H|D|C}_{rank}.png
│   │   ├── card_joker_{black|red}.png
│   │   └── card_suit_{S|H|D|C}.png
│   ├── dice/
│   │   └── {variant}/           # 各バリアントごとのダイス PNG
│   ├── alphanum/
│   │   └── {variant}/           # 各バリアントごとの英数字 PNG
│   └── mahjong/                 # （予定）
├── scripts/
│   ├── generate_cards_v2.py     # トランプ絵文字生成（現行）
│   ├── generate_all_v3.py       # ダイス・英数字一括生成（現行）
│   ├── generate_dice_faces.py   # ダイス出目イラスト生成
│   ├── inspect_font.py          # フォントグリフ検査
│   ├── extract_glyphs.py        # Secvier → SVGアウトライン抽出
│   ├── build.py                 # 全カテゴリ一括ビルド
│   ├── export_png.py            # SVG → PNG 変換
│   └── render_svg.py            # SVG合成ユーティリティ
├── docs/
│   └── glyph_map.txt            # inspect_font.py が自動生成
├── _original-fonts/             # 原本フォント（読み取り専用）
├── requirements.txt
├── LICENSE
├── AGENTS.md                    # エージェント共通指示書
└── CLAUDE.md                    # Claude 向け補足
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

```bash
# フォント検査（グリフ確認）
python scripts/inspect_font.py

# トランプ全62枚を生成 → dist/cards/
python scripts/generate_cards_v2.py
```

コートカード生成に **Noto Emoji の SVG ファイル**（18枚）が必要です。`src/noto_cards/` に配置してください（→ [Noto Emoji リリースページ](https://github.com/googlefonts/noto-emoji/releases)）。

### ダイス・英数字の生成

```bash
# 全バリアント × 全カテゴリ生成
python scripts/generate_all_v3.py

# 一括ビルド（dry-run確認）
python scripts/build.py --dry-run
python scripts/build.py
```

---

## 出力仕様

| 項目 | 仕様 |
|------|------|
| フォーマット | PNG（RGBA） |
| トランプサイズ | 128 × 128 px |
| ダイス・英数字サイズ | 128 × 128 px |
| 背景 | 透過（alpha） |
| カラーモード | sRGB |

---

## クレジット

### フォント

**Secvier** — RadianN_kswg / ラジアン（扇二春・柏木主税）による独自作字フォント。  
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

---

## ライセンス

本アセット群（Secvier フォントグリフ派生部分および独自デザイン部分）は **CC BY 4.0** で公開されています。

**[Creative Commons 表示 4.0 国際](https://creativecommons.org/licenses/by/4.0/deed.ja)**

著作者：RadianN_kswg / ラジアン（扇二春・柏木主税）

利用時のクレジット表記例:

```
Secvier emoji assets by RadianN_kswg / ラジアン（扇二春）
CC BY 4.0 https://creativecommons.org/licenses/by/4.0/
Includes Noto Emoji playing card illustrations by Google LLC (SIL OFL 1.1)
```

> **注意**: コートカードの人物図柄部分（Noto Emoji 派生）は SIL OFL 1.1 の条件に従います。
> 本アセットを二次配布する場合は両ライセンスの条件を確認してください。

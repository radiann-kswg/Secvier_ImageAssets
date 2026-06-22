# GitHub Copilot ワークスペース指示書 — Secvier ImageAssets

> 共通仕様の詳細は **[AGENTS.md](../AGENTS.md)** を参照してください。
> このファイルはCopilot固有の補足事項のみを記載します。

---

## プロジェクト概要

各種SNSおよびチャットサービス（Discord・Misskeyなど）向けに、
**RadianN_kswg / ラジアン（柏木主税）による独自フォント Secvier** と
**Claude による Agent 機能**、およびその他のアセット（Noto Emoji など）によって制作された
カスタム絵文字アセット群リポジトリ。

**著作権者**: RadianN_kswg / ラジアン（柏木主税） / **ライセンス**: CC BY 4.0
コートカード人物図柄: Noto Emoji (Google LLC, SIL OFL 1.1)

---

## 補完規則

### Python補完

- `from __future__ import annotations` を全スクリプトの先頭に記述
- 型ヒントは全引数・戻り値に付与（`Path`, `str`, `int`, `list[Path]` 等）
- docstringはGoogle スタイル（日本語記述可）
- フォントパスは常に `FONT_PATH = Path(__file__).parent.parent / "assets" / "fonts" / "Secvier.otf"` パターンを踏襲

### SVG補完

- `viewBox="0 0 512 512"` 固定
- `width` / `height` も `512` に統一
- フォント参照はBase64埋め込み（`data:font/otf;base64,...`）またはパスなし（アウトライン化）
- `fill` のデフォルト色: `#000000`（透過背景）

### ファイル配置

```
src/alphanum/char_{A-Z,0-9}.svg        ← extract_glyphs.py 出力（変更不要）
src/suits/{spade,heart,diamond,club}.svg  ← スートマーク SVG
src/noto_cards/*.svg                   ← Noto Emoji 原本（読み取り専用）
src/{dice,mahjong}/*.svg               ← SVGデザイン手作業 or スクリプト出力
svg2png/alphanum/char_*.png            ← SVG の単純PNG変換（装飾なし）
svg2png/suits/*.png                    ← スートマーク SVG の単純PNG変換
dist/cards/discord/card_*.png          ← generate_cards_dualmode.py 出力（256×256px）
dist/cards/misskey/card_*.png          ← generate_cards_dualmode.py 出力（256×320px）
dist/dice/{variant}/*.png              ← generate_all_v3.py 出力
dist/alphanum/{variant}/*.png          ← generate_all_v3.py 出力（通常版）
dist/alphanum_dualmode/{variant}/*.png ← generate_dualmode.py 出力（透過デュアルモード）
dist/suits_dualmode/*.png              ← generate_dualmode.py 出力（透過デュアルモード）
_exported-dist/*.zip                   ← build_misskey_zip.py 出力（.gitignore対象）
```

`dist/` への直接配置は禁止。`svg2png/` はユーティリティ用途（絵文字出力は `dist/`）。
`_exported-dist/` は `.gitignore` 対象のため git 管理外。

---

## 禁止事項

- `_original-fonts/` 内ファイルの変更・削除
- 第三者フォントのグリフパス使用
- `dist/` への直接ファイル配置
- ライセンス表記の削除・改ざん

---

## コミットメッセージ

```
<type>(<scope>): <subject>
```

| type    | 用途                         |
| ------- | ---------------------------- |
| `feat`  | 新機能・新アセット追加       |
| `fix`   | バグ修正                     |
| `build` | ビルドスクリプト変更         |
| `docs`  | ドキュメント更新             |
| `chore` | 設定ファイル・メタデータ変更 |
| `style` | SVGスタイル・見た目の調整    |

例: `feat(alphanum): add outlined SVGs for A-Z and 0-9`

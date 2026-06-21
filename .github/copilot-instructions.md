# GitHub Copilot ワークスペース指示書 — Secvier ImageAssets

> 共通仕様の詳細は **[AGENTS.md](../AGENTS.md)** を参照してください。
> このファイルはCopilot固有の補足事項のみを記載します。

---

## プロジェクト概要

独自フォント **Secvier**（作字：RadianN_kswg / ラジアン（扇二春・柏木主税））を使用した
絵文字アセット（PNG/SVG）制作リポジトリ。

**ライセンス**: CC BY 4.0 — 著作権者：RadianN_kswg / ラジアン（扇二春・柏木主税）

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
src/alphanum/char_{A-Z,0-9}.svg    ← extract_glyphs.py 出力（変更不要）
src/cards/card_{suit}_{value}.svg  ← render_svg.py 出力
src/{dice,mahjong}/*.svg           ← SVGデザイン手作業 or スクリプト出力
dist/**/*.png                      ← build.py 経由のみ（手動配置禁止）
```

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

| type | 用途 |
|---|---|
| `feat` | 新機能・新アセット追加 |
| `fix` | バグ修正 |
| `build` | ビルドスクリプト変更 |
| `docs` | ドキュメント更新 |
| `chore` | 設定ファイル・メタデータ変更 |
| `style` | SVGスタイル・見た目の調整 |

例: `feat(alphanum): add outlined SVGs for A-Z and 0-9`

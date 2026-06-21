# AGENTS.md — Secvier ImageAssets 共通エージェント指示書

このファイルは **GitHub Copilot** および **Claude Code** の両エージェントが参照する
統合ワークスペース指示書です。ツール固有の補足は末尾のセクションを参照してください。

---

## プロジェクト概要

独自フォント **Secvier**（作字：RadianN_kswg / ラジアン（扇二春・柏木主税））を用いて、
以下カテゴリの絵文字アセット（SVG + PNG）を制作するリポジトリです。

| カテゴリ | 内容 | 枚数 |
|---|---|---|
| トランプ | ♠♥♦♣ × A,2–10,J,Q,K + ジョーカー黒・赤 | 54枚 |
| ダイス | D4 / D6(×6面) / D8 / D10 / テンズテン(D%) / D12 / D20 | 7種 |
| 麻雀牌 | 萬子1–9 / 筒子1–9 / 索子1–9 / 字牌7枚（東南西北中發白） | 34枚 |
| 英数字 | A–Z（大文字） / 0–9 | 36枚 |

---

## 権限・ライセンス（最優先）

- **著作権者**：RadianN_kswg / ラジアン（扇二春・柏木主税）
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
├── CLAUDE.md                   ← Claude Code 向け補足（AGENTS.mdをインポート）
├── .github/
│   └── copilot-instructions.md ← GitHub Copilot 向け補足
├── assets/
│   └── fonts/
│       └── Secvier.otf         ← ビルド参照フォント（_original-fontsのコピー）
├── src/
│   ├── alphanum/               ← 英数字 SVGソース（アウトライン化済み）
│   ├── cards/                  ← トランプ SVGソース
│   ├── dice/                   ← ダイス SVGソース
│   ├── mahjong/                ← 麻雀牌 SVGソース
│   └── templates/              ← ベーステンプレートSVG
├── dist/
│   ├── alphanum/               ← 出力PNG（72px / 512px）
│   ├── cards/
│   ├── dice/
│   └── mahjong/
├── scripts/
│   ├── inspect_font.py         ← グリフ検査 → docs/glyph_map.txt
│   ├── extract_glyphs.py       ← フォントアウトライン → src/alphanum/ SVG
│   ├── render_svg.py           ← フォント埋め込みSVG生成（トランプ等の合成用）
│   ├── export_png.py           ← SVG → PNG変換
│   └── build.py                ← 全カテゴリ一括ビルド
├── docs/
│   └── glyph_map.txt           ← inspect_font.py が自動生成
├── _original-fonts/            ← 原本（読み取り専用）
├── requirements.txt
└── LICENSE
```

---

## ファイル命名規則

| カテゴリ | 命名パターン | 例 |
|---|---|---|
| 英数字 | `char_{文字}.svg` | `char_A.svg`, `char_0.svg` |
| トランプ | `card_{suit}_{value}.svg` | `card_spade_A.svg`, `card_joker_black.svg` |
| ダイス | `dice_{type}_{face}.svg` | `dice_d6_6.svg` |
| 麻雀牌 | `mj_{suit}_{id}.svg` | `mj_man_1.svg`, `mj_char_east.svg` |
| PNG出力 | `{stem}_72.png` / `{stem}_512.png` | `char_A_512.png` |

### suit / type / id の定義値

- **トランプ suit**: `spade` `heart` `diamond` `club` `joker`
- **トランプ value**: `A` `2`–`10` `J` `Q` `K`（jokerは `black` `red`）
- **ダイス type**: `d4` `d6` `d8` `d10` `d10tens` `d12` `d20`
- **麻雀 suit**: `man`（萬子）`pin`（筒子）`sou`（索子）`char`（字牌）
- **麻雀 char値**: `east` `south` `west` `north` `chun` `hatsu` `haku`

---

## 技術スタック

- **言語**: Python 3.11+
- **主要ライブラリ**:
  - `fonttools` — フォントグリフ解析・アウトライン抽出（`SVGPathPen`）
  - `cairosvg` — SVG→PNG変換
  - `Pillow` — PNG後処理（サイズ調整・最適化）
  - `svgwrite` — SVGファイル生成補助
  - `click` — CLIインターフェース
- **フォントファイル**: `assets/fonts/Secvier.otf`

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
pip install -r requirements.txt          # 初回セットアップ
python scripts/inspect_font.py           # フォント検査
python scripts/extract_glyphs.py         # 英数字グリフSVG抽出
python scripts/build.py                  # 全カテゴリビルド
python scripts/build.py --category cards # カテゴリ指定
python scripts/build.py --dry-run        # 実行確認（ファイル生成なし）
```

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

## Secvier v0.0-alpha 収録グリフ（確認済み）

```
グリフ総数: 43  /  Unicodeマッピング: 124
実質収録:   A–Z（大文字、小文字も同グリフにマップ） / 0–9
```

| カテゴリ | フォントグリフ利用 | 制作アプローチ |
|---|---|---|
| 英数字 | ✅ A–Z / 0–9 直接使用 | `extract_glyphs.py` でアウトライン化 |
| トランプ | ✅ 値文字（A/J/Q/K/2–10）はフォント、スートはSVG図形 | `render_svg.py` で合成 |
| ダイス | ❌ グリフなし | SVGで面ごとにデザイン |
| 麻雀牌 | ❌ グリフなし | SVGで牌ごとにデザイン |

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

## [Claude Code 向け補足]

- 新しいSVGを作る前に `src/templates/` のベーステンプレートを確認すること
- `docs/glyph_map.txt` を読んで利用可能グリフを把握してから作業すること
- Python依存の追加は `requirements.txt` に記録し、インストール手順も更新すること
- テスト実行: `python scripts/build.py --dry-run`

---

## [GitHub Copilot 向け補足]

- 補完提案はこのAGENTS.mdの命名規則・ディレクトリ規則に従うこと
- SVGの `viewBox` は常に `0 0 512 512`
- フォント参照は `assets/fonts/Secvier.otf` への相対パスまたはBase64埋め込みを使用すること
- 新規スクリプトは `scripts/` に配置し、`from __future__ import annotations` を先頭に記述すること

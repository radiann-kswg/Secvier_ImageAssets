@AGENTS.md

---

## Claude Code 固有の作業指針

### 優先確認事項

1. 作業開始前に `docs/glyph_map.txt` を確認し、利用可能グリフを把握すること
2. 新SVG作成前に `src/templates/` のベーステンプレートを確認すること
3. 英数字アセットは `scripts/extract_glyphs.py` で生成された
   アウトライン済みSVG（`src/alphanum/char_*.svg`）を起点にすること

### 現行メインスクリプト

| スクリプト | 対象 | 出力先 |
|---|---|---|
| `scripts/generate_cards_v2.py` | トランプ 62枚（スート別バリアント + Noto コートカード） | `dist/cards/` |
| `scripts/generate_all_v3.py` | ダイス・英数字（全5バリアント） | `dist/dice/`, `dist/alphanum/` |
| `scripts/generate_dice_faces.py` | ダイス出目イラスト | `dist/dice/` |

### スクリプト実行順序

```bash
# フォント検査（グリフ確認）
python scripts/inspect_font.py

# 英数字グリフ抽出（アウトライン化SVG → src/alphanum/）
python scripts/extract_glyphs.py

# トランプ絵文字生成（128×128px, Noto Emoji SVGが src/noto_cards/ に必要）
python scripts/generate_cards_v2.py

# ダイス・英数字生成（全バリアント）
python scripts/generate_all_v3.py

# 全カテゴリ一括ビルド（dry-run確認 → 実行）
python scripts/build.py --dry-run
python scripts/build.py
```

### ディレクトリ補足

- `svg2png/` — `src/alphanum/` や `src/suits/` の SVG を装飾なしで単純 PNG 変換したもの。
  スタイル付き絵文字出力（`dist/`）とは別管理。
- `src/noto_cards/` — Noto Emoji の Playing Card SVG 原本（読み取り専用扱い）。
  `generate_cards_v2.py` の `render_noto_figure()` が PyMuPDF で読み込む。

### メモリ・コンテキスト管理

- Python依存を追加した場合は `requirements.txt` を必ず更新すること（`PyMuPDF`, `numpy` 含む）
- 新カテゴリや新仕様を追加する場合は `docs/` に仕様書を作成すること
- コミットは `feat` / `fix` / `build` / `docs` / `chore` プレフィックスで行うこと

@AGENTS.md

---

## Claude Code 固有の作業指針

### 優先確認事項

1. 作業開始前に `docs/glyph_map.txt` を確認し、利用可能グリフを把握すること
2. 新SVG作成前に `src/templates/` のベーステンプレートを確認すること
3. 英数字アセットは `scripts/extract_glyphs.py` で生成された
   アウトライン済みSVG（`src/alphanum/char_*.svg`）を起点にすること

### 現行メインスクリプト

| スクリプト                           | 対象                                          | 出力先                                         |
| ------------------------------------ | --------------------------------------------- | ---------------------------------------------- |
| `scripts/generate_cards_v2.py`       | トランプ 62枚（スート別バリアント + Noto コートカード） | `dist/cards/`（旧フォーマット）      |
| `scripts/generate_cards_dualmode.py` | トランプ Discord/Misskey向け各62枚            | `dist/cards/discord/`, `dist/cards/misskey/`   |
| `scripts/generate_all_v3.py`         | ダイス・英数字（全5バリアント）               | `dist/dice/`, `dist/alphanum/`                 |
| `scripts/generate_dualmode.py`       | 英数字・スートマーク デュアルモード版         | `dist/alphanum_dualmode/`, `dist/suits_dualmode/` |
| `scripts/generate_dice_faces.py`     | ダイス出目イラスト                            | `dist/dice/`                                   |
| `scripts/extract_dela_kanji.py`      | Dela Gothic One から字牌・季節牌の漢字SVG抽出 | `src/noto_mahjong/`                            |
| `scripts/generate_mahjong_proto.py`  | 麻雀牌 SVGソース生成（牌本体 + parts/）       | `src/mahjong/`                                 |
| `scripts/generate_mahjong_emoji.py`  | 麻雀牌 Discord/Misskey向けPNG生成（41枚）     | `dist/mahjong/discord/`, `dist/mahjong/misskey/` |
| `scripts/build_misskey_zip.py`       | Misskey一括インポートzip生成                  | `_exported-dist/secvier-misskey-{timestamp}.zip` |

### スクリプト実行順序

```bash
# フォント検査（グリフ確認）
python scripts/inspect_font.py

# 英数字グリフ抽出（アウトライン化SVG → src/alphanum/）
python scripts/extract_glyphs.py

# トランプ絵文字生成（Discord/Misskey向け, Noto Emoji SVGが src/noto_cards/ に必要）
python scripts/generate_cards_dualmode.py

# 英数字・スートマーク デュアルモード生成（ライト/ダーク両対応 透過PNG）
python scripts/generate_dualmode.py

# ダイス・英数字生成（全バリアント）
python scripts/generate_all_v3.py

# 麻雀牌生成（SVGソース → Discord/Misskey向けPNG）
python scripts/extract_dela_kanji.py      # 字牌・季節牌の漢字SVG抽出（初回・フォント更新時）
python scripts/generate_mahjong_proto.py  # 牌SVGソース生成 → src/mahjong/
python scripts/generate_mahjong_emoji.py  # PNG生成 → dist/mahjong/{discord,misskey}/

# 全カテゴリ一括ビルド（dry-run確認 → 実行）
python scripts/build.py --dry-run
python scripts/build.py

# Misskey一括インポートzip生成（麻雀牌を含む全カテゴリ）
python scripts/build_misskey_zip.py
```

### ディレクトリ補足

- `svg2png/` — `src/alphanum/` や `src/suits/` の SVG を装飾なしで単純 PNG 変換したもの。
  スタイル付き絵文字出力（`dist/`）とは別管理。
- `src/noto_cards/` — Noto Emoji の Playing Card SVG 原本（読み取り専用扱い）。
  `generate_cards_dualmode.py` の `render_noto_figure()` が PyMuPDF で読み込む。
- `dist/alphanum_dualmode/` — 6バリアント（seiyuu/suigyoku/kougyoku/hakuji/kokuji/sakin）×
  36字 の透過PNG。`kokuji`（黒磁）は hakuji の色反転で、暗背景に映えるバリアント。
- `src/mahjong/` — 麻雀牌 SVGソース。`generate_mahjong_proto.py` が生成・更新する。
  `parts/` に筒子コイン・索子竹・字牌文字などの最小部品SVGを格納。
- `src/ext_mahjong/` — 外部素材（CC0/CC BY 4.0）。一索の鳥（CC0）と季節牌の花絵柄（CC BY 4.0）。
  ライセンス詳細は `src/ext_mahjong/CREDITS.md` を参照。**読み取り専用**として扱うこと。
- `src/noto_mahjong/` — `extract_dela_kanji.py` が抽出した字牌・季節牌の漢字SVGキャッシュ。
- `assets/fonts/delagothicone/` — Dela Gothic One woff2サブセット（SIL OFL 1.1）。
  字牌・季節牌の漢字レンダリングに使用。フォントファイルは改変・再頒布禁止。
- `_exported-dist/` — `build_misskey_zip.py` が出力する zip の格納先（`.gitignore` 対象）。

### メモリ・コンテキスト管理

- Python依存を追加した場合は `requirements.txt` を必ず更新すること（`PyMuPDF`, `numpy`, `scipy` 含む）
- 新カテゴリや新仕様を追加する場合は `docs/` に仕様書を作成すること
- コミットは `feat` / `fix` / `build` / `docs` / `chore` プレフィックスで行うこと

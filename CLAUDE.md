@AGENTS.md

---

## Claude Code 固有の作業指針

### 優先確認事項

1. 作業開始前に `docs/glyph_map.txt` を確認し、利用可能グリフを把握すること
2. 新SVG作成前に `src/templates/` のベーステンプレートを確認すること
3. 英数字アセットは `scripts/extract_glyphs.py` で生成された
   アウトライン済みSVG（`src/alphanum/char_*.svg`）を起点にすること

### スクリプト実行順序

```bash
# フォント検査（グリフ確認）
python scripts/inspect_font.py

# 英数字グリフ抽出（アウトライン化SVG → src/alphanum/）
python scripts/extract_glyphs.py

# 全カテゴリビルド（SVG生成 → PNG変換 → dist/）
python scripts/build.py

# 事前確認（dry-run）
python scripts/build.py --dry-run
```

### メモリ・コンテキスト管理

- Python依存を追加した場合は `requirements.txt` を必ず更新すること
- 新カテゴリや新仕様を追加する場合は `docs/` に仕様書を作成すること
- コミットは `feat` / `fix` / `build` / `docs` / `chore` プレフィックスで行うこと

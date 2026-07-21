# ギリシャ文字アセット仕様（Secvier v0.1-beta）

Secvier v0.1-beta で追加されたギリシャ大文字グリフ（Α–Ω, U+0391–U+03A9）を
英数字カテゴリと同等のデュアルモード絵文字として生成する仕様。

## 対象グリフ

大文字 24 字のみ（本バージョンのアセット化対象）。

| 文字 | ステム名  | Unicode | フォントグリフ名 |
| ---- | --------- | ------- | ---------------- |
| Α    | Alpha     | U+0391  | Alpha            |
| Β    | Beta      | U+0392  | Beta             |
| Γ    | Gamma     | U+0393  | Gamma            |
| Δ    | Delta     | U+0394  | Deltagreek       |
| Ε    | Epsilon   | U+0395  | Epsilon          |
| Ζ    | Zeta      | U+0396  | Zeta             |
| Η    | Eta       | U+0397  | Eta              |
| Θ    | Theta     | U+0398  | Theta            |
| Ι    | Iota      | U+0399  | Iota             |
| Κ    | Kappa     | U+039A  | Kappa            |
| Λ    | Lambda    | U+039B  | Lambda           |
| Μ    | Mu        | U+039C  | Mu               |
| Ν    | Nu        | U+039D  | Nu               |
| Ξ    | Xi        | U+039E  | Xi               |
| Ο    | Omicron   | U+039F  | Omicron          |
| Π    | Pi        | U+03A0  | Pi               |
| Ρ    | Rho       | U+03A1  | Rho              |
| Σ    | Sigma     | U+03A3  | Sigma            |
| Τ    | Tau       | U+03A4  | Tau              |
| Υ    | Upsilon   | U+03A5  | Upsilon          |
| Φ    | Phi       | U+03A6  | Phi              |
| Χ    | Chi       | U+03A7  | Chi              |
| Ψ    | Psi       | U+03A8  | Psi              |
| Ω    | Omega     | U+03A9  | Omegagreek       |

> ファイル名にはマルチバイト文字を用いず、ローマ字ステム（`char_Alpha` 等）を使用する。
> グリフ名の `Deltagreek` / `Omegagreek` は U+2206(∆)・U+2126(Ω) との衝突回避のための
> フォント内部名で、コードポイント経由で自動解決される。

## パイプライン

```
assets/fonts/Secvier.otf
  └─ extract_glyphs.py --charset greek
       └─ src/alphanum_greek/char_{Alpha..Omega}.svg   （アウトライン化, 24枚）
            └─ render_svg2png.py -c greek
                 └─ svg2png/alphanum_greek/char_*.png  （黒字白背景マスク, 512px）
                      └─ generate_dualmode.py (build_greek)
                           └─ dist/alphanum_greek_dualmode/{variant}/char_*_{512,128}.png
```

- **バリアント**: 英数字と同一の 6 種
  （seiyuu 星幽 / suigyoku 翠玉 / kougyoku 紅玉 / hakuji 白磁 / kokuji 黒磁 / sakin 砂金）
- **出力サイズ**: 512px（高解像度）/ 128px（標準絵文字）
- **スタイル**: 二重縁取り（外ハロー＋内キーライン＋宝石ボディ縦グラデ）。英数字と共通の `render()`。
- 枠付き通常版は `generate_all_v3.py`（5 バリアント）が `dist/alphanum_greek/{variant}/` に出力。

## Misskey インポート

`build_misskey_zip.py` の `_collect_greek()` が
`dist/alphanum_greek_dualmode/{variant}/char_*_128.png` を収集し、
カテゴリ `Secvier/06.ギリシャ文字_{バリアント名}` として梱包する。

- 絵文字名: `sv_{variant}_greek_{Name}`（例: `sv_seiyuu_greek_Alpha`）
- エイリアス: ローマ字名・小文字名・ギリシャ文字・バリアントキー・バリアント和名
  （例: `["Alpha", "alpha", "Α", "seiyuu", "星幽"]`）
- ライセンス: 標準（RadianN_kswg / ラジアン（柏木主税）, CC BY 4.0。外部素材なし）

## 合計枚数

- デュアルモード: 6 バリアント × 24 字 × 2 サイズ = **288 枚**
- Misskey 梱包（128px）: 6 バリアント × 24 字 = **144 エントリ**
- 枠付き通常版: 5 バリアント × 24 字 = **120 枚**

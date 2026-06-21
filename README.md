# Secvier ImageAssets

独自フォント **Secvier**（作字：RadianN_kswg / ラジアン（扇二春・柏木主税））を用いた絵文字アセット群です。

## 収録内容

| カテゴリ | 内容 |
|---|---|
| トランプ | ♠♥♦♣ × A,2–10,J,Q,K + ジョーカー（計53枚） |
| ダイス | D4 / D6 / D8 / D10 / テンズテン / D12 / D20 |
| 麻雀牌 | 萬子1–9 / 筒子1–9 / 索子1–9 / 字牌（東南西北中發白） |
| 英数字 | A–Z（大文字）/ 0–9 |

## ディレクトリ構成

```
Secvier_ImageAssets/
├── _original-fonts/     # 原本フォントファイル（作者保管用）
├── assets/
│   └── fonts/
│       └── Secvier.otf  # ビルドで参照するフォント
├── src/                 # SVGソースファイル
│   ├── templates/       # ベーステンプレート
│   ├── cards/           # トランプ
│   ├── dice/            # ダイス
│   ├── mahjong/         # 麻雀牌
│   └── alphanum/        # 英数字
├── dist/                # 出力PNG（各72×72px, 512×512px）
│   ├── cards/
│   ├── dice/
│   ├── mahjong/
│   └── alphanum/
├── scripts/             # ビルドスクリプト
│   ├── build.py         # 一括ビルド
│   ├── render_svg.py    # フォント→SVG生成
│   └── export_png.py    # SVG→PNG書き出し
└── docs/                # 制作ドキュメント
```

## セットアップ

```bash
# Python 3.11+ 推奨
pip install -r requirements.txt

# フォント情報の確認
python scripts/inspect_font.py

# 全カテゴリビルド
python scripts/build.py

# 特定カテゴリのみ
python scripts/build.py --category cards
python scripts/build.py --category dice
python scripts/build.py --category mahjong
python scripts/build.py --category alphanum
```

## 出力仕様

- フォーマット: SVG（マスター）/ PNG（配布用）
- サイズ: 72×72px（標準絵文字）/ 512×512px（高解像度）
- 背景: 透過
- カラーモード: sRGB

## ライセンス

**CC BY 4.0** — [クリエイティブ・コモンズ 表示 4.0 国際](https://creativecommons.org/licenses/by/4.0/deed.ja)

著作者：RadianN_kswg / ラジアン（扇二春・柏木主税）

利用時はクレジット表記をお願いします：
```
Secvier font & emoji assets by RadianN_kswg / ラジアン（扇二春）
CC BY 4.0 https://creativecommons.org/licenses/by/4.0/
```

## フォントについて

Secvier は RadianN_kswg / ラジアン（扇二春・柏木主税）が独自に作字したフォントです。
本リポジトリの絵文字アセットは、このフォントのグリフをベースに制作されています。

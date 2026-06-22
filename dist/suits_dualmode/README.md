# suits_dualmode — ライト/ダーク両モード対応 透過スート絵文字

Secvier スートマーク（`svg2png/suits/`）を alphanum と同一の二重縁取りで加工した
**背景透過PNG**。有彩色は `dist/cards` の4色デック配色に対応します。

## スート × 配色（各2種のみ）

| スート    | 配色1          | 配色2         |
| --------- | -------------- | ------------- |
| ♠ spade   | `blue`（青）   | `black`（黒） |
| ♥ heart   | `red`（赤）    | `white`（白） |
| ♦ diamond | `yellow`（黄） | `white`（白） |
| ♣ club    | `green`（緑）  | `black`（黒） |

## ファイル

```
dist/suits_dualmode/{suit}_{color}_{512|128}.png
例: spade_blue_512.png / heart_white_128.png
```

サイズ: `512`（高解像）/ `128`（標準絵文字）

## 生成

```bash
python scripts/generate_dualmode.py
```

---

© RadianN_kswg / ラジアン（柏木主税） — Secvier font — **CC BY 4.0**

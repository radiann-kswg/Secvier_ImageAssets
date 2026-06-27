# 麻雀牌 プロトタイプ SVG 仕様（Secvier 意匠 / 第3回添削反映）

生成: `scripts/generate_mahjong_proto.py`
中央字形: `scripts/extract_dela_kanji.py`（Dela Gothic One から漢字を抽出）
出力: `src/mahjong/mj_*.svg`（牌）, `src/mahjong/parts/*.svg`（最小部品）

## キャンバス・外枠

- アスペクト比 **5:7**（`360 × 504`）。
- 外枠はトランプ（♦）寄りの白角丸フレーム。**白牌でも視認できるよう太め**
  （外枠 stroke 9px ＋ 内側キーライン 4px）。
- **隅インデックス**：全牌の右上・左下（左下は 180°回転）。
  - 数牌＝番号＋スートマーク（萬子 `SV` / 索子 `I` / 筒子 `O`）
  - 字牌＝アルファベット（右上 E,S,W,N,H,G ／ 左下 E,S,W,N,T,B）
  - 季節牌＝英単語を Joker 風に縦書き

## 配色

赤(紅玉) `#B81430` / 緑(翠玉) `#218A48` / 紺・青(星幽) `#26346F` / 字色 `#1E1E2A`
赤ドラ 鮮赤 `#EC1B3A`

xhokir の絵柄色（一索の鳥・季節牌の花）は Secvier バリアントへ写像:
緑 `#004900`→翠玉 `#218A48` ／ 紺 `#00001b`→星幽 `#26346F` ／ 赤 `#b93c3c`→紅玉 `#B81430`。
筒子＝紺＋赤、索子＝緑＋赤 の各牌の色パターンも xhokir に一致させた。

## 各カテゴリ

| カテゴリ | 中央意匠 | 配置・配色 |
| --- | --- | --- |
| 萬子 1–9 | 数字（黒）＋ `SV`（赤）。他カテゴリと同程度のサイズに縮小 | — |
| 筒子 1–9 | Secvier "O" の**回転対称コイン**（輪と中心●を同心円に補正） | **xhokir 準拠の配色（紺＋赤・緑なし）**。三筒・七筒の斜めは**右肩下がり** |
| 索子 2–9 | Secvier "I"（端セリフ＝節）の**長さ方向対称の竹** | xhokir 準拠の配色（緑＋赤）。七索＝上1(赤)＋下3列×2行、八索＝左右端4本垂直・中4本を傾斜、九索＝中列を赤 |
| 索子 1 | **FluffyStuff(CC0) の麻雀牌「一索」鳥イラスト**（拡大配置） | — |
| 風牌 東南西北 | **Dela Gothic One** の漢字（紺・拡大）。Secvier に近い幾何字形 | E/S/W/N（両隅同字） |
| 三元牌 發 | Dela Gothic 漢字 發（緑・拡大） | 右上 H / 左下 T |
| 三元牌 中 | Dela Gothic 漢字 中（赤・拡大） | 右上 G / 左下 B |
| 三元牌 白 | なし | 外枠のみ |
| 季節牌 春夏秋冬 | **xhokir の花の絵柄**（一索と同位置・同サイズ）＋**季節漢字を右上に赤** | 英単語を**90°回転**（上下端から読める） |
| 赤ドラ 5m/5p/5s | 通常5牌の印字を鮮赤に置換 | `mj_{man,pin,sou}_5_red.svg` |

## 外部素材とライセンス（`src/ext_mahjong/CREDITS.md` 参照）

| 用途 | 素材 | 出典 | ライセンス |
| --- | --- | --- | --- |
| 季節牌の花の絵柄 | `season{1-4}_cc_by.svg` | xhokir/riichi-mahjong-tiles（FluffyStuff 由来・季節牌追加版） | **CC BY 4.0** |
| 一索の鳥 | `ichisou_bird_cc0.svg` | FluffyStuff/riichi-mahjong-tiles（xhokir Sou1 と同一） | **CC0**（PD） |
| 字牌・季節牌 漢字 | `assets/fonts/delagothicone/`（サブセット） | Dela Gothic One | **SIL OFL 1.1** |

- 本リポジトリは **CC BY 4.0**。xhokir の季節牌（CC BY 4.0）は ShareAlike が無いため**そのまま継承可能**
  （表示・改変明示は `src/ext_mahjong/CREDITS.md` に記載）。
- OFL 第5条より抽出字形 SVG は OFL の制約を受けず CC BY 4.0 で配布可。CC0 も互換。
- 不採用素材: Wikimedia(Cangjie6 系)＝多くが **CC BY-SA**（ShareAlike）で非互換／
  thetrev68・hifukasawa 等＝**LICENSE 不記載（全権利留保）**。

## 命名（AGENTS.md 準拠）

- 数牌: `mj_{man,pin,sou}_{1-9}.svg`、赤ドラ `mj_{man,pin,sou}_5_red.svg`
- 字牌: `mj_char_{east,south,west,north,hatsu,chun,haku}.svg`
- 季節牌: `mj_season_{spring,summer,autumn,winter}.svg`
- 部品: `parts/{sou_stick,pin_coin,letter_*}.svg`

## 実行

```bash
python scripts/extract_dela_kanji.py     # 字牌・季節牌の漢字を抽出（同梱フォント使用）
python scripts/generate_mahjong_proto.py # 牌・部品を生成
```

著作権者: RadianN_kswg / ラジアン（柏木主税） / CC BY 4.0

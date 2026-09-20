# bvmap — Claude Code 引き継ぎドキュメント

このファイルは `dwg7/bvmap` リポジトリのルートに置く、Claude Code向けの
プロジェクト文脈。新しいセッションを開始する際は、まずこのファイルを
読んでください。

過去の経緯・決定事項は `docs/decisions/` のADRに詳しく記録されています。
特に[0004](docs/decisions/0004-vertical-choonpu-workaround-does-not-work.md)、
[0005](docs/decisions/0005-goal-change-master-repo-and-starlight-polish.md)、
[0006](docs/decisions/0006-hfu-stars-is-already-master-repo.md)は
本プロジェクトの現在の目標を理解する上で必須です。

ADRが「経緯・判断の一次記録」であるのに対し、[docs/bvmap-starlight-cartographic-design.md](docs/bvmap-starlight-cartographic-design.md)は
地図技術者向けに書いた「結果として何を設計したか」の読み物です。GSI
`bvmap-dark` から帰納した地図学的知識(レイヤー順序体系、陸海の3層メヌエット、
道路・鉄道・建物のティア構造、色の意味体系等)を、`starlight-input.yaml`
と同期させてまとめています。新しいセッションで全体像を素早く掴みたい時は
ADRを1つずつ読むより先にこちらが役立ちます。

姉妹プロジェクト: [dwg7/kaga0](https://github.com/dwg7/kaga0/blob/main/CLAUDE.md)、
[dwg7/zukaku](https://github.com/dwg7/zukaku/blob/main/CLAUDE.md)(同じ「実装より先に調査」
という作法を踏襲)

## 1. 現在の目標(2026-09-20時点)

当初の目標([UNopenGIS/7#1012](https://github.com/UNopenGIS/7/issues/1012)、
縦書き棒音符「ー」対応)は、調査の結果MapLibre GL JSの現在の描画パイプライン
では回避策が機能しないことが判明したため終了した
([0004](docs/decisions/0004-vertical-choonpu-workaround-does-not-work.md))。
issue自体はコメントの上クローズ済み。

続けて「本リポジトリをstars.optgeo.orgのマスターリポジトリとして確立する」
という目標を立てたが、[`hfu/stars`](https://github.com/hfu/stars)が既に
その役割(`styles/`ディレクトリがMartinの配信設定`config/martin.yaml`から
直接参照され、`stars.optgeo.org/style/bvmap-dark`等を配信している)を
3週間前から果たしていたことが判明し、撤回した
([0006](docs/decisions/0006-hfu-stars-is-already-master-repo.md))。

**現在の目標は以下の1点**:

- **`bvmap-starlight`という名前にふさわしい、実際に磨き上げられたスタイルを
  開発する**。方向性は低彩度・明るめ・銀灰色寄り
  ([0003](docs/decisions/0003-bvmap-starlight-naming.md))

この目標に向けて、`generator/`(`docs/decisions/0009`以降)という
「`bvmap-dark.json`から`bvmap-starlight.json`を生成する」仕組みを構築した。
2段階で進めている:

- **Stage 1(再現優先、完了)**: `bvmap-dark.json`を寸分違わず再現できる
  ジェネレータを作ることで、GSIの実装イディオム(共有テーブル+疎な例外、
  等)を実地で検証した。123レイヤー中95レイヤーがYAML駆動で生成・
  28レイヤーがid参照つきのリテラル保持([0028](docs/decisions/0028-anno-remaining-layers-implemented.md)時点)
- **Stage 2(配色磨き上げ、進行中)**: `bvmap-dark.json`との差分が意図的に
  生まれることを前提に切り替えた([0029](docs/decisions/0029-assemble-writes-starlight-json.md))。
  「見た目の改善」(配色そのもの、[0030](docs/decisions/0030-starlight-first-color-pass.md)で第一稿)と、
  「見えないところの改善」(expressionの近代化・性能/柔軟性の向上・
  `patches`のネイティブ生成への移行、[0031](docs/decisions/0031-expression-modernization-rgb-normalization.md)から開始)
  を並行して進める方針。スプライト(GSIアイコン119個)のグレースケール化にも着手
  ([0036](docs/decisions/0036-sprite-grayscale-raster-exception.md)、`sprite/`ディレクトリ参照)。
  `glyphs`は`stars.optgeo.org`自前配信へ切り替え済み([0037](docs/decisions/0037-glyphs-hosting-switch.md))。
  `sprite`もホストURLが決まり次第同様に切り替える(`starlight-input.yaml`の`hosting:`セクション)

進め方の作法(探索的アプローチ・ケース・カンファレンス形式・ADR記録)は
`docs/decisions/`に蓄積されている。次のセッションは`HANDOVER.md`も参照。

## 2. リポジトリの役割分担(重要)

- **`dwg7/bvmap`(本リポジトリ)**: スタイル開発専用のワークスペース。配色
  調整・実験・比較検証(`examples/style-preview.html`)を行う場。ここは
  マスターリポジトリではない
- **`hfu/stars`**: 実際の配信設定・PR先。`config/martin.yaml`の
  `styles.paths: [/home/stars/styles]`から`stars.optgeo.org/style/<name>`
  が配信される。`bvmap-starlight`の配色調整が完成したら、
  `hfu/stars/styles/`へPRまたはファイルコピーの形で反映する
  ([0006](docs/decisions/0006-hfu-stars-is-already-master-repo.md))

新しいセッションを始める際は、**まず`hfu/stars`(特に`styles/`ディレクトリと
`docs/KNOWN_FACTS.md`)の最新状態を確認すること**。本リポジトリの
`style/bvmap-dark.json`はある時点のスナップショットであり、`hfu/stars`側で
継続的に更新されている可能性がある。

## 3. リポジトリ構成

```
dwg7/bvmap/
├── CLAUDE.md                          # このファイル
├── HANDOVER.md                        # セッション間引き継ぎ、次にやることの優先順
├── LICENSE
├── .gitignore                         # examples/vendor/ (CDNブロック環境向けのローカル退避先)
├── style/
│   ├── bvmap-dark.json                # stars.optgeo.org配信版のスナップショット、無加工
│   ├── bvmap-starlight.json           # generator/assemble.pyが書き出す生成結果(手動編集しない)
│   └── bvmap-starlight.md             # bvmap-starlightの説明
├── generator/
│   ├── starlight-input.yaml           # ジェネレーターの入力(palette・categories・
│   │                                   # priority_chains・layers・patches)
│   ├── load_input.py                  # YAMLを読み込みMapLibre式に変換
│   ├── assemble.py                    # 全123レイヤーを組み立て、bvmap-starlight.jsonへ書き出す
│   ├── tier_template.py               # 道路・鉄道・建物の複合ティア構造
│   ├── category_table.py              # vt_code(等)対応表→match式のフラットコンパイラ
│   ├── road_color.py / zl410_road_color.py / rail_tunnel_color.py / anno_symbol_color.py
│   │                                   # 優先順位付きcase連鎖等、flat_matchでは表現できない構造
│   ├── building_color.py              # 検証用(実運用はcategory_table.py経由)
│   ├── cool_transform.py              # Starlightの配色変換式(0030)の実コード版
│   └── sprite_grayscale.py            # スプライトのグレースケール化(0036)
├── sprite/
│   ├── std.png / std.json (+@2x)      # GSIオリジナルのスナップショット、無加工
│   └── bvmap-starlight.png / .json (+@2x)  # sprite_grayscale.pyの生成結果
├── docs/
│   └── decisions/                     # ADR(0001〜)。過去の調査・決定の一次情報源
└── examples/
    └── style-preview.html             # bvmap-dark/bvmap-starlight比較用プレビュー
                                        # (要: python3 -m http.server 等でローカル配信)
```

`style/bvmap-starlight.json`を配色調整したい場合は、このファイルを直接
編集せず、`generator/starlight-input.yaml`のpaletteセクションを編集して
`python3 generator/assemble.py`を実行すること(直接編集すると次回の
`assemble.py`実行で上書きされる)。同様に`sprite/bvmap-starlight.png`/`.json`も
直接編集せず、`python3 generator/sprite_grayscale.py`を実行すること。

## 4. 作業分担

- Claude Codeが担当してよい範囲: `bvmap-starlight`の配色調整・実験、
  `hfu/stars`への反映(PR作成)、`docs/decisions/`へのADR記録
- 人の手を残す範囲: `hfu/stars`側へのPRのマージ、本番反映のタイミング判断
  (運用上の影響が大きいため)

## 5. 現時点でのステータス

- [x] issue #1012 の内容確認・対応・クローズ(縦書き棒音符は将来のMapLibre
      GL JS本体の対応を待つ、[0004](docs/decisions/0004-vertical-choonpu-workaround-does-not-work.md)参照)
- [x] `gh`による認証済み横断検索での重複リポジトリ確認
      ([0001](docs/decisions/0001-duplicate-repository-check.md))
- [x] `style/bvmap-dark.json`をstars.optgeo.orgから取得・配置
- [x] `hfu/stars`が既にマスターリポジトリであることの確認
      ([0006](docs/decisions/0006-hfu-stars-is-already-master-repo.md))
- [x] ジェネレーターのStage 1(再現優先)完了。123レイヤー中95レイヤーが
      YAML駆動で生成、残り28レイヤーはid参照つきリテラル保持
      ([0009](docs/decisions/0009-generator-architecture-direction.md)〜[0028](docs/decisions/0028-anno-remaining-layers-implemented.md))
- [x] `generator/assemble.py`が`style/bvmap-starlight.json`へ実際に書き出す
      ([0029](docs/decisions/0029-assemble-writes-starlight-json.md))
- [ ] `bvmap-starlight`の配色磨き上げ(低彩度・明るめ・銀灰色寄り)——
      第一稿は着手済み([0030](docs/decisions/0030-starlight-first-color-pass.md))、継続中
- [ ] 「見えないところの改善」(expression近代化・`patches`のネイティブ生成
      移行等)——第一弾着手済み([0031](docs/decisions/0031-expression-modernization-rgb-normalization.md))、継続中
- [x] `hfu/stars`へのPR作成・反映([hfu/stars#12](https://github.com/hfu/stars/pull/12)、
      2026-09-20マージ・本番配置済み。`https://stars.optgeo.org/style/bvmap-starlight`で配信中。
      配色磨き上げ・「見えないところの改善」は今後も継続——反映は一度きりでなく都度PRする)

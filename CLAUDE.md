# bvmap — Claude Code 引き継ぎドキュメント

このファイルは `dwg7/bvmap` リポジトリのルートに置く、Claude Code向けの
プロジェクト文脈。新しいセッションを開始する際は、まずこのファイルを
読んでください。

過去の経緯・決定事項は `docs/decisions/` のADRに詳しく記録されています。
特に[0004](docs/decisions/0004-vertical-choonpu-workaround-does-not-work.md)、
[0005](docs/decisions/0005-goal-change-master-repo-and-starlight-polish.md)、
[0006](docs/decisions/0006-hfu-stars-is-already-master-repo.md)は
本プロジェクトの現在の目標を理解する上で必須です。

姉妹プロジェクト: [dwg7/kaga0](https://claude.ai/kaga0/CLAUDE.md)、
[dwg7/zukaku](https://claude.ai/zukaku/CLAUDE.md)(同じ「実装より先に調査」
という作法を踏襲)

## 1. 現在の目標(2026-09-19時点)

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
  ([0003](docs/decisions/0003-bvmap-starlight-naming.md))。配色調整はまだ
  未着手(`style/bvmap-starlight.json`は現時点で`bvmap-dark.json`と`name`
  フィールドのみ異なる)

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
├── LICENSE
├── .gitignore                         # examples/vendor/ (CDNブロック環境向けのローカル退避先)
├── style/
│   ├── bvmap-dark.json                # stars.optgeo.org配信版のスナップショット、無加工
│   ├── bvmap-starlight.json           # 配色磨き上げ用(現時点でbvmap-darkと同一)
│   └── bvmap-starlight.md             # bvmap-starlightの説明
├── docs/
│   └── decisions/                     # ADR。過去の調査・決定の一次情報源
└── examples/
    └── style-preview.html             # bvmap-dark/bvmap-starlight比較用プレビュー
                                        # (要: python3 -m http.server 等でローカル配信)
```

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
- [ ] `bvmap-starlight`の配色磨き上げ(低彩度・明るめ・銀灰色寄り)
- [ ] `hfu/stars`へのPR作成・反映

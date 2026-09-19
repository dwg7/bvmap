# bvmap — Claude Code 引き継ぎドキュメント

このファイルは `dwg7/bvmap` リポジトリのルートに置く、Claude Code向けの
プロジェクト文脈。新しいセッションを開始する際は、まずこのファイルを
読んでください。

過去の経緯・決定事項は `docs/decisions/` のADRに詳しく記録されています。
特に[0004](docs/decisions/0004-vertical-choonpu-workaround-does-not-work.md)と
[0005](docs/decisions/0005-goal-change-master-repo-and-starlight-polish.md)は
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

現在の目標は以下の2点([0005](docs/decisions/0005-goal-change-master-repo-and-starlight-polish.md)):

1. **`stars.optgeo.org`のbvmap系style.jsonのマスターリポジトリとして、
   本リポジトリを確立する**。現状、bvmap-darkの管理元はstars.optgeo.org
   自体にあり、GitHub上にソースを持つリポジトリは存在しない
   ([0001](docs/decisions/0001-duplicate-repository-check.md))。まだ着手
   していない調査項目: stars.optgeo.orgが現在どうデプロイ・運用されて
   いるか(サーバー側の構成、更新の仕組み)
2. **`bvmap-starlight`という名前にふさわしい、実際に磨き上げられた
   スタイルをstars.optgeo.orgに提供する**。方向性は低彩度・明るめ・
   銀灰色寄り([0003](docs/decisions/0003-bvmap-starlight-naming.md))。
   配色調整はまだ未着手(`style/bvmap-starlight.json`は現時点で
   `bvmap-dark.json`と`name`フィールドのみ異なる)

`stars.optgeo.org`側への実際の反映(このリポジトリを真にマスターにする
切り替え作業)は運用影響が大きいため、実行判断は藤村さんに委ねる。本
リポジトリでの作業は「反映できる状態を整える」ところまで。

## 2. リポジトリ構成

```
dwg7/bvmap/
├── CLAUDE.md                          # このファイル
├── LICENSE
├── .gitignore                         # examples/vendor/ (CDNブロック環境向けのローカル退避先)
├── style/
│   ├── bvmap-dark.json                # stars.optgeo.org配信版、無加工
│   ├── bvmap-starlight.json           # 配色磨き上げ用(現時点でbvmap-darkと同一)
│   └── bvmap-starlight.md             # bvmap-starlightの説明
├── docs/
│   └── decisions/                     # ADR。過去の調査・決定の一次情報源
└── examples/
    └── style-preview.html             # bvmap-dark/bvmap-starlight比較用プレビュー
                                        # (要: python3 -m http.server 等でローカル配信)
```

## 3. 作業分担

- Claude Codeが担当してよい範囲: style.jsonの取得・配置・配色調整、
  stars.optgeo.orgのデプロイ構成の調査、`docs/decisions/`へのADR記録
- 人の手を残す範囲: `stars.optgeo.org`側への実際の反映方法の最終判断
  (このリポジトリを新たなマスターにするか、既存の配信の仕組みを変える
  かは、運用上の影響が大きいため、実装後に人が判断する)

## 4. 現時点でのステータス

- [x] issue #1012 の内容確認・対応・クローズ(縦書き棒音符は将来のMapLibre
      GL JS本体の対応を待つ、[0004](docs/decisions/0004-vertical-choonpu-workaround-does-not-work.md)参照)
- [x] `gh`による認証済み横断検索での重複リポジトリ確認
      ([0001](docs/decisions/0001-duplicate-repository-check.md))
- [x] `style/bvmap-dark.json`をstars.optgeo.orgから取得・配置
- [ ] stars.optgeo.orgのデプロイ・運用構成の調査(マスターリポジトリ化の前提)
- [ ] `bvmap-starlight`の配色磨き上げ(低彩度・明るめ・銀灰色寄り)
- [ ] `stars.optgeo.org`側への反映方法の判断(藤村さん)

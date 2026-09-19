# 0005: 目標変更 — マスターリポジトリの確立とstarlightの配色磨き上げ

## 経緯

[UNopenGIS/7#1012](https://github.com/UNopenGIS/7/issues/1012)(縦書き棒音符「ー」対応)を発端に本リポジトリでの作業を開始したが、[0004](0004-vertical-choonpu-workaround-does-not-work.md)の通り、提案されていた回避策がMapLibre GL JSの現在の描画パイプラインでは機能しないことが判明した。ネイティブ対応(PR #8399等)は未マージで、userland側では完結しない。

この時点で、本リポジトリの目標を以下の2点に変更する。**縦書き棒音符問題への対応は目標から外す**([0004](0004-vertical-choonpu-workaround-does-not-work.md)の通り、将来のMapLibre側の進捗を待つ)。

## 新しい目標

1. **`stars.optgeo.org`のbvmap系style.jsonのマスターリポジトリとして、本リポジトリ(`dwg7/bvmap`)を確立する**。[0001](0001-duplicate-repository-check.md)で確認した通り、現状`bvmap-dark`の管理元はstars.optgeo.org自体にあり、GitHub上にソースを持つリポジトリは存在しない。この状態を解消し、本リポジトリを一次情報源にする
2. **`bvmap-starlight`という名前にふさわしい、実際に磨き上げられたstyleをstars.optgeo.orgに提供する**。[0003](0003-bvmap-starlight-naming.md)で決めた方向性(低彩度・明るめ・銀灰色寄り)の配色調整を、実際に手を動かして仕上げる

## 含意

- `style/bvmap-dark.json`(無加工のまま保持)と`style/bvmap-starlight.json`(縦書き回避策は撤去・配色磨き上げに転用)の位置づけが変わる。`bvmap-starlight.json`から`text-font: ["Choonpu"]`パッチを取り除き、配色調整用のベースとして再利用する
- 「マスターリポジトリとして確立する」ために、stars.optgeo.orgが現在どうデプロイ・運用されているか(サーバー側の構成、更新の仕組み)を調査する必要がある。これは新規の調査項目
- `stars.optgeo.org`側への実際の反映(このリポジトリを真にマスターにする切り替え作業)は引き続き運用影響が大きいため、実行判断は藤村さんに委ねる。本リポジトリでの作業は「反映できる状態を整える」ところまで

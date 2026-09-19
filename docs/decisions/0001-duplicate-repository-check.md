# 0001: 重複リポジトリ確認の結果

## 背景

[UNopenGIS/7#1012](https://github.com/UNopenGIS/7/issues/1012)着手前に、CLAUDE.mdの指示に従い`gh`の認証済み横断検索(`gh search code`、`gh repo list`)でbvmap-dark/optimal_bvmap関連の既存リポジトリを再確認した(2026-09-19)。公開Web検索ベースの手動調査だけでは`hfu/bvmap`の存在を見落としていたため。

## 確認した候補と判断

| リポジトリ | 更新時期 | 判断 |
|---|---|---|
| `hfu/bvmap` | 2025-07(1年以上前) | **不採用**。`style/std.ts`(123レイヤー、GSI `std.json`の忠実な移植で縦書きレイヤーも含む)を持つが、14ヶ月間更新が無くstars.optgeo.orgの現行配信版との一致が未検証。「starsにある現行style.jsonの品質を下げない」という前提のもと、参考情報としてのみ扱い、実装基盤には使わない |
| `optgeo/optbv-charites` | 2022-09 | 不採用。`@unvt/charites`ベースの旧世代アプローチ、命名も`optbv`(bvmapの前身) |
| `optgeo/optbv-intl` | 2022-09 | 不採用。同上 |
| `optgeo/toki` | (手動調査で既確認) | 不採用。experimental_bvmap向けの旧アプローチ |
| `optgeo/bvmap-overdrive` | 2025-12 | 不採用。MVT→MLT変換の実験であり、スタイリングとは無関係 |

`stars.optgeo.org/style/bvmap-dark`を実際に管理しているGitHubリポジトリは見つからなかった(`dwg7/kaga0`のADR 0014でも、bvmap-darkはstars.optgeo.orgから都度fetchしているだけでソースはGitHub上に無いことが裏付けられている)。CLAUDE.mdが定めた「管理リポジトリが見つかったら中断」の条件には該当せず、本リポジトリでの作業を継続する。

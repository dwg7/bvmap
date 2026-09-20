# 0018: 道路のvt_rdctg駆動色は、フラットなカテゴリ表コンパイラでは再現できない

[HANDOVER.md](../../HANDOVER.md)の次ステップ②「道路の`vt_rdctg`駆動色([0010](0010-color-semantic-categories.md))と建物の塗り/輪郭を、カテゴリ表コンパイラで再現できるか検証」の結果。`generator/road_color.py`、`generator/building_color.py`。

## 結果

**建物**(塗り・輪郭とも)は、`category_table.py`の`compile_match_expression()`を無改造のまま適用して完全一致した——Anno text-color/text-fontに続く3例目の確認([0017](0017-category-table-generator-stage1.md))。

**道路のvt_rdctg駆動色は、同じコンパイラでは再現できない**。実データを分解した結果、[0010](0010-color-semantic-categories.md)の当初の表は誤りを含んでいたことが判明した。

## 0010の訂正

[0010](0010-color-semantic-categories.md)は次の表を「道路種別の色」として提示した:

```
vt_motorway == 1        -> gray(157)
vt_rdctg = 国道          -> gray(160)
vt_rdctg = 都道府県道     -> gray(226)
vt_rdctg = 市区町村道等   -> gray(100)
vt_rdctg = 高速自動車国道等 -> gray(157)
vt_rdctg = その他/不明    -> gray(100)
```

実際に`bvmap-道路中心線色{0-4}`・`bvmap-道路中心線色橋{0-4}`のline-color式を分解すると、**この表は`vt_code`が橋梁関連(2704, 2714)の場合の分岐にのみ存在する**。橋梁関連でない一般の道路(大多数)では、`vt_rdctg`のmatchは`国道`・`都道府県道`・`高速自動車国道等`の3キーしか持たず、`市区町村道等`・`その他`・`不明`はこのmatchの対象にすらならず、**`vt_rnkwidth`(道路幅員ランク)/`vt_code`駆動の別の表**にフォールスルーする:

```
一般の道路(vt_codeが2704/2714でない場合):
  vt_motorway == 1        -> gray(157)  # 種別を問わず優先、変更なし
  vt_rdctg = 国道          -> gray(160)
  vt_rdctg = 都道府県道     -> gray(226)
  vt_rdctg = 高速自動車国道等 -> gray(157)
  それ以外(市区町村道等/その他/不明を含む) ->
    vt_code in [2721,2722,2723] -> gray(173)
    vt_code in [2731,2732,2733] -> gray(200)
    default                  -> gray(255)
    (zoom<14のみ: vt_rnkwidth=="3m-5.5m未満"の場合は上記より先にgray(173))

橋梁関連(vt_code in [2704,2714])の場合のみ、0010の元の表がそのまま使われる
(alphaが0.5になる以外は同じ):
  vt_motorway == 1        -> gray(157)
  vt_rdctg = 国道          -> gray(160)
  vt_rdctg = 都道府県道     -> gray(226)
  vt_rdctg = 市区町村道等   -> gray(100)
  vt_rdctg = 高速自動車国道等 -> gray(157)
  vt_rdctg = その他/不明    -> gray(100)
  default(この分岐内)      -> gray(100)
```

つまり「市区町村道等はgray(100)」は一般則ではなく、橋梁関連vt_code限定の値だった。一般の市区町村道等の色は、道路種別ではなく**幅員**(`vt_rnkwidth`/`vt_code`)で決まる——GSIの意図としては筋が通る(市区町村道等は種別内の幅員差が大きいので、種別より幅員で塗り分ける方が地図として意味がある)が、[0010](0010-color-semantic-categories.md)を書いた時点ではこの分岐(橋梁vt_code分岐)の中身を未確認のまま「別途確認」とだけ書いており、それが一般則だという仮の仮定のまま表を作ってしまっていた。

## なぜフラットなコンパイラでは再現できないか

`compile_match_expression(categories, property_table)`は「1つのプロパティ(`vt_code`)→1段の`match`」という形を前提にしている。道路色は:

1. `vt_code`(橋梁関連かどうか)による分岐選択
2. `vt_motorway`による優先上書き
3. `vt_rdctg`による`match`
4. その`match`のdefaultが、さらに`vt_rnkwidth`/`vt_code`による別の`match`にフォールスルー
5. さらにzoom(`step`)でtier0のみ追加のvt_rnkwidth=="不明"transparent分岐がある(これは[tier_template.py](../../generator/tier_template.py)がテンプレートごとリテラル保持することで既に対応済み、本ADRのスコープ外)

という、**複数プロパティにまたがる優先順位付きcase連鎖**であり、単一プロパティのフラットな表引きではない。`generator/road_color.py`は、この構造を「橋梁表」「一般表」「幅員フォールバック」という名前付きの部品に分解し、9/10レイヤー(tier0の`色0`以外)で完全一致を確認した——ただし`compile_match_expression()`を流用したのではなく、専用の組み立て関数を新規に書いた。

## 含意: コンパイラは1種類に統一できない

[0009](0009-generator-architecture-direction.md)の「色・フォント・アイコンは同じイディオムで実装できる」という仮説は、**単一プロパティのカテゴリ表**については3例(Anno text-color、text-font、建物塗り/輪郭)で裏付けられたが、**複数プロパティにまたがる優先順位付きロジック**(道路色)は別の形が必要——という結論になった。無理に1つのコンパイラに統合しようとせず、「フラット表引き」と「優先順位付きcase連鎖」の2つの部品を、必要な箇所でそれぞれ使う設計とする([0015](0015-unification-vs-semantic-separation.md)の「統合よりセマンティックな分離」の方針とも整合する)。

## Stage 1の進捗(更新)

- 道路・鉄道・建物の複合ティア構造([0016](0016-tier-generator-stage1.md)): 65/70完全一致
- カテゴリ表コンパイラ(Anno text-color/text-font、建物塗り/輪郭): 完全一致、`compile_match_expression()`単体で3例確認
- 道路vt_rdctg駆動色: 専用の優先順位付きcase連鎖として9/10完全一致(tier0の1例外は[0016](0016-tier-generator-stage1.md)がリテラル保持で対応済み)

まだ手を付けていない: 背景/AdmArea/WAの「踊り」、注記シンボル付きレイヤーの`let`包装パターン([0017](0017-category-table-generator-stage1.md)の未検証節)、その他の個別レイヤー(Cntr/Isbt/WStrA等)。

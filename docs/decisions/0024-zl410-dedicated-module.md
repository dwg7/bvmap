# 0024: ZL4-10専用モジュールの新設

[0022](0022-zl4-10-and-post-tier-layers-footprint.md)の③(ZL4-10)を実装した。`generator/zl410_road_color.py`。

## 結果

**PASS**。ZL4-10の3層(`bvmap-道路中心線ZL4-10国道`/`高速`/`bvmap-鉄道中心線ZL4-10`)全てを、専用の優先順位付きcase連鎖(道路2層)とカテゴリ表コンパイラ(鉄道1層)で再現した。Stage 1の123/123完全一致は維持(35 literal / 88 generated)。

## 実装して初めて分かった追加の事実

**国道レイヤーと高速レイヤーは、1つのテーブルを共有していなかった**。[0022](0022-zl4-10-and-post-tier-layers-footprint.md)の時点では「ZL4-10は独自のテーブルを持つ」までは分かっていたが、tierの`色`/`色橋`のように**2つのZL4-10道路レイヤー同士が同じテーブルを共有している**だろうと予想していた。実装のために2層のJSONを一字一句突き合わせたところ、**予想は外れた**:

- `道路中心線ZL4-10国道`の橋梁分岐は`vt_motorway`チェックを経てから`vt_rdctg`のmatchに入る(tierの一般道テーブルと同じ構造)
- `道路中心線ZL4-10高速`の橋梁分岐は`vt_motorway`チェックを一切経ず、直接`vt_rdctg`のmatchに入る

**もっともらしい理由**: `道路中心線ZL4-10高速`のfilterは`vt_rdctg=="高速自動車国道等"`だけに絞られており、この値は常にgray(157)(motorwayと同じ色)になる。つまりこのレイヤーの中では、motorwayフラグを再チェックする意味が最初から無い。一方`道路中心線ZL4-10国道`のfilterは国道/都道府県道/市区町村道等/主要道路を含み、これらの分類の中にmotorwayフラグが立った地物が混在しうるため、優先上書きのチェックが必要——という説明で辻褄が合う(GSI側の意図を直接確認したわけではなく、実装時に構造の違いから逆算した仮説)。

これは[0009](0009-generator-architecture-direction.md)/[0018](0018-road-color-not-flat-category-compiler.md)で繰り返し確認してきたパターンの再確認: **「同じ名前・同じ役割に見える2つのレイヤーが、実は別の構造を持つ」**——今回は「テーブルの値が違う」ではなく「構造(motorwayチェックの有無)そのものが違う」という、一段深いレベルでの相違だった。

## 実装方針

- `zl410_road_color.py`: `compile_kokudo_color()`/`compile_kousoku_color()`という2つの独立した関数。共通する`_match_body()`/`_width_ramp_match()`ヘルパーは共有しつつ、構造(motorwayチェックの有無)は関数ごとに固定——「同じに見えて実は違う」ものを無理に1つの関数にパラメータで吸収しようとしなかった
- `road_color.py`の`_rgba`/`_with_alpha`を再利用(コードレビューで指摘された「同じイディオムの重複」を、今回は最初から避けた)
- `category_table.compile_match_expression()`に`property`引数を追加し、実際に配線した。以前([0020](0020-yaml-wiring-stage1.md)の指摘#6)YAMLの`property`フィールドを「宣言だけで未使用」として削除したが、今回`bvmap-鉄道中心線ZL4-10`が`vt_code`ではなく`vt_rtcode`で分岐する実例が出たため、正当な理由を持って復活させた——投機的な一般化ではなく、実需要が先にあった
- `bvmap-dark.json`が`rgb()`と`rgba()`を同じ意味で混在させている件([0022](0022-zl4-10-and-post-tier-layers-footprint.md)で確認済み)に対応するため、`gray_100_rgb`トークンを追加

## Stage 1の進捗

35 literal(前回38から3減) / 88 generated・YAML-patched。

## 残り([0022](0022-zl4-10-and-post-tier-layers-footprint.md)の④)

軌道2層の色分け非対称性——GSI公式地物コード表との突き合わせが必要、保留のまま。

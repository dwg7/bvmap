# 0031: 「見えない改善」の第一弾——rgb()/rgba()表記の統一

藤村さんの方針転換: 「見た目のデザインの変化はこのくらいでいい。見た目の改善と見えないところの改善をうまく組み合わせていこう」——見えない改善の例として、expressionの近代化・性能/柔軟性の向上を挙げ、`patches`を徐々にネイティブ生成へ移行することも示唆された。

## やったこと

`bvmap-dark.json`は`rgb(r,g,b)`(3引数)と`rgba(r,g,b,a)`(4引数)を同じ意味で混在させていた([0022](0022-zl4-10-and-post-tier-layers-footprint.md)で確認済み)。Stage 1(再現優先)の間は、この表記の違いをbyte-exactに再現するため、`gray_100_rgb`/`gray_161_rgb`/`gray_88_rgb`/`gray_173_rgb`という、数値は同じだが文字列表現だけが違う重複トークンを4つ抱えていた。

[0029](0029-assemble-writes-starlight-json.md)でStage 2(意図的な差分が前提)に移行した今、この重複を解消する理由ができた。4つの`_rgb`トークンを削除し、全ての参照箇所を対応する`rgba()`版のトークンに差し替えた——`rgb()`という古い表記をExpression全体から追放し、`rgba()`に統一する、という意味で「expressionの近代化」の第一弾。

## 副産物: `load_input.py`の自己検証がStage 1の前提のままだった

この変更を機に、`load_input.py`の`__main__`自己検証が[0029](0029-assemble-writes-starlight-json.md)の意味転換に追従していなかったことが判明した——`assemble.py`は「idの並び順以外は差分があって当然」という前提に更新済みだったが、`load_input.py`は「`bvmap-dark.json`とbyte-exactに一致するはず」という古い前提のまま`STAGE 1 GATE: FAIL`を出していた(実害はなく、チェックの意味付けが古かっただけ)。

`STRUCTURAL_CHECKS`(フォント名・数値幅など、色を含まないため今も一致するはずの項目)と、それ以外(色を含むため意図的に差分が出て当然の項目)を分離し、後者を「差分があること自体が磨き上げの成果」として報告するように修正した。これも「見えない改善」——AI・人間どちらが読んでも、今の設計意図と矛盾しない検証結果が出るようにした。

## Stage 1の各モジュール自身の`__main__`は無改造

`road_color.py`/`zl410_road_color.py`/`rail_tunnel_color.py`/`anno_symbol_color.py`各々の`__main__`は、パラメータ無指定時に**モジュール自身のハードコードされた定数**(`bvmap-dark.json`の値そのまま)を使うため、今回のpalette変更の影響を受けず、引き続きPASSする。これらは「再現ロジックが正しいことの証明」という役割のまま、Stage 2に入っても変わらず有効。

## 次の「見えない改善」の候補

- `patches`のうち、まだ`color_overrides`を持たない層([0021](0021-patches-by-id-coverage-expansion.md)の20層のうち大半)を、実際にネイティブ生成(categories/priority_chains化)へ移していく
- 性能・柔軟性の向上余地は今後探る

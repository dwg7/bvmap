# 0023: 構造物3層・等高線/等深線+数値部4層の実装(0022の①②)

[0022](0022-zl4-10-and-post-tier-layers-footprint.md)で洗い出した4つの検討ポイントのうち、①(構造物3層)②(等高線・等深線+数値部)を実装した。

## 結果

- **構造物3層**: `bvmap-構造物面`(fill)・`bvmap-構造物線`(line)は、`categories.structure_fill`/`categories.structure_line`という新しい`flat_match`カテゴリとして`compile_match_expression()`で無改造再現できた——[0022](0022-zl4-10-and-post-tier-layers-footprint.md)の予想通り。`bvmap-構造物面の外周線`はvt_code分岐を持たない単一値(`gray_164`、建物の外周線と同じ値)だったため、`patches`の`color_overrides`で対応
- **等高線・等深線+数値部4層**: `bvmap-等高線`のline-color(`rgb(161,161,161)`)と`bvmap-等高線数値部`のtext-color(`rgba(161,161,161,1)`)が同一の意味を持つ値であることを反映し、`gray_161`(rgba形式)・`gray_161_rgb`(rgb形式)という2つのトークンに統一した(等深線/等深線数値部も同様に`gray_88`/`gray_88_rgb`)。副産物として、この`gray_161`/`gray_88`は元々`anno_161`/`anno_88`という名前でAnno text-colorランプ専用の値だと思っていたが、実は**同じvt_code(7352/7372)がAnnoランプの単独カテゴリとしても、独立した数値部シンボルレイヤーとしても、同じ色で現れる**ことが分かり、Anno専用ではなくなったためリネームした

## コードの変更点

`categories`は既存の`flat_match`エンジンをそのまま再利用できたが、`layers:`セクションに新しい`engine: standalone`を追加する必要があった。実装して初めて気づいた事実: **`layers:`セクションの既存のtier_templateエントリ(道路中心線色/建築物/建築物の外周線)は、実はコードから一度も読まれていなかった**——`assemble.py`の`build_tier_block()`は、YAMLの`layers:`を見るのではなく、レイヤーidの文字列prefixで判定する形にハードコードされていた。つまり`layers:`セクションはこれまで**設計意図を示すドキュメントとして書かれていただけ**で、実際の配線ではなかった。

**判断**: 今回新設した`bvmap-構造物面`/`bvmap-構造物線`(`engine: standalone`)は、`load_input.build_standalone_layers()`として実際に`layers:`セクションを読んで動かした——構造物は完全に独立した1レイヤーなので、tierのような複雑な展開ロジックは要らず、素直にYAML駆動にできた。既存のtier_template側のハードコードは、動作は正しく検証済みのため、今回のスコープでは触らなかった(リファクタリングして壊すリスクの方が大きいと判断)。結果として、同じ`layers:`セクションの中に「実際にYAMLから読まれるengine」と「まだ読まれていないengine」が混在する、という一時的な非対称が生じている——次にtier_template側を触る機会があれば解消したい。

## Stage 1完全一致は維持

`generator/assemble.py`は引き続き123/123完全一致。内訳: 38 literal(前回45から7減) / 85 generated・YAML-patched。

## 次に残っているもの([0022](0022-zl4-10-and-post-tier-layers-footprint.md)の③④)

- ZL4-10: 独自の優先順位付きcase連鎖が必要、専用モジュール新設 vs リテラル保持のままにするか未決定
- 軌道2層の色分け非対称性: GSI公式地物コード表との突き合わせが必要、保留

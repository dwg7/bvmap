# 0028: 注記(Anno)の残り実装——`let`包装パターンの解決を含む

[0027](0027-anno-remaining-4-layers-footprint.md)の踏み跡調査に基づき、注記の残り3層(`bvmap-注記道路番号`・`bvmap-注記シンボル付きソート順100以上`・`100未満`)を実装した。`bvmap-注記シンボル付き重なり`は確定的な一回性(色を持たない純アイコン層)のためリテラル保持のまま。

## 結果

**PASS**。Stage 1の123/123完全一致は維持(28 literal / 95 generated)。これで**注記9層のうち8層が生成済み**になった(残りは色を持たない`シンボル付き重なり`1層のみ)。

- `bvmap-注記道路番号`: `categories.anno_road_number_color`——単純な2分岐flat_match、新規コード不要
- `bvmap-注記シンボル付きソート順100以上/100未満`: [0017](0017-category-table-generator-stage1.md)以来の`let`包装パターンを、新設した`generator/anno_symbol_color.py`の`compile_symbol_text_color()`で再現した。既存の`categories.anno_text_color`(共有ランプ)を**丸ごと再利用**し、その上にズーム14を境にした透明化オーバーレイを被せる構造

## 設計判断

`priority_chains`に3つ目のビルダーパターンが必要になった:**「他のcategories.*エントリを参照する」**という、これまでの4つ(`road_color`/`zl410_kokudo`/`zl410_kosoku`/`rail_tunnel_main_color`、いずれもpaletteの値だけを参照)には無かった依存関係。`load_input.build_priority_chains()`のシグネチャに`categories`を追加し(全ビルダーに一様に渡す、ほとんどのビルダーは無視する)、`anno_symbol_text_color_*`ビルダーだけが`categories[entry["base_category"]]`で他のカテゴリの生成結果を直接参照する。

`assemble.py`側では、注記の色の出処が「共有ランプ」「単純な自前match」「ランプ+透明化オーバーレイ」の3種類に増えたため、`if lid not in LITERAL_ANNO_LAYERS: ...`という二値判定を、`ANNO_TEXT_COLOR_SOURCES`という`{レイヤーid: (categories|chains, 名前)}`の対応表に置き換えた——レイヤーごとにどの生成結果を使うかを明示的に一覧できる形にした。

## Stage 1の進捗

28 literal(前回31から3減) / 95 generated・YAML-patched。

## 残り

- tierブロック後の残り9層(道路縁・送電線・特定地区界等): [0009](0009-generator-architecture-direction.md)の「逃げ場」原則通りリテラル保持のままで良いと判断済み
- 注記の`bvmap-注記シンボル付き重なり`: 色を持たない純アイコン層、リテラル保持で確定
- これでStage 1のカラー生成に関する探索・実装は、一区切りついた。次はいよいよ本来の目的である`bvmap-starlight`の配色磨き上げ

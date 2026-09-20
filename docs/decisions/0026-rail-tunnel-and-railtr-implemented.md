# 0026: 鉄道トンネル系・軌道系の実装

[0025](0025-remaining-post-tier-13-layers-footprint.md)で洗い出した4層を実装した。

## 結果

**PASS**。Stage 1の123/123完全一致は維持(31 literal / 92 generated)。

- `bvmap-鉄道中心線地下トンネルククリ`(casing): `categories.rail_tunnel_kukuri_color`——単純な2分岐matchで、`compile_match_expression()`をそのまま流用できた
- `bvmap-鉄道中心線地下トンネル`(本体): `priority_chains.rail_tunnel_main_color`——defaultの枝が`case(vt_sngldbl=="駅部分")`を含む入れ子で、flat_matchでは表現できないため、新設した`generator/rail_tunnel_color.py`の`compile_main_color()`が構造を持つ
- `bvmap-軌道の中心線`/`bvmap-軌道の中心線トンネル`: `categories.railtr_surface_color`/`railtr_tunnel_color`——[0025](0025-remaining-post-tier-13-layers-footprint.md)で解明した「暗くなる種別(普通鉄道/特殊鉄道/路面の鉄道)は表層・トンネルで完全一致」という理解通り、どちらも単純なvt_codeフラットmatchで再現できた

## 設計判断

`priority_chains`セクションに、道路の優先順位付きcase連鎖(`engine: priority_case_chain`)とは別に、`engine: nested_match`という新しいタグを追加した(`rail_tunnel_main_color`)。ただし`load_input.py`の`build_priority_chains()`は、この`engine`文字列そのものでは分岐していない——**名前ごとに登録された専用ビルダー関数(`PRIORITY_CHAIN_BUILDERS`)が実際の挙動を完全に決める**ため、`engine`フィールドは人間・AI向けの説明用であり、コードの検証には使っていない。以前は`entry["engine"] != "priority_case_chain"`という文字列の完全一致を要求していたが、2種類目の構造が出てきたタイミングでこの制約を外した(名前が登録されているかどうかだけをチェックする形に単純化)。

## Stage 1の進捗

31 literal(前回35から4減) / 92 generated・YAML-patched。

## 残り

- tierブロック後の残り9層(道路縁・送電線・特定地区界等)は、[0009](0009-generator-architecture-direction.md)の「逃げ場」原則通りリテラル保持のままで良いと判断済み([0025](0025-remaining-post-tier-13-layers-footprint.md))
- 注記(Anno)の残り4層は、体系的な調査が効く領域だと判断し、他の実装が一区切りついてから着手する(藤村さんの方針)

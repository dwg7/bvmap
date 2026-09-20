# 0032: 残り28層のリテラル、ジェネレーターへの移行計画

「見えないところの改善」の一環として、`starlight-input.yaml`に残る28層のリテラル(`LITERAL_RANGES`9層・`LITERAL_ANNO_LAYERS`1層・`color_overrides`未設定の`patches`18層)を実データで精査し、ジェネレーターに馴染ませられるかを検討した。まだ実装はしていない——計画のみ。

## 分類結果

### Group A: 直接`compile_match_expression()`で再現できる(5層、新規コード不要)

| レイヤー | 構造 |
|---|---|
| `bvmap-地形表記面` | `match(vt_code)` 3分岐(7401/7402/7403)+透明default |
| `bvmap-地形表記線` | `match(vt_code)` 2分岐([7571,7572]/default)。**rgb()/rgba()混在あり**——[0031](0031-expression-modernization-rgb-normalization.md)の正規化も同時に行える |
| `bvmap-水部構造物面` | `match(vt_code)` 3分岐(5401/5411/default)。**defaultが黒**——他の同種レイヤーはdefaultが透明で、これだけ違う(未調査の差異) |
| `bvmap-水部構造物線` | `match(vt_code)` 2分岐(5521/default) |
| `bvmap-水涯線` | `match(vt_code)` 2分岐([5203,5233]/default) |

既存の`categories`(`flat_match`エンジン)にそのまま追加するだけ。建物・構造物で3回証明済みの仕組みの4回目の適用。

### Group B: 単一値、既存トークンで足りる(12層、新規コード・新規トークンとも不要)

`patches.color_overrides`に1行足すだけ。全て既存の`gray_100`(10層)または`gray_255`(1層、水部表記線polygonのfill-color)で表現できる:

海岸線堤防等に接する部分破線・水涯線堤防等に接する部分破線・水部表記線polygon(fill-color+fill-outline-colorの2プロパティ)・道路中心線破線・道路中心線階段・道路縁・道路構成線トンネル内の道路・道路構成線分離帯・送電線・送電線破線

### Group C: 単一値、新規パレットトークンが必要(7層)

| レイヤー | 値 | 新規トークン |
|---|---|---|
| `bvmap-水部表記線line` | 99 | `gray_99` |
| `bvmap-行政区画界線25000所属界`ほか3層(市区町村界・都府県界及び北海道総合振興局振興局界・地方界) | 35 | `gray_35`(4層共通) |
| `bvmap-行政区画界線国の所属界` | 27 | `gray_27`(他4層と値が違う理由は未調査のまま——[0021](0021-patches-by-id-coverage-expansion.md)から持ち越し) |
| `bvmap-特定地区界` | 150 | `gray_150` |

Group Bと同じ仕組み(`patches.color_overrides`)、パレットに新トークンを足すだけ。

### Group D: step式だが出力が単純な値(2層、既存の`step_outputs`機構で対応可能)

`bvmap-河川中心線人工水路地下`・`bvmap-河川中心線枯れ川部`——どちらも`["step",["zoom"],209,16,88]`という、backgroundで既に実装済み([0021](0021-patches-by-id-coverage-expansion.md))の`step_outputs`パッチ機構とそのまま同じ形。新規コード不要、`color_overrides`に`step_outputs: [gray_209, gray_88]`を書くだけ。

### Group E: step式の中にvt_code matchが入れ子(2層、小さな拡張が必要)

`bvmap-海岸線`(`step(zoom8, 単一値, match(vt_code))`)・`bvmap-河川中心線`(`step(zoom16, match(vt_code), match(vt_code))`)。現状の`apply_step_outputs()`は出力がpaletteトークン(単純な値)であることを前提にしており、出力自体が`match`式であるこの2層には使えない。**`step_outputs`の各要素が、パレットトークンに加えて`{from: "categories.xxx"}`参照も受け付けられるように拡張する**——`layers:`の`standalone`エンジンが既に持っている`{from: ...}`解決の仕組みを、`step_outputs`にも流用する形。小さな拡張で済む見込み。

### Group F: 色を持たない(1層、優先度低)

`bvmap-水部表記線point`——アイコンのみ。色の移行対象ではないが、`patches`にbase参照+literal_reasonだけの注釈エントリを足せば、`bvmap-注記シンボル付き重なり`(注記側の同種レイヤー)と扱いを揃えられる。純粋にドキュメント上の一貫性のためで、急ぐ理由はない。

## 推奨する着手順

新規コードが不要なものから、小さな拡張が要るものへ:

1. **Group A**(5層、既存コンパイラ流用)
2. **Group B**(12層、既存トークンのみ)
3. **Group D**(2層、既存step_outputs機構)
4. **Group C**(7層、新規トークン4つ)
5. **Group E**(2層、`step_outputs`への`{from:}`参照拡張)
6. **Group F**(1層、ドキュメント整合、任意)

1〜4を終えると、28層中26層がYAML駆動になり、残るのはGroup E(拡張待ち)とGroup F(色なし)のみになる見込み。

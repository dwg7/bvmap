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

## 訂正(2026-09-20、Fable(model: claude-fable-5-1)によるレビュー、自分でも裏取り済み)

リポジトリ全体を読んだ上でこの計画をレビューしてもらったところ、層ごとの式の形状の記述(Group A/D/Eの構造、水部構造物面のdefaultが黒である点、地形表記線のrgb/rgba混在)は実データと一致していたが、**機構面の主張に複数の誤りがあった**。いずれも実際に`generator/starlight-input.yaml`・`style/bvmap-starlight.json`を確認し、裏取り済み。

1. **層数が合っていない**: A(5)+B(12と記載、実際は10)+C(7)+D(2)+E(2)+F(1) = 記載上27、実際の列挙は25。28層との差分は`bvmap-注記シンボル付き重なり`(`LITERAL_ANNO_LAYERS`)——Fで比較対象として触れているだけで、どのグループにも正式には割り当てていなかった。「1〜4で26/28」という見込みも誤りで、正しくは24/28。

2. **Group B・Cの「patchesに1行足すだけ」は8層について成立しない**: 実際に`starlight-input.yaml`を確認したところ、Group Bの道路中心線破線・階段・道路縁・トンネル内の道路・分離帯・送電線・送電線破線の7層と、Group Cの特定地区界は、`patches`ではなく`assemble.py`の`LITERAL_RANGES`(位置指定)側にある。移行には①`base`+`literal_reason`付きの新規`patches`エントリを書く、②`LITERAL_RANGES`の除外インデックスに追加する、の両方が要る——「新規コード不要」は誤りで、`assemble.py`の編集を伴う(②を忘れると`literal_count`が二重計上される)。

3. **Group Aは`patches`→`layers: standalone`への「移動」であり前例が薄い**: 現在`patches`に注釈付きで登録済みの5層を`standalone`化する場合、`literal_reason`/`known_pattern_pending`の置き場所(`standalone`エントリにはこの欄がない)を新たに考える必要がある。

4. **Group Aにも新規トークンが要り、しかも偶然同値の流用可否という判断を伴う**: 地形表記面の217・239は未定義。233は`gray_233`(建物塗り)と、水部構造物面の200は`gray_200`(道路幅員ランプ)と偶然同値——[0020](0020-yaml-wiring-stage1.md)の`narrow_exception_color`の教訓(「値が偶然一致しているだけで意味的に同じとは限らない」)がそのまま当てはまる。水部系レイヤーに繰り返し現れる88/100を`gray_88`/`gray_100`に相乗りさせるか独立トークンにするかも未検討。Group Eの海岸線(z<8、130)のトークンも記載漏れ。

5. **最重要: この移行は「見えない改善」ではなく可視の配色変更になる**: [0030](0030-starlight-first-color-pass.md)以降パレットは変換済みだが(`gray_100`=113,114,116等)、実際に確認したところリテラル層は`style/bvmap-starlight.json`内でも生の`rgba(100,100,100,1)`のままだった(`bvmap-送電線`等で確認)。つまりGroup Bの移行は、該当27層を**初めてStarlight配色に乗せる**ことを意味し、目視確認が要る——構造面の作業ではなく、実質的に配色磨き上げ([0030](0030-starlight-first-color-pass.md))の続きとして扱うべきだった。

6. **Group Fは「任意」ではなく構造的価値がある**: B・Cで`LITERAL_RANGES`の8層を`patches`化すれば、`LITERAL_RANGES`に残るのは水部表記線pointの1層のみになる。Fの注釈エントリを足せば`LITERAL_RANGES`を丸ごと削除でき、[0020](0020-yaml-wiring-stage1.md)で指摘した「位置ベース選択は上流の並び替えに弱い」という脆弱性が完全に解消される——B・Cと同時に行うべきで、最後尾に置く理由がない。

### 訂正後の推奨順序

1. **方針決定**(実装前に1回のケース・カンファレンスで): 新トークンは0030の変換を適用するか、偶然同値のトークンへの相乗りを許すか
2. **Group B(`patches`に既にある3層: 海岸線堤防等破線・水涯線堤防等破線・水部表記線polygon)+ Group D(2層)**: 本当に1行で済む層。目視確認のウォームアップ
3. **Group B(`LITERAL_RANGES`にある7層)+ Group C(特定地区界)+ Group F**: `LITERAL_RANGES`退役をまとめて実施、位置ベース選択の脆弱性を解消
4. **Group C残り6層**(新規トークン3つ)
5. **Group A**(`patches`→`standalone`移動時の注釈の置き場所を決めてから)
6. **Group E**(`step_outputs`拡張 vs `rail_tunnel_main_color`同様の専用ビルダー、どちらにするか選んでから)

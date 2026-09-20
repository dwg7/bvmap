# HANDOVER — 2026-09-20時点

このファイルは、コンテキストのcompact直前に書き出した引き継ぎ。次のセッション(または
compact後の自分自身)は、まず`CLAUDE.md`→本ファイル→`docs/STARLIGHT_EXPLORATION.md`の順で
読むこと。

## 今どこにいるか

`bvmap-starlight`の配色磨き上げ([0005](docs/decisions/0005-goal-change-master-repo-and-starlight-polish.md)、
[0006](docs/decisions/0006-hfu-stars-is-already-master-repo.md)で確定した唯一の目標)に向けて、
以下の順で進めてきた:

1. 縦書き棒音符問題の調査・終了([0001](docs/decisions/0001-duplicate-repository-check.md)〜[0007](docs/decisions/0007-real-font-names-bypass-local-restriction.md))
2. ケース・カンファレンス形式で7つの判断事項を決定([0009](docs/decisions/0009-generator-architecture-direction.md)〜[0015](docs/decisions/0015-unification-vs-semantic-separation.md)、`docs/STARLIGHT_EXPLORATION.md`に一覧)
3. 決定した方針(ジェネレータ = Stage 0→1→2の段階的進化、核は「`vt_code`対応表→`match`式」コンパイラ)のStage 1実装を実施、完了
   - `generator/tier_template.py`: 道路・鉄道・建物の複合ティア構造。65/70完全一致([0016](docs/decisions/0016-tier-generator-stage1.md))
   - `generator/category_table.py`: 定数解決コンパイラ。注記の濃淡ランプ・フォント分岐で完全一致([0017](docs/decisions/0017-category-table-generator-stage1.md))
   - `generator/road_color.py`/`generator/building_color.py`: 道路vt_rdctg駆動色は専用の優先順位付きcase連鎖、建物はカテゴリ表コンパイラで無改造再現。道路色は[0010](docs/decisions/0010-color-semantic-categories.md)の表自体に誤りがあったと判明、[0018](docs/decisions/0018-road-color-not-flat-category-compiler.md)で訂正
   - `generator/assemble.py`: 全123レイヤーの組み立て、完全一致(Stage 1最終ゲート、[0019](docs/decisions/0019-stage1-final-assembly.md))。**今ここ**: Stage 1完了、次は本来の目的である配色磨き上げ(下記⑤)

## 次にやること(優先順)

1. **`bvmap-注記シンボル付きソート順100以上/100未満`の`let`包装パターンの解明**。同じ基本テーブルを`let`で包み、2レイヤー間にわずかな差分がある(text-sizeのズーム14例外と同種と推測、未検証)。[0017](docs/decisions/0017-category-table-generator-stage1.md)の「未検証」節参照
2. ~~道路の`vt_rdctg`駆動色と建物の塗り/輪郭を、カテゴリ表コンパイラで再現できるか検証~~ **完了(2026-09-20)**: 建物は`compile_match_expression()`で無改造再現([0010](docs/decisions/0010-color-semantic-categories.md)の元の仮説通り)。道路色は同じコンパイラでは再現できず、専用の優先順位付きcase連鎖(`generator/road_color.py`)が必要と判明——さらに[0010](docs/decisions/0010-color-semantic-categories.md)の道路色の表自体に誤りがあり、[0018](docs/decisions/0018-road-color-not-flat-category-compiler.md)で訂正済み
3. ~~残りの個別レイヤーの共有テーブル化せずリテラル保持で組み込む設計~~ **完了(2026-09-20)**: `generator/assemble.py`がリテラル保持で組み込み、[0019](docs/decisions/0019-stage1-final-assembly.md)に範囲と理由を記録
4. ~~全123レイヤーを組み立てて`bvmap-dark.json`と完全一致するか検証~~ **完了(2026-09-20、[0019](docs/decisions/0019-stage1-final-assembly.md))**: `generator/assemble.py`でPASS。Stage 1(reproduction-first generator)完了
5. ~~YAML入力(`sample-starlight-input.yaml`)からの配線~~ **完了(2026-09-20、[0020](docs/decisions/0020-yaml-wiring-stage1.md))**: `generator/starlight-input.yaml` + `generator/load_input.py`。コードレビュー([0020](docs/decisions/0020-yaml-wiring-stage1.md)追記)で3件修正、backgroundのstep式patchも`apply_step_outputs()`で解決し、被覆面ダンス3層は全てpalette駆動
6. 123レイヤーカバーの拡大、継続中。方針: 123カバーを至上命題にせず、既に検討済みの知見がある層から反映する
   - **完了(2026-09-20、[0021](docs/decisions/0021-patches-by-id-coverage-expansion.md))**: [0008](docs/decisions/0008-cartographic-layer-ordering.md)で役割確定済みの20層(陸水面・被覆面付随の線群、行政区画線、等高線・等深線)を`patches`にid参照で追加(色は未検証、注釈のみ)。backgroundのstep式patchも解決
   - **完了(2026-09-20、[0022](docs/decisions/0022-zl4-10-and-post-tier-layers-footprint.md)/[0023](docs/decisions/0023-structure-and-contour-layers-implemented.md))**: ZL4-10・tierブロック後の個別18層を踏み跡調査([0022](docs/decisions/0022-zl4-10-and-post-tier-layers-footprint.md))。うち構造物3層・等高線/等深線+数値部4層を実装([0023](docs/decisions/0023-structure-and-contour-layers-implemented.md))——構造物は新設した`layers: engine: standalone`でYAML駆動、等高線/等深線は数値部とpaletteトークンを共有するよう統一。副産物: `layers:`セクションのtier_templateエントリが実はコードから未使用(ドキュメントのみ)だったと判明
   - **完了(2026-09-20、[0024](docs/decisions/0024-zl410-dedicated-module.md))**: ZL4-10専用モジュール`generator/zl410_road_color.py`。国道/高速の2レイヤーは同じテーブルを共有していないと判明(motorwayチェックの有無という構造レベルの違い)——2つの独立した関数で実装。`category_table.compile_match_expression()`に`property`引数を実配線(鉄道のvt_rtcode分岐のため)
   - **完了(2026-09-20、[0025](docs/decisions/0025-remaining-post-tier-13-layers-footprint.md))**: 残り13層を踏み跡調査。GSI公式地物コード表(PDF)を実際に取得して、軌道2層の「非対称性」(以前は保留)を完全に解決——vt_codeは「種別2桁+状態1桁」の構造で、暗い色になる種別(01/11/31)は表層・トンネルで完全に一致していた(非対称に見えたのはパーティションの軸を誤認していたため)。副産物: 鉄道の幅係数テーブル・道路の幅員ランプが、tierと数値まで完全一致する形で別レイヤーに埋め込まれている(共有テーブルイディオムの3・4例目)ことも発見。実装はまだ(鉄道トンネル系・軌道系は専用モジュールが要りそう、残り10層は一回性でリテラルのままで良い)
   - **完了(2026-09-20、[0026](docs/decisions/0026-rail-tunnel-and-railtr-implemented.md))**: 鉄道トンネル系(2層)・軌道系(2層)を実装。`generator/rail_tunnel_color.py`を新設(鉄道トンネル本体のdefault枝がcase入れ子で、flat_matchでは表現できないため)。`priority_chains`に`engine: nested_match`という2つ目の構造タグを追加——ただしコードは`engine`文字列では分岐せず、名前ごとのビルダー登録だけで挙動が決まる設計に単純化した
   - **残り**: tierブロック後の残り9層(一回性でリテラル保持のままで良いと判断済み)、**注記(Anno)の残り4層**——体系的な調査が効く領域と判断し、他の実装が一区切りついた今から着手する
7. **次はここ**: 実際に`bvmap-starlight`の配色をStarlightの方向性(低彩度・明るめ・銀灰色寄り)へ磨き上げる(まだ着手していない、これが本来の目的)——今は`generator/starlight-input.yaml`のpaletteセクションを差し替えるだけで配色が変わる状態になっている。⑥で追加した20層の色検証も、この磨き上げ作業の一部として行う
7. `hfu/stars`へのPR作成([0006](docs/decisions/0006-hfu-stars-is-already-master-repo.md))

## 未解決のまま保留中の判断

- `font-faces`(自前フォントホスティング)は[0011](docs/decisions/0011-font-implementation-method.md)で保留。将来のMapLibreネイティブ縦書き対応([0004](docs/decisions/0004-vertical-choonpu-workaround-does-not-work.md)のPR #8399等)が`font-faces`前提でマージされたら再検討
- ジェネレータの入力形式(YAML)の具体的な構文は、まだPythonの辞書リテラルで代用している段階。[0009](docs/decisions/0009-generator-architecture-direction.md)の「まず中身の処理を固めてから入れ物を選ぶ」という順序に従い、意図的に後回しにしている
- スプライト(独自SDF・絵文字代替)は[0014](docs/decisions/0014-sprite-decisions.md)で全て見送り。着手条件はADR参照

## セッションの作法(重要、次のセッションも踏襲すること)

- **探索的アプローチ**: 先に枠組みを決めず、実データ(実タイル取得、実PDF確認、実コード実行)で仮説を検証してから帰納する。このセッションで何度も、戦略的に筋が通って見える仮説が実データ検証で覆った(AdmArea/WA関係、vt_code 5201系の意味、tier4のGSI側不整合等)
- **ケース・カンファレンス形式**: 判断事項を1つずつ「事実→論点→選択肢→判断→ADR記録」で解決する。まとめて戦略を決めない
- **ADRに訂正込みで記録する**: 間違った仮説も消さず、訂正として残す(cafebabeの`verification-discipline.md`にも通じる規律)
- **AI向けの構造化コメント**: 人間向けの説明文ではなく、将来のAIセッションが情報源を再度漁らずに済む意味メタデータとして書く(`~/.claude/projects/-Users-hfu-bvmap/memory/feedback_ai_consumable_documentation.md`参照)

## 実験用ファイル(削除・整理は未検討)

- `examples/style-preview.html`: bvmap-dark/bvmap-starlight比較用
- `examples/realfont-test.html` + `examples/fixtures/bvmap-dark-realfont-stack.json`: [0007](docs/decisions/0007-real-font-names-bypass-local-restriction.md)の実フォント名検証用
- `.claude/launch.json`: ローカル確認用の`python3 -m http.server 8765`設定

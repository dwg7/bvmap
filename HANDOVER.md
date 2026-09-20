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
3. **今ここ**: 決定した方針(ジェネレータ = Stage 0→1→2の段階的進化、核は「`vt_code`対応表→`match`式」コンパイラ)のStage 1実装を開始
   - `generator/tier_template.py`: 道路・鉄道・建物の複合ティア構造。65/70完全一致([0016](docs/decisions/0016-tier-generator-stage1.md))
   - `generator/category_table.py`: 定数解決コンパイラ。注記の濃淡ランプ・フォント分岐で完全一致([0017](docs/decisions/0017-category-table-generator-stage1.md))

## 次にやること(未着手、優先順)

1. **`bvmap-注記シンボル付きソート順100以上/100未満`の`let`包装パターンの解明**。同じ基本テーブルを`let`で包み、2レイヤー間にわずかな差分がある(text-sizeのズーム14例外と同種と推測、未検証)。[0017](docs/decisions/0017-category-table-generator-stage1.md)の「未検証」節参照
2. **道路の`vt_rdctg`駆動色([0010](docs/decisions/0010-color-semantic-categories.md))と建物の塗り/輪郭**を、カテゴリ表コンパイラで再現できるか検証
3. **残りの個別レイヤー**(background/AdmArea/WA、Cntr/Isbt、WStrA/WStrL、SpcfArea等)は、共有テーブル化せず、リテラル保持([0009](docs/decisions/0009-generator-architecture-direction.md)の「逃げ場」原則)で組み込む設計を詰める
4. 1〜3が揃ったら、**全123レイヤーを組み立てて`bvmap-dark.json`と完全一致するか検証**(Stage 1の最終ゲート)
5. Stage 1が通ったら、**実際に`bvmap-starlight`の配色をStarlightの方向性(低彩度・明るめ・銀灰色寄り)へ磨き上げる**作業(まだ着手していない、これが本来の目的)
6. `hfu/stars`へのPR作成([0006](docs/decisions/0006-hfu-stars-is-already-master-repo.md))

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

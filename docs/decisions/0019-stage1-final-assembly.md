# 0019: Stage 1最終ゲート — 全123レイヤーの組み立て、完全一致

[HANDOVER.md](../../HANDOVER.md)の次ステップ④「全123レイヤーを組み立てて`bvmap-dark.json`と完全一致するか検証」。`generator/assemble.py`。

## 結果

**PASS**。`style/bvmap-dark.json`の123レイヤー全てを、順序も内容もbyte-exactに再現した。

- 75レイヤー: 生成([0016](0016-tier-generator-stage1.md)のtier構造 + [0017](0017-category-table-generator-stage1.md)のカテゴリ表 + [0018](0018-road-color-not-flat-category-compiler.md)の道路優先順位連鎖 + 建物カテゴリ表)
- 48レイヤー: リテラル(未分解、下記)

これは単なる「コピーして辻褄を合わせた」結果ではない——各コンパイラの**出力を実際に差し込んで**、組み立て後もbyte-exactであることを確認した(単体テストが通っていても、組み合わせた瞬間に破綻する、というインテグレーションの一般的なリスクをここで潰した)。

## 何が「リテラル」に分類されたか、なぜか

| 範囲 | レイヤー数 | 理由 |
|---|---|---|
| `background`/`bvmap-行政区画`/`bvmap-水域`/地形表記/水部/等高線等(0-22) | 23 | 個々に独立したロジック。「被覆面ダンス」等、意味のある構造が眠っている可能性は高いが、まだ言語化前([sample-starlight-input.yaml](../../generator/sample-starlight-input.yaml)の`patches`セクションが試作) |
| ZL4-10低ズーム概観(23-25) | 3 | tier構造(0-4)の外にある独立レイヤー、設計上tierブロックから除外([0016](0016-tier-generator-stage1.md)) |
| tierブロック後の個別レイヤー(96-113、破線道路・トンネル・構造物・送電線等) | 18 | 個々に独立したロジック、未調査 |
| 注記(Anno)のうち、let包装パターン2層+パターン共有なし2層 | 4 | [0017](0017-category-table-generator-stage1.md)の未検証事項(let包装)、および共有パターンが存在しない2層(シンボル付き重なり・道路番号) |

合計48レイヤー。次のケース・カンファレンスの候補群であり、[0009](0009-generator-architecture-direction.md)の「逃げ場」原則通り、無理に共有テーブル化していない。

## 統合で見つかった追加の事実

- **建物の塗り・輪郭は、全5tierで完全に同一の`match`式**(tier間で一切変化しない)。[0010](0010-color-semantic-categories.md)の建物カテゴリは、tierの概念と無関係に独立して存在する
- **注記(Anno)のtext-fontの水域・海岸分岐は7レイヤーが共有するが、text-colorの共有ランプは5レイヤーのみ**——let包装された2レイヤー(シンボル付きソート順100以上/100未満)は、フォントは共有パターンに従うがカラーは未解明のまま、という非対称な状態にある。プロパティごとに「どこまで共有されるか」が異なるという[0017](0017-category-table-generator-stage1.md)の発見が、ここでも再確認された
- **実装上の罠**: `tier_template.py`の`generate_tier_block()`は`paint`辞書を参照渡しで使い回している(tier1のテンプレートがtier1-4全ての層に同一オブジェクトとして共有される)。`assemble.py`で生成済みカテゴリ表の値を差し込む際、ディープコピーなしに書き換えると**読み込み元の`bvmap-dark.json`のインメモリ表現そのものを汚染する**バグを踏むところだった(ファイル自体は書き換わらないが、比較対象の「正解」がその場で書き換わり、見かけ上の一致が意味を失う)。組み立てて初めて表面化した罠であり、単体のジェネレーターモジュールを見ているだけでは気づけなかった

## Stage 1の完了

[0009](0009-generator-architecture-direction.md)で設計したStage 1(reproduction-first generator)は、これで完了とする。次はHANDOVER.mdの⑤——実際にStarlightの配色を磨き上げる作業(本来の目的)に進む。その際、48レイヤーの「リテラル」群は、[sample-starlight-input.yaml](../../generator/sample-starlight-input.yaml)で試作した`patches`(base参照 + palette化した色のオーバーライド)の実装対象になる。

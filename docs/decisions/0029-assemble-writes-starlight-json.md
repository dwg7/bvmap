# 0029: `assemble.py`が`style/bvmap-starlight.json`へ書き出すように

配色磨き上げに着手する前に気づいた欠落: これまでの`generator/assemble.py`はメモリ上でbyte-exact一致を検証するだけで、**生成結果をファイルへ書き出したことが一度もなかった**。`style/bvmap-starlight.json`は[0003](0003-bvmap-starlight-naming.md)の時点から`name`フィールドだけが違う`bvmap-dark.json`のコピーのままだった。

## 変更

`generator/assemble.py`の`__main__`を、常に`style/bvmap-starlight.json`へ書き出すように変更した。同時に、判定の意味を変えた:

- **これまで**: 生成結果が`bvmap-dark.json`とbyte-exactに一致するかどうかがPASS/FAILの基準(Stage 1の目的そのもの)
- **これから**: `id`の並び順・重複の無さ(構造的な健全性)だけをハード条件として残す。内容の差分(`bvmap-dark.json`との色の違い)は、**paletteを意図的に変えれば当然発生するもの**として、警告ではなく単なる情報として報告する

これは[0009](0009-generator-architecture-direction.md)で設計したStage 1(reproduction-first)からStage 2(実際の配色磨き上げ)への移行そのもの——「bvmap-dark.jsonと一致すること」が目的だった段階から、「意図的に一致しなくなること」が目的の段階に変わった。

## 動作確認

`starlight-input.yaml`のpaletteをまだ一切変更していない状態で実行し、差分0件(`bvmap-dark.json`と意味的に完全一致、`name`フィールドのみ異なる)を確認した——書き出しパスが正しく動作することを、実際に値を変える前に確認できた。

## 次

`starlight-input.yaml`のpaletteを実際に編集し、`python3 generator/assemble.py`を実行するたびに`style/bvmap-starlight.json`が更新される。`examples/style-preview.html`でbvmap-dark/bvmap-starlightを切り替えながら見比べられる。

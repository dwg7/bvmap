# 0021: patchesをid参照化して23層に拡大(123件カバーへの最初の一歩)

「123レイヤーカバーを至上命題にすると、YAMLが場当たり的になる」という懸念([HANDOVER.md](../../HANDOVER.md))を踏まえ、レイヤーを足す作業の中で既に検討済みの知見を反映しながら進めた最初の増分。

## やったこと

1. **backgroundのstep式パッチを実装**。`generator/load_input.py`に`apply_step_outputs()`を追加し、`["step", input, out0, stop1, out1, ...]`の**出力値だけ**をpalette参照で差し替えられるようにした(構造=zoomの区切り位置はbaseのまま)。これで「被覆面ダンス」3層(`bvmap-行政区画`・`bvmap-水域`・`background`)は全てpalette駆動になった
2. **`docs/decisions/0008`(地図学的レイヤー順序体系)で役割が確定済みの20層**(陸水面・被覆面付随の線群、行政区画線、等高線・等深線)を、`starlight-input.yaml`の`patches`にid参照で追加。**色は検証していないため`color_overrides`は書いていない**——役割の注釈(なぜこの層か、0008のどの段に属するか)だけを反映した。色を検証せずにpalette化するのは、それこそ捏造になるため見送った
3. `assemble.py`の`LITERAL_RANGES`から「layers 0-22」の位置範囲指定を丸ごと削除した——この23層は全て`patches`でid参照されるようになったため。副産物として、[前回のコードレビュー](0020-yaml-wiring-stage1.md)で指摘した「位置ベースの選択は上流の並び替えに弱い」という懸念(指摘#3、当時は見送り)が、この23層分については解消された

## 判断基準: どこまでを今回のスコープに含めたか

- **含めた**: [0008](0008-cartographic-layer-ordering.md)で役割が既に実データ検証済みの層。既存の理解を反映するだけなので、捏造のリスクがない
- **含めなかった**: ZL4-10低ズーム概観(3層)・tierブロック後の個別レイヤー(18層、破線道路・トンネル・構造物・送電線等)・注記の一部(4層)。これらは[0008](0008-cartographic-layer-ordering.md)でも役割が確定していない、またはまだ調査していない——ここに手を広げると、まさに「場当たり的な注釈」になってしまうため、今回は見送った

## `literal_count`の計算をやり直した

`patches`が「idベースで参照するが色は未検証」という層を含むようになったため、旧来の`literal_count = LITERAL_RANGES合計 + LITERAL_ANNO_LAYERS - len(patches)`という式が壊れた(patchesがLITERAL_RANGESの部分集合であることを前提にしていたが、もう成り立たない)。`build_patches()`が「実際に色を上書きしたid集合」を返すように変更し、`literal_count = LITERAL_RANGES合計 + LITERAL_ANNO_LAYERS + (patches総数 - 実際に上書きしたid数)`という、patchesの内訳に依存しない式に直した。

## Stage 1完全一致は維持

`generator/assemble.py`は引き続き123/123完全一致。内訳: 45 literal(今回の20層を含む、色は未検証) / 78 generated・YAML-patched。

## 次に必要な確認(未着手)

- 今回追加した20層それぞれの色を、実データで検証してpalette化する(Starlightの配色磨き上げの一部として)。特に`bvmap-行政区画界線国の所属界`だけ他の行政区画界線(gray_35)と違う色(gray_27)を使っている理由は未調査
- ZL4-10・tierブロック後の個別レイヤー・注記の残り4層は、まだ[0008](0008-cartographic-layer-ordering.md)レベルの役割確定すら済んでいない——それぞれ着手前に踏み跡調査が必要

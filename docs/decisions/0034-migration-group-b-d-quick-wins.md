# 0034: 0032移行、Group B(既存patches3層)+ Group D(2層)実装

[0033](0033-new-token-policy.md)の方針決定を受けて、[0032](0032-literal-layers-generator-migration-plan.md)訂正後の推奨順序の最初の一手を実装した。

## 実装した5層

- `bvmap-海岸線堤防等に接する部分破線`・`bvmap-水涯線堤防等に接する部分破線`: `color_overrides.line-color: gray_100`(既存の汎用トークン、[0010](0010-color-semantic-categories.md) §4)
- `bvmap-水部表記線polygon`: `fill-color: gray_255`・`fill-outline-color: gray_100`(2プロパティとも既存トークン)
- `bvmap-河川中心線人工水路地下`・`bvmap-河川中心線枯れ川部`: `color_overrides.line-color.step_outputs: [gray_209, gray_88_hydro]`——backgroundで実装済みの`step_outputs`機構をそのまま適用

## 新規トークン

`gray_88_hydro`を新設した([0033](0033-new-token-policy.md)の「陸水面クラスタ」例外)。生の値は既存`gray_88`と同じ88だが、Anno側の意味(group_b・等深線)とは独立させ、陸水面・被覆面付随の線群専用にした。`gray_209`(水域塗り)は、河川=水という意味的な関連が明確なため、[0033](0033-new-token-policy.md)の「検証済みの一致」の例外として流用した(判断根拠として本ADRに明記)。

## 検証

`generator/load_input.py`・`generator/assemble.py`とも全ゲートPASS。`literal_count`が28→23に減少(5層分)。`style/bvmap-starlight.json`を実際に確認し、5層全てが生の`bvmap-dark`値ではなく変換後のStarlight値(例: `rgba(100,100,100,1)`→`rgba(113,114,116,1)`)になっていることを確認した——[0032](0032-literal-layers-generator-migration-plan.md)の訂正で指摘された通り、この移行は可視の配色変更でもある。

## 次

[0032](0032-literal-layers-generator-migration-plan.md)訂正後の順序3: `LITERAL_RANGES`にある7層(道路中心線破線・階段・道路縁・道路構成線トンネル内の道路・分離帯・送電線・送電線破線)+特定地区界+Group F、をまとめて実施し、`LITERAL_RANGES`を退役させる。

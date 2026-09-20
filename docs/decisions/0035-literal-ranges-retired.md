# 0035: `LITERAL_RANGES`の退役

[0032](0032-literal-layers-generator-migration-plan.md)訂正後の推奨順序3を実装した——`LITERAL_RANGES`(位置指定)にあった8層(道路中心線破線・階段・道路縁・道路構成線トンネル内の道路・分離帯・送電線・送電線破線・特定地区界)を`patches`へid参照で移し、Group F(`bvmap-水部表記線point`、色を持たない)も注釈のみのpatchとして追加した。

## 結果

**`assemble.py`から`LITERAL_RANGES`を完全に削除した**。これで`starlight-input.yaml`にある123レイヤー全てが、`patches`/`layers`/tierブロック/注記ブロックのいずれかで**idベースに**参照されるようになった——生の配列位置(インデックス)に依存する箇所がコードから無くなった。

[0020](0020-yaml-wiring-stage1.md)のコードレビューで指摘した「位置ベースの選択は上流の`bvmap-dark.json`の並び替えに弱い」という懸念(指摘#3、当時は見送り)が、これで完全に解消された。[CLAUDE.md](../../CLAUDE.md)が明記する通り`bvmap-dark.json`は`hfu/stars`側で継続的に更新される可能性があるスナップショットであり、この耐性向上は実質的な意味を持つ。

## 新規トークン

`gray_150`(特定地区界専用、既存トークンと非衝突)を追加。値には[0030](0030-starlight-first-color-pass.md)の変換を適用済み([0033](0033-new-token-policy.md)の方針通り)。

## 検証

`literal_count`が23→15に減少(8層分)。全ゲートPASS。`style/bvmap-starlight.json`で`bvmap-送電線`・`bvmap-特定地区界`が変換後のStarlight値になっていることを確認。`bvmap-水部表記線point`は`paint`キー自体を持たない(元データ通り、アイコンのみ)ことを確認済み。

## 残る「literal」は15層

- `bvmap-注記シンボル付き重なり`(色を持たない、1層)
- `color_overrides`未設定の`patches`14層(0021の陸水面クラスタ・行政区画線のうち、まだGroup A/Cとして手を付けていないもの)

## 次

[0032](0032-literal-layers-generator-migration-plan.md)訂正後の順序4([0033](0033-new-token-policy.md)の方針に基づきGroup C残り6層、新規トークン`gray_99`/`gray_35`/`gray_27`)、続いてGroup A(5層、`patches`→`standalone`移動)、Group E(2層、`step_outputs`の`{from:}`参照拡張)。

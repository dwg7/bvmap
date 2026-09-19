# bvmap

[GSI(国土地理院)の最適化ベクトルタイル(optimal_bvmap)](https://github.com/gsi-cyberjapan/optimal_bvmap)を元にした
MapLibreスタイル、`bvmap`(標準版)と`bvmap-dark`(ダーク版、実際の配色は
クリーム/アイボリー系の明るい配色)の`style.json`を管理するリポジトリ。
[stars.optgeo.org](https://stars.optgeo.org)と
[dwg7/zukaku](https://github.com/dwg7/zukaku)の両方で、このスタイルが
参照される。

なぜ`bvmap-dark`ではなく`bvmap`という名前か: 将来light/dark両方の
バリアントを管理する可能性を考慮し、対象をdarkだけに限定しない、機能名
としてのリポジトリ名にしている。

## スタイル一覧

- `style/bvmap-dark.json` — stars.optgeo.orgで現在配信中のスタイルの無加工コピー
- `style/bvmap-starlight.json` — Apple「Starlight」の色調(低彩度・明るめ・
  銀灰色寄り)を目指して磨き上げ中のスタイル。詳細は
  [style/bvmap-starlight.md](style/bvmap-starlight.md)

## プレビュー

```bash
python3 -m http.server 8765
```

を実行し、`http://localhost:8765/examples/style-preview.html`を開くと、
2つのスタイルを切り替えて比較できる。

## 経緯・意思決定の記録

`docs/decisions/`にADR(Architecture Decision Record)として記録している。
特に以下は本プロジェクトの背景を理解する上で重要:

- [0001: 重複リポジトリ確認の結果](docs/decisions/0001-duplicate-repository-check.md)
- [0003: bvmap-starlightという命名](docs/decisions/0003-bvmap-starlight-naming.md)
- [0004: 縦書き棒音符(ー)ワークアラウンドは機能しない](docs/decisions/0004-vertical-choonpu-workaround-does-not-work.md)
- [0005: 目標変更](docs/decisions/0005-goal-change-master-repo-and-starlight-polish.md)

## License

[LICENSE](LICENSE)参照。

# 0006: `hfu/stars`が既にマスターリポジトリだった — 目標の再修正

## 発見

[0005](0005-goal-change-master-repo-and-starlight-polish.md)で「`stars.optgeo.org`のbvmap系style.jsonのマスターリポジトリとして本リポジトリを確立する」という目標を立てたが、調査の結果、**その役割は既に[`hfu/stars`](https://github.com/hfu/stars)が3週間前(2026-08-30)から果たしていた**ことが判明した。

根拠:

- `hfu/stars/config/martin.yaml`の`styles.paths: [/home/stars/styles]`が、Martin tileserverの`/style/<name>`エンドポイントをこのディレクトリから直接配信する設定になっている(`stars.optgeo.org/style/bvmap-dark`のURL構造と一致)
- `hfu/stars/styles/bvmap-dark.json`のコミットメッセージが「Add styles/ as canonical source for production map styles」(2026-08-30)
- 内容を意味的に比較した結果、現在ライブ配信されているものと完全に一致(123レイヤー、差分ゼロ)
- コミット履歴は活発(2026-09-01まで、VBMラベル調整やpositron.jsonの追加等)で、明確に生きた運用リポジトリである

[0001](0001-duplicate-repository-check.md)の重複確認時にこれを見逃していたのは、`gh search code "bvmap-dark"`がファイル内容に対する検索であり、`styles/bvmap-dark.json`自体の中身(JSON)には「bvmap-dark」という文字列が含まれていなかったため(ファイル名だけの一致は拾えなかった)。

## 決定: 役割分担の再定義

目標を以下のように修正する:

- **`dwg7/bvmap`(本リポジトリ)**: スタイル開発専用のワークスペース。配色調整・実験・比較検証(`examples/style-preview.html`)を行う場。「マスターリポジトリとして確立する」という目標は撤回する
- **`hfu/stars`**: 実際の配信設定・PR先。`bvmap-starlight`の配色調整が完成したら、`hfu/stars/styles/`へPRまたはファイルコピーの形で反映する

[0005](0005-goal-change-master-repo-and-starlight-polish.md)の目標2(「bvmap-starlightという名前にふさわしい、実際に磨き上げられたスタイルを提供する」)は変更なく継続する。反映先が明確になったことで、むしろ具体化した。

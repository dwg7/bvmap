# 0011: フォント実装方式(ケース・カンファレンスの結論、ケース3)

## 結論

**実フォント名を`text-font`に直接書く方式で確定**。`font-faces`(自前ファイルホスティング)は保留。

## 根拠

[0007](0007-real-font-names-bypass-local-restriction.md)で、`@font-face`/`local()`を一切使わず`text-font`にプラットフォーム標準フォント名を直接列挙する方式(例: `["Hiragino Mincho ProN", "Yu Mincho", "MS Mincho", "Noto Serif CJK JP"]`)が、macOS Brave実機で動作することを確認済み。`local()`のフィンガープリンティング対策を経由しないため、Chrome系ブラウザでも信頼性が高いと考えられる。

`font-faces`は実ファイルをホスティングする必要があり、フォントライセンスの確認・配信コストが発生する。現時点でその投資に見合う具体的な必要性(例: 本物の斜体フォントの導入)が無いため保留する。

## 今後`font-faces`を再検討する条件

- MapLibre GL JS本体の縦書きネイティブ対応(PR #8399等、[0004](0004-vertical-choonpu-workaround-does-not-work.md)参照)が`font-faces`前提でマージされ、縦書き棒音符問題に再着手する場合
- 実フォント名直書き方式で対応できない、独自にホストしたいフォントが具体的に必要になった場合

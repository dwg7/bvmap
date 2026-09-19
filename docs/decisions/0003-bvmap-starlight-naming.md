# 0003: bvmap-starlightという命名

## 経緯

[0002](0002-bvmap-starlight-vertical-choonpu.md)の作業を始めた際、`bvmap-dark`からフォークした仮の名前として`bvmap-spacegray`を使っていた。しかし実際にレンダリングされた(フォーク元の)`bvmap-dark`を確認したところ、想定していた「暗い配色(黒背景のダークモード、Space Grayのような濃いグラファイト色)」ではなく、**温かみのあるクリーム/アイボリー系の背景に、淡い銀灰色の道路**という、むしろ明るく落ち着いた配色であることが判明した。「dark」も「Space Gray」も、この実態を正確に表していなかった。

## 採用した名前: bvmap-starlight

Appleの製品色名「Starlight」(明るい銀・シャンパン寄りの色調。2026年3月発表のMacBook Air M5でも現役で、廃止されていないことを確認済み)が、この実際の見た目に近い。加えて、このスタイルが`stars.optgeo.org`でホストされているという事実と、「stars → starlight」という語呂が重なる。

この機会に、配色自体も意図的にStarlightの方向性(低彩度・明るめ・銀灰色寄り)へ一貫性を持って仕上げる方針とする。「近づける」というより、既にその方向性にあった配色を磨き上げる作業と捉える(具体的な配色調整は本ADR時点では未着手、別途着手する)。

## `bvmap-dark`識別子との関係(判断保留)

今回のリネームは、このフォーク内(`bvmap-spacegray` → `bvmap-starlight`)に閉じたものであり、**フォーク元の`bvmap-dark`という識別子自体は対象外**。[UNopenGIS/7#1012](https://github.com/UNopenGIS/7/issues/1012)自身の問題再現URL(`https://dwg7.unopengis.org/zukaku/...&style=bvmap-dark`)が示す通り、`?style=bvmap-dark`というクエリパラメータは既にzukaku側で生きており、既存のリンク・ブックマークを壊さない配慮が要る。

`bvmap-starlight`を将来`stars.optgeo.org`/zukakuへ反映する段階になったら、以下のいずれかを選び、その時点でADRを追記すること(現時点では判断保留):

- `bvmap-dark`という識別子を、`bvmap-starlight`へのエイリアス(後方互換)として残す
- あるいは、zukaku側のクエリパラメータも含めて、コーディネートして一括改名する

## スコープ外: 「本当に暗い(黒背景の)」配色

`bvmap-dark`が実際にはダークモードではなかった、という事実が判明した以上、真にOLED向けの暗い配色が必要になるのは別の需要(例: kikimimiのOpen MCTダッシュボードのような、暗い画面との親和性が高い場面)が出てきた時である。その時は`bvmap-starlight`とは別の、新しい名前で新設する(鳥の子色 = torinokoは「紙」文脈向けに温存済み、暗色向けの名前は別途検討)。今回、starlightの配色調整の中に、無理に「暗さ」の要素を混ぜ込まない。

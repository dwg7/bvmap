# 0043: 暗色版 `bvmap-nightsky` を第2パレットとして試作する

dorayaki(点群→Gaussian スプラットのタイル実験)のセッションからの依頼(2026-11-22)。デモのベースマップに
bvmap-starlight(白背景)を使うと、スプラットの隙間が白く見えて質が低く映る。スプラットの平均色は
rgb(68,71,67)(無彩色に近い暗いオリーブ灰)。**暗い緑系の汎用スタイルを starlight の対として持つ**。
名前は hfu さんが 2026-11-22 に `bvmap-nightsky` と決定(他候補: midnight / moonlight)。
`bvmap-dark.json` の名は使わない(実体は白背景の GSI 原本、[0006](0006-hfu-stars-is-already-master-repo.md)周辺参照)。

## 結論(試作の到達点)

- 第2パレットを `starlight-input.yaml` の `variants.nightsky` に置き、
  `python3 generator/assemble.py nightsky` で `style/bvmap-nightsky.json` を生成できる。
  引数なしの `assemble.py` は従来どおり starlight を出し、**`style/bvmap-starlight.json` はバイト単位で無変化**(確認済み)。
- 機械変換版(dorayaki 案)と比べた差は、手調整した 2 トークン(水・縁取り)が効く 13 層だけ(下表)。
- 配信は 2026-11-22 に完了した(下の「配信の経緯」)。試作時点では PR・反映は未実施だった。

## 設計

### 1. 機械変換版の再現(ステップ①)

`generator/night_transform.py`(明るさ反転: `t=(r+g+b)/765`、`out = DARK + (1-t)*(LIGHT-DARK)`、DARK `#2f3a30`、
LIGHT `#eaedea`、alpha 維持。[0030](0030-starlight-first-color-pass.md)の `cool_transform.py` と同じ位置づけの「導出式をコードで残す」もの)と
`experiments/nightsky/mechanical.py`(公開中 starlight の全 `rgb()/rgba()` 文字列に適用、出力は gitignore の
`experiments/nightsky/out/`)。異なる色文字列 55 個(`rgba` 51 + `rgb(...)` 4 ほか。提案書は `rgba()` のみ言及だが、
鉄道・海岸線などに `rgb(100,100,100)` / `rgb(255,255,255)` 形のリテラルがあるので両方変換)。
観察用に左右同期の比較ページ `experiments/nightsky/compare.html`(`python3 -m http.server` で配信)。

### 2. パレット切替の仕組み(ステップ②)

- `variants.<name>.palette` は基本 `palette:` と**完全に同じトークン名**を持つこと。過不足は
  `load_input.load()` が `KeyError` で止める(トークンの付け忘れは「その層だけ明るさが逆」という静かな不具合になるため)。
  トークン名は識別子(`gray_255` は nightsky では暗緑)。名前を作り直すと starlight 側の ADR 参照が全部壊れるので変えない。
- 値の導出: 全 32 トークン(starlight の 31 + 新設 `halo`)を一度 `night_transform` で機械変換し、手調整は下の 2 つだけ
  (+ `transparent` は alpha 0 のため据え置き)。`python3 generator/night_transform.py` が「式との差分=手調整」を常に一覧する。
- **トークン化されていないリテラルの色**(道路・鉄道のティア層の縁取り/白抜き、水涯線・海岸線・地形表記系、など。
  nightsky 出力で 48 層)は、生成の最初に `bvmap-dark.json` の複製へ `night_transform` を掛けておく
  (`assemble.py` の `raw_layers`)ことで、パレットと同じ式・同じ序列に載る(= literal fallback)。
  これは暫定の仕組みで、本来は [0032](0032-literal-layers-generator-migration-plan.md)のトークン化が進むほど不要になる。
- `literal_color_tokens:`(新設、全パレット共通): 文字の縁取りのように「リテラルのままだが式の内側にある」色へ、
  式の構造を保ったままトークンを付ける。`tokenize_literal_colors()` が `palette:<token>` のプレースホルダに置き、
  組み立ての最後に `resolve_palette_refs()` が解決する。starlight は値が変わらず出力無変化。

### 3. 決めたこと

| 項目 | 決定 | 理由 |
|---|---|---|
| 背景の step(zoom<4 / 4–8 / ≥8) | 出力順 `[gray_255, gray_209, gray_255]` はそのまま。**`gray_209`(水)を手調整**: `rgba(30,40,43,1)`(式なら `rgba(78,87,78,1)`) | 式のままだと水(海)が地面より**明るく**なる(starlight の「海が地面より暗い」の逆)。地図の約束として海は地面より暗く、少し青みへ。zoom 5.5 の日本列島で、地面=暗緑・海=一段暗い青緑の分離を確認 |
| 文字の縁取り(白を使う 7 注記層 + 等高線/等深線数値部の計 9 層) | 新トークン `halo` = `rgba(38,48,39,1)`(式なら地面と同色 `rgba(47,58,48,1)`)。starlight 側は `rgba(255,255,255,1)` で無変化 | 縁取りは文字を道路線(地面より明るい)・建物から浮かせる役で、地面そのものではない。地面と同色にせず少し暗くした。`gray_255` を流用しなかった理由もこれ |
| リテラルのまま残る 9 層(`assemble.py` の literal 数) | literal fallback(上記)で変換。個別チューニングはしない | 9 層は`color_overrides`が無い patches 8 層(地形表記面・地形表記線・水部構造物面・水部構造物線・海岸線・河川中心線・水涯線・水部表記線point)と`bvmap-注記シンボル付き重なり`。東京(zoom 16〜17)・渋谷で破綻は見えず。細部は未確認(下記) |
| 意図して共有される 2 トークン | `gray_88`(Anno の group_b ⇔ 等深線・同数値部)と `gray_161`(Anno の c7352 ⇔ 等高線・同数値部)は**共有のまま**、手調整もしない | トークン名で共有しているので自動的に同値が保たれる。nightsky の値はそれぞれ `rgba(166,171,166,1)` / `rgba(110,118,110,1)`。`gray_88_hydro` は starlight では偶然 `gray_88` と同値だが([0033](0033-new-token-policy.md))別トークンのままで、nightsky でも式から同値になるだけ(連動させていない) |
| スプライト | `generator/sprite_nightsky.py`(明暗反転: BT.601 で輝度化 → 同じ `reverse_lightness`)→ `sprite/bvmap-nightsky{,@2x}.{png,json}`(119 アイコン、形状無変化、@2x は [0036](0036-sprite-grayscale-raster-exception.md)と同じ複製) | starlight のスプライトは透明地に暗い灰のアイコンで、暗背景では見えない(機械変換版の観察でも確認)。パレットと同じ式で反転するので、道路番号の文字(`anno_road_number_color` の白→暗緑/黒→明灰)と盾アイコンの明暗が揃う |
| 出典表示 | `variants.nightsky.hosting.source_attribution`: 改変内容に「明暗反転」を追加 | [0038](0038-sprite-modification-attribution.md)の改変明示の義務 |

### 4. 見え方(ステップ①②の観察、ブラウザの左右同期比較)

- 東京駅 zoom 16〜17、渋谷 zoom 17.3: 建物・鉄道・道路・文字とも読める。縁取りは地面より暗く文字が線から浮く。
  博物館・「X」の記号は明るいアイコンとして見える(starlight のスプライトのままだと暗地で沈む)。
- 日本列島 zoom 5.5: 地面(行政区画)= `gray_255` 暗緑、海(背景)= 水トークンで一段暗い。
- 道路: 地面と同色の「白い」道路本体(幅員ランプの default)は暗緑のまま、縁取りが明灰になり、
  「暗い道を明るい線が縁取る」見え方。序列は反転(starlight では地面より暗かった幹線が、nightsky では地面より明るい)。
  都道府県道(`gray_226`)は地面にほぼ溶ける(starlight でも地面との差は小さい。比は保たれている)。

## 未確認・未決(次の判断材料)

- 全 123 層の個別確認はしていない。確認したのは東京駅・渋谷(zoom 16〜17.3)と日本列島(zoom 5.5)のみ。
  dorayaki のデモ(河津 zoom 20 / 15.2)は機械変換版でのみ見られており、生成版での再確認は dorayaki 側に残る。
- ~~道路番号の盾・等高線数値~~ → 配信後にライブで確認済み(下記)。zoom 4〜8 の陸海境界の細部は、ライブでは未確認(zoom 5.5 のローカル確認のみ)。
- 建物の塗りは地面より**明るい**(starlight は暗い)。建物を目立たせる/沈ませるかは配色の好みで、手調整余地。
- ~~スプライトの配信 URL が未配信~~ → 配信済み(下記)。
- dorayaki 向けの「スプラット向け設定」(20% フェード、データから決めた緑み)を nightsky 本体に入れるかは bvmap の設計判断。今回は DARK/LIGHT を提案書の値のままとした。

## bvmap-koicha への影響(触っていない・メモのみ)

- koicha 側 `style/make_koicha_starlight.py` は「上流の公開スナップショット」から生成する。nightsky を作っても **koicha には影響しない**
  (スナップショットを更新しない限り)。
- 将来、koicha の暗色版を出すなら、公開 starlight へ `night_transform` 的な処理を掛ける方式ではなく、
  この `variants` を koicha の生成器が参照する形が筋(タイルは同一、スタイルだけ違う)。
  その場合 koicha の命名規則(D20)は koicha 側が決める。
- なお `literal_color_tokens` と `halo` の追加で starlight 出力は無変化なので、koicha のスナップショット差分は出ない。

## 配信の経緯(2026-11-22、追記)

1. [dwg7/bvmap#1](https://github.com/dwg7/bvmap/pull/1)(本 ADR の試作)を hfu さんがマージ。固定 commit は `6d74f864e4503ee209febfe7c048fda2ee9f4d6f`。
2. [hfu/stars#18](https://github.com/hfu/stars/pull/18)(`styles/bvmap-nightsky.json`、`assets/sprites.json` の `bvmap-nightsky`、`config/martin.yaml` の `sprites.paths`)を出し、hfu さんがマージ。
   `sprites.json` はソースを上記の固定 commit・sha256(json `f5184d39…`、png `a5a4fe23…`)で固定し、改変表示に「グレースケール化・明暗反転」を明記([0038](0038-sprite-modification-attribution.md))。
3. 本番反映は stars の gatekeeper セッションが、hfu さん本人の承認を得て実施(12:59 JST に Martin 再起動、/health は約 6 秒で 200)。この作業(bvmap 側)は本番に触れていない。
   `/style/bvmap-nightsky`(123 層)、`/sprite/bvmap-nightsky` と @2x(各 119 アイコン、pixelRatio 1/2)が 200。他スタイルは無変化(48 ソース・10 スタイル・4 sprite)。
4. スプライト忠実度(stars 側で測定、`assets/sprites.json` の `fidelity` に記録): 上流シート(6d74f864)と配信 PNG を比べ、アルファ不一致 0、完全不透明画素の色不一致 0、半透明の縁でアルファ荷重の色誤差は最大 0.98/255(bvmap-starlight と同じ性質)。配信 PNG の sha256 がシートと一致しないのは、Martin が SVG から組み立て直すため。
5. ライブのスプライトでの目視(bvmap 側): 河津 zoom 15.2・16.3 で等高線とその数値(200・242・300)と地図記号が暗緑地に読める。東京・新橋 zoom 16 で国道 15 号の盾の数字と記号が明るく表示される。

### 残る未確認
全 123 層の個別確認、河津 zoom 20(dorayaki のデモ側)、zoom 4〜8 の陸海境界のライブ確認、建物の塗りが地面より明るいことの是非(配色の好み)。

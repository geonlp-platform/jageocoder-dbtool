Jageocoder 用辞書データベースクリエーター jageocoder-dbcreator
--------------------------------------------------------------

# このソフトウェアについて

Jageocoder-dbcreator (本ソフト) は、[日本の住所ジオコーダー Jageocoder](https://jageocoder.info-proto.com/) 用の住所データベースを作成するソフトウェアです。

最新の住所を解析したり、対応する経緯度を取得したい場合は、本ソフトを利用する必要はありません。 [Jageocoder データファイル一覧](https://www.info-proto.com/static/jageocoder/latest/) からダウンロードしてください。

ダウンロードできるデータファイルは、国の機関が公開しているオープンデータから作成しているため、市販されている詳細地図データに比べると精度が低かったり、網羅範囲が狭いことがあります。購入したり独自に調査して作成した地図データがあり、その地図に対応する住所データベースを作りたい場合には、本ソフトを利用してください。

# 対象とする利用者

本ソフトは Python 3 で実装されたコマンドライン用プログラムです。対象とする利用者は以下の技能を持っていることを想定しています。

- Python 3 の実行環境を構築できる
- コマンドラインでファイルを操作できる
- 地図データを変換するために [QGIS](https://qgis.org/) などの GIS を操作できる

また本ソフトは、 Windows 上のコマンドプロンプト、各種 Linux、 MacOS X で動作確認しています。

# インストール手順

## Python 3.x 仮想環境の作成

Python 3.x のインストール手順と仮想環境の作成方法が分からない場合は、環境に合わせて別紙を参照してください。本ソフトが動作する Python のバージョンは 3.10, 3.11, 3.12 です。

- Linux の場合: "Python のインストールと仮想環境作成手順 (Linux)"
- MacOSX の場合: "Python のインストールと仮想環境作成手順 (MacOSX)"
- Windows コマンドプロンプトの場合: "Python のインストールと仮想環境作成手順 (cmd.exe)"

## 本ソフトのインストール

本ソフトは Python の公式ソフトウェアリポジトリである [PyPI](https://pypi.org/) からダウンロード、インストールします。仮想環境を有効化した状態で次のコマンドを実行してください。
```
(.venv) pip install jageocoder-dbcreator
```

インストールに成功すると `jageocoder_dbcreator` コマンドが実行できるようになります。実行すると簡単なヘルプが表示されます。

> インストールする時は `jageocoder-(ハイフン)dbcreator` 、実行するときは `jageocoder_(アンダースコア)dbcreator` なので間違えないようにしてください。

```
(.venv) jageocoder_dbcreator
Usage:
  jageocoder_dbcreator ( -h | --help )
  jageocoder_dbcreator convert [-d] [--text-dir=<dir>] [--db-dir=<dir>] [--codekey=<codekey>] [--code=<attrs>] [--pref=<attrs>] [--county=<attrs>] [--city=<attrs>] [--ward=<attrs>] [--oaza=<attrs>] [--aza=<attrs>] [--block=<attrs>] [--bld=<attrs>] <geojsonfile>...
  jageocoder_dbcreator check [-d] [--output=<file>] [--codekey=<codekey>] [--code=<attrs>] [--pref=<attrs>] [--county=<attrs>] [--city=<attrs>] [--ward=<attrs>] [--oaza=<attrs>] [--aza=<attrs>] [--block=<attrs>] [--bld=<attrs>] <geojsonfile>...
```

## (参考) 本ソフトのアンインストール

本ソフトをもう利用しない場合は、仮想環境を無効化してから `.venv` ディレクトリごと削除してください。

Linux, MacOSX の場合は `rm -r` でディレクトリ以下を削除します。
```
(.venv) deactivate
rm -r .venv
```

Windows の場合は `rmdir /S` でディレクトリを中身ごと削除します。
```
(.venv) deactivate
> rmdir /S .venv
```

# 使い方

## 地図データの準備

本ソフトでは、 [GeoJSON](https://geojson.org/) 形式の地図データから、 Jageocoder 用の住所データベースを作成します。利用したい地図データが GeoJSON 形式ではない場合、お手数ですが [QGIS](https://qgis.org/) などの GIS ソフトウェアを利用して読み込み、 GeoJSON 形式でエクスポートしてください。また、 GeoJSON 形式の地図データにもいろいろな種類がありますが、本ソフトが対応しているのは「 Point, Polygon, Multipolygon をジオメトリに持つ Feature」のリスト (1行に1オブジェクトを含む JSONL フォーマットのファイル) または「Point, Polygon, Multipolygon をジオメトリに持つ FeatureCollection」です。 LineString をジオメトリに持つデータ (道路など) は利用できません。

サンプルとして、G空間情報センターより「法務省登記所備付地図データ変換済」の北海道室蘭市のデータを利用します (データダウンロードには無償のユーザ登録が必要です)。
https://www.geospatial.jp/ckan/dataset/aigid-moj-01205 を開き、 `01205_室蘭市_公共座標12系_筆R_2024.geojsonGeoJSON` リンクからダウンロードに進んでください。 `01205__12_r_2024.geojson` という GeoJSON 形式のファイルがダウンロードされます。

このファイルを  で開き、室蘭市役所付近のポリゴンをクリックすると、次のような属性を持っていることが分かります。

- ID: H000000072
- 市区町村C: 01205
- 大字コード: 017
- 丁目コード: 000
- 小字コード: 0000
- 予備コード: 00
- 市区町村名: 室蘭市
- 大字名: 幸町
- 丁目名: NULL
- 地番: 130-1
- 精度区分: 甲二
- 座標値種別: 測量成果
- 地図名: H20430201205031
- 座標系: 公共座標12系
- 測地系判別: 測量

<img src="muroran-chibanzu-2024.jpg" width="100%" />

この地図データから、「室蘭市幸町130-1」を「室蘭市 / 幸町/ 130-1」と解析し、ポリゴンの中心付近の経緯度を返すことができる住所データベースを作ります。

## 代表点座標と住所の確認

Jageocoder は住所を以下のレベルに分けて管理します。

- Pref: 都道府県  (「北海道」など)
- City: 市町村・特別区 (「室蘭市」「千代田区」など)
- Ward: 政令市の区 (「天王寺区」など)
- Oaza: 大字 (「市場町切幡」など)
- Aza: 字・丁目 (「字古田」など)
- Block: 街区・地番 (「201番地」など)
- Bld: 住居番号・枝番 (「1」など)

そのため、地図データから住所データベースを作る際には、元の地図データに格納されている属性を対応するレベルに割り当てる必要があります。

また、 Jageocoder は座標を経緯度で管理します。そのため、地図データがポリゴンで提供されている場合、ポリゴン内の１点を代表点として算出したり、ポリゴンの識別コードを登録しておく必要があります。

`jageocoder_dbcreator` では、これらの指定をオプションで行います。

まず元の地図データの割り当てが正しく行えているかを確認するため、 `jageocoder_dbcreator check` コマンドを実行します。

```
jageocoder_dbcreator check --code=ID --pref==北海道 --city=市区町村名 --oaza=大字名 --aza=丁目名 --block={地番}番地 01205__12_r_2024.geojson --output=01205__12_r_2024_point.geojsonl
```

オプションの意味は次の通りです。

- `--code=ID`: `ID` 属性を識別コードとして利用します。
- `--pref==北海道`: 入力データには「都道府県」に該当する属性が含まれていないため、 Pref レベルに常に「北海道」を指定します。決まった値を指定する場合は `==` を使います。
- `--city=市区町村名`: `市区町村名` 属性を City レベルに割り当てます。
- `--oaza=大字名`: `大字名` 属性を Oaza レベルに割り当てます。
- `--aza=丁目名`: `丁目名` 属性を Aza レベルに割り当てます。
- `--block={地番}番地`: `地番` 属性の値の後ろに `番地` を結合した文字列を Block レベルに割り当てます。
- `--output=...`: 割り当てた結果を確認するための GeoJSON データを指定したファイル名に出力します。このオプションを省略すると標準出力 (画面) に表示されます。

この例では Ward レベルと Bld レベルには何も割り当てられていないため、常に空欄になります。
実行すると `01205__12_r_2024_point.geojsonl` という JSONL 形式のファイルが作成されます。 QGIS で開くと図のように代表点の位置と住所の割り当てを確認することができます。

<img src="muroran-point-2024.jpg" witdh="100%" />

また、 `hcode` という属性に GeoJSON の `ID` の値が入っていることも確認できます。
> この属性名を変更したい場合は、 `--codekey=muroran` のように指定できます。省略すると `hcode` になります。


jageocoder_dbcreator convert --id=99 --title="登記所備付地図データ" --url="https://www.geospatial.jp/ckan/organization/aigid-moj-map" --code=ID --pref==北海道 --city=市区町村名 --oaza=大字名 --aza=丁目名 --block={地番}番地 testdata/01205__12_r_2024.geojson --db-dir=murorandb

jageocoder search --db-dir=db 幸町１３０－１
{"matched": "幸町１３０－１", "candidates": [{"id": 19381, "name": "130-1番地", "x": 140.9738006591797, "y": 42.31498336791992, "level": 7, "priority": 99, "note": "hcode:H000000072", "fullname": ["北海道", "室蘭市", "幸町", "130-1番地"]}]}

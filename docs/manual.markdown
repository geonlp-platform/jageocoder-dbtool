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

サンプルとして、G空間情報センターより「法務省登記所備付地図データ変換済」の北海道室蘭市のデータを利用します (データダウンロードには無償のユーザ登録が必要です)。
https://www.geospatial.jp/ckan/dataset/aigid-moj-01205 を開き、 `01205_室蘭市_公共座標12系_筆R_2024.geojsonGeoJSON` リンクからダウンロードに進んでください。 `01205__12_r_2024.geojson` という GeoJSON 形式のファイルがダウンロードされます。

このファイルを [QGIS](https://qgis.org/) で開き、室蘭市役所付近のポリゴンをクリックすると、次のような属性を持っていることが分かります (画像) 。

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

jageocoder_dbcreator check --code=ID --pref==北海道 --city=市区町村名 --oaza=大字名 --aza=丁目名 --block={地番}番地 ..\Downloads\01205__12_r_2024.geojson --output ..\Downloads\01205__12_r_2024_point.geojsonl

jageocoder_dbcreator convert --code=ID --pref==北海道 --city=市区町村名 --oaza=大字名 --aza=丁目名 --block={地番}番地 ..\Downloads\01205__12_r_2024.geojson

jageocoder search --db-dir=db 幸町１３０－１
{"matched": "幸町１３０－１", "candidates": [{"id": 19381, "name": "130-1番地", "x": 140.9738006591797, "y": 42.31498336791992, "level": 7, "priority": 99, "note": "hcode:H000000072", "fullname": ["北海道", "室蘭市", "幸町", "130-1番地"]}]}

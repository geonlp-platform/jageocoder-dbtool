import logging
import sys

from .metadata import Catalog
from .convertor import Convertor

from docopt import docopt

HELP = """
Jageocoder 用住所データベースファイル作成ツール

Usage:
  {p} ( -h | --help )
  {p} ( -v | --version )
  {p} check [-d] [--output=<file>] \
[--codekey=<codekey>] [--code=<attrs>] \
[--pref=<attrs>] [--county=<attrs>] [--city=<attrs>] \
[--ward=<attrs>] [--oaza=<attrs>] [--aza=<attrs>] \
[--block=<attrs>] [--bld=<attrs>] <geojsonfile>...
  {p} geojson2db [-d] [--text-dir=<dir>] [--db-dir=<dir>] \
[--id=<id>] [--title=<title>] [--url=<url>] \
[--codekey=<codekey>] [--code=<attrs>] \
[--pref=<attrs>] [--county=<attrs>] [--city=<attrs>] \
[--ward=<attrs>] [--oaza=<attrs>] [--aza=<attrs>] \
[--block=<attrs>] [--bld=<attrs>] <geojsonfile>...
  {p} geojson2text [-d] [--text-dir=<dir>] \
[--id=<id>] [--title=<title>] [--url=<url>] \
[--codekey=<codekey>] [--code=<attrs>] \
[--pref=<attrs>] [--county=<attrs>] [--city=<attrs>] \
[--ward=<attrs>] [--oaza=<attrs>] [--aza=<attrs>] \
[--block=<attrs>] [--bld=<attrs>] <geojsonfile>...
  {p} text2db [-d] [--db-dir=<dir>] (--text-dir=<dir>|<textfile>...)

Options:
  -h --help         このヘルプを表示
  -v --version      このツールのバージョンを表示
  -d --debug        デバッグ用情報を出力
  --text-dir=<dir>  テキスト形式データを出力するディレクトリを指定
  --db-dir=<dir>    住所データベース出力ディレクトリを指定 [default: db]
  --id=<id>         データセットのIDを1から99の整数で指定 [default: 99]
  --title=<title>   データセットのタイトルを指定 [default: (no name)]
  --url=<url>       データセット詳細のURLを指定
  --output=<file>   チェック結果を出力するファイルを指定
  --codekey=<key>   固有のコードのキーを指定 [default: hcode]
  --code=<attrs>    固有のコードを含む属性
  --pref=<attrs>    都道府県名とする属性、または固定値
  --county=<attrs>  郡・支庁・島名とする属性、または固定値
  --city=<attrs>    市町村・特別区名とする属性、または固定値
  --ward=<attrs>    区名とする属性、または固定値
  --oaza=<attrs>    大字名とする属性
  --aza=<attrs>     字・丁目名とする属性
  --block=<attrs>   街区・地番名とする属性
  --bld=<attrs>     住居番号・枝番とする属性

Notes:
  <attrs> は GeoJSON の "properties" 属性の直下の属性名を指定します．
  * 複数の属性を指定したい場合は "," で区切って列挙してください
  * 固定値を指定したい場合は "==" の後に値を直接記述してください
  * "{{x}}" のように指定すると、属性xの値を埋め込んだ文字列を作ります。
    たとえば "{{chome}}丁目" を指定すると、chome の値が 1 ならば
    "1丁目" になります。

Examples:

指定したパラメータに従って住所を構築し、入力 GeoJSON の
代表点座標を計算し、Point 型の GeoJSON を標準出力に出力します。

  {p} check --pref==東京都 --city=shi \
--ward=ku --oaza=chomei --aza={{chome}}丁目 \
--block={{banchi}}番地 --bld=go testdata/15ku_wgs84.geojson

GeoJSON ファイルから住所データベースを作成します．

  {p} geojson2db --code=FID --pref==東京都 --city=shi \
--ward=ku --oaza=chomei --aza={{chome}}丁目 \
--block={{banchi}}番地 --bld=go testdata/15ku_wgs84.geojson

GeoJSON ファイルからテキスト形式データを作成します．

  {p} geojson2text --code=FID --pref==東京都 --city=shi \
--ward=ku --oaza=chomei --aza={{chome}}丁目 \
--block={{banchi}}番地 --bld=go \
--text-dir=text/ testdata/15ku_wgs84.geojson

テキスト形式データから住所データベースを作成します．

  {p} text2db --text-dir=texts

""".format(p='dbtool')


def main():
    args = docopt(HELP)

    if args["--version"]:
        print(Catalog.get_version())

    if args['--debug']:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    # Set logger
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s:%(name)s:%(lineno)s:%(message)s')
    )
    for target in ('jageocoder', 'jageocoder_dbtool',):
        logger = logging.getLogger(target)
        logger.setLevel(log_level)
        logger.addHandler(console_handler)

    # 属性のマッピング
    convertor = Convertor()
    for key in (
        "pref", "county", "city", "ward",
            "oaza", "aza", "block", "bld", "code"):
        arg = args[f"--{key}"]

        if arg:
            convertor.fieldmap[key] = arg.split(",")

    if args["--codekey"]:
        convertor.codekey = args["--codekey"]

    if args["--text-dir"]:
        convertor.text_dir = args["--text-dir"]

    if args["--db-dir"]:
        convertor.db_dir = args["--db-dir"]

    if args["--id"]:
        id = int(args["--id"])
        if args["--id"] != str(id) or id < 1 or id >= 100:
            print(
                "'--id' は1から99までの整数値を指定してください",
                file=sys.stderr)
            exit(0)

        convertor.dataset_meta["id"] = id

    if args["--title"]:
        convertor.dataset_meta["title"] = args["--title"]

    if args["--url"]:
        convertor.dataset_meta["url"] = args["--url"]

    # ディスパッチ
    if args["check"]:
        convertor.point_geojson(
            args["<geojsonfile>"],
            args["--output"])
    elif args["geojson2db"]:
        textfiles = convertor.geojson2text(args["<geojsonfile>"])
        convertor.text2db(textfiles=textfiles)
    elif args["geojson2text"]:
        convertor.text_dir = convertor.text_dir or "texts"
        textfiles = convertor.geojson2text(args["<geojsonfile>"])
    elif args["text2db"]:
        if args["--text-dir"]:
            convertor.text2db(textfiles=None)
        else:
            convertor.text2db(textfiles=args["<textfile>"])


if __name__ == '__main__':
    main()

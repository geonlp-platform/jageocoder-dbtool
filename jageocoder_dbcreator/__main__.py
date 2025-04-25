import logging

from docopt import docopt

from jageocoder_dbcreator.convertor import Convertor

HELP = """
Jageocoder 用住所データベースファイル作成ツール

Usage:
  {p} [-h]
  {p} convert [-d] [--text-dir=<dir>] [--db-dir=<dir>] \
[--codekey=<codekey>] [--code=<attrs>] \
[--pref=<attrs>] [--county=<attrs>] [--city=<attrs>] \
[--ward=<attrs>] [--oaza=<attrs>] [--aza=<attrs>] \
[--block=<attrs>] [--bld=<attrs>] <geojsonfile>...
  {p} check [-d] [--output=<file>] \
[--codekey=<codekey>] [--code=<attrs>] \
[--pref=<attrs>] [--county=<attrs>] [--city=<attrs>] \
[--ward=<attrs>] [--oaza=<attrs>] [--aza=<attrs>] \
[--block=<attrs>] [--bld=<attrs>] <geojsonfile>...

Options:
  -h --help         このヘルプを表示
  -d --debug        デバッグ用情報を出力
  --text-dir=<dir>  テキスト形式データを出力するディレクトリを指定
  --db-dir=<dir>    辞書データベース出力ディレクトリを指定 [default: ./db]
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

'db' ディレクトリに辞書データベースを作成します．

  {p} convert --code=FID --pref==東京都 --city=shi \
--ward=ku --oaza=chomei --aza={{chome}}丁目 \
--block={{banchi}}番地 --bld=go testdata/15ku_wgs84.geojson

""".format(p='jageocoder_dbcreator')


def main():
    args = docopt(HELP)
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
    for target in ('jageocoder', 'jageocoder_dbcreator',):
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

    # ディスパッチ
    if args["check"]:
        convertor.point_geojson(
            args["<geojsonfile>"],
            args["--output"])

    if args["convert"]:
        convertor.convert(args["<geojsonfile>"])


if __name__ == '__main__':
    main()

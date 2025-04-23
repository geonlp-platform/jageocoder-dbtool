import jageocoder_dbcreator
import logging
import os
from docopt import docopt

HELP = """
Jageocoder 用住所データベースファイル作成ツール

Usage:
  {p} [-h]
  {p} [-d] [--check] [--text-dir=<dir>] [--db-dir=<dir>] \
    [--pref=<attrs>] [--county=<attrs>] [--city=<attrs>] \
    [--ward=<attrs>] [--oaza=<attrs>] [--aza=<attrs>] \
    [--block=<attrs>] [--bld=<attrs>] <geojsonfile>...

Options:
  -h --help         このヘルプを表示
  -d --debug        デバッグ用情報を出力
  --check           辞書データチェック用の GeoJSON ファイルを出力
  --text-dir=<dir>  テキスト形式データ出力ディレクトリを指定
  --db-dir=<dir>    辞書データベース出力ディレクトリを指定 [default: ./db]
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
  複数の属性を指定したい場合は "," で区切って列挙します．
  固定値を指定したい場合は "==" の後に値を直接記述してください．

Example:

  python -m {p} --code=FID --pref==東京都 --city=shi --ward=ku \
    --oaza=chomei --aza=chome --block=banchi --bld=go

  'db' ディレクトリ以下に辞書データベースを作成します．
""".format(p='jageocoder_dbcreator')

if __name__ == '__main__':
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
    for target in ('jageocoder', 'jageocoder_converter',):
        logger = logging.getLogger(target)
        logger.setLevel(log_level)
        logger.addHandler(console_handler)

    # Set parameters
    kwargs = {
        'use_postcode': not args['--no-postcode'],
        'use_geolod': not args['--no-geolod'],
        'use_oaza': not args['--no-oaza'],
        'use_gaiku': not args['--no-gaiku'],
        'use_geolonia': not args['--no-geolonia'],
        'use_jusho': not args['--no-jusho'],
        'use_basereg': not args['--no-basereg'],
        'use_chiban': False,
        'quiet': args['--quiet'],
    }

    # Set paths
    basedir = os.getcwd()
    output_dir = args['--output-dir']

    if args['--db-dir'] is None:
        kwargs['db_dir'] = None
    elif os.path.isabs(args['--db-dir']):
        kwargs['db_dir'] = args['--db-dir']
    else:
        kwargs['db_dir'] = os.path.join(
            output_dir, args['--db-dir']
        )

    if os.path.isabs(args['--download-dir']):
        kwargs['download_dir'] = args['--download-dir']
    else:
        kwargs['download_dir'] = os.path.join(
            output_dir, args['--download-dir']
        )

    if os.path.isabs(args['--textdata-dir']):
        kwargs['textdata_dir'] = args['--textdata-dir']
    else:
        kwargs['textdata_dir'] = os.path.join(
            output_dir, args['--textdata-dir']
        )

    # Set target prefectures
    if len(args['<prefcodes>']) == 0:
        kwargs['prefs'] = None
    else:
        kwargs['prefs'] = args['<prefcodes>']

    # Run converters
    db_dir = jageocoder_converter.convert(**kwargs)

    print("Finished. The dictionary created in {}.".format(
        os.path.abspath(db_dir)))
    print((
        "You may delete '{d}/' containing downloaded files "
        "and '{t}/' containg text files created during "
        "the conversion process.").format(
        d=os.path.abspath(kwargs['download_dir']),
        t=os.path.abspath(kwargs['textdata_dir'])
    ))

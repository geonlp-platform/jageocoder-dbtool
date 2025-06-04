import bz2
from collections import OrderedDict
import glob
import json
import logging
import os
import re
from pathlib import Path
import sys
import tempfile
from typing import Any, Iterable, List, Optional, Sequence, TextIO, Tuple

from jageocoder.address import AddressLevel
from jageocoder.node import AddressNode
import shapely
from tqdm import tqdm

from . import spatial
from .customtypes import AddressType, PathLikeType, PathListType
from .data_manager import DataManager
from .metadata import Catalog


logger = logging.getLogger(__name__)


class ConvertorException(Exception):
    pass


class Convertor(object):

    NONAME_COLUMN = f'{AddressNode.NONAME};{AddressLevel.OAZA}'
    re_inline = re.compile(r'(\{(.+?)\})')

    def __init__(self):
        self.db_dir: Path = Path.cwd() / "db/"
        self.tmpdir: Optional[tempfile.TemporaryDirectory] = None
        self.text_dir: Optional[PathLikeType] = None
        self.do_check = False
        self.fieldmap = {
            "pref": [],
            "county": [],
            "city": [],
            "ward": [],
            "oaza": [],
            "aza": [],
            "block": [],
            "bld": [],
            "code": [],
        }
        self.codekey = "hcode"
        self.dataset_meta = {
            "id": 99,
            "title": "(no name)",
            "url": "",
        }

    def get_textdir(self) -> Path:
        if self.text_dir is None:
            raise RuntimeError("text_dir がセットされていません")

        return Path(self.text_dir)

    def _parse_geojson(self, geojson: Path):
        """
        geojson ファイルから Feature を1つずつ取り出すジェネレータ。
        """
        filetype = "jsonl"
        with open(geojson, "r", encoding="utf-8") as fin:
            try:
                head = fin.readline()
            except UnicodeDecodeError:
                raise ConvertorException((
                    f"ファイル '{geojson}' の先頭行に UTF-8 以外の"
                    "文字が含まれているためスキップします．"))

            try:
                obj = json.loads(head)
                if "type" in obj and obj["type"] == "FeatureCollection":
                    filetype = "featurecollection"

            except json.decoder.JSONDecodeError:
                filetype = "featurecollection"

            fin.seek(0)
            if filetype == "jsonl":
                logger.debug("   JSONL として処理します．")
                filesize = geojson.stat().st_size
                with tqdm(total=filesize) as pbar:
                    try:
                        for lineno, line in enumerate(fin):
                            obj = json.loads(line)
                            if "type" not in obj or \
                                    obj["type"] != "Feature":
                                raise ConvertorException((
                                    f"ファイル '{geojson}' の {lineno} 行目の"
                                    "フォーマットが正しくないのでスキップします．"))

                            yield obj
                            linesize = len(line.encode())
                            pbar.update(linesize)
                    except UnicodeDecodeError:
                        raise ConvertorException((
                            f"ファイル '{geojson}' の {lineno} 行目に UTF-8 以外の"
                            "文字が含まれているためスキップします．"))

            else:
                logger.debug("   FeatureCollection として処理します．")
                collection = json.load(fin)
                if "type" not in collection or \
                        collection["type"] != "FeatureCollection":
                    raise ConvertorException(
                        f"ファイル '{geojson}' のフォーマットが正しくない")

                with tqdm(total=len(collection["features"])) as pbar:
                    for feature in collection["features"]:
                        yield feature
                        pbar.update(1)

    def _extract_field(self, feature: dict, el: str, allow_zero: bool = False) -> str:
        """
        Feature の property 部から el で指定された属性の値を取得する。

        ただし el の先頭が "=" の場合、後に続く文字列を返す (固定値)。
        el に '{<x>}' が含まれる場合、 <x> の部分を property 部の x 属性から
        取得して文字列を構築する。
        """

        def __is_none(v: Any) -> bool:
            """
            None 値判定を行う。 None 値の場合に True。

            以下の場合に None とみなす。
            - str の場合: 空欄・"none"・"null"・"na" (case insensitive)
            - int, float の場合: 0 以下 (0を含む)
            - その他: None, False

            """
            if v is None:
                return True

            if isinstance(v, str):
                return v.lower() in ("", "none", "null", "na")

            if isinstance(v, (int, float)):
                return v <= 0.0

            if isinstance(v, (list, tuple)):
                return len(v) == 0

            if isinstance(v, bool):
                return v is False

            raise ConvertorException(
                "属性値の型 '{}' は非対応です".format(type(v)))

        if el[0] == "=":  # 固定値
            return el[1:]

        matches = self.re_inline.findall(el)
        if len(matches) == 0:  # properties の下の属性を参照
            if el in feature["properties"]:
                v = feature["properties"][el]
                if allow_zero is False and __is_none(v):
                    return ""

                return str(v)

            return ""

        # properties の下の属性を利用して文字列を構築
        for m in matches:
            e = m[1]
            if e in feature["properties"]:
                v = feature["properties"][e]
                if __is_none(v):
                    return ""

                el = el.replace(m[0], str(v))

        return el

    def _get_names(self, feature: dict) -> List[AddressType]:
        """
        Feature の property 部から住所要素リストを作成する。
        """
        names = []
        if "pref" in self.fieldmap:
            # 都道府県を設定
            for e in self.fieldmap["pref"]:
                val = self._extract_field(feature, e)
                if val is not None:
                    names.append((AddressLevel.PREF, val))

        if "county" in self.fieldmap:
            # 郡・支庁
            for e in self.fieldmap["county"]:
                val = self._extract_field(feature, e)
                if val is not None:
                    names.append((AddressLevel.COUNTY, val))

        if "city" in self.fieldmap:
            # 市町村・特別区
            for e in self.fieldmap["city"]:
                val = self._extract_field(feature, e)
                if val is not None:
                    names.append((AddressLevel.CITY, val))

        if "ward" in self.fieldmap:
            # 区
            for e in self.fieldmap["ward"]:
                val = self._extract_field(feature, e)
                if val is not None:
                    names.append((AddressLevel.WARD, val))

        if "oaza" in self.fieldmap:
            # 大字
            for e in self.fieldmap["oaza"]:
                val = self._extract_field(feature, e)
                if val is not None:
                    names.append((AddressLevel.OAZA, val))

        if "aza" in self.fieldmap:
            # 字・丁目
            for e in self.fieldmap["aza"]:
                val = self._extract_field(feature, e)
                if val is not None:
                    names.append((AddressLevel.AZA, val))

        if "block" in self.fieldmap:
            # 街区・地番
            for e in self.fieldmap["block"]:
                val = self._extract_field(feature, e)
                if val is not None:
                    names.append((AddressLevel.BLOCK, val))

        if "bld" in self.fieldmap:
            # 住居番号・枝番
            for e in self.fieldmap["bld"]:
                val = self._extract_field(feature, e)
                if val is not None:
                    names.append((AddressLevel.BLD, val))

        return names

    def _to_text(self, geojson: Path) -> Optional[Path]:
        """
        geojson を解析し、テキスト形式データを text_dir に生成する。
        変換に成功した場合、テキスト形式データのパスを返し、
        失敗した場合は None を返す。
        """
        output_path = self.text_path / (geojson.stem + ".txt.bz2")
        logger.debug(f"テキスト形式データを '{output_path}' に出力中...")
        try:
            with bz2.open(output_path, "wt", encoding="utf-8") as fout:
                # dataset metadata
                print("# " + json.dumps(
                    Catalog.create_metadata(**self.dataset_meta),
                    ensure_ascii=False
                ), file=fout)
                # Data body
                for feature in self._parse_geojson(geojson):
                    names = self._get_names(feature)
                    x, y = self.get_xy(feature["geometry"])
                    note = None
                    if "code" in self.fieldmap:
                        code = ""
                        for e in self.fieldmap["code"]:
                            v = self._extract_field(
                                feature, e, allow_zero=True)
                            if v is not None:
                                code += v

                        if code != "":
                            note = f"{self.codekey}:{code}"

                    self.print_line(
                        fout,
                        self.dataset_meta["id"],
                        names,
                        x, y,
                        note
                    )

        except ConvertorException as e:
            print(e, file=sys.stderr)
            output_path.unlink()
            output_path = None

        return output_path

    def _to_point_geojson(
        self, geojson: Path,
        output: Optional[PathLikeType]
    ):
        """
        geojson を解析し、チェック用の Point GeoJSON を標準出力に出力。
        """
        abspath = None
        if output is None:
            fout = sys.stdout
            logger.debug("標準出力に出力します．")
        else:
            fout = open(output, "w", encoding="utf-8")
            abspath = Path(output).absolute()
            logger.debug(f"'{abspath}' に出力します．")

        # チェック用の Point GeoJSON を出力
        try:
            for feature in self._parse_geojson(geojson):
                names = self._get_names(feature)
                x, y = self.get_xy(feature["geometry"])
                code = None
                if "code" in self.fieldmap:
                    code = ""
                    for e in self.fieldmap["code"]:
                        v = self._extract_field(feature, e, allow_zero=True)
                        if v is not None:
                            code += v

                address = OrderedDict()
                i = 0
                for level in (
                    (AddressLevel.PREF, "pref"),
                    (AddressLevel.COUNTY, "county"),
                    (AddressLevel.CITY, "city"),
                    (AddressLevel.WARD, "ward"),
                    (AddressLevel.OAZA, "oaza"),
                    (AddressLevel.AZA, "aza"),
                    (AddressLevel.BLOCK, "block"),
                    (AddressLevel.BLD, "bld"),
                ):
                    while i < len(names):
                        n = names[i]
                        if n[0] == level[0]:
                            if level[1] not in address:
                                address[level[1]] = n[1]
                            else:
                                address[level[1]] += f" {n[1]}"
                            i += 1
                        else:
                            break

                point_feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [x, y],
                    },
                    "properties": {
                        self.codekey: code,
                        "address": " ".join([n[1] for n in names]),
                        **address,
                    }
                }
                print(
                    json.dumps(point_feature, ensure_ascii=False),
                    file=fout
                )

        except ConvertorException as e:
            print(e, file=sys.stderr)
            if abspath:
                abspath.unlink()

        if output is not None:
            fout.close()

    def point_geojson(
            self,
            geojsons: Iterable[PathLikeType],
            output: Optional[PathLikeType]):
        """
        チェック用ポイント GeoJSON を出力する
        """
        for geojson in geojsons:
            geojson_path = Path(geojson)
            basename = geojson_path.name
            logger.debug(f"'{basename}' を処理します．")
            self._to_point_geojson(geojson_path, output)

        return

    def create_workdir(self):
        """
        作業用一時ディレクトリを作成する
        """
        if self.tmpdir is None:
            self.tmpdir = tempfile.TemporaryDirectory()

        return Path(self.tmpdir.name)

    def delete_workdir(self):
        """
        作業用一時ディレクトリを削除する
        """
        if self.tmpdir is not None:
            del self.tmpdir
            self.tmpdir = None

    def geojson2text(self, geojsons: Iterable[os.PathLike]) -> List[Path]:
        """
        GeoJSON ファイルからテキスト形式データを作成する

        変換に成功したテキスト形式データのパスのリストを返す。
        """
        if self.text_dir is not None:
            self.text_path = Path(self.text_dir).absolute()
            if not self.text_path.exists():
                self.text_path.mkdir()

            logger.debug(f"テキスト形式データを '{self.text_path}' の下に出力します．")

        else:
            self.text_path = self.create_workdir()
            logger.debug((
                "テキスト形式データを一時ディレクトリ "
                f"'{self.text_path}' の下に出力します．"))

        # GeoJSON ファイルをテキストファイルに変換
        textfiles = []
        for geojson in geojsons:
            geojson_path = Path(geojson)
            basename = geojson_path.name
            logger.debug(f"'{basename}' を処理します．")
            textfile_path = self._to_text(geojson_path)
            if textfile_path:
                textfiles.append(textfile_path)

        return textfiles

    def text2db(
        self,
        textfiles: Optional[PathListType] = None,
        targets: Optional[Sequence[str]] = None,
    ):
        if textfiles is None:
            if self.text_dir:
                texts = os.path.join(self.text_dir, "*.txt.bz2")
                textfiles = glob.glob(texts)  # type: ignore

            if textfiles is None or len(textfiles) == 0:
                raise RuntimeError("textfile または text_dir のどちらかを指定してください")

        textfiles = [Path(file) for file in textfiles]

        manager = DataManager(
            db_dir=self.db_dir,
            text_dir=self.text_dir,
            targets=targets,
        )

        # テキストファイルからデータベースを作成
        manager.register(textfiles)

        # 検索インデックスを作成
        manager.create_index()

        db_path = Path(self.db_dir).absolute()
        logger.debug(f"データベースを '{db_path}' に構築完了．")

    def get_xy(self, geometry: dict) -> Tuple[float, float]:
        """
        Geometry を解析して代表点座標を取得する
        """
        polygon: List[List[float]] = []
        if geometry["type"] == "Point":
            return geometry["coordinates"]
        elif geometry["type"] == "MultiPoint":
            return geometry["coordinates"][0]
        elif geometry["type"] == "Polygon":
            polygon = geometry["coordinates"]
        elif geometry["type"] == "MultiPolygon":
            max_poly = None
            max_area = 0
            for _poly in geometry["coordinates"]:
                outer_polygon = _poly[0]
                inner_polygons = _poly[1:]
                poly_wgs84 = shapely.Polygon(outer_polygon, inner_polygons)
                poly_utm = spatial.transform_polygon(
                    poly_wgs84, 4326, 3857, True)
                area = poly_utm.area
                if area > max_area:
                    max_poly = _poly
                    max_area = area

            assert (max_poly is not None)
            polygon = max_poly
        else:
            raise ConvertorException(
                "対応していない geometry type: {}".format(
                    geometry["type"]))

        outer_polygon = polygon[0]
        inner_polygons = polygon[1:]
        poly_wgs84 = shapely.Polygon(outer_polygon, inner_polygons)
        poly_utm = spatial.transform_polygon(poly_wgs84, 4326, 3857, True)
        center_utm = spatial.get_center(poly_utm)
        center_wgs84 = spatial.transform_point(center_utm, 3857, 4326)
        return (center_wgs84.y, center_wgs84.x)

    def print_line(
        self,
        fp: TextIO,
        priority: int,
        names: List[AddressType],
        x: float,
        y: float,
        note: Optional[str] = None
    ) -> None:
        """
        テキストデータ一行分のレコードを出力。
        """
        line = ""

        prev_level = 0
        for name in names:
            if name[1] == '':
                continue

            # Insert NONAME-Oaza when a block name comes immediately
            # after the municipality name.
            level = name[0]
            if prev_level <= AddressLevel.WARD and level >= AddressLevel.BLOCK:
                line += self.NONAME_COLUMN

            line += '{:s};{:d},'.format(name[1], level)
            prev_level = level

        if priority is not None:
            line += '!{:02d},'.format(priority)

        line += "{},{}".format(x or 999, y or 999)
        if note is not None:
            line += ',{}'.format(str(note))

        print(line, file=fp)

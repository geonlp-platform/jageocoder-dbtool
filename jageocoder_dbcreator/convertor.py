import bz2
import json
import logging
import re
from pathlib import Path
import tempfile
from typing import TextIO, Optional, List, Tuple, Iterator

from jageocoder.address import AddressLevel
from jageocoder.dataset import Dataset
from jageocoder.node import AddressNode

import shapely

from jageocoder_dbcreator.data_manager import DataManager
from jageocoder_dbcreator import spatial


Address = Tuple[int, str]
logger = logging.getLogger(__name__)


class Convertor(object):

    NONAME_COLUMN = f'{AddressNode.NONAME};{AddressLevel.OAZA}'
    kansuji = ['〇', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    trans_kansuji_zarabic = str.maketrans(
        '一二三四五六七八九', '１２３４５６７８９')
    re_inline = re.compile(r'(.*)\{(.+?)\}(.*)')

    def __init__(self):
        self.db_dir = Path.cwd() / "db/"
        self.text_dir = None
        self.title = "(noname)"
        self.url = ""
        self.pref_code = "00"
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

    def _parse_geojson(self, geojson: Path):
        """
        geojson ファイルから Feature を1つずつ取り出すジェネレータ。
        """
        filetype = "jsonl"
        with open(geojson, "r") as fin:
            head = fin.readline()
            try:
                obj = json.loads(head)
                if "type" in obj and obj["type"] == "FeatureCollection":
                    filetype = "featurecollection"

            except json.decoder.JSONDecodeError:
                filetype = "featurecollection"

            fin.seek(0)
            if filetype == "jsonl":
                for lineno, line in enumerate(fin):
                    obj = json.loads(line)
                    if "type" not in obj or \
                            obj["type"] != "Feature":
                        raise RuntimeError(
                            f"ファイル '{geojson}' の {lineno} 行目のフォーマットが正しくない"
                        )

                    yield obj

            else:
                collection = json.load(fin)
                if "type" not in collection or \
                        collection["type"] != "FeatureCollection":
                    raise RuntimeError(
                        f"ファイル '{geojson}' のフォーマットが正しくない")

                for feature in collection["features"]:
                    yield feature

    def _extract_field(self, feature: dict, el: str, allow_zero: bool = False) -> str:
        """
        Feature の property 部から el で指定された属性の値を取得する。

        ただし el の先頭が "=" の場合、後に続く文字列を返す (固定値)。
        el に '{<x>}' が含まれる場合、 <x> の部分を property 部の x 属性から
        取得して文字列を構築する。
        """
        def __is_none(v: any) -> bool:
            if isinstance(v, str):
                return v == ""

            if isinstance(v, (int, float)):
                return v <= 0

            if isinstance(v, (list, tuple)):
                return len(v) == 0

            return v is None

        if el[0] == "=":  # 固定値
            return el[1:]

        m = self.re_inline.match(el)
        if m is None:  # properties の下の属性を参照
            if el in feature["properties"]:
                v = feature["properties"][el]
                if allow_zero is False and __is_none(v):
                    return None

                return str(v)

            return None

        # properties の下の属性を利用して文字列を構築
        e = m.group(2)
        if e in feature["properties"]:
            v = feature["properties"][e]
            if __is_none(v):
                return None

            return m.group(1) + str(v) + m.group(3)

        return None

    def _get_names(self, feature: dict) -> List[Address]:
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

    def _to_text(self, geojson: Path, text_dir: Path):
        """
        geojson を解析し、テキスト形式データを text_dir に生成する。
        """
        stem = geojson.stem
        if not stem.startswith(self.pref_code + "_"):
            stem = self.pref_code + "_" + stem

        output_path = text_dir / (stem + ".txt.bz2")
        with bz2.open(output_path, "wt") as fout:
            for feature in self._parse_geojson(geojson):
                names = self._get_names(feature)
                x, y = self.get_xy(feature["geometry"])
                note = None
                if "code" in self.fieldmap:
                    code = ""
                    for e in self.fieldmap["code"]:
                        v = self._extract_field(feature, e, allow_zero=True)
                        if v is not None:
                            code += v

                    if code != "":
                        note = f"{self.codekey}:{code}"

                self.print_line(
                    fout,
                    99,
                    names,
                    x, y,
                    note
                )

    def _to_point_geojson(self, geojson: Path):
        """
        geojson を解析し、チェック用の Point GeoJSON を標準出力に出力。
        """
        # チェック用の Point GeoJSON を出力
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

            address = " ".join([n[1] for n in names])
            point_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [x, y],
                },
                "properties": {
                    self.codekey: code,
                    "address": address,
                }
            }
            print(
                json.dumps(point_feature, ensure_ascii=False)
            )

    def point_geojson(self, geojsons: Iterator[Path]):
        """
        チェック用ポイント GeoJSON を出力する
        """
        for geojson in geojsons:
            self._to_point_geojson(Path(geojson))

        return

    def convert(self, geojsons: Iterator[Path]):
        """
        データベースを作成する
        """
        temp_dir = None
        if self.text_dir is not None:
            text_dir = Path(self.text_dir)
            if not text_dir.exists():
                text_dir.mkdir()

        else:
            temp_dir = tempfile.TemporaryDirectory()
            text_dir = temp_dir.name

        # GeoJSON ファイルをテキストファイルに変換
        for geojson in geojsons:
            self._to_text(Path(geojson), Path(text_dir))

        manager = DataManager(
            db_dir=self.db_dir,
            text_dir=text_dir,
            targets=(self.pref_code,),
        )

        # メタデータを出力
        datasets = Dataset(db_dir=manager.db_dir)
        datasets.create()
        records = [{
            "id": 99,
            "title": self.title,
            "url": self.url,
        }]
        datasets.append_records(records)

        # テキストファイルからデータベースを作成
        manager.register()

        # 検索インデックスを作成
        manager.create_index()

    def get_xy(self, geometry: dict) -> Tuple[float, float]:
        """
        Geometry を解析して代表点座標を取得する
        """
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

            polygon = max_poly
        else:
            raise RuntimeError(
                "Unsupported geometry type: {}".format(
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
        names: List[Address],
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


if __name__ == "__main__":
    convertor = Convertor()
    convertor.title = "東京歴史地図"
    convertor.url = ""
    convertor.codekey = "tokyo15ku"
    convertor.pref_code = "13"

    convertor.fieldmap["pref"] = ["=東京都"]
    convertor.fieldmap["city"] = ["shi"]
    convertor.fieldmap["ward"] = ["ku"]
    convertor.fieldmap["oaza"] = ["chomei"]
    convertor.fieldmap["aza"] = ["{chome}丁目"]
    convertor.fieldmap["block"] = ["{banchi}番地"]
    convertor.fieldmap["bld"] = ["go"]
    convertor.fieldmap["code"] = ["FID"]

    convertor.point_geojson([
        Path(__file__).absolute().parent.parent / "testdata/15ku_wgs84.geojson"
    ])

    convertor.text_dir = Path.cwd() / "texts/"
    convertor.convert([
        Path(__file__).absolute().parent.parent / "testdata/15ku_wgs84.geojson"
    ])

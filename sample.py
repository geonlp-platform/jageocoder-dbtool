import bz2
import json
import logging
from pathlib import Path
from typing import TextIO, Union, Optional, List, Tuple

from jageocoder.address import AddressLevel
from jageocoder.dataset import Dataset
from jageocoder.node import AddressNode

import shapely

from jageocoder_dbtool.data_manager import DataManager
from jageocoder_dbtool import spatial


Address = Tuple[int, str]
NONAME_COLUMN = f'{AddressNode.NONAME};{AddressLevel.OAZA}'
kansuji = ['〇', '一', '二', '三', '四', '五', '六', '七', '八', '九']
trans_kansuji_zarabic = str.maketrans(
    '一二三四五六七八九', '１２３４５６７８９')

logger = logging.getLogger(__name__)


def main():
    cwd = Path(__file__).parent
    manager = DataManager(
        db_dir=cwd / "db/",
        text_dir=cwd / "texts/",
        targets=('00',),
    )

    # Create point geojson
    render_points(
        cwd / "testdata/15ku_wgs84.geojson",
        manager.text_dir
    )

    # Convert geojson to text
    convert(
        cwd / "testdata/15ku_wgs84.geojson",
        manager.text_dir
    )

    # Write dataset metadata
    datasets = Dataset(db_dir=manager.db_dir)
    datasets.create()
    records = [{
        "id": 99,
        "title": "東京歴史地名",
        "url": "",
    }]
    datasets.append_records(records)

    # Register text files to db
    manager.register()

    # Create index
    manager.create_index()


def get_xy(geometry: dict) -> Tuple[float, float]:
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
            poly_utm = spatial.transform_polygon(poly_wgs84, 4326, 3857, True)
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
    fp: TextIO,
    priority: int,
    names: List[Address],
    x: float,
    y: float,
    note: Optional[str] = None
) -> None:
    """
    Outputs a single line of information.
    If the instance variable priority is set,
    add '!xx' next to the address element names.

    Parameters
    ----------
    names: [[int, str]]
        List of address element level and name
    x: float
        X value (Longitude)
    y: float
        Y value (Latitude)
    note: str, optional
        Notes (used to add codes, identifiers, etc.)
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
            line += NONAME_COLUMN

        line += '{:s};{:d},'.format(name[1], level)
        prev_level = level

    if priority is not None:
        line += '!{:02d},'.format(priority)

    line += "{},{}".format(x or 999, y or 999)
    if note is not None:
        line += ',{}'.format(str(note))

    print(line, file=fp)


def convert(datapath: Path, textdir: Path):
    with open(datapath, "r") as fin:
        feature_collection = json.load(fin)

    if not textdir.exists():
        textdir.mkdir()

    with bz2.open(textdir / "00_sample.txt.bz2", "wt") as fout:

        for feature in feature_collection["features"]:
            props = feature["properties"]
            names = []
            names.append((AddressLevel.PREF, "東京都"))
            names.append((AddressLevel.CITY, props["shi"]))
            names.append((AddressLevel.WARD, props["ku"]))
            names.append((AddressLevel.OAZA, props["chomei"]))
            if props["chome"]:
                names.append((AddressLevel.AZA, "{}丁目".format(props["chome"])))

            if props["banchi"]:
                names.append(
                    (AddressLevel.BLOCK, "{}番地".format(props["banchi"])))

            if props["go"]:
                names.append((AddressLevel.BLD, "{}".format(str(props["go"]))))

            x, y = get_xy(feature["geometry"])
            note = "hcode:{}".format(props["FID"])

            print_line(
                fout,
                99,
                names,
                x, y,
                note
            )


def render_points(datapath: Path, textdir: Path):
    with open(datapath, "r") as fin:
        feature_collection = json.load(fin)

    if not textdir.exists():
        textdir.mkdir()

    basename = datapath.name.replace(".geojson", "_pnt.geojson")
    output_path = str(textdir / basename)

    with open(output_path, "w") as fout:

        for feature in feature_collection["features"]:
            props = feature["properties"]
            x, y = get_xy(feature["geometry"])
            fid = props["FID"]
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [x, y]
                },
                "properties": {
                    "FID": fid
                }
            }
            print(json.dumps(feature), file=fout)


if __name__ == "__main__":
    main()

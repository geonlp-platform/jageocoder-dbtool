"""
Spatial functions
"""
import pyproj
import shapely


"""
Point functions
"""


def transform_point(
    pt: shapely.Point,
    from_epsg: int = 4326,
    to_epsg: int = 3857,
    reverse_xy: bool = False,
) -> shapely.Point:
    """
    Transform the point between CRSs.
    """
    proj = pyproj.Transformer.from_crs(from_epsg, to_epsg)
    if reverse_xy:
        coords = proj.transform(pt.y, pt.x)
    else:
        coords = proj.transform(pt.x, pt.y)

    return shapely.Point(coords)


"""
Polygon functions
"""


def transform_polygon(
    poly: shapely.Polygon,
    from_epsg: int = 4326,
    to_epsg: int = 3857,
    reverse_xy: bool = False,
) -> shapely.Polygon:
    """
    Transform the polygon between CRSs.
    """

    def _tf_ring(proj, ring: shapely.geometry.LinearRing):
        assert (type(ring) == shapely.geometry.LinearRing)
        _ring = []
        for v in ring.coords:
            if reverse_xy:
                _v = proj.transform(v[1], v[0])
            else:
                _v = proj.transform(v[0], v[1])
            _ring.append(_v)

        return _ring

    proj = pyproj.Transformer.from_crs(from_epsg, to_epsg)
    new_exterior = _tf_ring(proj, poly.exterior)
    new_interiors = [_tf_ring(proj, interior)
                     for interior in poly.interiors]
    new_polygon = shapely.Polygon(new_exterior, new_interiors)
    return new_polygon


def get_center(poly: shapely.Polygon) -> shapely.Point:
    """
    Return the center point of the polygon.
    """
    pt = poly.centroid
    if poly.contains(pt):
        # The centroid is in the polygon.
        return pt

    nv = get_nearest_vert(poly, pt)
    buf = nv.buffer(5.0)   # 5.0 unit buffer
    inter = poly.intersection(buf)
    pt = inter.centroid
    return pt


def get_nearest_vert(
    poly: shapely.Polygon,
    pt: shapely.Point
) -> shapely.Point:
    """
    Return the coords of the vert
    which is most closest to the specified point.
    """
    vertices = poly.exterior.coords
    nearest_vertex = min(
        vertices, key=lambda v: pt.distance(shapely.Point(v)))
    distance = pt.distance(shapely.Point(nearest_vertex))

    if len(poly.interiors) > 0:
        for interior in poly.interiors:
            for _nv in interior.coords:
                _dist = pt.distance(shapely.Point(_nv))
                if _dist < distance:
                    distance = _dist
                    nearest_vertex = _nv

    return shapely.Point(nearest_vertex)

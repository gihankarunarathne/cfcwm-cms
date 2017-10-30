import tempfile
import os
from ..resource import ResourceManager
from curw.rainfall.wrf.extraction.spatial_utils import get_voronoi_polygons


def create_kub_timeseries():
    points = {
        'Colombo': [79.8653, 6.898158],
        'IBATTARA3': [79.86, 6.89],
        'Isurupaya': [79.92, 6.89],
        'Borella': [79.86, 6.93, ],
        'Kompannaveediya': [79.85, 6.92],
    }

    shp = ResourceManager.get_resource_path('shp/klb-wgs84/klb-wgs84.shp')
    out = tempfile.mkdtemp(prefix='voronoi_')
    result = get_voronoi_polygons(points, shp, ['OBJECTID', 1], output_shape_file=os.path.join(out, 'out.shp'))
    print(result)
    return []


def create_klb_timseries():
    return []

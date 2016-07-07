from django.contrib.gis.gdal import DataSource
import zipfile
import os
import django
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../geogeeksms/"))
os.environ["DJANGO_SETTINGS_MODULE"] = "geogeeksms.settings"
django.setup()

from geostatements.models import Gazetteer
from django.contrib.gis.utils import LayerMapping

z = zipfile.ZipFile('GazetteerOfAustralia2012Package.zip', 'r')
f = z.extract('Gazetteer2012_GML.zip')
gz = zipfile.ZipFile(f, 'r')
gf = gz.extract('Gazetteer2012GML.gml')
ds = DataSource(gf)
layer = ds[0]

gazetteer_mapping = {
    'gml_id': 'gml_id',
    'objectid': 'OBJECTID',
    'record_id': 'RECORD_ID',
    'name': 'NAME',
    'feat_code': 'FEAT_CODE',
    'cgdn': 'CGDN',
    'authority_id': 'AUTHORITY_ID',
    'concise_gaz': 'CONCISE_GAZ',
    'latitude': 'LATITUDE',
    'lat_degrees': 'lat_degrees',
    'lat_minutes': 'lat_minutes',
    'lat_seconds': 'lat_seconds',
    'longitude': 'LONGITUDE',
    'long_degrees': 'long_degrees',
    'long_minutes': 'long_minutes',
    'long_seconds': 'long_seconds',
    'state_id': 'STATE_ID',
    'status': 'STATUS',
    'map_100k': 'MAP_100K',
    'place_id': 'Place_ID',
    'variant_name': 'VARIANT_NAME',
    'postcode': 'POSTCODE',
    'geom': 'POINT',
}


def run(verbose=True):
    lm = LayerMapping(
        Gazetteer, gf, gazetteer_mapping,
    )
    lm.save(strict=True, verbose=verbose)


if __name__ == '__main__':
    run()

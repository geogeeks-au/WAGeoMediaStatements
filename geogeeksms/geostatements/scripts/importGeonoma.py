from django.contrib.gis.gdal import DataSource
import zipfile
import os
import django
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../geogeeksms/"))
os.environ["DJANGO_SETTINGS_MODULE"] = "geogeeksms.settings"
django.setup()

from geostatements.models import Geonoma
from django.contrib.gis.utils import LayerMapping

gf = 'GeographicNamesGEONOMALGATE_013/GeographicNamesGEONOMALGATE_013_1.shp'
ds = DataSource(gf)
layer = ds[0]

geonoma_mapping = {
'gid' : 'gid',
'feature_nu' : 'feature_nu',
'geographic' : 'geographic',
'feature_cl' : 'feature_cl',
'name_appro' : 'name_appro',
'easting' : 'easting',
'northing' : 'northing',
'zone' : 'zone',
'decimal_la' : 'decimal_la',
'decimal_lo' : 'decimal_lo',
'geom' : 'POINT',
}



def run(verbose=True):
    lm = LayerMapping(
        Geonoma, gf, geonoma_mapping,
    )
    lm.save(strict=True, verbose=verbose)


if __name__ == '__main__':
    run()

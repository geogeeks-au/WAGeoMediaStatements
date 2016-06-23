from __future__ import unicode_literals
from django.contrib.postgres.fields import JSONField

from django.contrib.gis.db import models

parse_lib = [
    ("polyglot", "polylglot"),
]

geo_lib = [
    ("geocoder", "geocoder"),
]

# Create your models here.
class StatementLocation(models.Model):
    location_tag = models.CharField(max_length=200)
    geocoded_data = JSONField()
    geom = models.GeometryField()
    parse_lib = models.CharField(max_length=25, choices=parse_lib)
    geo_lib = models.CharField(max_length=25, choices=geo_lib)


class GeoStatement(models.Model):
    link = models.URLField()
    statement = models.TextField()
    statement_date = models.DateField()
    json = JSONField()
    location = models.ManyToManyField(StatementLocation)

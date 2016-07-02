from __future__ import unicode_literals
from django.contrib.postgres.fields import JSONField

from django.contrib.gis.db import models

parse_lib = [
    ("polyglot", "polylglot"),
]

geo_lib = [
    ("geocoder", "geocoder"),
]


class StatementLocation(models.Model):
    location_tag = models.CharField(max_length=200)
    geocoded_data = JSONField()
    geom = models.GeometryField()
    parse_lib = models.CharField(max_length=25, choices=parse_lib)
    geo_lib = models.CharField(max_length=25, choices=geo_lib)


class LocationSpan(models.Model):
    """
    Model used for keeping track of a statement location's postitions
    in our media statement's. Probably useful for highlighting stuff,
    later.
    """
    location = models.ForeignKey(StatementLocation)
    start_pos = models.IntegerField()
    end_pos = models.IntegerField()


class GeoStatement(models.Model):
    link = models.URLField()
    statement = models.TextField()
    statement_date = models.DateField()
    json = JSONField()
    location = models.ManyToManyField(StatementLocation)
    spans = models.ManyToManyField(LocationSpan)



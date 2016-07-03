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

class Gazetteer(models.Model):
    gml_id = models.CharField(max_length=15)
    objectid = models.IntegerField()
    record_id = models.CharField(max_length=11)
    name = models.CharField(max_length=99)
    feat_code = models.CharField(max_length=4)
    cgdn = models.CharField(max_length=1)
    authority_id = models.CharField(max_length=3)
    concise_gaz = models.CharField(max_length=1)
    latitude = models.FloatField()
    lat_degrees = models.IntegerField()
    lat_minutes = models.IntegerField()
    lat_seconds = models.IntegerField()
    longitude = models.FloatField()
    long_degrees = models.IntegerField()
    long_minutes = models.IntegerField()
    long_seconds = models.IntegerField()
    state_id = models.CharField(max_length=3)
    status = models.CharField(max_length=1)
    map_100k = models.IntegerField()
    place_id = models.IntegerField()
    variant_name = models.CharField(max_length=138)
    postcode = models.IntegerField()
    geom = models.PointField(srid=4236)



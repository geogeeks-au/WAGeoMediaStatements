from __future__ import unicode_literals
from django.contrib.postgres.fields import JSONField
from django.utils.encoding import smart_text
from django.contrib.gis.db import models

parse_lib = [
    ("polyglot", "polylglot"),
    ("geograpy", "geograpy"),
    ("combined", "combined"),
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
    bad_loc_flag = models.BooleanField(default=False)

    def __str__(self):
        return smart_text(self.location_tag)


class LocationSpan(models.Model):
    """
    Model used for keeping track of a statement location's postitions
    in our media statement's. Probably useful for highlighting stuff,
    later.
    """
    location = models.ForeignKey(StatementLocation)
    start_pos = models.IntegerField()
    end_pos = models.IntegerField()

    def __str__(self):
        return smart_text(self.location.location_tag)

class GeoStatement(models.Model):
    link = models.URLField()
    statement = models.TextField()
    statement_date = models.DateField()
    json = JSONField()
    location = models.ManyToManyField(StatementLocation)
    spans = models.ManyToManyField(LocationSpan)
    minister = models.ManyToManyField('Minister')

    def __str__(self):
        return smart_text(self.link)

class Gazetteer(models.Model):
    gml_id = models.CharField(max_length=50)
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

    def __str__(self):
        return smart_text("%s, %s" % (self.name, self.state_id))


class Minister(models.Model):
    first_names = models.CharField(max_length=100)
    house = models.CharField(max_length=10)
    electorate = models.CharField(max_length=60)
    last_name = models.CharField(max_length=50)
    page = models.URLField()
    email = models.EmailField(blank=True)
    party = models.CharField(max_length=15)
    office_address = models.CharField(max_length=250, blank=True)
    position = models.CharField(max_length=150, blank=True)
    current_member = models.BooleanField(default=False)

    def __str__(self):
        return smart_text("%s %s" % (self.first_names, self.last_name))

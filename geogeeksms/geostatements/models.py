from __future__ import unicode_literals
from django.contrib.postgres.fields import JSONField

from django.contrib.gis.db import models


# Create your models here.
class StatementLocation(models.Model):
    location_tag = models.CharField(max_length=200)
    geocoded_data = JSONField()
    geom = models.GeometryField()


class GeoStatement(models.Model):
    link = models.URLField()
    statement = models.TextField()
    statement_date = models.DateField()
    json = JSONField()
    location = models.ManyToManyField(StatementLocation)

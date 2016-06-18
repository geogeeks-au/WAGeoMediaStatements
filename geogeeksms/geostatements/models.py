from __future__ import unicode_literals

from django.db import models

# Create your models here.
class StatementLocation(models.Model):
	location_tag = models.CharField(max_length=200)
	geocoded_data = models.JSONField()
	geom = models.GeometryField()

class GeoStatement(models.Model):
	link = models.UrlField()
	statement = models.TextField()
	json = models.JSONField()
	location = models.ManyToManyField(StatementLocation)

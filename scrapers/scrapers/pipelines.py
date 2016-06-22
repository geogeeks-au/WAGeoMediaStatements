# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import json
from django.contrib.gis.geos import GEOSGeometry
from polyglot.text import Text
import geocoder
import os
import sys
import django
import logging

# Can't remember if I need to use __file__ here
sys.path.append("../../../geogeeksms/")
os.environ["DJANGO_SETTINGS_MODULE"] = "geogeeksms.settings"
django.setup()

from geogeeksms.geostatements.models import *


class MediaStatementsDB(object):

    collection_name = 'mediastatements'
    geocoded = {}

    def __init__(self):
        self.ids_seen = set()

    def geocode_locations(self, locations):
        """
        Attempt to geocode each location in locations using Google
        :param locations:
        :return: A list of tuples of information we were able to geocode
        """
        geolocs = []
        for loc in locations:
            # Check cache
            if loc in self.geocoded:
                geolocs.append(self.geocoded[loc])
                continue
            # try looking up using google
            if loc not in ["WA", "Western Australia", "Australia"]:
                g = geocoder.google(loc, components="country:AU|administrative_area:WA")
                # Todo: Probably create this as a named tuple or something
                geoloc = g.geojson
                geolocs.append(geoloc)
                self.geocoded[loc] = geoloc
        return geolocs

    def process_item(self, item, spider):
        """
        We need to use self.db to write stuff into our database
        We also need to set up our data structures.
        #if item['id'] in self.ids_seen:
        #    raise DropItem("Duplicate item found: %s" % item)
        :param item:
        :param spider:
        :return:
        """
        db_locs = []
        logging.info("Processing statement {}".format(item['title']))
        text = Text(item['statement'])
        # For all I-LOC make an attempt to geocode but restrict to WA
        locations = set([" ".join(e) for e in text.entities if e.tag == u'I-LOC'])
        # It's never to soon to optimize.
        # To save repeats lets store these in a dictionary
        item['locations'] = self.geocode_locations(locations)
        for location in item['locations']:
            geom = GEOSGeometry(location)
            gdata = location
            location = location['properties']['location']
            sl, created = StatementLocation.objects.get_or_create(location, gdata, geom)
            db_locs.append(sl)
        link = item['link']
        statement = item['statement']
        statement_date = item['date']
        data = {'minister': item['minister'], 'portfolio': item['portfolio']}
        gs = GeoStatement.objects.get_or_create(link, statement, statement_date, data)
        gs.add(db_locs)

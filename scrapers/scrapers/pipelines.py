# -*- coding: utf-8 -*-

# Define your item pipelines here
# Consider moving Geocoding stuff out of pipeline for testing
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
from django.utils.dateparse import parse_date

# Can't remember if I need to use __file__ here
sys.path.append(os.path.join(os.path.dirname(__file__), "../../geogeeksms/"))
os.environ["DJANGO_SETTINGS_MODULE"] = "geogeeksms.settings"
django.setup()

from geostatements.models import *


class MediaStatementsDB(object):
    collection_name = 'mediastatements'
    geocoded = {}

    def __init__(self):
        self.ids_seen = set()

    def find_locations_polyglot(self, statement):
        """
        Uses PolyGLot NLP to find Named entities and passes back a set of locations found
        :param statement:
        :return:
        """
        # Probably should be using e.start and e.end for entities so we know where they are in statement
        text = Text(statement)
        # For all I-LOC make an attempt to geocode but restrict to WA
        return set([" ".join(e) for e in text.entities if e.tag == u'I-LOC'])

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
                geolocs.append(g)
                self.geocoded[loc] = g
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
        # I think we can get positions of location in Statement which might be good to save

        # It's never to soon to optimize.
        # To save repeats lets store these in a dictionary
        item['locations'] = self.geocode_locations(self.find_locations_polyglot(item['statement']))
        for location in item['locations']:
            geom = GEOSGeometry(location.wkt)
            gdata = location.json
            location_tag = location['properties']['location']
            sl, created = StatementLocation.objects.get_or_create(
                location_tag=location_tag,
                geocoded_data=gdata,
                geom=geom,
                parse_lib="polyglot",
                geo_lib="geocoder"

            )
            db_locs.append(sl)
        link = item['link']
        statement = item['statement']
        statement_date = item['date']
        data = {'minister': item['minister'], 'portfolio': item['portfolio']}
        gs = GeoStatement.objects.get_or_create(
            link=link,
            statement=statement,
            statement_date=parse_date(statement_date),
            json=data)
        gs.location.add(db_locs)

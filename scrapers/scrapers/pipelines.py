# -*- coding: utf-8 -*-

# Define your item pipelines here
# Consider moving Geocoding stuff out of pipeline for testing
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
# TODO: Use SyntaxNet and tensorflow to pull out locations
from scrapy.exceptions import DropItem
import json
from django.contrib.gis.geos import GEOSGeometry
from polyglot.text import Text
from geograpy import extraction
import geocoder
import os
import sys
import django
import logging
import datetime

# Can't remember if I need to use __file__ here
sys.path.append(os.path.join(os.path.dirname(__file__), "../../geogeeksms/"))
os.environ["DJANGO_SETTINGS_MODULE"] = "geogeeksms.settings"
django.setup()

from geostatements.models import *


class MinistersDB(object):
    collection_name = 'ministers'

    def process_item(self, item, spider):
        """
        Process ministers
        :param item:
        :param spider:
        :return:
        """
        if spider.name != 'wamins':
            return item
        currentMember = True if item['email'] else False
        mins, created = Minister.objects.get_or_create(first_names=item['first_name'],
                                                       email=item['email'],
                                                       last_name=item['last_name'],
                                                       house=item['house'],
                                                       electorate=item['electorate'],
                                                       party=item['party'],
                                                       page=item['page'],
                                                       office_address=item['office_address'],
                                                       position=item['position'],
                                                       current_member=currentMember)


class MediaStatementsDB(object):
    collection_name = 'mediastatements'
    geocoded = {}

    def __init__(self):
        self.ids_seen = set()

    def find_locations_polyglot(self, statement):
        """
        Uses PolyGLot NLP to find Named entities and passes back a set of locations found
        TODO: I think we need to expand this to check if extra words possibly.
        Return a better match.
        i.e Leach -> Highway, Bull-> Creek Railway Station,
        Main -> Roads Western Australia, Kwinanna Freeway.
        Try to check Gazeteer and database first, use googlemaps as fallback.
        Perform something similar as to geograpy LOC = Likely, ORG = Possible, Person=Unlikley
        :param statement:
        :return:
        """
        # Probably should be using e.start and e.end for entities so we know where they are in statement
        text = Text(statement)
        # For all I-LOC make an attempt to geocode but restrict to WA
        # We should attempt to record the span of each tag
        locations = []
        spans = []
        for e in text.entities:
            if e.tag == u'I-LOC' or e.tag == u'I-ORG':
                locations.append(" ".join(e))
                spans.append((e.start, e.end))
        return locations, spans

    def find_geograpy_locations(self, statement):
        """
        I actually extended geograpy to include more potential locations.
        I think we get a few more false postivies, so we need to do some filtering.
        TODO: Change the extraction script to include allow for supplying tags.
        Person and Organisation tags should be flagged as possible locations.`x
        :param statement:
        :return:
        """
        e = extraction.Extractor(text=statement)
        e.find_entities()
        return e.places

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
        Using Django to write our Statement, Locations etc
        #if item['id'] in self.ids_seen:
        #    raise DropItem("Duplicate item found: %s" % item)
        :param item:
        :param spider:
        :return:
        """
        if spider.name != "wams":
            return item
        db_locs = []
        logging.info("Processing statement {}".format(item['title']))
        # I think we can get positions of location in Statement which might be good to save

        # It's never to soon to optimize.
        # To save repeats lets store these in a dictionary
        # Find ids if not create
        polyglot_locations, location_spans = self.find_locations_polyglot(item['statement'])
        for pl_loc in polyglot_locations:
            qsl = StatementLocation.objects.filter(location_tag=pl_loc)
            # Geocoded location exists in database
            if qsl:
                sl = qsl[0]
            else:
                geocoded_loc = self.geocode_locations([pl_loc])
                geom = GEOSGeometry(location.wkt)
                gdata = location.json

                location_tag = location.json['location']
                try:
                    sl, created = StatementLocation.objects.get_or_create(
                        location_tag=location_tag,
                        geocoded_data=gdata,
                        geom=geom,
                        parse_lib="polyglot",
                        geo_lib="geocoder"
                    )
                except:
                    logging.error("Couldn't write to db")
            db_locs.append(sl)
        link = item['link']
        statement = item['statement']
        statement_date = item['date']
        data = {'minister': item['minister'], 'portfolio': item['portfolio']}
        try:
            gs, created = GeoStatement.objects.get_or_create(
                link=link,
                statement=statement,
                statement_date=datetime.datetime.strptime(statement_date, "%d/%m/%Y"),
                json=data)
            gs.location.add(db_locs)
        except:
            logging.error("Failed to write geostatement %s" % item['title'])

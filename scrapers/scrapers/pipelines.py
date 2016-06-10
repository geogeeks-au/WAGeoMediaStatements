# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import psycopg2
import json


class JsonMediaStatementsPipe(object):
    """
    This will be our gecoded stuff
    """

    def __init__(self):
        self.file = open('mstablegeo.json', 'wb')
        self.file.write("[")

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + ",\n"
        self.file.write(line)
        return item

    def close_spider(self):
        self.file.write("]")
        self.file.close()

class MediaStatementsDB(object):

    collection_name = 'mediastatements'

    def __init__(self, postgres_uri, postgres_db, postges_user, postgres_pass ):
        self.ids_seen = set()

    def process_item(self, item, spider):
        """
        We need to use self.db to write stuff into our database
        We also need to set up our data structures.
        :param item:
        :param spider:
        :return:
        """
        if item['id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['id'])
            return item


    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            postgres_host=crawler.settings.get('POSTGRES_URI'),
            postgres_db=crawler.settings.get('POSTGRES_DB'),
            postges_user=crawler.settings.get('POSTGRES_USER'),
            postges_pass=crawler.settings.get('POSTGRES_PASS'),
            postges_port=crawler.settings.get('POSTGRES_PORT'),
        )


    def open_spider(self, spider):
        self.client= psycopg2.connect(database=self.postgres_db,
                                      user=self.postgres_user,
                                      host=self.postgres_host,
                                      port=self.postgres_port,
                                      password=self.postgres_pass)
        self.db = self.client.cursor()


    def close_spider(self, spider):
        self.db.close()
        self.client.close()

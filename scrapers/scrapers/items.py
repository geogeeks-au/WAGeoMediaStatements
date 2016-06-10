# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class MediaStatementRow(Item):
    # define the fields for your item here like:
    date = Field()
    minister = Field()
    portfolio = Field()
    title = Field()
    link = Field()

class MediaStatement(Item):
    title = Field()
    statement = Field()
    locations = Field()

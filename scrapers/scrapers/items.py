# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class MediaStatement(Item):
    date = Field()
    minister = Field()
    portfolio = Field()
    title = Field()
    link = Field()
    statement = Field()
    locations = Field()

class Minister(Item):
    first_name = Field()
    email = Field()
    last_name = Field()
    house = Field()
    electorate = Field()
    party = Field()
    page = Field()
    office_address = Field()
    position = Field()

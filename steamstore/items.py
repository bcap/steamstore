# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ListingItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    type = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    reviews_url = scrapy.Field()
    reviews = scrapy.Field()
    tags = scrapy.Field()
    developer = scrapy.Field()
    publisher = scrapy.Field()

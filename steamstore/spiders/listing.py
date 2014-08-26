# -*- coding: utf-8 -*-
import scrapy
import re

from functools import partial
from scrapy import log
from steamstore.items import ListingItem


class ListingSpider(scrapy.Spider):
    name = "listing"
    allowed_domains = ["store.steampowered.com"]
    start_urls = (
        'http://store.steampowered.com/search/?sort_by=Name&sort_order=ASC',
    )

    url_pattern = re.compile(r'/?\?.*$')
    type_icon_pattern = re.compile(r'^.*/ico_type_(\w+).gif')

    get_first = lambda self, l: l[0] if l else None


    def parse(self, response):
        "Generate data and requests walking through each item in each search page"

        for item in self._parse_items(response):
            yield item

        for page_request in self._parse_search_pages(response):
            yield page_request


    def _parse_items(self, response):
        "Generate item data and requests for each item page"

        for sel in response.xpath('//div[@id="search_result_container"]/div[6]/a'):
            item = ListingItem()
            item['name'] = self.get_first(sel.xpath('div[@class="col search_name ellipsis"]/h4/text()').extract())
            item['type'] = self.type_icon_pattern.sub(r'\1', self.get_first(sel.xpath('div[@class="col search_type"]/img/@src').extract()))
            item['price'] = self.get_first(sel.xpath('div[@class="col search_price"]/text()').extract())
            item['url'] = self.url_pattern.sub('', self.get_first(sel.xpath('@href').extract()))
            yield item

            parse_item_function = ListingSpider.__dict__.get('parse_{}'.format(item['type']))
            if parse_item_function:
                yield scrapy.Request(item['url'], callback=partial(parse_item_function, self))
            else:
                self.log('No method for handling type "{}", skipping'.format(item['type']), level=log.WARNING)


    def _parse_search_pages(self, response):
        "Generate requests for each search page"

        for sel in response.xpath('//*[@id="search_result_container"]/div[4]/div[@class="search_pagination_right"]/a/@href'):
            yield scrapy.Request(sel.extract())


    #def parse_vid(self, response):
    #    print response


    #def parse_app(self, response):
    #    print response
# -*- coding: utf-8 -*-
import scrapy
import re
from steamstore.items import ListingItem


class ListingSpider(scrapy.Spider):
    name = "listing"
    allowed_domains = ["store.steampowered.com"]
    start_urls = (
        'http://store.steampowered.com/search/?sort_by=Name&sort_order=ASC',
    )

    def parse(self, response):

        get_first = lambda l: l[0] if l else None

        url_pattern = re.compile(r'/?\?.*$')

        for sel in response.xpath('//div[@id="search_result_container"]/div[6]/a'):
            item = ListingItem()
            item['name'] = get_first(sel.xpath('div[@class="col search_name ellipsis"]/h4/text()').extract())
            item['price'] = get_first(sel.xpath('div[@class="col search_price"]/text()').extract())
            item['url'] = url_pattern.sub('', get_first(sel.xpath('@href').extract()))
            yield item

            #yield scrapy.Request(item['url'], callback=self.parse_item_page)

        for sel in response.xpath('//*[@id="search_result_container"]/div[4]/div[@class="search_pagination_right"]/a/@href'):
            yield scrapy.Request(sel.extract())


    def parse_item_page(self, response):

        print response

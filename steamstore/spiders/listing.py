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

    url_pattern = re.compile(r'/?\?.*$')
    type_icon_pattern = re.compile(r'^.*/ico_type_(\w+).gif')

    get_first = lambda self, l: l[0] if l else None


    def parse(self, response):

        for sel in response.xpath('//div[@id="search_result_container"]/div[6]/a'):
            item = ListingItem()
            item['name'] = self.get_first(sel.xpath('div[@class="col search_name ellipsis"]/h4/text()').extract())
            item['type'] = self.type_icon_pattern.sub(r'\1', self.get_first(sel.xpath('div[@class="col search_type"]/img/@src').extract()))
            item['price'] = self.get_first(sel.xpath('div[@class="col search_price"]/text()').extract())
            item['url'] = self.url_pattern.sub('', self.get_first(sel.xpath('@href').extract()))
            yield item

            #yield scrapy.Request(item['url'], callback=self.parse_item_page)

        for sel in response.xpath('//*[@id="search_result_container"]/div[4]/div[@class="search_pagination_right"]/a/@href'):
            yield scrapy.Request(sel.extract())


    def parse_item_page(self, response):

        print response

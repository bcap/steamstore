# -*- coding: utf-8 -*-
import scrapy
import re
from steamstore.items import Game


class ListingSpider(scrapy.Spider):
    name = "listing"
    allowed_domains = ["store.steampowered.com"]
    start_urls = (
        'http://store.steampowered.com/search/?sort_by=Released&sort_order=DESC',
    )

    def parse(self, response):

        get_first = lambda l: l[0] if l else None

        url_pattern = re.compile(r'/?\?.*$')

        for sel in response.xpath('//div[@id="search_result_container"]/div[6]/a'):
            game = Game()
            game['name'] = get_first(sel.xpath('div[@class="col search_name ellipsis"]/h4/text()').extract())
            game['price'] = get_first(sel.xpath('div[@class="col search_price"]/text()').extract())
            game['url'] = url_pattern.sub('', get_first(sel.xpath('@href').extract()))
            yield game

            #yield scrapy.Request(game['url'], callback=self.parse_game_page)

        for sel in response.xpath('//*[@id="search_result_container"]/div[4]/div[@class="search_pagination_right"]/a/@href'):
            yield scrapy.Request(sel.extract())


    def parse_game_page(self, response):

        print response

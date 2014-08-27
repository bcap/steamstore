# -*- coding: utf-8 -*-
import scrapy
import re

from functools import partial
from scrapy import log
from steamstore.items import ListingItem


class ListingSpider(scrapy.Spider):
    name = "listing"
    allowed_domains = ["store.steampowered.com", "steamcommunity.com"]
    start_urls = (
        'http://store.steampowered.com/search/?sort_by=Name&sort_order=ASC',
    )

    url_pattern = re.compile(r'/?\?.*$')
    type_icon_pattern = re.compile(r'^.*/ico_type_(\w+).gif')
    acceptance_pattern = re.compile(r'(\d+) of (\d+) people')

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
            item['id'] = item['url'][item['url'].rindex('/') + 1 :]

            parse_item_function = ListingSpider.__dict__.get('parse_{}'.format(item['type']))
            if parse_item_function:
                yield scrapy.Request(item['url'], callback=partial(parse_item_function, self), meta={'item': item})
            else:
                self.log('No method for handling type "{}", returning basic item info'.format(item['type']), level=log.WARNING)
                yield item


    def _parse_search_pages(self, response):
        "Generate requests for each search page"

        for sel in response.xpath('//*[@id="search_result_container"]/div[4]/div[@class="search_pagination_right"]/a/@href'):
            yield scrapy.Request(sel.extract())


    def parse_app(self, response):
        app = response.meta['item']
        reviews_url = self.get_first(response.xpath('//*[@id="ViewAllReviewsall"]/a/@href').extract())
        if reviews_url:
            app['reviews_url'] = self.url_pattern.sub('', reviews_url)
            yield scrapy.Request(self._review_page_url(app, 1, 0), callback=self.parse_reviews, meta={'app': app})
        else:
            yield app


    def _review_page_url(self, app, page, offset):
        template = 'http://steamcommunity.com/app/{}/homecontent/?userreviewsoffset={}&p={}&appHubSubSection=10&browsefilter=toprated'
        return template.format(app['id'], offset, page)


    def parse_reviews(self, response):
        app = response.meta['app']
        app['reviews'] = list()

        for sel in response.xpath('//div[@class="apphub_UserReviewCardContent"]'):

            content = self.get_first(sel.xpath('div[@class="apphub_CardTextContent"]/text()').extract())
            recommendation = self.get_first(sel.xpath('//div[@class="reviewInfo"]/div[@class="title"]/text()').extract())
            acceptance = self.get_first(sel.xpath('div[@class="found_helpful"]/text()').extract())

            review = dict()

            review['content'] = content.strip() if content else None
            review['recommendation'] = recommendation.strip() if recommendation else None
            review['acceptance'] = acceptance.strip() if acceptance else None

            match = self.acceptance_pattern.match(review['acceptance'])
            if match:
                review['acceptance_score'] = (int(match.group(1)), int(match.group(2)))
            elif review['acceptance'].index('1 person') > 0:
                review['acceptance_score'] = (1, 1)
            else:
                review['acceptance_score'] = (0, 0)

            app['reviews'].append(review)

        yield app
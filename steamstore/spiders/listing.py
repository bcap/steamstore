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
            item['name'] = self._extract(sel, 'div[@class="col search_name ellipsis"]/h4/text()')
            item['type'] = self.type_icon_pattern.sub(r'\1', self._extract(sel, 'div[@class="col search_type"]/img/@src'))
            item['price'] = self._extract(sel, 'div[@class="col search_price"]/text()')
            item['url'] = self.url_pattern.sub('', self._extract(sel, '@href'))
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

        app['developer'] = self._extract(response, '//div[@class="details_block"]/b[text()="Developer:"]/following-sibling::a[1]/text()')
        app['publisher'] = self._extract(response, '//div[@class="details_block"]/b[text()="Publisher:"]/following-sibling::a[1]/text()')
        app['tags'] = map(unicode.strip, response.xpath('//div[@id="game_highlights"]//div[@class="glance_tags popular_tags"]/a/text()').extract())

        reviews_url = self._extract(response, '//*[@id="ViewAllReviewsall"]/a/@href')
        if reviews_url:
            app['reviews_url'] = self.url_pattern.sub('', reviews_url)
            yield self._review_page_request(app, 1, 0)
        else:
            yield app


    def parse_reviews(self, response):
        app = response.meta['app']
        page = response.meta['page']
        offset = response.meta['offset']

        if not 'reviews' in app:
            app['reviews'] = list()

        processed_reviews = 0

        for sel in response.xpath('//div[@class="apphub_UserReviewCardContent"]'):
            content = self._extract(sel, 'div[@class="apphub_CardTextContent"]/text()')
            recommendation = self._extract(sel, '//div[@class="reviewInfo"]/div[@class="title"]/text()')
            acceptance = self._extract(sel, 'div[@class="found_helpful"]/text()')

            review = dict()
            review['content'] = content.strip() if content else None
            review['recommendation'] = recommendation.strip() if recommendation else None
            review['acceptance'] = acceptance.strip() if acceptance else None
            review['acceptance_score'] = self._extract_acceptance_score(review['acceptance'])
            app['reviews'].append(review)

            processed_reviews = processed_reviews + 1

        if processed_reviews > 0:
            yield self._review_page_request(app, page + 1, offset + processed_reviews)

        # no more reviews found, now we are done
        else:
            yield app


    def _extract_acceptance_score(self, acceptance_string):
        match = self.acceptance_pattern.match(acceptance_string)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        elif acceptance_string.startswith('1 person'):
            return (1, 1)
        else:
            return (0, 0)


    def _review_page_request(self, app, page, offset):
        template = 'http://steamcommunity.com/app/{}/homecontent/?userreviewsoffset={}&p={}&appHubSubSection=10&browsefilter=toprated'
        url = template.format(app['id'], offset, page)
        return scrapy.Request(url, callback=self.parse_reviews, meta={'app': app, 'page': page, 'offset': offset})


    def _extract(self, selector, xpath):
        data = selector.xpath(xpath).extract()
        return data[0].strip() if data else None

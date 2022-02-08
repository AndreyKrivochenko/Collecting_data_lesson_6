import uuid

import bson
import scrapy
from scrapy.http import HtmlResponse

from bookparser.items import BookparserItem


class Book24ruSpider(scrapy.Spider):
    name = 'book24ru'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=python',
                  'https://book24.ru/search/?q=java']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.python_i = 1
        self.java_i = 1

    def parse(self, response: HtmlResponse):
        if response.status == 200:
            next_page = ''
            if response.url.endswith('python'):
                self.python_i += 1
                next_page = f'https://book24.ru/search/page-{self.python_i}/?q=python'
            elif response.url.endswith('java'):
                self.java_i += 1
                next_page = f'https://book24.ru/search/page-{self.java_i}/?q=java'
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath('//div[contains(@class, "catalog__product-list-holder")]//a[contains(@class, "product-card__name")]//@href').getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        url = response.url
        title = response.xpath('//h1//text()').get()
        author = response.xpath('//span[@class="product-characteristic__label"][contains(text(), "Автор")]/..//following-sibling::div//text()').get()
        main_price = response.xpath('//span[contains(@class, "product-sidebar-price__price-old")]//text()').get()
        if main_price:
            discount_price = response.xpath('//meta[@itemprop="price"]//@content').get()
        else:
            discount_price = 0
            main_price = response.xpath('//meta[@itemprop="price"]//@content').get()
        rating = response.xpath('//div[@itemprop="aggregateRating"]//span[@class="rating-widget__main-text"]//text()').get()
        _id = bson.Binary.from_uuid(uuid.uuid3(uuid.NAMESPACE_URL, url))
        yield BookparserItem(_id=_id, url=url, title=title, author=author, main_price=main_price,
                             discount_price=discount_price, rating=rating)

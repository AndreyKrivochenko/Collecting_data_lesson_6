import uuid

import bson
import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/python/?stype=0',
                  'https://www.labirint.ru/search/java/?stype=0']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@class='pagination-next__text']//@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath('//a[@class="product-title-link"]//@href').getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        url = response.url
        title = response.xpath('//h1//text()').get()
        author = response.xpath('//a[@data-event-label="author"]//text()').get()
        main_price = response.xpath('//span[@class="buying-priceold-val-number"]//text()').get()
        discount_price = response.xpath('//span[@class="buying-pricenew-val-number"]//text()').get()
        rating = response.xpath('//div[@id="rate"]//text()').get()
        _id = bson.Binary.from_uuid(uuid.uuid4())
        yield BookparserItem(_id=_id, url=url, title=title, author=author, main_price=main_price,
                             discount_price=discount_price, rating=rating)

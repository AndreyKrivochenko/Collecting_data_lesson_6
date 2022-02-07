import scrapy


class Book24ruSpider(scrapy.Spider):
    name = 'book24ru'
    allowed_domains = ['book24.ru']
    start_urls = ['http://book24.ru/']

    def parse(self, response):
        pass

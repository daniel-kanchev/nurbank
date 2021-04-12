import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from nurbank.items import Article


class nurbankSpider(scrapy.Spider):
    name = 'nurbank'
    start_urls = ['https://www.nurbank.kz/en/about/news']

    def parse(self, response):
        links = response.xpath('//div[@class="title"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[text()="Следующая →"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h3/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//h6/text()').get()
        if date:
            date = " ".join(date.split())

        content = response.xpath('//div[@class="page"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()

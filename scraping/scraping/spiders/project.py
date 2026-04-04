import scrapy


class ProjectSpider(scrapy.Spider):
    name = "project"
    allowed_domains = ["devpost.com"]
    start_urls = ["https://devpost.com"]

    def parse(self, response):
        pass

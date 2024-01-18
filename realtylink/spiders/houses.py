import scrapy
from scrapy.http import Response


class HousesSpider(scrapy.Spider):
    name = "houses"
    allowed_domains = ["realtylink.org"]
    start_urls = ["https://realtylink.org/en/properties~for-rent"]

    def parse(self, response: Response, **kwargs):
        pass

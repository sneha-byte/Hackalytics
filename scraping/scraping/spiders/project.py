from typing import AsyncIterator, Any
import pandas as pd
import scrapy
from scrapy.http import Response
from scrapy.spiders import CrawlSpider

class ProjectSpider(CrawlSpider):
    name="ProjectSpider"
    allowed_domains = ["devpost.com"]

    def __init__(self, dataset=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.df = pd.read_csv(dataset)

    async def start(self) -> AsyncIterator[Any]:
        for _, row in self.df.iterrows():
            yield scrapy.Request(
                url=row["url"] + "project-gallery",
                callback=self.parse_gallery,
                meta={
                    "hackathon_id": row["id"]
                }
            )

    async def parse_gallery(self, response: Response):
        meta = {
            "hackathon_id": response.meta.get("hackathon_id")
        }
        # Parse the gallery page
        for entry_href in response.css('.gallery-item a::attr(href)').getall():
            yield scrapy.Request(
                url=entry_href,
                callback=self.parse_project_page,
                meta=meta,
                priority=1
            )

        # Parse the next page if available
        # Disabled to reduce data size
        # next_page = response.css('ul.pagination a[rel="next"]::attr(href)').get()
        #
        # if next_page:
        #     yield response.follow(
        #         next_page,
        #         callback=self.parse_gallery,
        #         meta=meta,
        #         priority=1
        #     )

    async def parse_project_page(self, response: Response):
        sel = response.css("#gallery+div").xpath(".//text()[not(ancestor::code or ancestor::pre)]")

        return {
            "title": response.css("#app-title::text").get(),
            "description": response.css("#app-title+p::text").get(),
            "built-with": response.css(".cp-tag.recognized-tag a::text").getall(),
            "is-winner": bool(response.css(".winner").get()),
            "full-description": " ".join(sel.getall()),
            "hackathon_id": response.meta.get("hackathon_id")
        }
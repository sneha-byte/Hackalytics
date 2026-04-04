from typing import AsyncIterator, Any
import pandas as pd
import scrapy
from scrapy.spiders import CrawlSpider
from urllib.parse import urlparse, parse_qs

class HackathonLocationSpider(CrawlSpider):
    name="HackathonLocationSpider"
    allowed_domains = ["devpost.com"]

    def __init__(self, dataset=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.df = pd.read_csv(dataset)

    async def start(self) -> AsyncIterator[Any]:
        for _, row in self.df.iterrows():
            yield scrapy.Request(
                url=row["url"],
                callback=self.parse_home_page,
                meta={
                    "hackathon_id": row["id"]
                }
            )

    async def parse_home_page(self, response: scrapy.http.Response):
        hackathon_id = response.meta.get("hackathon_id")
        if outer := response.css("i.fas.fa-map-marker-alt+div.info"):
            if google_map_url := outer.css("a::attr(href)").get():
                parsed_url = urlparse(google_map_url)
                query_params = parse_qs(parsed_url.query)
                geo_location = query_params["q"][0].strip()
            else:
                geo_location = outer.css("::text").get().strip()
        elif response.css("i.fas.fa-globe").get():
            geo_location = "Online"
        else:
            raise ValueError(f"Could not parse geo location from {hackathon_id}")

        return {
            "id": hackathon_id,
            "geo_location": geo_location
        }
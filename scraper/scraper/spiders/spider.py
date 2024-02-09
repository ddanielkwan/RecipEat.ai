from pathlib import Path
from typing import Any, Iterable
import logging
import scrapy
from scrapy.http import Request, Response



class RecipeSpider(scrapy.Spider):
    #https://www.allrecipes.com/recipes-a-z-6735880
    name = "recipe_scraper"

    def start_requests(self) -> Iterable[Request]:
        urls = ["https://www.allrecipes.com/recipes-a-z-6735880"]

        for url in urls:
            yield scrapy.Request(url, callback=self.parse)

  
    

    def parse(self, response: Response, **kwargs: Any) -> Any:
        
        page = response.url.split("/")[-2]
        filename = f"{page}.html"
        Path(filename).write_bytes(response.body)
        



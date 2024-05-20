from pathlib import Path
from typing import Any, Iterable
import logging
import scrapy
from scrapy.http import Request, Response
import re
import os
os.makedirs('output', exist_ok=True)
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

class RecipeSpider(scrapy.Spider):
    #https://www.allrecipes.com/recipes-a-z-6735880
    name = "recipe_scraper"

    def start_requests(self) -> Iterable[Request]:
        urls = ["https://www.allrecipes.com/recipes-a-z-6735880"]

        for url in urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        '''parser for main page to get links and text'''
        output_dir = 'output'
        page = response.url.split("/")[-2]
        #in XPath dot. refers to the current context node so relative path
        #/ means onyl signel child // means all descendants with div no matter nested
        list_of_topics = response.xpath('//div[@id="mntl-alphabetical-list_1-0"]/div')#.getall()
        for topic in list_of_topics:
            # div with the class mntl-alphabetical-list__group
            # group_div = topic.xpath('.//div[contains(@class, "mntl-alphabetical-list__group")]')
            
           # ul with the class loc mntl-link-list
            link_list = topic.xpath('.//ul[contains(@class, "loc mntl-link-list")]')

            list_items = link_list.xpath('.//li')
            for li in list_items:
                text = li.xpath('.//text()').getall()[0]  
                link = li.xpath('.//a/@href').get() 
             
                print("------------")
                print(text, link) #-> [' Whole30\n'] https://www.allrecipes.com/recipes/22590/healthy-recipes/whole30/
                filename= f"output/{text.strip()}.txt"
                if link:
                    yield scrapy.Request(url=link, callback=self.parse_recipe_page, meta={'filename': filename})
                # with open(filename, "a+", encoding='utf-8') as f:
                #     pass
    
    def parse_recipe_page(self, response: Response, **kwargs: Any) -> Any:

        file_path = response.meta['filename']
        



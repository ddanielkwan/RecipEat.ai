'''scrapy crawl recipe_scraper'''
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
                try:
                    parent = "C://Users//Daniel Kwan//Desktop//RecipEat.ai-backend//scraper//output"
                    filename= f"{text.strip()}"
                    path = os.path.join(parent, filename) 
                    os.makedirs(path) 
                except OSError as e:
                    print(e)
                if link:
                    yield scrapy.Request(url=link, callback=self.parse_recipe_page, meta={'filename': filename})
                # with open(filename, "a+", encoding='utf-8') as f:
                #     pass
    
    def parse_recipe_page(self, response: Response, **kwargs: Any) -> Any:
        #need this file name to write to file 
        filename = response.meta['filename']

        individual_recipes = response.xpath('//a[contains(@id, "mntl-card-list-items_") and not(ancestor::section[@id="mntl-sc-block_3-0"])]/@href').getall()
        for recipe_link in individual_recipes:
            yield scrapy.Request(url=recipe_link, callback=self.parse_content_page, meta={'filename': filename})


    def parse_content_page(self, response: Response, **kwangs:Any) -> Any:
        title = response.xpath('//h1[@class="article-heading type--lion"]//text()').get()
        filename = f"{response.meta['filename']}/{title}.txt"
        parent = "C://Users//Daniel Kwan//Desktop//RecipEat.ai-backend//scraper//output"
                 
        path = os.path.join(parent, filename) 
        
        #['Prep Time:', '10 mins', 'Cook Time:', '35 mins', 'Total Time:', '45 mins', 'Servings:', '6 ']
        cookinfo = list(filter(lambda x : x!='\n',response.xpath('//div[@class="mntl-recipe-details__item"]//text()').getall()))

        #['1', ' ', 'large (about 2 pounds) ', 'cauliflower, cut into small florets', '2', ' ', 'tablespoons', ' 
        # ', 'olive oil', 'salt and freshly ground black pepper to taste', '2/3', ' ', 'cups', ' ', 'sweet chili sauce', '2', ' ', 'teaspoons', ' ', 'soy sauce', '1', ' ', 'teaspoon', ' ', 'chile garlic sauce', ', such as Sriracha®', '1', ' ', 'green onion, sliced', '1/2', ' ', 'teaspoon', ' ', 'toasted sesame seeds for 
        # garnish (optional)']
        #ingredients
        ingredients = response.xpath('//ul[contains(@class, "mntl-structured-ingredients__list")]//li[contains(@class, "mntl-structured-ingredients__list-item")]//p//text()').getall()
        
        #[' Preheat the oven to 400 degrees F (200 degrees C), and set a rack in the upper third of the oven. Line a large baking sheet with parchment paper.\n', ' Place cauliflower florets in a large bowl. Top with olive oil, salt, and pepper; toss to coat. Arrange cauliflower on the prepared baking sheet in a single even layer.\n', ' Bake in the preheated oven on the upper rack until tender, about 30 minutes.\n', ' Meanwhile, bring sweet chili sauce, soy sauce, and Sriracha to a boil in a small saucepan over medium-high heat. Reduce heat to low and cook for 5 minutes.\n', ' Remove the baking sheet from the oven. Drizzle sauce on top and gently stir to coat.\n', ' Divide cauliflower between serving plates and top with green onion slices. Garnish with toasted sesame seeds.\n']
        # directionns
        directions = response.xpath('//p[contains(@class, "comp mntl-sc-block mntl-sc-block-html")]//text()').getall()
        # ['140', 'Calories', '5g ', 'Fat', '22g ', 'Carbs', '3g ', 'Protein']
        nutrition = response.xpath('//td[contains(@class,"mntl-nutrition-facts-summary__table-cell type--dog")]//text()').getall()        

         # Combine the extracted data into a single string
        content = f"Title: {title}\n\n"
        content += "Cook Info:\n" + "\n".join(cookinfo) + "\n\n"
        content += "Ingredients:\n" + "\n".join(ingredients) + "\n\n"
        content += "Directions:\n" + "\n".join(directions) + "\n\n"
        content += "Nutrition:\n" + "\n".join(nutrition) + "\n"

        # Write the content to the file, creating it if it doesn't exist
        with open(path, 'a+', encoding='utf-8') as file:
            file.write(content)
            file.write("\n\n")  # Add a couple of newlines for separation between entries

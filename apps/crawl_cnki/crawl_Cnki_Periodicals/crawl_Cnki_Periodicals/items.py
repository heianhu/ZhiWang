# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class ArticleItem(scrapy.Item):
    url = scrapy.Field()
    filename = scrapy.Field()
    title = scrapy.Field()
    periodicals = scrapy.Field()
    issuing_time = scrapy.Field()
    cited = scrapy.Field()
    keywords = scrapy.Field()
    abstract = scrapy.Field()
    DOI = scrapy.Field()
    remark = scrapy.Field()

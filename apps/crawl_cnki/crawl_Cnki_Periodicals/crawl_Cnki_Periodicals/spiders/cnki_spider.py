# -*- coding: utf-8 -*-
import scrapy
from crawl_data.models import Periodicals

class CnkiSpiderSpider(scrapy.Spider):
    name = 'cnki_spider'
    # allowed_domains = ['cnki.net']
    start_urls = ['http://kns.cnki.net/']

    def start_requests(self):
        """
        控制开始
        从数据库中找出所要爬取的url
        """
        periodicals = Periodicals.objects.all()  # 找到标记的期刊
        # periodicals = Periodicals.objects.filter(issn_number='1004-6577')  # 找到指定的期刊

        for periodical in periodicals:


            yield scrapy.Request(url=summary.url, headers=self.header, callback=self.parse,
                                     meta={'summary': summary})


    def parse(self, response):
        periodicals = Periodicals.objects.all()  # 找到标记的期刊
        for periodical in periodicals:


            yield scrapy.Request(url=summary.url, headers=self.header, callback=self.parse,
                                     meta={'summary': summary})
# -*- coding: utf-8 -*-
import scrapy
import re
from selenium import webdriver  # 导入Selenium的webdriver
from selenium.webdriver.support.ui import Select  # 导入Select
from selenium.webdriver.common.keys import Keys  # 导入Keys
from selenium.webdriver.chrome.options import Options  # Chrome设置内容
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from crawl_data.models import Periodicals
from crawl_cnki.crawl_Cnki_Periodicals.crawl_Cnki_Periodicals.items import ArticleItemLoader, ArticleItem
import time
from .BrowserSelect import CrawlCnkiSummary


class CnkiSpiderSpider(scrapy.Spider):
    name = 'cnki_spider'
    # allowed_domains = ['cnki.net']
    start_urls = ['http://kns.cnki.net/']
    header = {
        'Host': 'kns.cnki.net',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
    }
    split_word = re.compile(
        r'(QueryID=[a-zA-Z0-9.]&|CurRec=\d*&|DbCode=[a-zA-Z]*&|urlid=[a-zA-Z0-9.]*&|yx=[a-zA-Z]*)',
        flags=re.I
    )
    re_issuing_time = re.compile(
        '((?!0000)[0-9]{4}[-/]((0[1-9]|1[0-2])[-/](0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])[-/](29|30)|(0[13578]|1[02])[-/]31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)[-/]02[-/]29)'
    )
    _root_url = 'http://nvsm.cnki.net'
    crawlcnkisummary_gen = CrawlCnkiSummary()

    def start_requests(self):
        """
        控制开始
        从数据库中找出所要爬取的url
        """
        periodicals = Periodicals.objects.all()  # 找到标记的期刊
        # periodicals = Periodicals.objects.filter(issn_number='1004-6577')  # 找到指定的期刊

        for periodical in periodicals:
            for summary, url in self.crawlcnkisummary_gen.crawl_periodicals_summary(periodical.issn_number):
                yield scrapy.Request(url=url, headers=self.header, callback=self.parse,
                                     meta={'summary': summary, 'periodical': periodical.id})

    def parse(self, response):
        summary = response.meta.get('summary')
        periodical = response.meta.get('periodical')
        item_loader = ArticleItemLoader(item=ArticleItem, response=response)
        item_loader.add_value('title', summary.css('.fz14::text').extract())
        item_loader.add_value('filename', response.url)
        item_loader.add_value('issuing_time', summary.css('.cjfdyxyz + td::text').extract())
        item_loader.add_value('periodical', periodical)

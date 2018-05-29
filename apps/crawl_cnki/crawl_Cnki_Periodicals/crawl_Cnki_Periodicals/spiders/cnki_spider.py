# -*- coding: utf-8 -*-
import scrapy
import re
from selenium import webdriver  # 导入Selenium的webdriver
from selenium.webdriver.support.ui import Select  # 导入Select
from selenium.webdriver.common.keys import Keys  # 导入Keys
from selenium.webdriver.chrome.options import Options  # Chrome设置内容
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from crawl_cnki.models import Periodical, Article_References, References, Article
from crawl_cnki.crawl_Cnki_Periodicals.crawl_Cnki_Periodicals.items import ArticleItemLoader, ArticleItem, \
    ReferenceItem, ReferenceItemLoader
import time
from scrapy.selector import Selector
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options  # Chrome设置内容
import logging


# from .BrowserSelect import CrawlCnkiSummary
from crawl_cnki.crawl_Cnki_Periodicals.crawl_Cnki_Periodicals.RegularExpressions import *
from crawl_cnki.crawl_Cnki_Periodicals.crawl_Cnki_Periodicals.settings import REFERENCES_DBNAME


class CnkiSpiderSpider(scrapy.Spider):
    name = 'cnki_spider'
    # allowed_domains = ['cnki.net']
    start_urls = ['http://kns.cnki.net/']
    header = {
        'Host': 'kns.cnki.net',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
    }

    # crawlcnkisummary_gen = CrawlCnkiSummary()

    def __init__(self, *args, **kwargs):
        """
        初始化，建立与Django的models连接，设置初始值
        :param use_Chrome: True使用Chrome，False使用PhantomJS
        :param executable_path: PhantomJS路径
        """
        self.article_count = 0


        self._root_url = 'http://kns.cnki.net'

        self.search_url = self._root_url + '/kns/brief/result.aspx?dbprefix=CJFQ'
        self.sort_page_url = (
            # 第一次来先将时间由新到旧排序
            "/kns/brief/brief.aspx?{0}RecordsPerPage=20&QueryID=1&ID=&pagemode=L&dbPrefix=CJFQ&Fields=&DisplayMode=listmode&SortType=(%E5%8F%91%E8%A1%A8%E6%97%B6%E9%97%B4%2c%27TIME%27)+desc&PageName=ASP.brief_result_aspx#J_ORDER&",
            # 第二次来将时间由旧到新排序
            "/kns/brief/brief.aspx?{0}RecordsPerPage=20&QueryID=1&ID=&pagemode=L&dbPrefix=CJFQ&Fields=&DisplayMode=listmode&SortType=(%E5%8F%91%E8%A1%A8%E6%97%B6%E9%97%B4%2c%27TIME%27)&PageName=ASP.brief_result_aspx#J_ORDER&"
        )

    def start_requests(self):
        """
        控制开始
        从数据库中找出所要爬取的url
        """
        # articles = Article.objects.filter(remark__icontains='{')
        # for article in articles:
        #     article.keywords = ''
        #     article.abstract = ''
        #     article.DOI = ''
        #     article.remark = ''
        #     article.save()

        # articles = Article.objects.filter(remark='')[:1]
        articles = Article.objects.filter(filename='JYYJ201710008')
        for article in articles:
            yield scrapy.Request(
                url=article.url, headers=self.header, callback=self.parse, meta={'article': article}
            )

    def parse(self, response):
        """
        解析文章细节
        :param response:
        :return:
        """
        # summary = response.meta.get('summary','')
        # periodicals = response.meta.get('periodical')
        article = response.meta.get('article')
        item_loader = ArticleItemLoader(item=ArticleItem(), response=response)
        # 文章部分
        # item_loader.add_value('url', response.url)
        # item_loader.add_value('filename', response.url)
        # item_loader.add_value('title', 'testtitle')
        # item_loader.add_value('issuing_time', '2020-2-2')
        # item_loader.add_value('periodicals', periodicals)

        # 文章剩余细节
        item_loader.add_css('remark', '.wxBaseinfo p')

        # 文章作者和机构部分
        item_loader.add_css('authors_id', '.author')
        item_loader.add_css('authors_name', '.author')
        item_loader.add_css('org_id', '.orgn')
        item_loader.add_css('org_name', '.orgn')
        item_loader.add_value('article', article)
        article_item = item_loader.load_item()
        yield article_item

        # 参考文献部分

        # 记住此文章名
        filename = article.filename

        # 此url用于探测该文章有多少页参考文献

        # # eel的分段式url
        # refers_url = 'http://kns.cnki.net/kcms/detail/frame/list.aspx?dbcode=CJFQ&filename={}&' \
        #              'RefType=1&CurDBCode=CJFQ&page=1'.format(filename)

        # 整合式url
        refers_url = 'http://kns.cnki.net/kcms/detail/frame/list.aspx?dbcode=CJFQ&filename={0}&RefType=1&page=1'.format(
            filename)

        yield scrapy.Request(url=refers_url, headers=self.header, callback=self.parse_refer_pages,
                             meta={'article': article, 'cur_page': 1})

    def parse_refer_pages(self, response):
        """
        解析每篇文章的参考文献页面数
        :param response:
        :return:
        """
        article = response.meta.get('article', '')
        cur_page = response.meta.get('cur_page')
        refers_url = response.url.split('page=')[0] + 'page=' + str(cur_page + 1)

        # 找到每个期刊的数量
        every_page = []  # 每种引用期刊的数量
        for references_name in REFERENCES_DBNAME:
            every_page.append(
                int(response.xpath('//span[@id="pc_{}"]/text()'.format(references_name)).extract_first(default=0))
            )

        page = max(every_page)  # 找到最大的参考文献库个数，定制翻页次数
        page = (page / 10)  # 每页有10条数据


        # 爬取参考文献
        div_s = response.css('.essayBox')  # 拿到所有含有文献列表的模块
        for div in div_s:
            # 分块提取信息
            # 判断当前块所属库
            dbId = div.css('.dbTitle span::attr(id)').extract_first()
            dbId = dbId[3:]
            li_s = div.css('li')

            # 提取中国学术期刊网络出版总库信息
            for li in li_s:
                try:
                    refer = li.extract()
                    refer = RE_refers.search(refer).group(1)
                    item_loader = ReferenceItemLoader(item=ReferenceItem(), response=response)
                    item_loader.add_value('article', article)

                    # 将source和参考文献一起传入，供后续按数据库分类清洗
                    item_loader.add_value('info', [dbId, refer])
                    # remark保存为原始信息
                    item_loader.add_value('remark', [dbId, refer])

                    reference_item = item_loader.load_item()
                    yield reference_item
                except TypeError:
                    continue
                except IndexError:
                    # 数据没有url获取他内容，不完整，不具备参考价值
                    continue



        # 继续爬剩下的
        if page > cur_page:
            # 网页+1继续获取信息
            yield scrapy.Request(
                url=refers_url, headers=self.header, callback=self.parse_refer_pages,
                meta={'article': article, 'cur_page': cur_page + 1}
            )











    # def parse_refer_pages(self, response):
    #     """
    #     解析每篇文章的参考文献页面数
    #     :param response:
    #     :return:
    #     """
    #     article = response.meta.get('article', '')
    #     # 各个数据库的代码号
    #     sources = ['CJFQ', 'CDFD', 'CMFD', 'CBBD', 'SSJD', 'CRLDENG', 'CCND', 'CPFD']
    #
    #     # 获取各个数据库的页数 如:pages: [1,1,1,1,3,3,1,1]
    #     pages = []
    #     for source in sources:
    #         css_partten = '#pc_{}::text'.format(source)
    #         # 每个数据库中条数
    #         nums = int(response.css(css_partten).extract_first(default=0))
    #         # 由条数计算页数
    #         pc = (nums - 1) // 10 + 1
    #         pages.append(pc)
    #
    #     # 如果所有数据库都是0页,即此文章没有参考文献
    #     if not any(pages):
    #         return
    #
    #     # 每个数据库的每一页为一个url
    #     for i, source in enumerate(sources):
    #         for page in range(1, pages[i] + 1):
    #             # 按数据库和页码格式化每一个url
    #             url = 'http://kns.cnki.net/kcms/detail/frame/list.aspx?' \
    #                   'dbcode=CJFQ&filename={0}&RefType=1&CurDBCode={1}&page={2}' \
    #                 .format(article.filename, source, page)
    #
    #             # 每一个url只解析一种数据库的一页参考文献
    #             yield scrapy.Request(url=url, headers=self.header, callback=self.parse_references,
    #                                  dont_filter=True,
    #                                  meta={'article': article,
    #                                        'source': source})

    def parse_references(self, response):
        """
        每次调用只解析一种数据库的参考文献，根据meta中的source确定是那种种类
        :param response:
        :return:
        """

        article = response.meta.get('article', '')
        source = response.meta.get('source', '')
        essayBoxs = response.css('.essayBox').extract()
        refers = []

        # essayBoxs 是一个html页面中所有的数据库box，只有一个box是需要提取的(符合source)
        for box in essayBoxs:
            if source in box:
                refers = RE_refers.findall(box)
                break

        for refer in refers:
            item_loader = ReferenceItemLoader(item=ReferenceItem(), response=response)
            item_loader.add_value('article', article)

            # 将source和参考文献一起传入，供后续按数据库分类清洗
            item_loader.add_value('info', [source, refer])
            # remark保存为原始信息
            item_loader.add_value('remark', [source, refer])

            reference_item = item_loader.load_item()
            yield reference_item

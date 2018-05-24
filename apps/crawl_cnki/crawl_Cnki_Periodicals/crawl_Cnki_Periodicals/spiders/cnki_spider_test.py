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


class CnkiSpiderSpider(scrapy.Spider):
    name = 'cnki_spider_test'
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

        articles = Article.objects.all()[:5]
        for article in articles:
            yield scrapy.Request(
                url=article.url, headers=self.header, callback=self.parse, meta={'article': article}
            )



    def do_search(self, search_url, issn_number):
        """
        使用浏览器执行 以某个issn 搜索动作
        :param search_url: 执行搜索界面的 url
        :param issn_number:搜索条件
        :return: 搜到的可翻页的summary_url, 总页数, cookies
        """

        # 无界面运行
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(chrome_options=chrome_options)  # 指定使用的浏览器，初始化webdriver


        driver.get(search_url)
        elem = driver.find_element_by_id("magazine_value1")  # 找到name为q的元素，这里是个搜索框
        elem.send_keys(issn_number)
        select = Select(driver.find_element_by_id('magazine_special1'))  # 通过Select来定义该元素是下拉框
        select.select_by_index(1)  # 通过下拉元素的位置来选择
        elem.send_keys(Keys.RETURN)  # 相当于回车键，提交
        driver.switch_to.frame('iframeResult')

        # time.sleep(2)

        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "GridTableContent"))
            )

            # print(driver.page_source)

            # url = driver.find_element_by_class_name("groupsorttitle").get_attribute('href')

            # match = re.search(r'queryid=([\d]+)\">相关度', driver.page_source)
            # queryid = match.group(1)

            # # 搜索结果列表页的url
            # summary_url = self._root_url + '/kns/brief/brief.aspx?curpage=1&RecordsPerPage=20&QueryID=0&ID=&' \
            #                 'turnpage=1&dbPrefix=CJFQ&PageName=ASP.brief_result_aspx#J_ORDER&'
            # driver.get(url=summary_url)
            # 拿到cookies
            cookies = driver.get_cookies()
            # 拿到最大页数
            pagenums = Selector(text=driver.page_source).css('.countPageMark::text').extract()
            try:
                pagenums = int(pagenums[0].split('/')[1])
            except:
                pagenums = 1


        finally:
            driver.close()
        return pagenums, cookies

    def parse_summary(self, response):
        """
        解析文章url和概览
        :param response:
        :return:
        """
        # summarys = response.css('.GridTableContent tr')[1:]
        #
        # for summary in summarys:
        #     # for summary in summarys[:1]:  # 暂时只取第一条文章
        #     url = summary.css('.fz14::attr(href)').extract()[0]
        #     # 改成正常的url
        #     url = url.split('/kns')[-1]
        #     url = 'http://kns.cnki.net/KCMS' + url
        #     url = ''.join(url.split())  # 有些url中含有空格
        #     url = RE_split_word.sub('', url)
        #
        #     self.article_count += 1
        #     if self.article_count % 500 == 0:
        #         print("正在处理约第{0:6} 篇文献".format(self.article_count))
        #         logging.info("正在处理约第{0:6} 篇文献".format(self.article_count))
        #



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
        refers_url = 'http://kns.cnki.net/kcms/detail/frame/list.aspx?dbcode=CJFQ&filename={}&' \
                     'RefType=1&CurDBCode=CJFQ&page=1'.format(filename)

        yield scrapy.Request(url=refers_url, headers=self.header, callback=self.parse_refer_pages,
                             meta={'article': article})

    def parse_refer_pages(self, response):
        """
        解析每篇文章的参考文献页面数
        :param response:
        :return:
        """
        article = response.meta.get('article', '')
        # 各个数据库的代码号
        sources = ['CJFQ', 'CDFD', 'CMFD', 'CBBD', 'SSJD', 'CRLDENG', 'CCND', 'CPFD']

        # 获取各个数据库的页数 如:pages: [1,1,1,1,3,3,1,1]
        pages = []
        for source in sources:
            css_partten = '#pc_{}::text'.format(source)
            # 每个数据库中条数
            nums = int(response.css(css_partten).extract_first(default=0))
            # 由条数计算页数
            pc = (nums - 1) // 10 + 1
            pages.append(pc)

        # 如果所有数据库都是0页,即此文章没有参考文献
        if not any(pages):
            return

        # 每个数据库的每一页为一个url
        for i, source in enumerate(sources):
            for page in range(1, pages[i] + 1):
                # 按数据库和页码格式化每一个url
                url = 'http://kns.cnki.net/kcms/detail/frame/list.aspx?' \
                      'dbcode=CJFQ&filename={0}&RefType=1&CurDBCode={1}&page={2}' \
                    .format(article.filename, source, page)

                # 每一个url只解析一种数据库的一页参考文献
                yield scrapy.Request(url=url, headers=self.header, callback=self.parse_references,
                                     dont_filter=True,
                                     meta={'article': article,
                                           'source': source})

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

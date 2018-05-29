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

        articles = Article.objects.filter(remark='')[:1000]
        # articles = Article.objects.filter(filename='JYYJ201709016')
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
            li_s = div.css('li')
            if dbId == 'pc_CJFQ':
                # 提取中国学术期刊网络出版总库信息
                for li in li_s:
                    try:
                        a_s = li.css('a')
                        url = 'http://kns.cnki.net' + a_s[0].css('a::attr(href)').extract_first()
                        title = a_s[0].css('a::text').extract_first()
                        if len(title) > 255:
                            title = title[:255]
                        authors = li.css('li::text').extract_first().split('[J].')[-1].split('.&nbsp&nbsp')[0]
                        if len(authors) > 255:
                            authors = authors[:255]
                        source = a_s[1].css('a::text').extract_first()
                        issuing_time = a_s[2].css('a::text').extract_first().rsplit()[0]
                        if not ReferencesCJFQ.objects.filter(url=url):
                            # 在数据库中没有这条数据信息
                            CJFQ_item = ReferencesCJFQItem()
                            CJFQ_item['url'] = url
                            CJFQ_item['title'] = title
                            CJFQ_item['authors'] = authors
                            CJFQ_item['source'] = source
                            CJFQ_item['issuing_time'] = issuing_time
                            yield CJFQ_item
                            CJFQ_list.append(CJFQ_item['database_id'])
                        else:
                            CJFQ_list.append(str(ReferencesCJFQ.objects.filter(url=url)[0].id))
                    except TypeError:
                        continue
                    except IndexError:
                        # 数据没有url获取他内容，不完整，不具备参考价值
                        continue
            elif dbId == 'pc_CDFD':
                # 提取中国博士学位论文全文数据库
                try:
                    for li in li_s:
                        a_s = li.css('a')
                        url = 'http://kns.cnki.net' + a_s[0].css('a::attr(href)').extract_first()
                        title = a_s[0].css('a::text').extract_first()
                        if len(title) > 255:
                            title = title[:255]
                        authors = li.css('li::text').extract_first().split('[D].')[-1]
                        if len(authors) > 255:
                            authors = authors[:255]
                        source = a_s[1].css('a::text').extract_first()
                        issuing_time = li.css('li').extract_first().split('</a>')[-1].split('</li>')[0].rsplit()[0]
                        if not ReferencesCDFD.objects.filter(url=url):
                            # 在数据库中没有这条数据信息
                            CDFD_item = ReferencesCDFDItem()
                            CDFD_item['url'] = url
                            CDFD_item['title'] = title
                            CDFD_item['authors'] = authors
                            CDFD_item['source'] = source
                            CDFD_item['issuing_time'] = issuing_time
                            yield CDFD_item
                            CDFD_list.append(CDFD_item['database_id'])
                        else:
                            CDFD_list.append(str(ReferencesCDFD.objects.filter(url=url)[0].id))
                except IndexError:
                    # 数据没有url获取他内容，不完整，不具备参考价值
                    continue
            elif dbId == 'pc_CMFD':
                # 提取中国优秀硕士学位论文全文数据库
                try:
                    for li in li_s:
                        a_s = li.css('a')
                        url = 'http://kns.cnki.net' + a_s[0].css('a::attr(href)').extract_first()
                        title = a_s[0].css('a::text').extract_first()
                        if len(title) > 255:
                            title = title[:255]
                        authors = li.css('li::text').extract_first().split('[D].')[-1]
                        if len(authors) > 255:
                            authors = authors[:255]
                        source = a_s[1].css('a::text').extract_first()
                        issuing_time = li.css('li').extract_first().split('</a>')[-1].split('</li>')[0].rsplit()[0]
                        if not ReferencesCMFD.objects.filter(url=url):
                            # 在数据库中没有这条数据信息
                            CMFD_item = ReferencesCMFDItem()
                            CMFD_item['url'] = url
                            CMFD_item['title'] = title
                            CMFD_item['authors'] = authors
                            CMFD_item['source'] = source
                            CMFD_item['issuing_time'] = issuing_time
                            yield CMFD_item
                            CMFD_list.append(CMFD_item['database_id'])
                        else:
                            CMFD_list.append(str(ReferencesCMFD.objects.filter(url=url)[0].id))
                except IndexError:
                    # 数据没有url获取他内容，不完整，不具备参考价值
                    continue
            elif dbId == 'pc_CBBD':
                # 提取中国图书全文数据库
                try:
                    for li in li_s:
                        all_info = li.css('li::text').extract_first().rsplit()
                        title = all_info[0]
                        if len(title) > 255:
                            title = title[:255]
                        authors = all_info[3]
                        if len(authors) > 255:
                            authors = authors[:255]
                        source = all_info[1]
                        issuing_time = all_info[4]
                        if not ReferencesCBBD.objects.filter(
                                Q(title=title) & Q(authors=authors) & Q(source=source) & Q(issuing_time=issuing_time)):
                            CBBD_item = ReferencesCBBDItem()
                            CBBD_item['title'] = title
                            CBBD_item['authors'] = authors
                            CBBD_item['source'] = source
                            CBBD_item['issuing_time'] = issuing_time
                            yield CBBD_item
                            CBBD_list.append(CBBD_item['database_id'])
                        else:
                            CBBD_list.append(
                                str(
                                    ReferencesCBBD.objects.filter(
                                        Q(title=title) & Q(authors=authors) & Q(source=source) & Q(
                                            issuing_time=issuing_time)
                                    )[0].id
                                )
                            )
                except IndexError:
                    # 数据没有url获取他内容，不完整，不具备参考价值
                    continue
            elif dbId == 'pc_SSJD':
                # 提取国际期刊数据库
                for li in li_s:
                    url = 'http://kns.cnki.net' + li.css('a::attr(href)').extract_first()
                    title = li.css('a::text').extract_first()
                    if len(title) > 255:
                        title = title[:255]
                    all_info = li.css('li::text').extract_first().split('\r\n')
                    info = all_info[1]
                    if len(info) > 255:
                        info = info[:255]
                    issuing_time = all_info[2]
                    if not ReferencesSSJD.objects.filter(url=url):
                        SSJD_item = ReferencesSSJDItem()
                        SSJD_item['url'] = url
                        SSJD_item['title'] = title
                        SSJD_item['info'] = info
                        SSJD_item['issuing_time'] = issuing_time
                        yield SSJD_item
                        SSJD_list.append(SSJD_item['database_id'])
                    else:
                        SSJD_list.append(str(ReferencesSSJD.objects.filter(url=url)[0].id))
            elif dbId == 'pc_CRLDENG':
                # 提取外文题录数据库
                for li in li_s:
                    try:
                        title = li.css('a::text').extract_first()
                        if len(title) > 255:
                            title = title[:255]
                        all_info = li.css('li::text').extract_first().split('\r\n')
                        if len(all_info) < 3:
                            # 数据个数不符
                            continue
                        info = all_info[1]
                        if len(info) > 255:
                            info = info[:255]
                        issuing_time = all_info[2]
                        if not ReferencesCRLDENG.objects.filter(
                                Q(title=title) & Q(info=info) & Q(issuing_time=issuing_time)):
                            CRLDENG_item = ReferencesCRLDENGItem()
                            CRLDENG_item['title'] = title
                            CRLDENG_item['info'] = info
                            CRLDENG_item['issuing_time'] = issuing_time
                            yield CRLDENG_item
                            CRLDENG_list.append(CRLDENG_item['database_id'])
                        else:
                            CRLDENG_list.append(
                                str(
                                    ReferencesCRLDENG.objects.filter(
                                        Q(title=title) & Q(info=info) & Q(issuing_time=issuing_time)
                                    )[0].id
                                )
                            )
                    except TypeError:
                        continue
            elif dbId == 'pc_CCND':
                # 中国重要报纸全文数据库
                for li in li_s:
                    url = 'http://kns.cnki.net' + li.css('a::attr(href)').extract_first()
                    title = li.css('a::text').extract_first()
                    if len(title) > 255:
                        title = title[:255]
                    all_info = li.css('li::text').extract_first().split('\r\n')
                    authors = all_info[1].split('&nbsp&nbsp')[0]
                    if len(authors) > 255:
                        authors = authors[:255]
                    source = all_info[1].split('&nbsp&nbsp')[-1]
                    issuing_time = all_info[2]
                    if not ReferencesCCND.objects.filter(url=url):
                        # 在数据库中没有这条数据信息
                        CCND_item = ReferencesCCNDItem()
                        CCND_item['url'] = url
                        CCND_item['title'] = title
                        CCND_item['authors'] = authors
                        CCND_item['source'] = source
                        CCND_item['issuing_time'] = issuing_time
                        yield CCND_item
                        CCND_list.append(CCND_item['database_id'])
                    else:
                        CCND_list.append(str(ReferencesCCND.objects.filter(url=url)[0].id))
            elif dbId == 'pc_CPFD':
                for li in li_s:
                    url = 'http://kns.cnki.net' + li.css('a::attr(href)').extract_first()
                    title = li.css('a::text').extract_first()
                    if len(title) > 255:
                        title = title[:255]
                    all_info = li.css('li::text').extract_first().split('\r\n')
                    info = all_info[1]
                    if len(info) > 255:
                        info = info[:255]
                    issuing_time = all_info[2]
                    if not ReferencesCPFD.objects.filter(url=url):
                        CPFD_item = ReferencesCPFDItem()
                        CPFD_item['url'] = url
                        CPFD_item['title'] = title
                        CPFD_item['info'] = info
                        CPFD_item['issuing_time'] = issuing_time
                        yield CPFD_item
                        CPFD_list.append(CPFD_item['database_id'])
                    else:
                        CPFD_list.append(str(ReferencesCPFD.objects.filter(url=url)[0].id))
            else:
                print('当前块所属库dbId错误!url=', response.url)


        # 继续爬剩下的
        if page > cur_page:
            # 网页+1继续获取信息
            yield scrapy.Request(
                url=refers_url, headers=self.header, callback=self.parse_refer_pages,
                meta={'article': article, 'cur_page': cur_page + 1}
            )











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

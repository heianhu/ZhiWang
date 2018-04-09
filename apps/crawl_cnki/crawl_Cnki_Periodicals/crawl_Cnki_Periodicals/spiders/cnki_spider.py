# -*- coding: utf-8 -*-
import scrapy
import re
from selenium import webdriver  # 导入Selenium的webdriver
from selenium.webdriver.support.ui import Select  # 导入Select
from selenium.webdriver.common.keys import Keys  # 导入Keys
from selenium.webdriver.chrome.options import Options  # Chrome设置内容
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from crawl_data.models import Periodicals
from crawl_cnki.crawl_Cnki_Periodicals.crawl_Cnki_Periodicals.items import ArticleItemLoader, ArticleItem, ReferenceItem, ReferenceItemLoader
import time
from scrapy.selector import Selector

# from .BrowserSelect import CrawlCnkiSummary


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

    # crawlcnkisummary_gen = CrawlCnkiSummary()

    def __init__(self):
        """
        初始化，建立与Django的models连接，设置初始值
        :param use_Chrome: True使用Chrome，False使用PhantomJS
        :param executable_path: PhantomJS路径
        """
        self.split_word = re.compile(
            r'(QueryID=[a-zA-Z0-9.]&|CurRec=\d*&|DbCode=[a-zA-Z]*&|urlid=[a-zA-Z0-9.]*&|yx=[a-zA-Z]*)',
            flags=re.I
        )
        self.re_issuing_time = re.compile(
            '((?!0000)[0-9]{4}[-/]((0[1-9]|1[0-2])[-/](0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])[-/](29|30)|(0[13578]|1[02])[-/]31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)[-/]02[-/]29)')
        self._root_url = 'http://nvsm.cnki.net'

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
        # periodicals = Periodicals.objects.all()  # 期刊
        periodicals = Periodicals.objects.filter(issn_number='1674-7216')  # 暂时只用一个issn

        # 对每一个issn进行爬取
        for periodical in periodicals:
            summary_url, pagenums, cookies = self.do_search(self.search_url, periodical.issn_number)

            # for page in range(1, pagenums + 1):
            for page in range(1):  # 暂时只搜一页
            # curr_page = "curpage={0}&turnpage={0}&".format(page)
                # page_url = summary_url.format(curr_page)
                # 遍历每一页
                yield scrapy.Request(url=summary_url, headers=self.header,
                                callback=self.parse_summary, cookies=cookies,
                                meta={'periodical': periodical.id})


    def do_search(self, search_url, issn_number):
        """
        使用浏览器执行 以某个issn 搜索动作
        :param search_url: 执行搜索界面的 url
        :param issn_number:搜索条件
        :return: 搜到的可翻页的summary_url, 总页数, cookies
        """
        driver = webdriver.Chrome() #初始化webdriver
        driver.get(search_url)
        elem = driver.find_element_by_id("magazine_value1")  # 找到name为q的元素，这里是个搜索框
        elem.send_keys(issn_number)
        select = Select(driver.find_element_by_id('magazine_special1'))  # 通过Select来定义该元素是下拉框
        select.select_by_index(1)  # 通过下拉元素的位置来选择
        elem.send_keys(Keys.RETURN)  # 相当于回车键，提交
        time.sleep(2)
        # 搜索结果列表页的url
        summary_url = self._root_url + '/kns/brief/brief.aspx?curpage=1&RecordsPerPage=20&QueryID=20&ID=&turnpage=1&dbPrefix=CJFQ&PageName=ASP.brief_result_aspx#J_ORDER&'
        driver.get(url=summary_url)
        # 拿到cookies
        cookies = driver.get_cookies()
        # 拿到最大页数
        pagenums = Selector(text=driver.page_source).css('.countPageMark::text').extract()
        try:
            pagenums = int(pagenums[0].split('/')[1])
        except:
            pagenums = 1

        driver.close()

        return summary_url, pagenums, cookies



    def parse_summary(self, response):
        """
        解析文章url和概览
        :param response:
        :return:
        """
        summarys = response.css('.GridTableContent tr')[1:]
        for summary in summarys[:1]:  # 暂时只取第一条文章
            url = summary.css('.fz14::attr(href)').extract()[0]
            # 改成正常的url
            url = url.split('/kns')[-1]
            url = 'http://kns.cnki.net/KCMS' + url
            url = ''.join(url.split())  # 有些url中含有空格
            url = self.split_word.sub('', url)

            # 将summary中的网页元素传给后续的parse函数，以统一解析文章所有细节
            yield scrapy.Request(url=url, headers=self.header,
                                 callback=self.parse,
                                 meta={'summary': summary,
                                       'periodical': response.meta.get('periodical')
                                     })


    def parse(self, response):
        """
        解析文章细节
        :param response:
        :return:
        """
        summary = response.meta.get('summary')
        periodicals = response.meta.get('periodical')

        item_loader = ArticleItemLoader(item=ArticleItem(), response=response)
        # 文章主体部分
        item_loader.add_value('url', response.url)
        item_loader.add_value('filename', response.url)
        item_loader.add_value('title', summary.css('.fz14::text').extract())
        item_loader.add_value('issuing_time', summary.css('.cjfdyxyz + td::text').extract())
        item_loader.add_value('periodicals', periodicals)
        # TODO 文章剩余细节
        # item_loader.add_css('cited', periodical)
        # item_loader.add_css('keywords', periodical)
        # item_loader.add_css('abstract', periodical)
        # item_loader.add_css('DOI', periodical)
        # item_loader.add_css('DOI', periodical)
        # item_loader.add_css('remark', periodical)


        # 文章作者和机构部分
        item_loader.add_css('authors_id', '.author')
        item_loader.add_css('authors_name', '.author')
        item_loader.add_css('org_id', '.orgn')
        item_loader.add_css('org_name', '.orgn')

        article_item = item_loader.load_item()
        yield article_item


        # 参考文献部分

        # 记住此文章
        filename = article_item['filename']

        # 各个数据库的代码号
        sources = ['CJFQ', 'CDFD', 'CMFD', 'CBBD', 'SSJD', 'CRLDENG', 'CCND', 'CPFD']

        # 获取各个数据库的页数 如:pages: [1,1,1,1,3,3,1,1]
        pages = []
        for source in sources:
            pc = int(response.xpath('//span[@id="pc_{0}"]/text()'.format(source)).extract_first(default=1))
            pages.append(pc)


        # 每个数据库的每一页为一个url
        for i, source in enumerate(sources):
            for page in range(1, pages[i]+1):
                # 按数据库和页码格式化每一个url
                url = 'http://kns.cnki.net/kcms/detail/frame/list.aspx?' \
                                 'dbcode=CJFQ&filename={0}&RefType=1&CurDBCode={1}&page={2}' \
                                    .format(filename, source, page)

                # 每一个url只解析一种数据库的一页参考文献
                yield scrapy.Request(url=url, headers=self.header, callback=self.parse_references,
                                     meta={'filename': filename,
                                           'source': source})


    def parse_references(self, response):
        """
        每次调用只解析一种数据库的参考文献，根据meta中的source确定是那种种类
        :param response:
        :return:
        """

        filename = response.meta.get('filename', '')
        source = response.meta.get('source', '')
        essayBoxs = response.css('.essayBox').extract()
        refers = []

        # essayBoxs 是一个html页面中所有的数据库box，只有一个box是需要提取的(符合source)
        for box in essayBoxs:
            if source in box:
                refers = re.findall(r'</em>([\s\S]*?)</li>', box)
                break

        for refer in refers:
            item_loader = ReferenceItemLoader(item=ReferenceItem(), response=response)
            item_loader.add_value('article', filename)
            item_loader.add_value('source', source)
            item_loader.add_value('url', refer)
            item_loader.add_value('title', refer)
            item_loader.add_value('authors', refer)
            item_loader.add_value('issuing_time', refer)
            item_loader.add_value('remark', refer)

            reference_item = item_loader.load_item()
            yield reference_item

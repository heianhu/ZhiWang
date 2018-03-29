#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'

import os
import sys
from django.core.wsgi import get_wsgi_application
from selenium import webdriver  # 导入Selenium的webdriver
from selenium.webdriver.support.ui import Select  # 导入Select
from selenium.webdriver.common.keys import Keys  # 导入Keys
from selenium.webdriver.chrome.options import Options  # Chrome设置内容
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from scrapy.selector import Selector
from datetime import datetime
import time
import re
from django.db.models import Q
from django.db import IntegrityError

pathname = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.extend([pathname, ])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ZhiWang.settings")
application = get_wsgi_application()
from crawl_data.models import Summary, Periodicals, References


class CrawlCnkiSummary(object):
    _root_url = 'http://nvsm.cnki.net'

    def __init__(self, use_Chrome=True, executable_path=''):
        """
        初始化，建立与Django的models连接，设置初始值
        :param use_Chrome: True使用Chrome，False使用PhantomJS
        :param executable_path: PhantomJS路径
        """
        self.split_word = re.compile(
            r'(QueryID=0&|CurRec=\d+&|DbCode=[a-zA-Z]+&|urlid=[a-zA-Z0-9.]*&|yx=[a-zA-Z]*)',
            flags=re.I
        )
        self.re_issuing_time = re.compile(
            '((?!0000)[0-9]{4}[-/]((0[1-9]|1[0-2])[-/](0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])[-/](29|30)|(0[13578]|1[02])[-/]31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)[-/]02[-/]29)')
        self.use_Chrome = use_Chrome
        self.executable_path = executable_path

    def test(self):
        # summary = Summary()
        # summary.abstract = 'ok'
        # print(summary.abstract)
        summarys = Summary.objects.filter(Q(url__icontains='yx=') | Q(url__icontains='urlid='))
        all_count = summarys.count()
        count = 1
        for summary in summarys:
            print(str(count) + '/' + str(all_count))
            count += 1
            summary.url = self.split_word.sub('', summary.url)
            try:
                summary.save()
            except IntegrityError:
                summary.delete()

    def get_periodicals_summary(self, keyword, *args, first=True):
        """
        获取期刊概览
        因为在url中不能调用排序功能，所以目前只能拿到前6000个
        内含去重功能
        :param keyword: Periodicals对象
        """
        start_url = self._root_url + '/kns/brief/result.aspx?dbprefix=CJFQ'

        if self.use_Chrome:
            # 使用Chrome
            # 设置Chrome无界面化
            # chrome_options = Options()
            # chrome_options.add_argument('--headless')
            # chrome_options.add_argument('--disable-gpu')
            # driver = webdriver.Chrome(chrome_options=chrome_options)  # 指定使用的浏览器，初始化webdriver
            driver = webdriver.Chrome()  # 指定使用的浏览器，初始化webdriver
        else:
            desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
            desired_capabilities["phantomjs.page.settings.userAgent"] = \
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
            desired_capabilities["phantomjs.page.settings.loadImages"] = False
            driver = webdriver.PhantomJS(executable_path=self.executable_path)  # 不载入图片，爬页面速度会快很多

        driver.get(start_url)
        elem = driver.find_element_by_id("magazine_value1")  # 找到name为q的元素，这里是个搜索框
        elem.send_keys(keyword.issn_number)
        select = Select(driver.find_element_by_id('magazine_special1'))  # 通过Select来定义该元素是下拉框
        select.select_by_index(1)  # 通过下拉元素的位置来选择
        elem.send_keys(Keys.RETURN)  # 相当于回车键，提交
        time.sleep(2)
        driver.get(
            url=self._root_url + '/kns/brief/brief.aspx?curpage=1&RecordsPerPage=20&QueryID=20&ID=&turnpage=1&dbPrefix=CJFQ&PageName=ASP.brief_result_aspx#J_ORDER&'
        )
        # 根据时间排序
        if first:
            # 第一次来先将时间由新到旧排序
            every_page_url = "/kns/brief/brief.aspx?{0}RecordsPerPage=20&QueryID=1&ID=&pagemode=L&dbPrefix=CJFQ&Fields=&DisplayMode=listmode&SortType=(%E5%8F%91%E8%A1%A8%E6%97%B6%E9%97%B4%2c%27TIME%27)+desc&PageName=ASP.brief_result_aspx#J_ORDER&"
        else:
            # 第二次来将时间由旧到新排序
            every_page_url = "/kns/brief/brief.aspx?{0}RecordsPerPage=20&QueryID=1&ID=&pagemode=L&dbPrefix=CJFQ&Fields=&DisplayMode=listmode&SortType=(%E5%8F%91%E8%A1%A8%E6%97%B6%E9%97%B4%2c%27TIME%27)&PageName=ASP.brief_result_aspx#J_ORDER&"
        t_selector = Selector(text=driver.page_source)
        pagenums = t_selector.css('.countPageMark::text').extract()
        try:
            # 拿到最大页数
            pagenums = int(pagenums[0].split('/')[1])
        except:
            pagenums = 1

        have_done = 0  # 监测是否已经提取过该概览
        for num in range(1, pagenums + 1):
            print(keyword.issn_number + ":page-" + str(num))
            curr_page = "curpage={0}&turnpage={0}&".format(num)
            if num == 1:
                page_url = every_page_url.format('')
            else:
                page_url = every_page_url.format(curr_page)
            # 遍历每一页
            driver.get(
                self._root_url + page_url
            )
            t_selector = Selector(text=driver.page_source)
            summarys = t_selector.css('.GridTableContent tr')[1:]
            # 获取每一个细节
            for i in summarys:
                if have_done >= 100:
                    # 如果有5个连续的url已重复表示之后的也都有收录过了
                    driver.quit()
                    return
                url = i.css('.fz14::attr(href)').extract()[0]

                # 改成正常的url
                url = url.split('/kns')[-1]
                url = 'http://kns.cnki.net/KCMS' + url
                url = ''.join(url.split())  # 有些url中含有空格
                url = self.split_word.sub('', url)
                # 查询是否已经有该url
                have_url = Summary.objects.filter(url=url)
                if have_url:
                    # 如果有收录过该url，则跳过本次，计数器+1
                    have_done += 1
                    continue
                else:
                    have_done = 0
                title = i.css('.fz14::text').extract()
                if not title:
                    continue
                else:
                    title = title[0]
                if len(title) > 255:
                    title = title[:255]
                authors = i.css('.author_flag a::text').extract()
                authors = ','.join(authors)
                if len(authors) > 255:
                    authors = authors[:255]
                # source = i.css('.cjfdyxyz a::text').extract()[0]
                issuing_time = i.css('.cjfdyxyz + td::text').extract()[0]
                issuing_time = self.re_issuing_time.search(issuing_time)
                if issuing_time is None:
                    issuing_time = '1900-01-01'
                else:
                    issuing_time = issuing_time.group(0)
                if '/' in issuing_time:
                    issuing_time = issuing_time.replace('/', '-')
                cited = i.css('.KnowledgeNetcont a::text').extract()
                if not cited:
                    cited = 0
                else:
                    cited = int(cited[0])

                # print(url)
                summary = Summary()
                summary.url = url
                summary.title = title
                summary.authors = authors
                summary.source = keyword
                summary.issuing_time = datetime.strptime(issuing_time, '%Y-%m-%d').date()
                summary.cited = cited
                summary.have_detail = False
                summary.detail = None
                summary.save()
        driver.quit()

    def crawl_periodicals_summary(self, *args, start_num=0, mark=False, issn_number=0):
        """
        爬取期刊概览内容
        :param start_num: periodicals中ID-1
        :param mark: 若mark为True，则爬取数据库中标记(mark=true)的期刊概览内容，False则爬取全部期刊概览内容
        :param issn_number: issn号
        :return:
        """
        if mark:
            keywords = Periodicals.objects.filter(mark=True)[start_num:]
        elif issn_number:
            keywords = Periodicals.objects.filter(issn_number=issn_number)
        else:
            keywords = Periodicals.objects.all()[start_num:]
        count = start_num
        for i in keywords:
            count += 1
            print(count, i.issn_number, 'new->old')
            self.get_periodicals_summary(i)
            print(count, i.issn_number, 'old->new')
            self.get_periodicals_summary(i, first=False)

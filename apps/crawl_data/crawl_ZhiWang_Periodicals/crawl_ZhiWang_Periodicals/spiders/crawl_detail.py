# -*- coding: utf-8 -*-
import scrapy
from django.db.models import Q  # 数据库中用多操作
import re

from crawl_data.models import Summary, Periodicals, Detail
from items import DetailItem


class CrawlDetailSpider(scrapy.Spider):
    name = 'crawl_detail'
    header = {
        'Host': 'kns.cnki.net',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
    }
    start_urls = ['http://kns.cnki.net/']

    def start_requests(self):
        """
        控制开始
        从数据库中找出所要爬取的url
        """
        periodicals = Periodicals.objects.filter(mark=True)  # 找到标记的期刊
        summarys = Summary.objects.filter(Q(have_detail=False) & Q(source__in=periodicals))  # 标记且没有爬去过的
        print(summarys.count())
        count = 0
        for summary in summarys:
            print(count)
            count += 1
            # 去重
            # 有些文章在不同的期刊中投放了两次，导致之前爬去过，现在又来了一遍，只要将这次的summary指向之前的detail即可
            paper_id = re.search('filename=((.*?))&', summary.url).group(1)  # 文章ID Detail.detail_id
            detail = Detail.objects.filter(detail_id=paper_id)
            if detail:
                print('Duplicate')
                summary.detail = detail[0]
                summary.have_detail = True
                summary.save()
            else:
                yield scrapy.Request(url=summary.url, headers=self.header, callback=self.parse,
                                     meta={'summary': summary})

    def parse(self, response):
        """
        爬取文章的详情
        :param response:
        :return:
        """
        summary = response.meta.get('summary')
        try:
            # 有英文名字，即新版本
            date = response.css(".sourinfo a::text").extract()[2].split()[0]  # 文章的年月 Detail.detail_date
        except IndexError:
            try:
                # 没有英文名字，即旧版本
                date = response.css(".sourinfo a::text").extract()[1].split()[0]
            except IndexError:
                date = response.css(".sourinfo p::text").extract()[0].split()[0]

        paper_id = re.search('filename=((.*?))&', response.url).group(1)  # 文章ID Detail.detail_id

        authors_info = response.css('.author a::attr(onclick)').re('(\(.*\))')
        authors_dic = {}  # id:name     作者信息 Detail.authors     Authors.authors_id:Authors.authors_name
        for i in authors_info:
            author_name = i.split("','")[1]
            author_id = i.split("','")[-1].split("'")[0]
            authors_dic[author_id] = author_name

        # orgs_info = response.css('.orgn a').re('(\(.*\))')
        orgs_info = response.css('.orgn a::attr(onclick)').re(r'\((.*)\)')
        orgs_dic = {}  # id:name   单位信息 Detail.organizations    Organization.organization_id:Organization.organization_name
        for i in orgs_info:
            org_name = i.split("','")[1]
            org_id = i.split("','")[-1].split("'")[0]
            orgs_dic[org_id] = org_name

        abstract = response.xpath('//span[@id="ChDivSummary"]/text()').extract_first()  # 概要 Detail.detail_abstract

        keyword = response.xpath('//div[@class="wxBaseinfo"]').re(r'\(\'kw\'.*\)', )
        keywords = ""  # 关键字 Detail.detail_keywords
        for i in keyword:
            keywords += i.split("','")[1] + ' '

        detail_item = DetailItem()
        detail_item['detail_id'] = paper_id
        detail_item['detail_keywords'] = keywords
        detail_item['detail_abstract'] = abstract
        detail_item['detail_date'] = date
        detail_item['authors_dic'] = authors_dic
        detail_item['organizations_dic'] = orgs_dic
        detail_item['summary'] = summary

        yield detail_item

    def parse_references(self, response):
        """
        处理参考文献，提取出各项
        :param response:
        :return:
        """

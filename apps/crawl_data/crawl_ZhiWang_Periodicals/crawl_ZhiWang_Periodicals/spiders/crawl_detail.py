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
        # periodicals = Periodicals.objects.filter(mark=True)  # 找到标记的期刊
        # summarys = Summary.objects.filter(Q(have_detail=False) & Q(source__in=periodicals))  # 标记且没有爬去过的
        # print(summarys.count())
        # count = 0
        # for summary in summarys:
        #     print(count)
        #     count += 1
        #     # 去重
        #     # 有些文章在不同的期刊中投放了两次，导致之前爬去过，现在又来了一遍，只要将这次的summary指向之前的detail即可
        #     paper_id = re.search('filename=((.*?))&', summary.url).group(1)  # 文章ID Detail.detail_id
        #     detail = Detail.objects.filter(detail_id=paper_id)
        #     if detail:
        #         print('Duplicate')
        #         summary.detail = detail[0]
        #         summary.have_detail = True
        #         summary.save()
        #     else:
        #         yield scrapy.Request(url=summary.url, headers=self.header, callback=self.parse,
        #                              meta={'summary': summary})

        # 在现有数据基础上新增引用内容
        details = Detail.objects.filter(detail_id='ZJYX201710014')  # 找到标记的期刊
        print(details.count())
        count = 0
        for detail in details:
            print(count)
            count += 1
            if detail.references is None:
                references_url = 'http://kns.cnki.net/kcms/detail/frame/list.aspx?dbcode=CJFQ&filename={0}&RefType=1&page=1'.format(
                    detail.detail_id)
                yield scrapy.Request(url=references_url, headers=self.header, callback=self.parse_references,
                                     meta={'detail': detail, 'cur_page': 1})

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
        # 中国学术期刊网络出版总库
        # id = "pc_CJFQ"
        # 中国博士学位论文全文数据库
        # id = "pc_CDFD"
        # 中国优秀硕士学位论文全文数据库
        # id = "pc_CMFD"
        # 中国图书全文数据库
        # id = "pc_CBBD"
        # 国际期刊数据库
        # id = "pc_SSJD"
        # 外文题录数据库
        # id = "pc_CRLDENG"
        # 只有
        # 中国学术期刊网络出版总库
        # 中国博士学位论文全文数据库
        # 中国优秀硕士学位论文全文数据库
        # 国际期刊数据库
        # 这四个是有url的
        detail = response.meta.get('detail')
        cur_page = response.meta.get('cur_page')
        references_url = response.url.split('page=')[0] + 'page=' + str(cur_page + 1)
        pc_CJFQ = int(response.xpath('//span[@id="pc_CJFQ"]/text()').extract_first(default=0))
        pc_CDFD = int(response.xpath('//span[@id="pc_CJFQ"]/text()').extract_first(default=0))
        pc_CMFD = int(response.xpath('//span[@id="pc_CMFD"]/text()').extract_first(default=0))
        pc_CBBD = int(response.xpath('//span[@id="pc_CBBD"]/text()').extract_first(default=0))
        pc_SSJD = int(response.xpath('//span[@id="pc_SSJD"]/text()').extract_first(default=0))
        pc_CRLDENG = int(response.xpath('//span[@id="pc_CRLDENG"]/text()').extract_first(default=0))
        page = max(pc_CJFQ, pc_CDFD, pc_CMFD, pc_CBBD, pc_SSJD, pc_CRLDENG)  # 找到最大的参考文献库个数，定制翻页次数
        page = (page / 10) + 1  # 每页有10条数据
        div = response.css('.essayBox')  # 拿到所有含有文献列表的模块

        if page > cur_page:
            # 网页+1继续获取信息
            yield scrapy.Request(url=references_url, headers=self.header, callback=self.parse_references,
                                 meta={'detail': detail, 'cur_page': cur_page + 1})



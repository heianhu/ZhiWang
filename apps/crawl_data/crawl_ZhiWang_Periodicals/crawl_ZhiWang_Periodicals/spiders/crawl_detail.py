# -*- coding: utf-8 -*-
import scrapy
from django.db.models import Q  # 数据库中用多操作
import re

from crawl_data.models import Summary, Periodicals, Detail
from crawl_data.crawl_ZhiWang_Periodicals.crawl_ZhiWang_Periodicals.items import DetailItem, ReferencesCJFQItem, \
    ReferencesCMFDItem, ReferencesCDFDItem, ReferencesCBBDItem, \
    ReferencesSSJDItem, ReferencesCRLDENGItem, ReferencesItem, ReferencesCCNDItem, ReferencesCPFDItem
from crawl_data.models import ReferencesCJFQ, ReferencesCMFD, ReferencesCDFD, ReferencesCBBD, ReferencesSSJD, \
    ReferencesCRLDENG, References, ReferencesCCND, ReferencesCPFD
from .SelectData import select_detail, select_references
from settings import REFERENCES_DBNAME, INCREMENTAL_CRAWL_DETAIL


class CrawlDetailSpider(scrapy.Spider):
    _re_filename = re.compile('filename=((.*?))&')
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
        # periodicals = Periodicals.objects.filter(issn_number='1004-6577')  # 找到指定的期刊
        summarys = Summary.objects.filter(Q(have_detail=False) & Q(source__in=periodicals))  # 标记且没有爬去过的
        all_count = summarys.count()
        count = 0
        for summary in summarys:
            print(count, '/', all_count)
            count += 1
            # 去重
            # 有些文章在不同的期刊中投放了两次，导致之前爬去过，现在又来了一遍，只要将这次的summary指向之前的detail即可
            paper_id = self._re_filename.search(summary.url).group(1)  # 文章ID Detail.detail_id
            detail = Detail.objects.filter(detail_id=paper_id)
            if detail:
                # print('Duplicate')
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

        detail_item = DetailItem()
        paper_id, keywords, abstract, date, authors_dic, orgs_dic = select_detail(response=response)
        detail_item['detail_id'] = paper_id
        detail_item['detail_keywords'] = keywords
        detail_item['detail_abstract'] = abstract
        detail_item['detail_date'] = date
        detail_item['authors_dic'] = authors_dic
        detail_item['organizations_dic'] = orgs_dic
        detail_item['summary'] = summary

        yield detail_item
        detail = Detail.objects.get(Q(detail_id=paper_id) & Q(summary=summary))
        references_url = 'http://kns.cnki.net/kcms/detail/frame/list.aspx?dbcode=CJFQ&filename={0}&RefType=1&page=1'.format(
            detail.detail_id)
        references_list_dict = dict()
        for references_name in REFERENCES_DBNAME:
            references_list_dict[references_name + '_list'] = []

        yield scrapy.Request(url=references_url, headers=self.header, callback=self.parse_references,
                             meta={'detail': detail, 'cur_page': 1, 'references_list_dict': references_list_dict})

    def parse_references(self, response):
        detail = response.meta.get('detail')
        cur_page = response.meta.get('cur_page')
        references_url = response.url.split('page=')[0] + 'page=' + str(cur_page + 1)

        every_page = []  # 每种引用期刊的数量
        references_list_dict = response.meta.get('references_list_dict')
        for references_name in REFERENCES_DBNAME:
            every_page.append(
                int(response.xpath('//span[@id="pc_{}"]/text()'.format(references_name)).extract_first(default=0))
            )

        page = max(every_page)  # 找到最大的参考文献库个数，定制翻页次数
        page = (page / 10)  # 每页有10条数据

        select_references(response, **references_list_dict)

        if page > cur_page:
            # 网页+1继续获取信息
            yield scrapy.Request(url=references_url, headers=self.header, callback=self.parse_references,
                                 meta={'detail': detail, 'cur_page': cur_page + 1,
                                       'references_list_dict': references_list_dict})
        else:
            # # Debug
            # print('CJFQ_list:', CJFQ_list)
            # print('CDFD_list:', CDFD_list)
            # print('CMFD_list:', CMFD_list)
            # print('CBBD_list:', CBBD_list)
            # print('SSJD_list:', SSJD_list)
            # print('CRLDENG_list:', CRLDENG_list)
            # print('CCND_list:', CCND_list)
            # print('CPFD_list:', CPFD_list)

            if sum(len(x) for x in references_list_dict.values()) == 0:
                references = References.objects.filter(id=76438)[0]
            else:
                references = References()
                for references_name in REFERENCES_DBNAME:
                    references.__setattr__(references_name, ' '.join(references_list_dict[references_name + '_list']))
                references.save()
            detail.references = references
            detail.save()

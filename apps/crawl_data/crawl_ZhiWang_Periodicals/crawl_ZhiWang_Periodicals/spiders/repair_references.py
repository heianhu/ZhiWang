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
from .SelectData import select_references
from settings import REFERENCES_DBNAME


class RepairReferencesSpider(scrapy.Spider):
    _re_filename = re.compile('filename=((.*?))&')
    name = 'repair_references'
    header = {
        'Host': 'kns.cnki.net',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
    }
    start_urls = ['http://kns.cnki.net/']

    def start_requests(self):
        """
        控制开始
        从数据库中找出所有的引用均为空的参考文献id
        """
        references = References.objects.filter(CJFQ='', CDFD='', CMFD='', CBBD='', SSJD='', CRLDENG='', CCND='',
                                               CPFD='')  # 找到全是空白的数据
        details = Detail.objects.filter(references__in=references)
        # details = Detail.objects.filter(references=None)
        print(details.count())
        count = 1
        for detail in details:
            print(count)
            count += 1
            references_url = \
                'http://kns.cnki.net/kcms/detail/frame/list.aspx?dbcode=CJFQ&filename={0}&RefType=1&page=1' \
                    .format(detail.detail_id)
            references_list_dict = dict()
            for references_name in REFERENCES_DBNAME:
                references_list_dict[references_name + '_list'] = []
            yield scrapy.Request(url=references_url, headers=self.header, callback=self.parse,
                                 meta={'detail': detail, 'cur_page': 1, 'references_list_dict': references_list_dict})

    def parse(self, response):
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

        for item in select_references(response, **references_list_dict):
            yield item

        if page > cur_page:
            # 网页+1继续获取信息
            yield scrapy.Request(url=references_url, headers=self.header, callback=self.parse,
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
                detail.references = References.objects.filter(id=76438)[0]
            else:
                if detail.references.id == 76438:
                    references = References()
                    for references_name in REFERENCES_DBNAME:
                        references.__setattr__(references_name,
                                               ' '.join(references_list_dict[references_name + '_list'])
                                               )
                    references.save()
                    detail.references = references
                else:
                    for references_name in REFERENCES_DBNAME:
                        detail.references.__setattr__(references_name,
                                                      ' '.join(references_list_dict[references_name + '_list'])
                                                      )
                    detail.references.save()
            detail.save()

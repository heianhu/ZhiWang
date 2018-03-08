# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_djangoitem import DjangoItem
from crawl_data.models import Detail, Summary, Authors, Organization, ReferencesCJFQ, ReferencesCMFD, ReferencesCDFD, \
    ReferencesCBBD, ReferencesSSJD, ReferencesCRLDENG, References, ReferencesCCND


class DetailItem(scrapy.Item):
    detail_id = scrapy.Field()  # 论文ID
    detail_keywords = scrapy.Field()  # 关键字
    detail_abstract = scrapy.Field()  # 摘要
    detail_date = scrapy.Field()  # 文章年月
    authors_dic = scrapy.Field()
    organizations_dic = scrapy.Field()
    summary = scrapy.Field()
    references = scrapy.Field()

    def processing_authors(self):
        authors_database_id = []
        for authors_id, authors_name in self.authors_dic.items():
            # 处理作者信息
            if authors_id == '':
                # ID为空的时候
                author = Authors()
                author.authors_id = ''
                author.authors_name = authors_name
                author.save()
                authors_database_id.append(authors_name)
            elif Authors.objects.filter(authors_id=authors_id) and authors_id != '':
                # 不为空的ID已经在数据库中了
                authors_database_id.append(str(Authors.objects.get(authors_id=authors_id).id))
                continue
            else:
                author = Authors()
                if len(authors_id) >= 20:
                    # 当一个人存储了一堆人的ID时候，则舍弃这堆ID
                    author.authors_id = ''
                    author.authors_name = authors_name
                    author.save()
                    authors_database_id.append(authors_name)
                else:
                    author.authors_id = authors_id
                    author.authors_name = authors_name
                    author.save()
                    authors_database_id.append(str(Authors.objects.filter(authors_id=authors_id)[0].id))
        return authors_database_id

    def processing_organizations(self):
        organization_database_id = []
        for organization_id, organization_name in self.organizations_dic.items():
            # 处理组织信息
            if organization_id == '':
                # ID为空的时候
                organization = Organization()
                organization.organization_id = ''
                organization.organization_name = organization_name
                organization.save()
                organization_database_id.append(organization_name)
            elif Organization.objects.filter(organization_id=organization_id):
                # 不为空的ID已经在数据库中了
                organization_database_id.append(str(Organization.objects.get(organization_id=organization_id).id))
                continue
            else:
                organization = Organization()
                if len(organization_id) >= 20:
                    # 当一个人存储了一堆人的ID时候，则舍弃这堆ID
                    organization.organization_id = ''
                    organization.organization_name = organization_name
                    organization.save()
                    organization_database_id.append(organization_name)
                else:
                    organization.organization_id = organization_id
                    organization.organization_name = organization_name
                    organization.save()
                    organization_database_id.append(
                        str(Organization.objects.filter(organization_id=organization_id)[0].id))
        return organization_database_id

    def insert_database(self):
        authors_database_id = self.processing_authors()
        organization_database_id = self.processing_organizations()

        detail = Detail()
        detail.detail_id = self.detail_id
        detail.detail_keywords = self.detail_keywords
        if not self.detail_abstract:
            detail.detail_abstract = ''
        else:
            detail.detail_abstract = self.detail_abstract

        detail.detail_date = self.detail_date
        detail.authors = ' '.join(authors_database_id)
        detail.organizations = ' '.join(organization_database_id)
        detail.save()
        self.summary.detail = detail
        self.summary.have_detail = True
        self.summary.save()


class ReferencesItem(scrapy.Item):
    CJFQ = scrapy.Field()
    CDFD = scrapy.Field()
    CMFD = scrapy.Field()
    CBBD = scrapy.Field()
    SSJD = scrapy.Field()
    CRLDENG = scrapy.Field()

    def insert_database(self):
        references = References()
        references.CJFQ = ' '.join(self['CJFQ'])
        references.CDFD = ' '.join(self['CDFD'])
        references.CMFD = ' '.join(self['CMFD'])
        references.CBBD = ' '.join(self['CBBD'])
        references.SSJD = ' '.join(self['SSJD'])
        references.CRLDENG = ' '.join(self['CRLDENG'])
        references.save()


class ReferencesCJFQItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    authors = scrapy.Field()
    source = scrapy.Field()
    issuing_time = scrapy.Field()

    def insert_database(self):
        CJFQ = ReferencesCJFQ()
        CJFQ.url = self['url']
        CJFQ.title = self['title']
        CJFQ.authors = self['authors']
        CJFQ.source = self['source']
        CJFQ.issuing_time = self['issuing_time']
        CJFQ.save()


class ReferencesCDFDItem(ReferencesCJFQItem):
    def insert_database(self):
        CDFD = ReferencesCDFD()
        CDFD.url = self['url']
        CDFD.title = self['title']
        CDFD.authors = self['authors']
        CDFD.source = self['source']
        CDFD.issuing_time = self['issuing_time']
        CDFD.save()


class ReferencesCMFDItem(ReferencesCJFQItem):
    def insert_database(self):
        CMFD = ReferencesCMFD()
        CMFD.url = self['url']
        CMFD.title = self['title']
        CMFD.authors = self['authors']
        CMFD.source = self['source']
        CMFD.issuing_time = self['issuing_time']
        CMFD.save()


class ReferencesCBBDItem(scrapy.Item):
    """
    中国图书全文数据库
    """
    title = scrapy.Field()
    authors = scrapy.Field()
    source = scrapy.Field()
    issuing_time = scrapy.Field()

    def insert_database(self):
        CBBD = ReferencesCBBD()
        CBBD.title = self['title']
        CBBD.authors = self['authors']
        CBBD.source = self['source']
        CBBD.issuing_time = self['issuing_time']
        CBBD.save()


class ReferencesSSJDItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    info = scrapy.Field()
    issuing_time = scrapy.Field()

    def insert_database(self):
        SSJD = ReferencesSSJD()
        SSJD.url = self['url']
        SSJD.title = self['title']
        SSJD.info = self['info']
        SSJD.issuing_time = self['issuing_time']
        SSJD.save()


class ReferencesCRLDENGItem(scrapy.Item):
    title = scrapy.Field()
    info = scrapy.Field()
    issuing_time = scrapy.Field()

    def insert_database(self):
        CRLDENG = ReferencesCRLDENG()
        CRLDENG.title = self['title']
        CRLDENG.info = self['info']
        CRLDENG.issuing_time = self['issuing_time']
        CRLDENG.save()


class ReferencesCCNDItem(ReferencesCJFQItem):
    def insert_database(self):
        CCND = ReferencesCCND()
        CCND.url = self['url']
        CCND.title = self['title']
        CCND.authors = self['authors']
        CCND.source = self['source']
        CCND.issuing_time = self['issuing_time']
        CCND.save()

# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from crawl_cnki.models import Article, Periodical, Author, Article_Author, Organization, Article_Organization, \
    References, Article_References
from w3lib.html import remove_tags
# import django.db.utils.IntegrityError
# import pymysql.err.IntegrityError
from django.db.utils import IntegrityError as djIntegrityError
from pymysql.err import IntegrityError as pyIntegrityError

import re

from .utils import *


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class ArticleItem(scrapy.Item):
    # 文章主体部分
    id = scrapy.Field()
    url = scrapy.Field()
    filename = scrapy.Field(
        input_processor=MapCompose(get_filename_from_url)
    )
    title = scrapy.Field()
    periodicals = scrapy.Field()
    issuing_time = scrapy.Field(
        input_processor=MapCompose(get_issuing_time)
    )
    article = scrapy.Field()
    remark = scrapy.Field(
        output_processor=parse_article
    )

    # 作者部分
    authors_id = scrapy.Field(
        input_processor=MapCompose(remove_space, get_authors_str),
        output_processor=get_authors_id
    )
    authors_name = scrapy.Field(
        input_processor=MapCompose(remove_space, get_authors_str),
        output_processor=get_authors_name
    )

    # 机构部分
    org_id = scrapy.Field(
        input_processor=MapCompose(remove_space, get_authors_str),
        output_processor=get_authors_id
    )
    org_name = scrapy.Field(
        input_processor=MapCompose(remove_space, get_authors_str),
        output_processor=get_authors_name
    )

    def save_to_mysql_article(self):

        # article = Article()
        article = self['article']
        article.keywords = self['remark'].get('keywords', '')
        article.abstract = self['remark'].get('abstract', '')
        article.DOI = self['remark'].get('DOI', '')
        article.remark = self.get('remark', '')

        try:
            article.save()
            # 文章已经存在
        except djIntegrityError or pyIntegrityError:
            article = Article.objects.get(filename=self.get('filename', ''))

        return article

    def save_to_mysql_author(self):
        authors = []
        for author_id, name in zip(self.get('authors_id', ''), self.get('authors_name', '')):
            author = Author()
            author.authors_id = author_id
            author.authors_name = name
            try:
                author.save()
                # 已经存在
            except djIntegrityError or pyIntegrityError:

                author = Author.objects.get(authors_id=author_id, authors_name=name)
            authors.append(author)
        return authors

    def save_to_mysql_org(self):
        orgs = []
        for org_id, name in zip(self.get('org_id', ''), self.get('org_name', '')):
            org = Organization()
            org.organization_id = org_id
            org.organization_name = name
            try:
                org.save()
                # 已经存在
            except djIntegrityError or pyIntegrityError:
                org = Organization.objects.get(organization_id=org_id, organization_name=name)
            orgs.append(org)
        return orgs

    def save_to_mysql_article_author(self, article, authors):
        """
        文章-作者 的m2m表
        :param article:单片文章的id
        :param authors: 文章对应的多个作者id 列表
        :return:
        """
        for author in authors:
            article_author = Article_Author()
            # article_author.article_id = Article.objects.get(id=article)
            # article_author.author_id = Author.objects.get(id=author)
            article_author.article = article
            article_author.author = author
            try:
                article_author.save()
            # 如果已经存在
            except djIntegrityError or pyIntegrityError:
                pass

    def save_to_mysql_article_org(self, article, orgs):
        """
        文章-机构 的m2m表
        :param article:单片文章的id
        :param orgs: 文章对应的多个机构id 列表
        :return:
        """
        for org in orgs:
            article_org = Article_Organization()
            # article_author.article_id = Article.objects.get(id=article)
            # article_author.author_id = Author.objects.get(id=author)
            article_org.article = article
            article_org.organization = org
            try:
                article_org.save()
            # 如果已经存在
            except djIntegrityError or pyIntegrityError:
                pass


class ReferenceItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class ReferenceItem(scrapy.Item):
    article = scrapy.Field()
    remark = scrapy.Field(
        output_processor=get_value
    )
    info = scrapy.Field(
        output_processor=CleanRefers()
    )

    def save_to_mysql_refer(self):
        article = self.get('article', '')
        refer = References()

        refer.url = self['info'].get('url', '')

        # 如果获取到的title为空字符串(从remark解析失败)，则填入remark的前255字符串。因为refer的title是要求unique的
        refer.title = self['info'].get('title', '') or self.get('remark', '')[:255]
        refer.authors = self['info'].get('author', '')
        refer.source = self['info'].get('source', '')
        refer.dbID = self['info'].get('dbID', '')
        refer.issuing_time = self['info'].get('issuing_time', '')
        refer.remark = self.get('remark', '')
        try:
            refer.save()
            # 已经存在
        except djIntegrityError or pyIntegrityError:
            print(refer.title)
            refer = References.objects.get(title=self['info'].get('title', ''), issuing_time =self['info'].get('issuing_time', ''), dbID=self['info'].get('dbID', ''))
        return article, refer

    def save_to_mysql_article_refer(self, article, refer):
        article_refer = Article_References()
        article_refer.article = article
        article_refer.references = refer
        try:
            article_refer.save()
        # 如果已经存在
        except djIntegrityError or pyIntegrityError:
            pass

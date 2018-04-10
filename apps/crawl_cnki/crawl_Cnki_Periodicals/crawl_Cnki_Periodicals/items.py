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
from django.db.utils import IntegrityError
import re

from .utils import *


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class ArticleItem(scrapy.Item):
    # 文章主题部分
    id = scrapy.Field()
    url = scrapy.Field()
    filename = scrapy.Field(
        input_processor=MapCompose(get_filename_from_url)
    )
    title = scrapy.Field()
    periodicals = scrapy.Field()
    issuing_time = scrapy.Field()
    cited = scrapy.Field()
    keywords = scrapy.Field()
    abstract = scrapy.Field()
    DOI = scrapy.Field()
    remark = scrapy.Field()

    def save_to_mysql_article(self):

        article = Article()
        article.filename = self.get('filename', '')
        article.title = self.get('title', '')
        article.url = self.get('url', '')
        periodicals = self.get('periodicals', '')
        article.periodicals = Periodical.objects.get(id=periodicals)
        # article.issuing_time = self.get('issuing_time', '')
        article.issuing_time = '2017-04-17'
        article.cited = self.get('cited', 0)
        article.keywords = self.get('keywords', '')
        article.abstract = self.get('abstract', '')
        article.DOI = self.get('DOI', '')
        article.remark = self.get('remark', '')

        try:
            article.save()
            # 文章已经存在
        except IntegrityError as e:
            article = Article.objects.get(filename=self.get('filename', ''))

        return article

    # 作者部分
    authors_id = scrapy.Field(
        input_processor=MapCompose(get_authors_str),
        output_processor=get_authors_id

    )
    authors_name = scrapy.Field(
        input_processor=MapCompose(get_authors_str),
        output_processor=(get_authors_name)
    )

    def save_to_mysql_author(self):
        authors = []
        for author_id, name in zip(self.get('authors_id', ''), self.get('authors_name', '')):
            author = Author()
            author.authors_id = author_id
            author.authors_name = name
            try:
                author.save()
                # 已经存在
            except IntegrityError as e:
                author = Article.objects.get(authors_id=author_id)
            authors.append(author)
        return authors

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
            article_author.save()

    # 机构部分
    org_id = scrapy.Field(
        input_processor=MapCompose(get_authors_str),
        output_processor=get_authors_id
    )
    org_name = scrapy.Field(
        input_processor=MapCompose(get_authors_str),
        output_processor=(get_authors_name)
    )

    def save_to_mysql_org(self):
        orgs = []
        for org_id, name in zip(self.get('org_id', ''), self.get('org_name', '')):
            org = Organization()
            org.organization_id = org_id
            org.organization_name = name
            try:
                org.save()
                # 已经存在
            except IntegrityError as e:
                org = Article.objects.get(organization_id=org_id)
            orgs.append(org)
        return orgs

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
            article_org.save()


class ReferenceItemLoader(ItemLoader):
    pass
    # default_output_processor = TakeFirst()


class ReferenceItem(scrapy.Item):
    article = scrapy.Field()
    url = scrapy.Field(
        input_processor=MapCompose(get_url_from_refer)
    )
    title = scrapy.Field(
        input_processor=MapCompose(get_title_from_refer)
    )
    authors = scrapy.Field()
    source = scrapy.Field()
    issuing_time = scrapy.Field()
    remark = scrapy.Field(
        input_processor=MapCompose(clean_refers)
    )

    # TODO
    def save_to_mysql_refer(self):
        article = Article.objects.get(filename=self.get('article', ''))
        refer = References()
        # refer.url = self.get('url', '')
        # refer.title = self.get('title', '')
        # refer.authors = self.get('authors', '')
        # refer.source = self.get('source', '')
        # refer.issuing_time = self.get('issuing_time', '')
        refer.url = ''
        refer.title = ''
        refer.authors = ''
        refer.source = ''
        refer.issuing_time = ''
        refer.remark = self.get('remark', '')
        try:
            refer.save()
            # 已经存在
        except IntegrityError as e:
            refer = References.objects.get(title=self.get('title', ''))
        return article, refer

    def save_to_mysql_article_refer(self, article, refer):
        article_refer = Article_References()
        article_refer.article = article
        article_refer.references = refer
        article_refer.save()

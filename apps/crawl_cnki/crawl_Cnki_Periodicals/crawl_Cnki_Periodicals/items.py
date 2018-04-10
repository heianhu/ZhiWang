# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from crawl_cnki.models import Article, Periodical, Author, Article_Author, Organization, Article_Organization, References, Article_References
from w3lib.html import remove_tags
from django.db.utils import IntegrityError

import re


def get_filename_from_url(url):
    """
    从url中提取filename
    :param url: 'http://...&filename=JAXK201803001&R...'
    :return: 'JAXK201803001'
    """
    filename = re.search('filename=((.*?))&', url).group(1)
    return filename

def get_authors_str(value):
    """
    从html中提取作者字信息
    :param value:
    :return:  "('au','张三','10086'),('au','张四','10087')"
    """
    authors = re.findall('TurnPageToKnet\((.*?)\)', value)
    return authors

def get_authors_name(authors):
    """
    从str中提取作者姓名列表
    :param authors: "('au','张三','10086'),('au','张四','10087')"
    :return: ['张三','张四']
    """
    author_name = []
    for author in authors:
        author_name.append(author.split("\',\'")[1])
    return author_name

def get_authors_id(authors):
    """
    从str中提取作者id列表
    :param authors:  "('au','张三','10086'),('au','张四','10087')"
    :return: ['10086','10087']
    """
    author_id = []
    for author in authors:
        author_id.append(author.split("\',\'")[-1][:-1])
    return author_id

def get_issuing_time(value):
    """
    提取格式化的日期
    :param value:
    :return:
    """
    match = re.search(r'([\d]+-[\d]+-[\d]+)', value)
    try:
        date = match.group(1)
    except Exception as e:
        print(e)
        date = '1970-1-1'
    return date

def parse_article(value):
    """
    :param value: 由多个<p>组成的列表
    :return:
    """
    # 按<p>中的<label>中的id分别解析不通内容
    info = {'keywords': '', 'fund': '', 'catalog': '', 'abstract': '', 'DOI': ''}

    def clean_abstract(p):
        match = re.search(r'ChDivSummary">(.*?)</span>', p)
        info['abstract'] = match.group(1)

    def clean_keyword(p):
        keywords = re.findall(r'TurnPageToKnet\(\'kw\',\'(.*?)\',\'[\d]*\'\)', p)
        info['keywords'] = keywords

    def clean_fund(p):
        fund = re.findall(r'TurnPageToKnet\(\'fu\',\'(.*?)\',\'[\d]*\'\)', p)
        info['fund'] = fund

    def clean_DOI(p):
        match = re.search(r'</label>(.*?)</p>', p)
        info['DOI'] = match.group(1)

    for p in value:
        p = re.sub('\n|\r|  ', '', p)
        try:
            if 'catalog_ABSTRACT' in p:
                clean_abstract(p)
            elif 'catalog_KEYWORD' in p:
                clean_keyword(p)
            elif 'catalog_FUND' in p:
                clean_fund(p)
            elif 'catalog_ZCDOI' in p:
                clean_DOI(p)
        except Exception as e:
            print(e)
    return info


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
    remark = scrapy.Field(
        output_processor=parse_article
    )

    # 作者部分
    authors_id = scrapy.Field(
        input_processor=MapCompose(get_authors_str),
        output_processor=get_authors_id
    )
    authors_name = scrapy.Field(
        input_processor=MapCompose(get_authors_str),
        output_processor=(get_authors_name)
    )

    # 机构部分
    org_id = scrapy.Field(
        input_processor=MapCompose(get_authors_str),
        output_processor=get_authors_id
    )
    org_name = scrapy.Field(
        input_processor=MapCompose(get_authors_str),
        output_processor=(get_authors_name)
    )


    def save_to_mysql_article(self):

        article = Article()
        article.filename = self.get('filename', '')
        article.title = self.get('title', '')
        article.url = self.get('url', '')
        periodicals = self.get('periodicals', '')
        article.periodicals = Periodical.objects.get(id=periodicals)
        article.issuing_time = self.get('issuing_time', '')
        article.cited = self.get('cited', 0)
        article.keywords = self['remark'].get('keywords', '')
        article.abstract = self['remark'].get('abstract', '')
        article.DOI = self['remark'].get('DOI', '')
        article.remark = self.get('remark', '')

        try:
            article.save()
            # 文章已经存在
        except IntegrityError as e:
            article = Article.objects.get(filename=self.get('filename', ''))

        return article

    def save_to_mysql_author(self):
        authors = []
        for author_id, name in zip(self.get('authors_id', ''), self.get('authors_name','')):
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




class CleanRefers(object):
    """
    清洗refer类，当作函数调用，作为Item中output_processor的参数
    """
    def __call__(self, refer):
        self.info = {'url': '', 'title': '', 'author': '', 'source': '', 'issuing_time': ''}
        """
        :param refer: ['refer_dbcode','refer_str']
        :return: refer_info
        """
        source = refer[0]  # 数据库代码
        refer = refer[1]  # 参考文献内容
        # 先统一去除一些无用的字符
        refer = re.sub('\n|\r|  ', '', refer)
        # 根据数据库代码调用相应的清洗函数
        clean_func = getattr(self, 'clean_{}'.format(source))
        try:
            self.info = clean_func(refer)
        # 捕获函数中正则匹配的异常
        except Exception as e:
            print(e)

        return self.info

    def clean_CJFQ(self, refer):
        match = re.search(r'href="(.*?)">(.*?)</a>(.*?)<a(.*?)>(.*?)</a>(.*?)<a(.*?)>(.*?)</a>', refer)

        self.info['url'] = match.group(1)
        self.info['title'] = match.group(2)
        self.info['author'] = match.group(3)
        self.info['source'] = match.group(5)
        self.info['issuing_time'] = match.group(8)

        return self.info

    def clean_CDFD(self, refer):
        match = re.search(r'href="(.*?)">(.*?)</a>(.*?)<a(.*?)>(.*?)</a>(.*?)([\d]{4})', refer)

        self.info['url'] = match.group(1)
        self.info['title'] = match.group(2)
        self.info['author'] = match.group(3)
        self.info['source'] = match.group(5)
        self.info['issuing_time'] = match.group(7)

        return self.info

    def clean_CMFD(self, refer):
        match = re.search(r'href="(.*?)">(.*?)</a>(.*?)<a(.*?)>(.*?)</a>(.*?)([\d]{4})', refer)

        self.info['url'] = match.group(1)
        self.info['title'] = match.group(2)
        self.info['author'] = match.group(3)
        self.info['source'] = match.group(5)
        self.info['issuing_time'] = match.group(7)

        return self.info

    def clean_CBBD(self, refer):
        match = re.search(r'(.*?)\.(.*?),(.*?),.*?([\d]{4})', refer)

        self.info['title'] = match.group(1)
        self.info['source'] = match.group(2)
        self.info['author'] = match.group(3)
        self.info['issuing_time'] = match.group(4)

        return self.info

    def clean_SSJD(self, refer):
        match = re.search(r'href="([\s\S]*?)">(.*?)</a>([\s\S]*?)([\d\(\)]+)', refer)

        self.info['url'] = match.group(1)
        self.info['title'] = match.group(2)
        self.info['author'] = match.group(3)
        self.info['issuing_time'] = match.group(4)

        return self.info

    def clean_CRLDENG(self, refer):
        match = re.search(r'<a([\s\S]*?)>(.*?)</a>([\s\S]*?)([\d]{4})', refer)
        self.info['title'] = match.group(2)
        self.info['author'] = match.group(3)
        self.info['issuing_time'] = match.group(4)
        return self.info

    def clean_CCND(self, refer):
        match = re.search(r'<a([\s\S]*?)>(.*?)</a>([\s\S]*?)\.(.*?)\.([\d]{4}\([\d+]\))', refer)

        self.info['url'] = match.group(1)
        self.info['title'] = match.group(2)
        self.info['author'] = match.group(3)
        self.info['source'] = match.group(4)
        self.info['issuing_time'] = match.group(5)

        return self.info

    # TODO 没找到此数据库
    def clean_CPFD(self, refer):
        pass

        return self.info

class ReferenceItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

class ReferenceItem(scrapy.Item):
    article = scrapy.Field()
    remark = scrapy.Field(
        output_processor=CleanRefers()
    )

    def save_to_mysql_refer(self):
        article = Article.objects.get(filename=self.get('article', ''))
        refer = References()

        refer.url = self['remark'].get('url', '')
        refer.title = self['remark'].get('title', '')
        refer.authors = self['remark'].get('author', '')
        refer.source = self['remark'].get('source', '')
        refer.issuing_time = self['remark'].get('issuing_time', '')
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





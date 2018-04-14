#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'
import re

RE_FILENAME = re.compile(r'filename=((.*?))&')
RE_AUTHORS = re.compile('TurnPageToKnet\((.*?)\);?">')
RE_REFER_URL = re.compile(r'href=\"(.*?)\">')
RE_REFER_TITLE = re.compile(r'<a(.*?)>(.*?)</a>')

def get_value(value):
    return value

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
        keywords = ';'.join(keywords)
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


def get_filename_from_url(url):
    """
    从url中提取filename
    :param url: 'http://...&filename=JAXK201803001&R...'
    :return: 'JAXK201803001'
    """
    filename = RE_FILENAME.search(url).group(1)
    return filename


def get_authors_str(value):
    """
    从html中提取作者字信息
    :param value:
    :return:  "('au','张三','10086'),('au','张四','10087')"
    """
    authors = RE_AUTHORS.findall(value)
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

def remove_space(value):
    value =  re.sub('\n|\r|  |&amp|;nbsp', '', value)
    return value


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
        if '</a>' in refer:
            match = re.search(r'href="(.*?)">(.*?)</a>(.*?)<a(.*?)>(.*?)</a>(.*?)<a(.*?)>(.*?)</a>', refer)

            self.info['url'] = match.group(1)
            self.info['title'] = match.group(2)
            self.info['author'] = match.group(3)
            self.info['source'] = match.group(5)
            self.info['issuing_time'] = match.group(8)
        else:
            # '白血病微环境对正常造血的影响[J]. 宫跃敏,程涛.&amp;nbsp&amp;nbsp中华血液学杂志.2015(01)'
            match = re.search(r'(.*?)\.(.*?)\.(.*?)\.(.*?)', refer)
            self.info['title'] = match.group(1)
            self.info['author'] = match.group(2)
            self.info['source'] = match.group(3)
            self.info['issuing_time'] = match.group(4)
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
        if '</a>' in refer:
            """<a onclick="OpenCRLDENG('Association of3its');">ality traits</a>. Yang H,Xu Z Y,Lei M G,et al. Journal of Applied Genetics. """
            match = re.search(r'<a([\s\S]*?)>(.*?)</a>([\s\S]*)', refer)
            self.info['title'] = match.group(2)
            self.info['author'] = match.group(3)
        else:
            # ['CRLDENG', ' Arciero. International Journal of Biological Markers\r\n        . 2003']
            match = re.search(r'([\s\S]*)\.[\s]?([\d]*)', refer)
            self.info['title'] = match.group(1)
            self.info['issuing_time'] = match.group(2)

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


USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1" \
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11", \
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6", \
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6", \
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1", \
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5", \
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5", \
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3", \
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"

]


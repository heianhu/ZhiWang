#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'
import re
from .RegularExpressions import *
import logging
def get_value(value):
    return value


def get_issuing_time(value):
    """
    提取格式化的日期
    :param value:
    :return:
    """
    match = RE_ISSUING_TIME.search(value)
    try:
        date = match.group(1)
    except Exception as e:
        print('时间解析错误', e)
        print('value:', value)

        msg = '时间解析错误: {}\nvalue: {}'.format(e, value)
        logging.warning(msg)

        date = '1970-1-1'
    if '/' in date:
        date = date.replace('/', '-')
    return date


def parse_article(value):
    """
    :param value: 由多个<p>组成的列表
    :return:
    """
    # 按<p>中的<label>中的id分别解析不通内容
    info = {'keywords': '', 'fund': '', 'catalog': '', 'abstract': '', 'DOI': ''}

    def clean_abstract(p):
        match = RE_clean_abstract.search(p)
        info['abstract'] = match.group(1)

    def clean_keyword(p):
        keywords = RE_clean_keyword.findall(p)
        keywords = ';'.join(keywords)
        info['keywords'] = keywords

    def clean_fund(p):
        fund = RE_clean_fund.findall(p)
        info['fund'] = fund

    def clean_DOI(p):
        match = RE_clean_DOI.search(p)
        info['DOI'] = match.group(1)

    for p in value:
        p = RE_remove_space.sub('', p)
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
            print('文章解析错误', e)
            print('p:', p)
            msg = '文章解析错误: {}\np: {}'.format(e, p)
            logging.warning(msg)
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
        author_name.append(author.split("\',\'")[1][:255])
    return author_name


def get_authors_id(authors):
    """
    从str中提取作者id列表
    :param authors:  "('au','张三','10086'),('au','张四','10087')"
    :return: ['10086','10087']
    """
    author_id = []
    for author in authors:
        id = author.split("\',\'")[-1][:-1]
        id = id.split(';')
        author_id += id
    return author_id


def remove_space(value):
    return RE_remove_space.sub('', value)


class CleanRefers(object):
    """
    清洗refer类，当作函数调用，作为Item中output_processor的参数
    """

    def __call__(self, refer):
        self.info = {'url': '', 'title': '', 'author': '', 'source': '', 'dbID': '', 'issuing_time': ''}
        """
        :param refer: ['refer_dbcode','refer_str']
        :return: refer_info
        """
        refer_source = refer[0]  # 数据库代码
        self.info['dbID'] = refer_source
        refer_content = refer[1]  # 参考文献内容
        # 先统一去除一些无用的字符
        refer_content = RE_remove_space.sub('', refer_content)
        # 根据数据库代码调用相应的清洗函数
        clean_func = getattr(self, 'clean_{}'.format(refer_source))
        try:
            self.info = clean_func(refer_content)
            # 截取前255个字符以能够插入数据库
            self.info['title'] = self.info['title'][:255]
            self.info['author'] = self.info['author'][:255]
        # 捕获函数中正则匹配的异常
        except Exception as e:
            msg = 'refer解析错误: {}\nrefer: {}'.format(e, refer)
            print(msg)
            logging.warning(msg)
        return self.info

    def clean_CJFQ(self, refer):
        if '</a>' in refer:
            match = RE_clean_CJFQ.search(refer)

            self.info['url'] = match.group(1)
            self.info['title'] = match.group(2)
            self.info['author'] = match.group(3)
            self.info['source'] = match.group(5)
            self.info['issuing_time'] = match.group(8)
        else:
            content = refer.split('.')
            # 有作者
            # '白血病微环境对正常造血的影响[J]. 宫跃敏,程涛.&amp;nbsp&amp;nbsp中华血液学杂志.2015(01)'
            if len(content) == 4:
                self.info['title'] = content[0]
                self.info['author'] = content[1]
                self.info['source'] = content[2]
                self.info['issuing_time'] = content[3]
            # 没有作者
            # '补好真理标准讨论这一课教育问题要来一次大讨论[J].教育研究.1979(04)'
            elif len(content) == 3:

                self.info['title'] = content[0]
                self.info['source'] = content[1]
                self.info['issuing_time'] = content[2]
        return self.info

    def clean_CDFD(self, refer):
        # 有2个</a>
        if len(re.findall('</a>', refer)) == 2:
            match = RE_clean_CDFD.search(refer)
            self.info['url'] = match.group(1)
            self.info['title'] = match.group(2)
            self.info['author'] = match.group(3)
            self.info['source'] = match.group(5)
            self.info['issuing_time'] = match.group(7)
        elif len(re.findall('</a>', refer)) == 1:
            match = RE_clean_CDFD_else.search(refer)
            # '<a target="kcmstarget" href="/kcms/detail/detail.aspx?filename=2009141782.nh&amp;dbcode=CDFD&amp;dbname=CDFD2009&amp;v=">社会资本与大学发展研究</a>[D]. 侯志军. 2008'
            self.info['url'] = match.group(1)
            self.info['title'] = match.group(2)
            self.info['author'] = match.group(3)
            self.info['issuing_time'] = match.group(4)

        return self.info

    def clean_CMFD(self, refer):
        # 有2个</a>
        if len(re.findall('</a>', refer)) == 2:
            match = RE_clean_CMFD.search(refer)
            self.info['url'] = match.group(1)
            self.info['title'] = match.group(2)
            self.info['author'] = match.group(3)
            self.info['source'] = match.group(5)
            self.info['issuing_time'] = match.group(7)
        elif len(re.findall('</a>', refer)) == 1:
            # '<a target="kcmstarget" href="/kcms/detail/detail.aspx?filename=1015027968.nh;dbcode=CMFD;dbname=CMFD2015;v=">基于LabVIEW的涡轮增压器测试台上位机开发</a>[D]. 张力. 2014'
            match = RE_clean_CMFD_else.search(refer)
            self.info['url'] = match.group(1)
            self.info['title'] = match.group(2)
            self.info['author'] = match.group(3)
            self.info['issuing_time'] = match.group(4)
        return self.info

    def clean_CBBD(self, refer):

        # '大学的理想[M].浙江教育出版社,(英)约翰·亨利·纽曼(JohnHenryNewman)著, 2001'
        # '西洋教育通史[M].商务印书馆,雷通群 著, '
        match = RE_clean_CBBD.search(refer)

        self.info['title'] = match.group(1)
        self.info['source'] = match.group(2)
        self.info['author'] = match.group(3)
        self.info['issuing_time'] = match.group(4)

        return self.info

    def clean_SSJD(self, refer):
        match = RE_clean_SSJD.search(refer)

        self.info['url'] = match.group(1)
        self.info['title'] = match.group(2)
        self.info['author'] = match.group(3)
        self.info['issuing_time'] = match.group(4)

        return self.info

    def clean_CRLDENG(self, refer):
        if '</a>' in refer:
            """<a onclick="OpenCRLDENG('Association of3its');">ality traits</a>. Yang H,Xu Z Y,Lei M G,et al. Journal of Applied Genetics. """
            match = RE_clean_CRLDENG.search(refer)
            self.info['title'] = match.group(2)
            self.info['author'] = match.group(3)
        else:
            # ['CRLDENG', ' Arciero. International Journal of Biological Markers\r\n        . 2003']
            match = RE_clean_CRLDENG_else.search(refer)
            self.info['title'] = match.group(1)
            self.info['issuing_time'] = match.group(2)

        return self.info

    def clean_CCND(self, refer):

        # '<a target="kcmstarget" href="/kcms/detail/detail.aspx?filename=CJYB20031224ZZ18;dbcode=CCND;dbname=ccnd2003;v=">专科学校升格要不要降温</a>[N].唐景莉.中国教育报.2003'
        match = RE_clean_CCND.search(refer)

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

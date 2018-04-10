#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'
import re

RE_FILENAME = re.compile(r'filename=((.*?))&')
RE_AUTHORS = re.compile('TurnPageToKnet\((.*?)\)')
RE_REFER_URL = re.compile(r'href=\"(.*?)\">')
RE_REFER_TITLE = re.compile(r'<a(.*?)>(.*?)</a>')


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


# TODO
def clean_refers(value):
    return value


# TODO
def get_url_from_refer(refer):
    match = RE_REFER_URL.search(refer)
    if match:
        url = match.group(1).replace('&amp;', '&')
        url = 'http://kns.cnki.net/' + url
        return url
    else:
        return ''


# TODO
def get_title_from_refer(refer):
    title = ''
    # 带超链接
    if '</a>' in refer:
        match = RE_REFER_TITLE.search(refer)
        if match:
            title = match.group(2)
    # 不带超链接
    else:
        pass
    return title


# TODO
def get_author_from_refer(refer):
    return refer

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'
import re

RE_FILENAME = re.compile(r'filename=((.*?))&')
RE_AUTHORS = re.compile('TurnPageToKnet\((.*?)\)[;]?">') #已修改1次(增加分号)
RE_REFER_URL = re.compile(r'href=\"(.*?)\">')
RE_REFER_TITLE = re.compile(r'<a(.*?)>(.*?)</a>')
RE_ISSUING_TIME = re.compile(r'([\d]+[-/][\d]+[-/][\d]+)')    # 在summary页中匹配issuing_time
RE_remove_space = re.compile('\n|\r|  |&amp|;nbsp')
RE_clean_abstract = re.compile(r'ChDivSummary">(.*?)</span>', )
RE_clean_keyword = re.compile(r'TurnPageToKnet\(\'kw\',\'(.*?)\',\'[\d]*\'\)', )
RE_clean_fund = re.compile(r'TurnPageToKnet\(\'fu\',\'(.*?)\',\'[\d]*\'\)', )
RE_clean_DOI = re.compile(r'</label>(.*?)</p>', )
RE_clean_CJFQ = re.compile(r'href="(.*?)">(.*?)</a>(.*?)<a(.*?)>(.*?)</a>(.*?)<a(.*?)>(.*?)</a>')
RE_clean_CDFD = re.compile(r'href="(.*?)">(.*?)</a>(.*?)<a(.*?)>(.*?)</a>(.*?)([\d]{4})',)
RE_clean_CDFD_else = re.compile(r'href="(.*?)">(.*?)</a>(.*)\.([\d\s]*)', )
RE_clean_CMFD = re.compile(r'href="(.*?)">(.*?)</a>(.*?)<a(.*?)>(.*?)</a>(.*?)([\d]{4})', )
RE_clean_CMFD_else = re.compile(r'href="(.*?)">(.*?)</a>(.*)\.([\d\s]*)', )

# RE_clean_CBBD = re.compile(r'(.*?)\.(.*?),(.*?),.*?([\d]{4})', )
RE_clean_CBBD = re.compile(r'(.*?)\.(.*?),(.*?),([\d\s]*)', ) # 已修改一次

RE_clean_SSJD = re.compile(r'href="([\s\S]*?)">(.*?)</a>([\s\S]*?)([\d\(\)]+)', )
RE_clean_CRLDENG = re.compile(r'<a([\s\S]*?)>(.*?)</a>([\s\S]*)', )
RE_clean_CRLDENG_else = re.compile(r'([\s\S]*)\.[\s]?([\d]*)', )
# RE_clean_CCND = re.compile(r'<a([\s\S]*?)>(.*?)</a>([\s\S]*)\.(.*?)\.([\d]{4}\([\d\w]+\))', )  # 已修改2次
RE_clean_CCND = re.compile(r'<a([\s\S]*?)>(.*?)</a>([\s\S]*)\.(.*?)\.(.*)', )  # 已修改3次

RE_split_word = re.compile(
    r'(QueryID=[a-zA-Z0-9.]&|CurRec=\d*&|DbCode=[a-zA-Z]*&|urlid=[a-zA-Z0-9.]*&|yx=[a-zA-Z]*)',
    flags=re.I
)
RE_refers = re.compile(r'</em>([\s\S]*?)</li>')

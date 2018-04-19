#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'
import re

RE_FILENAME = re.compile(r'filename=((.*?))&')
RE_AUTHORS = re.compile('TurnPageToKnet\((.*?)\)">')
RE_REFER_URL = re.compile(r'href=\"(.*?)\">')
RE_REFER_TITLE = re.compile(r'<a(.*?)>(.*?)</a>')
RE_ISSUING_TIME = re.compile(r'([\d]+-[\d]+-[\d]+)')
RE_remove_space = re.compile('\n|\r|  |&amp|;nbsp')
RE_remove_space_2 = re.compile('\n|\r|  ')
RE_clean_abstract = re.compile(r'ChDivSummary">(.*?)</span>', )
RE_clean_keyword = re.compile(r'TurnPageToKnet\(\'kw\',\'(.*?)\',\'[\d]*\'\)', )
RE_clean_fund = re.compile(r'TurnPageToKnet\(\'fu\',\'(.*?)\',\'[\d]*\'\)', )
RE_clean_DOI = re.compile(r'</label>(.*?)</p>', )
RE_clean_CJFQ = re.compile(r'href="(.*?)">(.*?)</a>(.*?)<a(.*?)>(.*?)</a>(.*?)<a(.*?)>(.*?)</a>')
RE_clean_CJFQ_else = re.compile(r'(.*?)\.(.*?)\.(.*?)\.(.*?)')
RE_clean_CDFD = re.compile(r'href="(.*?)">(.*?)</a>(.*?)<a(.*?)>(.*?)</a>(.*?)([\d]{4})',)
RE_clean_CMFD = re.compile(r'href="(.*?)">(.*?)</a>(.*?)<a(.*?)>(.*?)</a>(.*?)([\d]{4})', )
RE_clean_CBBD = re.compile(r'(.*?)\.(.*?),(.*?),.*?([\d]{4})', )
RE_clean_SSJD = re.compile(r'href="([\s\S]*?)">(.*?)</a>([\s\S]*?)([\d\(\)]+)', )
RE_clean_CRLDENG = re.compile(r'<a([\s\S]*?)>(.*?)</a>([\s\S]*)', )
RE_clean_CRLDENG_else = re.compile(r'([\s\S]*)\.[\s]?([\d]*)', )
RE_clean_CCND = re.compile(r'<a([\s\S]*?)>(.*?)</a>([\s\S]*?)\.(.*?)\.([\d]{4}\([\d+]\))', )
RE_split_word = re.compile(
    r'(QueryID=[a-zA-Z0-9.]&|CurRec=\d*&|DbCode=[a-zA-Z]*&|urlid=[a-zA-Z0-9.]*&|yx=[a-zA-Z]*)',
    flags=re.I
)
RE_refers = re.compile(r'</em>([\s\S]*?)</li>')
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'
import re


def select_detail(response):
    try:
        # 有英文名字，即新版本
        date = response.css(".sourinfo a::text").extract()[2].split()[0]  # 文章的年月 Detail.detail_date
    except IndexError:
        try:
            # 没有英文名字，即旧版本
            date = response.css(".sourinfo a::text").extract()[1].split()[0]
        except IndexError:
            date = response.css(".sourinfo p::text").extract()[0].split()[0]

    paper_id = re.search('filename=((.*?))&', response.url).group(1)  # 文章ID Detail.detail_id

    authors_info = response.css('.author a::attr(onclick)').re('(\(.*\))')
    authors_dic = {}  # id:name     作者信息 Detail.authors     Authors.authors_id:Authors.authors_name
    for i in authors_info:
        author_name = i.split("','")[1]
        author_id = i.split("','")[-1].split("'")[0]
        authors_dic[author_id] = author_name

    # orgs_info = response.css('.orgn a').re('(\(.*\))')
    orgs_info = response.css('.orgn a::attr(onclick)').re(r'\((.*)\)')
    orgs_dic = {}  # id:name   单位信息 Detail.organizations    Organization.organization_id:Organization.organization_name
    for i in orgs_info:
        org_name = i.split("','")[1]
        org_id = i.split("','")[-1].split("'")[0]
        orgs_dic[org_id] = org_name

    abstract = response.xpath('//span[@id="ChDivSummary"]/text()').extract_first()  # 概要 Detail.detail_abstract

    keyword = response.xpath('//div[@class="wxBaseinfo"]').re(r'\(\'kw\'.*\)', )
    keywords = ""  # 关键字 Detail.detail_keywords
    for i in keyword:
        keywords += i.split("','")[1] + ' '

    return paper_id, keywords, abstract, date, authors_dic, orgs_dic

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Eeljiang'

from scrapy.cmdline import execute  # 执行scrapy脚本
import sys
import os


def start_scrapy():

    sys.path.append(  # 加入变量
        os.path.dirname(  # 父目录文件地址
            os.path.abspath(__file__)  # 当前文件地址
        ))
    # execute(['scrapy', 'crawl', 'crawl_detail'])
    execute(['scrapy', 'crawl', 'cnki_spider'])
    # execute(['scrapy', 'crawl', 'cnki_spider_test'])

    # execute(['scrapy', 'crawl', 'incremental_crawl_detail'])


if __name__ == '__main__':
    start_scrapy()

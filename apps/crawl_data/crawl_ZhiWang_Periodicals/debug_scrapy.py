#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'

from scrapy.cmdline import execute  # 执行scrapy脚本
import sys
import os

sys.path.append(  # 加入变量
    os.path.dirname(  # 父目录文件地址
        os.path.abspath(__file__)  # 当前文件地址
    ))
execute(['scrapy', 'crawl', 'crawl_detail'])

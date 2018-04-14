#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Eeljiang'

from scrapy.cmdline import execute  # 执行scrapy脚本
import sys
import os
from multiprocessing import Pool

issns = ['1674-7216',
'1674-7224',
'1674-7232',
'1674-7240',
'1674-7259',
'1674-7267']

def start_scrapy(issn):
    print('开始爬取issn：',issn)
    sys.path.append(  # 加入变量
        os.path.dirname(  # 父目录文件地址
            os.path.abspath(__file__)  # 当前文件地址
        ))
    # execute(['scrapy', 'crawl', 'crawl_detail'])
    execute(['scrapy', 'crawl', 'cnki_spider', '-a', 'issn={}'.format(issn)])
    # execute(['scrapy', 'crawl', 'incremental_crawl_detail'])
    print('结束爬取issn：',issn)


def speak(a):
    print(a)


if __name__=='__main__':
    start_scrapy('1674-7216')

    # print('Parent process %s.' % os.getpid())
    # p = Pool(4)
    # for i, issn in enumerate(issns):
    #     p.apply_async(start_scrapy, args=issn)
    # print('Waiting for all subprocesses done...')
    # p.close()
    # p.join()
    # print('All subprocesses done.')

    # from concurrent import futures
    # executor = futures.ProcessPoolExecutor(max_workers=10)
    # results = executor.map(start_scrapy, issns)
    # # results = executor.map(speak, issns)
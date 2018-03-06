#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'

from apps.crawl_data.crawl_summary import CrawlCnkiSummary

crawl_cnki_summary = CrawlCnkiSummary(use_Chrome=False,
                                      executable_path='/home/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
crawl_cnki_summary.crawl_periodicals_summary()
# crawl_cnki_summary.test()

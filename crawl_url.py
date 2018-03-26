#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'

from apps.crawl_data.crawl_summary import CrawlCnkiSummary

crawl_cnki_summary = CrawlCnkiSummary(use_Chrome=True,
                                      # executable_path='/Users/heianhu/phantomjs-2.1.1-macosx/bin/phantomjs'
                                      )
# crawl_cnki_summary.crawl_periodicals_summary(mark=True, start_num=33)
# crawl_cnki_summary.crawl_periodicals_summary(issn_number='1004-6577')
crawl_cnki_summary.test()

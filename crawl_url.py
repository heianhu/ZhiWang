#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'

from apps.crawl_data.crawl_summary import CrawlCnkiSummary

crawl_cnki_summary = CrawlCnkiSummary(use_Chrome=True,)
crawl_cnki_summary.crawl_periodicals_summary(mark=True)
# crawl_cnki_summary.test()

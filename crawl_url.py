#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'

from apps.crawl_cnki.crawl_Cnki_Periodicals.crawl_Cnki_Periodicals.crawl_summary import CrawlCnkiSummary
import sys
import os

if __name__ == '__main__':
    crawl_cnki_summary = CrawlCnkiSummary(
        use_GPU=True,
        # executable_path='/Users/heianhu/phantomjs-2.1.1-macosx/bin/phantomjs'
    )
    crawl_cnki_summary.crawl_periodicals_summary(mark=True)

# -*- coding: utf-8 -*-

# Scrapy settings for crawl_ZhiWang_Periodicals project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
import sys
import os

BATH_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(BATH_DIR, 'ArticleSpider'))  # 配置当前路径

BOT_NAME = 'crawl_ZhiWang_Periodicals'

SPIDER_MODULES = ['crawl_ZhiWang_Periodicals.spiders']
NEWSPIDER_MODULE = 'crawl_ZhiWang_Periodicals.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'crawl_ZhiWang_Periodicals (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'crawl_ZhiWang_Periodicals.middlewares.CrawlZhiwangPeriodicalsSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'crawl_ZhiWang_Periodicals.middlewares.MyCustomDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'crawl_ZhiWang_Periodicals.pipelines.CrawlZhiwangPeriodicalsPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# 所要爬取的参考文献的dbname
REFERENCES_DBNAME = ('CJFQ',  # 中国学术期刊网络出版总库 id = "pc_CJFQ"
                     'CDFD',  # 中国博士学位论文全文数据库 id = "pc_CDFD"
                     'CMFD',  # 中国优秀硕士学位论文全文数据库 id = "pc_CMFD"
                     'CBBD',  # 中国图书全文数据库 id = "pc_CBBD"
                     'SSJD',  # 国际期刊数据库 id = "pc_SSJD"
                     'CRLDENG',  # 外文题录数据库 id = "pc_CRLDENG"
                     'CCND',  # 中国重要报纸全文数据库 id = "pc_CCND"
                     'CPFD',  # 中国重要会议论文全文数据库 id="pc_CPFD"
                     )

# 是否为增量爬取数据
INCREMENTAL_CRAWL_DETAIL = False

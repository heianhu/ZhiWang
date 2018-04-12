# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from selenium import webdriver


class CrawlCnkiPeriodicalsSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class Use_seleniumMiddleware(object):
    def process_request(self, request, spider):
        driver = webdriver.Chrome()  # 初始化webdriver
        driver.get('http://localhost')
        for cookie in request.cookies:
            driver.add_cookie(cookie)
        driver.get(request.url)
        # # 所有 url 都走 browser
        # browser = webdriver.Chrome()
        # # 先启动浏览器才能添加 cookie
        # browser.get('http://localhost')
        #
        # # 从文件中读取 cookies
        # with open('/Users/eeljiang/Desktop/zhihuCookies', 'rb') as f:
        #     Cookies = pickle.load(f)
        #
        # for cookie in Cookies:
        #     browser.add_cookie(cookie)

        # print("开始访问：{0}".format(request.url))
        # browser.get(request.url)
        # time.sleep(5)

        # pass
        # if request.url in spider.start_urls:
        #     # browser = webdriver.Chrome()
        #     print("开始访问：{0}".format(request.url))
        #     spider.browser.get(request.url)
        #     time.sleep(3)
        #
        #     # 按一下 esc 关掉账号异常验证的框
        #     actions = ActionChains(spider.browser)
        #     actions.send_keys(Keys.ESCAPE)
        #     actions.perform()
        #
        #     print("开始滚动")
        #     for i in range(3):
        #         spider.browser.execute_script(
        #             "window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
        #         time.sleep(3)
        #
        #     url = spider.browser.current_url
        #     body = spider.browser.page_source
        #     # browser.quit()
        #
        #     return HtmlResponse(url=url, body=body, encoding="utf-8", request=request)

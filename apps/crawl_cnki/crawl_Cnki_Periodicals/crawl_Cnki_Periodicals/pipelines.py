# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from crawl_cnki.crawl_Cnki_Periodicals.crawl_Cnki_Periodicals.items import ArticleItem, ReferenceItem


class CrawlCnkiPeriodicalsPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, ArticleItem):
            try:
                # 写入基础表
                article = item.save_to_mysql_article()
                authors = item.save_to_mysql_author()
                orgs = item.save_to_mysql_org()

                # 写入 m2m 的表
                item.save_to_mysql_article_author(article, authors)
                item.save_to_mysql_article_org(article, orgs)
            except Exception as e:
                print(e)

        elif isinstance(item, ReferenceItem):
            try:
                pass
                # 写入基础表
                article, refer = item.save_to_mysql_refer()

                # 写入 m2m 的表
                item.save_to_mysql_article_refer(article, refer)
            except Exception as e:
                print(e)

        return item


# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from django.db.utils import IntegrityError
from crawl_data.models import Authors, Organization, Detail


class CrawlZhiwangPeriodicalsPipeline(object):
    def process_item(self, item, spider):
        item.insert_database()
        return item
        # authors_database_id = []
        # organization_database_id = []
        # summary = item['summary']
        #
        # for authors_id, authors_name in item['authors_dic'].items():
        #     # 处理作者信息
        #     if authors_id == '':
        #         # ID为空的时候
        #         author = Authors()
        #         author.authors_id = ''
        #         author.authors_name = authors_name
        #         author.save()
        #         authors_database_id.append(authors_name)
        #     elif Authors.objects.filter(authors_id=authors_id) and authors_id != '':
        #         # 不为空的ID已经在数据库中了
        #         authors_database_id.append(str(Authors.objects.get(authors_id=authors_id).id))
        #         continue
        #     else:
        #         author = Authors()
        #         if len(authors_id) >= 20:
        #             # 当一个人存储了一堆人的ID时候，则舍弃这堆ID
        #             author.authors_id = ''
        #             author.authors_name = authors_name
        #             author.save()
        #             authors_database_id.append(authors_name)
        #         else:
        #             author.authors_id = authors_id
        #             author.authors_name = authors_name
        #             author.save()
        #             authors_database_id.append(str(Authors.objects.filter(authors_id=authors_id)[0].id))
        # for organization_id, organization_name in item['organizations_dic'].items():
        #     # 处理组织信息
        #     if organization_id == '':
        #         # ID为空的时候
        #         organization = Organization()
        #         organization.organization_id = ''
        #         organization.organization_name = organization_name
        #         organization.save()
        #         organization_database_id.append(organization_name)
        #     elif Organization.objects.filter(organization_id=organization_id):
        #         # 不为空的ID已经在数据库中了
        #         organization_database_id.append(str(Organization.objects.get(organization_id=organization_id).id))
        #         continue
        #     else:
        #         organization = Organization()
        #         if len(organization_id) >= 20:
        #             # 当一个人存储了一堆人的ID时候，则舍弃这堆ID
        #             organization.organization_id = ''
        #             organization.organization_name = organization_name
        #             organization.save()
        #             organization_database_id.append(organization_name)
        #         else:
        #             organization.organization_id = organization_id
        #             organization.organization_name = organization_name
        #             organization.save()
        #             organization_database_id.append(str(Organization.objects.filter(organization_id=organization_id)[0].id))
        #
        # detail = Detail()
        # detail.detail_id = item['detail_id']
        # detail.detail_keywords = item['detail_keywords']
        # if not item['detail_abstract']:
        #     detail.detail_abstract = ''
        # else:
        #     detail.detail_abstract = item['detail_abstract']
        #
        # detail.detail_date = item['detail_date']
        # detail.authors = ' '.join(authors_database_id)
        # detail.organizations = ' '.join(organization_database_id)
        # detail.save()
        # summary.detail = detail
        # summary.have_detail = True
        # summary.save()
        #
        # return item

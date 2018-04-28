from django.db import models
import time
from ZhiWang.settings import SEARCH_DIC


# Create your models here.

class SearchFilter(models.Model):
    """
    搜索条件
    """
    username = models.CharField(verbose_name='username', max_length=255, default='', blank=True)
    session_id = models.CharField(verbose_name='session_id', max_length=255, default='')
    time = models.CharField(verbose_name='时间戳', default='', max_length=20)
    filterPara = models.TextField(verbose_name='搜索条件', default='')

    class Meta:
        verbose_name = '搜索条件'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    def search_time(self):
        """
        显示搜索时间
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(self.time[:10])))

    search_time.short_description = '搜索时间'

    def search_filterPara(self):
        search_filter = eval(self.filterPara)
        search_filter_keys = tuple(SEARCH_DIC.keys())
        text = '{}:{}{}{},{}:{},{}:{},{}:{},{}:{}'.format(
            # 题目或其他搜索条件
            SEARCH_DIC.get(search_filter_keys[0], 'txt_2_sel').get(search_filter.get(search_filter_keys[0], ''), 'SU'),
            search_filter.get(search_filter_keys[1], ''),
            SEARCH_DIC.get(search_filter_keys[2], '').get(search_filter.get(search_filter_keys[2], '')),
            search_filter.get(search_filter_keys[3], ''),
            # 作者
            SEARCH_DIC.get(search_filter_keys[4], 'au_1_sel').get(search_filter.get(search_filter_keys[4], 'AU'), ''),
            search_filter.get(search_filter_keys[5], ''),
            # 机构组织
            SEARCH_DIC.get(search_filter_keys[6], 'org_1_sel').get(search_filter.get(search_filter_keys[6], 'ORG'), ''),
            search_filter.get(search_filter_keys[7], ''),
            # 文献号或名字
            SEARCH_DIC.get(search_filter_keys[8], 'magazine_1_sel').get(search_filter.get(search_filter_keys[8]),
                                                                        'issn_number'),
            search_filter.get(search_filter_keys[9], ''),
            # 时间
            SEARCH_DIC.get(search_filter_keys[10], '发表时间'),
            search_filter.get(search_filter_keys[10], '')
        )
        return text

    search_filterPara.short_description = '搜索内容'

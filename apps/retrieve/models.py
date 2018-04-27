from django.db import models
import time


# Create your models here.

class SearchFilter(models.Model):
    """
    搜索条件
    """
    username = models.CharField(verbose_name='username', max_length=255, default='', blank=True)
    session_id = models.CharField(verbose_name='session_id', max_length=255, default='')
    time = models.CharField(verbose_name='时间戳', default='', max_length=20)
    filterPara = models.TextField(verbose_name='搜索条件', default='')

    def __str__(self):
        return self.username

    def search_time(self):
        """
        显示搜索时间
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(self.time[:10])))

    # def search_filterPara(self):
    #     search_filter = eval(self.filterPara)
    #     text = '{}:{}{}{},{}:{},{}:{},{},{}'.format()

    class Meta:
        verbose_name = '搜索条件'
        verbose_name_plural = verbose_name

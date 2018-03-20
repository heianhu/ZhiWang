from django.db import models

# Create your models here.

class SearchFilter(models.Model):
    """
    搜索条件
    """
    session_id = models.CharField(verbose_name='session_id', max_length=255, default='')
    time = models.CharField(verbose_name='时间戳', default='', max_length=20)
    filterPara = models.TextField(verbose_name='搜索条件', default='')


    class Meta:
        verbose_name = '搜索条件'
        verbose_name_plural = verbose_name

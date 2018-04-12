from django.db import models
from datetime import datetime


# Create your models here.

class Periodical(models.Model):
    """
    期刊名称以及issn号
    """
    name = models.CharField(max_length=255, verbose_name='期刊名称', default='')
    issn_number = models.CharField(max_length=50, verbose_name='期刊ISSN', default='')
    mark = models.BooleanField(default=False, verbose_name='是否为标记的指定期刊')

    class Meta:
        verbose_name = '期刊列表'
        verbose_name_plural = verbose_name


class Article(models.Model):
    """
    文章概览
    """
    url = models.URLField(max_length=255, verbose_name='文章的url', unique=True)
    filename = models.CharField(unique=True, verbose_name='论文ID', max_length=64)
    title = models.CharField(max_length=255, verbose_name='文章的题名')
    periodicals = models.ForeignKey(Periodical, verbose_name='文章的来源')
    issuing_time = models.DateField(verbose_name='发表时间', default=datetime.now)
    cited = models.IntegerField(verbose_name='被引用次数', default=0, blank=True)
    keywords = models.CharField(max_length=255, verbose_name='关键字', default='', blank=True)
    abstract = models.TextField(verbose_name='摘要', default='', blank=True)
    DOI = models.CharField(max_length=255, verbose_name='doi', default='', blank=True)
    remark = models.TextField(verbose_name='备注', blank=True)

    class Meta:
        verbose_name = '文章信息'
        verbose_name_plural = verbose_name


class Author(models.Model):
    """
    作者
    """
    authors_id = models.CharField(verbose_name='作者ID', max_length=20)
    authors_name = models.CharField(max_length=255, verbose_name='作者名字')

    class Meta:
        verbose_name = '作者信息'
        verbose_name_plural = verbose_name


class Organization(models.Model):
    """
    组织
    """
    organization_id = models.CharField(verbose_name='单位ID', max_length=20)
    organization_name = models.CharField(verbose_name='单位名称', max_length=255)

    class Meta:
        verbose_name = '单位信息'
        verbose_name_plural = verbose_name


class References(models.Model):
    """
    参考文献
    """
    url = models.URLField(max_length=255, verbose_name='参考文献的url')
    title = models.TextField(verbose_name='参考文献的题名')
    authors = models.TextField(max_length=255, verbose_name='参考文献的作者')
    source = models.CharField(max_length=255, verbose_name='参考文献的来源')
    issuing_time = models.CharField(max_length=255, verbose_name='发表时间')
    remark = models.TextField(verbose_name='备注')

    class Meta:
        verbose_name = '参考文献'
        verbose_name_plural = verbose_name


class Article_References(models.Model):
    article = models.ForeignKey(Article, verbose_name='文章')
    references = models.ForeignKey(References, verbose_name='参考文献')

    class Meta:
        verbose_name = '参考文献'
        verbose_name_plural = verbose_name


class Article_Author(models.Model):
    article = models.ForeignKey(Article, verbose_name='文献', blank=True)
    author = models.ForeignKey(Author, verbose_name='作者', blank=True)


class Article_Organization(models.Model):
    article = models.ForeignKey(Article, verbose_name='文献', blank=True)
    organization = models.ForeignKey(Organization, verbose_name='机构', blank=True)

from django.db import models

# Create your models here.
from datetime import datetime


class Periodicals(models.Model):
    """
    期刊名称以及issn号
    """
    name = models.CharField(max_length=255, verbose_name='期刊名称', default='')
    issn_number = models.CharField(max_length=50, verbose_name='期刊ISSN', default='')
    mark = models.BooleanField(default=False, verbose_name='是否为标记的指定期刊')

    class Meta:
        verbose_name = '期刊列表'
        verbose_name_plural = verbose_name


class ReferencesCJFQ(models.Model):
    """
    参考文献
    中国学术期刊网络出版总库
    """
    url = models.URLField(max_length=255, verbose_name='文章的url', unique=True)
    title = models.CharField(max_length=255, verbose_name='文章的题名')
    authors = models.CharField(max_length=255, verbose_name='文章的作者')
    source = models.CharField(max_length=255, verbose_name='文章的来源')
    issuing_time = models.CharField(max_length=255, verbose_name='发表时间')

    class Meta:
        verbose_name = '参考文献(中国学术期刊网络出版总库)'
        verbose_name_plural = verbose_name


class ReferencesCDFD(models.Model):
    """
    参考文献
    中国博士学位论文全文数据库
    """
    url = models.URLField(max_length=255, verbose_name='文章的url', unique=True)
    title = models.CharField(max_length=255, verbose_name='文章的题名')
    authors = models.CharField(max_length=255, verbose_name='文章的作者')
    source = models.CharField(max_length=255, verbose_name='文章的来源')
    issuing_time = models.CharField(max_length=255, verbose_name='发表时间')

    class Meta:
        verbose_name = '参考文献(中国博士学位论文全文数据库)'
        verbose_name_plural = verbose_name


class ReferencesCMFD(models.Model):
    """
    参考文献
    中国优秀硕士学位论文全文数据库
    """
    url = models.URLField(max_length=255, verbose_name='文章的url', unique=True)
    title = models.CharField(max_length=255, verbose_name='文章的题名')
    authors = models.CharField(max_length=255, verbose_name='文章的作者')
    source = models.CharField(max_length=255, verbose_name='文章的来源')
    issuing_time = models.CharField(max_length=255, verbose_name='发表时间')

    class Meta:
        verbose_name = '参考文献(中国优秀硕士学位论文全文数据库)'
        verbose_name_plural = verbose_name


class ReferencesCBBD(models.Model):
    """
    参考文献
    中国图书全文数据库
    """
    title = models.CharField(max_length=255, verbose_name='文章的题名')
    authors = models.CharField(max_length=255, verbose_name='文章的作者')
    source = models.CharField(max_length=255, verbose_name='文章的来源')
    issuing_time = models.CharField(max_length=255, verbose_name='发表时间')

    class Meta:
        verbose_name = '参考文献(中国图书全文数据库)'
        verbose_name_plural = verbose_name


class ReferencesSSJD(models.Model):
    """
    参考文献
    国际期刊数据库
    """
    url = models.URLField(max_length=255, verbose_name='文章的url', unique=True)
    title = models.CharField(max_length=255, verbose_name='文章的题名')
    info = models.CharField(max_length=255, verbose_name='文章的所有信息')
    issuing_time = models.CharField(max_length=255, verbose_name='发表时间')

    class Meta:
        verbose_name = '参考文献(国际期刊数据库)'
        verbose_name_plural = verbose_name


class ReferencesCRLDENG(models.Model):
    """
    参考文献
    外文题录数据库
    """
    info = models.CharField(max_length=255, verbose_name='文章的所有信息')
    issuing_time = models.CharField(max_length=255, verbose_name='发表时间')

    class Meta:
        verbose_name = '参考文献(外文题录数据库)'
        verbose_name_plural = verbose_name


class References(models.Model):
    """
    参考文献
    """
    CJFQ = models.CharField(max_length=255, verbose_name='中国学术期刊网络出版总库', help_text='中国学术期刊网络出版总库在数据库中的ID集合，用空格分开',
                            default='',
                            blank=True, null=True)
    CDFD = models.CharField(max_length=255, verbose_name='中国博士学位论文全文数据库', help_text='中国博士学位论文全文数据库在数据库中的ID集合，用空格分开',
                            default='',
                            blank=True, null=True)
    CMFD = models.CharField(max_length=255, verbose_name='中国优秀硕士学位论文全文数据库', help_text='中国优秀硕士学位论文全文数据库在数据库中的ID集合，用空格分开',
                            default='',
                            blank=True, null=True)
    CBBD = models.CharField(max_length=255, verbose_name='中国图书全文数据库', help_text='中国图书全文数据库在数据库中的ID集合，用空格分开', default='',
                            blank=True, null=True)
    SSJD = models.CharField(max_length=255, verbose_name='国际期刊数据库', help_text='国际期刊数据库在数据库中的ID集合，用空格分开', default='',
                            blank=True, null=True)
    CRLDENG = models.CharField(max_length=255, verbose_name='外文题录数据库', help_text='外文题录数据库在数据库中的ID集合，用空格分开', default='',
                               blank=True, null=True)

    class Meta:
        verbose_name = '参考文献'
        verbose_name_plural = verbose_name


class Detail(models.Model):
    """
    文章细节
    """
    detail_id = models.CharField(unique=True, verbose_name='论文ID', max_length=20)
    detail_keywords = models.CharField(max_length=255, verbose_name='关键字', default='', blank=True, null=True)
    detail_abstract = models.TextField(verbose_name='摘要', default='', blank=True, null=True)
    detail_date = models.CharField(max_length=50, verbose_name='文章年月', default='', blank=True, null=True)
    authors = models.CharField(max_length=255, verbose_name='作者ID集合', help_text='作者在数据库中的ID集合，用空格分开', default='',
                               blank=True, null=True)
    organizations = models.CharField(max_length=255, verbose_name='单位ID集合', help_text='单位在数据库中的ID集合，用空格分开', default='',
                                     blank=True, null=True)
    references = models.ForeignKey(References, verbose_name='参考文献', blank=True, null=True)

    class Meta:
        verbose_name = '文章详情信息'
        verbose_name_plural = verbose_name


class Summary(models.Model):
    """
    文章概览
    """
    url = models.URLField(max_length=255, verbose_name='文章的url', unique=True)
    title = models.CharField(max_length=255, verbose_name='文章的题名')
    authors = models.CharField(max_length=255, verbose_name='文章的作者')
    source = models.ForeignKey(Periodicals, verbose_name='文章的来源')
    issuing_time = models.DateField(verbose_name='发表时间', default=datetime.now)
    cited = models.IntegerField(verbose_name='被引用次数', default=0, null=True, blank=True)
    have_detail = models.BooleanField(verbose_name='是否获取过详细内容', default=False)
    detail = models.ForeignKey(Detail, verbose_name='详细信息', blank=True, null=True)

    class Meta:
        verbose_name = '文章概览'
        verbose_name_plural = verbose_name


class Authors(models.Model):
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'
import re
from django.db.models import Q  # 数据库中用多操作

from crawl_data.crawl_ZhiWang_Periodicals.crawl_ZhiWang_Periodicals.items import DetailItem, ReferencesCJFQItem, \
    ReferencesCMFDItem, ReferencesCDFDItem, ReferencesCBBDItem, \
    ReferencesSSJDItem, ReferencesCRLDENGItem, ReferencesItem, ReferencesCCNDItem, ReferencesCPFDItem
from crawl_data.models import ReferencesCJFQ, ReferencesCMFD, ReferencesCDFD, ReferencesCBBD, ReferencesSSJD, \
    ReferencesCRLDENG, References, ReferencesCCND, ReferencesCPFD


def select_detail(response):
    try:
        # 有英文名字，即新版本
        date = response.css(".sourinfo a::text").extract()[2].split()[0]  # 文章的年月 Detail.detail_date
    except IndexError:
        try:
            # 没有英文名字，即旧版本
            date = response.css(".sourinfo a::text").extract()[1].split()[0]
        except IndexError:
            date = response.css(".sourinfo p::text").extract()[0].split()[0]

    paper_id = re.search('filename=((.*?))&', response.url).group(1)  # 文章ID Detail.detail_id

    authors_info = response.css('.author a::attr(onclick)').re('(\(.*\))')
    authors_dic = {}  # id:name     作者信息 Detail.authors     Authors.authors_id:Authors.authors_name
    for i in authors_info:
        author_name = i.split("','")[1]
        author_id = i.split("','")[-1].split("'")[0]
        authors_dic[author_id] = author_name

    # orgs_info = response.css('.orgn a').re('(\(.*\))')
    orgs_info = response.css('.orgn a::attr(onclick)').re(r'\((.*)\)')
    orgs_dic = {}  # id:name   单位信息 Detail.organizations    Organization.organization_id:Organization.organization_name
    for i in orgs_info:
        org_name = i.split("','")[1]
        org_id = i.split("','")[-1].split("'")[0]
        orgs_dic[org_id] = org_name

    abstract = response.xpath('//span[@id="ChDivSummary"]/text()').extract_first()  # 概要 Detail.detail_abstract

    keyword = response.xpath('//div[@class="wxBaseinfo"]').re(r'\(\'kw\'.*\)', )
    keywords = ""  # 关键字 Detail.detail_keywords
    for i in keyword:
        keywords += i.split("','")[1] + ' '

    return paper_id, keywords, abstract, date, authors_dic, orgs_dic


def select_references(response, *args,
                      CJFQ_list, CDFD_list, CMFD_list, CBBD_list, SSJD_list, CRLDENG_list, CCND_list, CPFD_list):
    """
    处理参考文献，提取出各项

    中国学术期刊网络出版总库
    id = "pc_CJFQ"


    <li class="">
        <em>[1]</em>
        <a target="kcmstarget" href="/kcms/detail/detail.aspx?filename=JXKX200305012&amp;dbcode=CJFQ&amp;dbname=CJFD2003&amp;v=">基于Voronoi图的快速成型扫描路径生成算法研究</a>
    [J]. 陈剑虹,马鹏举,田杰谟,刘振凯,卢秉恒.&nbsp&nbsp
        <a onclick="getKns55NaviLink('','CJFQ','CJFQbaseinfo','JXKX');">机械科学与技术</a>.
        <a onclick="getKns55NaviLinkIssue('','CJFQ','CJFQyearinfo','JXKX','2003','05')">2003(05)</a>
    </li>

    <li class="">
        <em>[1]</em>
        <a target="kcmstarget" href="/kcms/detail/detail.aspx?filename=BDZK201405003&amp;dbcode=CJFQ&amp;dbname=CJFD2014&amp;v=">作为马克思哲学思想起点的伊壁鸠鲁哲学</a>
    [J]. 聂锦芳.&nbsp&nbsp
        <a onclick="getKns55NaviLink('','CJFQ','CJFQbaseinfo','BDZK');">北京大学学报(哲学社会科学版)</a>.
        <a onclick="getKns55NaviLinkIssue('','CJFQ','CJFQyearinfo','BDZK','2014','05')">2014(05)</a>
    </li>

    <li class="">
        <em>[1]</em>
        <a target="kcmstarget" href="/kcms/detail/detail.aspx?filename=DXWJ201301031&amp;dbcode=CJFQ&amp;dbname=CJFD2013&amp;v=">多屏融合下的流媒体技术</a>
    [J]. &nbsp&nbsp
        <a onclick="getKns55NaviLink('WEEvREcwSlJHSldRa1FhdkJkVWI2K2N5enhlaTBhaUNkaXdtbFlLSjM5dz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4ggI8Fm4gTkoUKaID8j8gFw!!','CJFQ','CJFQbaseinfo','DXWJ');">电信网技术</a>.
        <a onclick="getKns55NaviLinkIssue('WEEvREcwSlJHSldRa1FhdkJkVWI2K2N5enhlaTBhaUNkaXdtbFlLSjM5dz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4ggI8Fm4gTkoUKaID8j8gFw!!','CJFQ','CJFQyearinfo','DXWJ','2013','01')">2013(01)</a>
    </li>


    中国博士学位论文全文数据库
    id = "pc_CDFD"


    <li class="">
        <em>[1]</em>
        <a target="kcmstarget" href="/kcms/detail/detail.aspx?filename=2010135951.nh&amp;dbcode=CDFD&amp;dbname=CDFD2010&amp;v=">心理弹性与压力困扰、适应的关系</a>
    [D]. 蔡颖.
        <a onclick="getKns55UnitNaviLink('','CDFD','GTSFU');">天津师范大学</a>
     2010
     </li>


    中国优秀硕士学位论文全文数据库
    id = "pc_CMFD"


    <li class="">
        <em>[1]</em>
        <a target="kcmstarget" href="/kcms/detail/detail.aspx?filename=2010135951.nh&amp;dbcode=CDFD&amp;dbname=CDFD2010&amp;v=">心理弹性与压力困扰、适应的关系</a>
    [D]. 蔡颖.
        <a onclick="getKns55UnitNaviLink('','CDFD','GTSFU');">天津师范大学</a>
     2010
     </li>


    中国图书全文数据库
    id = "pc_CBBD"


    数据均是堆成一坨的

    创客[M].                      马克思与亚里士多德[M].
        中信出版社                    华东师范大学出版社
        ,                      ,
        安德森,                     麦卡锡,
        2012                    2014


    国际期刊数据库
    id = "pc_SSJD"


    <li class="">
        <em>[1]</em>
        <a target="kcmstarget" href="/kcms/detail/detail.aspx?filename=SJES13011300168223&amp;dbcode=SJES">Thriving not just surviving: A review of research on teacher resilience</a>
        [J] .
        Susan Beltman,Caroline Mansfield,Anne Price.&nbsp&nbspEducational Research Review .
        2011
        (3)
    </li>


    外文题录数据库
    id = "pc_CRLDENG"


    中国重要报纸全文数据库
    id = "pc_CCND"


    <li class="">
        <em>[1]</em>
        <a target="kcmstarget" href="/kcms/detail/detail.aspx?filename=CJYB201704190051&amp;dbcode=CCND&amp;dbname=CCND2017&amp;v=">是核心还是综合</a>
    [N].
    杨志成.&nbsp&nbsp中国教育报.
    2017
    (005)
    </li>


    中国重要会议论文全文数据库
    id="pc_CPFD"

    <li class="">
        <em>[1]</em>
        <a target="kcmstarget" href="/kcms/detail/detail.aspx?filename=JYJJ200912001163&amp;dbcode=CPFD&amp;dbname=CPFD2011&amp;v=">高等教育经费省际投入支出的公平性研究</a>
    [A].
    张炜.2009年中国教育经济学学术年会论文集[C].
    2009
    </li>



    只有
    中国学术期刊网络出版总库
    中国博士学位论文全文数据库
    中国优秀硕士学位论文全文数据库
    国际期刊数据库
    这四个是有url的
    :param response:
    :return:
    """
    div_s = response.css('.essayBox')  # 拿到所有含有文献列表的模块
    for div in div_s:
        # 分块提取信息
        # 判断当前块所属库
        dbId = div.css('.dbTitle span::attr(id)').extract_first()
        li_s = div.css('li')
        if dbId == 'pc_CJFQ':
            # 提取中国学术期刊网络出版总库信息
            for li in li_s:
                try:
                    a_s = li.css('a')
                    url = 'http://kns.cnki.net' + a_s[0].css('a::attr(href)').extract_first()
                    title = a_s[0].css('a::text').extract_first()
                    if len(title) > 255:
                        title = title[:255]
                    authors = li.css('li::text').extract_first().split('[J].')[-1].split('.&nbsp&nbsp')[0]
                    if len(authors) > 255:
                        authors = authors[:255]
                    source = a_s[1].css('a::text').extract_first()
                    issuing_time = a_s[2].css('a::text').extract_first().rsplit()[0]
                    if not ReferencesCJFQ.objects.filter(url=url):
                        # 在数据库中没有这条数据信息
                        CJFQ_item = ReferencesCJFQItem()
                        CJFQ_item['url'] = url
                        CJFQ_item['title'] = title
                        CJFQ_item['authors'] = authors
                        CJFQ_item['source'] = source
                        CJFQ_item['issuing_time'] = issuing_time
                        yield CJFQ_item
                    CJFQ_list.append(str(ReferencesCJFQ.objects.filter(url=url)[0].id))
                except TypeError:
                    continue
                except IndexError:
                    # 数据没有url获取他内容，不完整，不具备参考价值
                    continue
        elif dbId == 'pc_CDFD':
            # 提取中国博士学位论文全文数据库
            try:
                for li in li_s:
                    a_s = li.css('a')
                    url = 'http://kns.cnki.net' + a_s[0].css('a::attr(href)').extract_first()
                    title = a_s[0].css('a::text').extract_first()
                    if len(title) > 255:
                        title = title[:255]
                    authors = li.css('li::text').extract_first().split('[D].')[-1]
                    if len(authors) > 255:
                        authors = authors[:255]
                    source = a_s[1].css('a::text').extract_first()
                    issuing_time = li.css('li').extract_first().split('</a>')[-1].split('</li>')[0].rsplit()[0]
                    if not ReferencesCDFD.objects.filter(url=url):
                        # 在数据库中没有这条数据信息
                        CDFD_item = ReferencesCDFDItem()
                        CDFD_item['url'] = url
                        CDFD_item['title'] = title
                        CDFD_item['authors'] = authors
                        CDFD_item['source'] = source
                        CDFD_item['issuing_time'] = issuing_time
                        yield CDFD_item
                    CDFD_list.append(str(ReferencesCDFD.objects.filter(url=url)[0].id))
            except IndexError:
                # 数据没有url获取他内容，不完整，不具备参考价值
                continue
        elif dbId == 'pc_CMFD':
            # 提取中国优秀硕士学位论文全文数据库
            try:
                for li in li_s:
                    a_s = li.css('a')
                    url = 'http://kns.cnki.net' + a_s[0].css('a::attr(href)').extract_first()
                    title = a_s[0].css('a::text').extract_first()
                    if len(title) > 255:
                        title = title[:255]
                    authors = li.css('li::text').extract_first().split('[D].')[-1]
                    if len(authors) > 255:
                        authors = authors[:255]
                    source = a_s[1].css('a::text').extract_first()
                    issuing_time = li.css('li').extract_first().split('</a>')[-1].split('</li>')[0].rsplit()[0]
                    if not ReferencesCMFD.objects.filter(url=url):
                        # 在数据库中没有这条数据信息
                        CMFD_item = ReferencesCMFDItem()
                        CMFD_item['url'] = url
                        CMFD_item['title'] = title
                        CMFD_item['authors'] = authors
                        CMFD_item['source'] = source
                        CMFD_item['issuing_time'] = issuing_time
                        yield CMFD_item
                    CMFD_list.append(str(ReferencesCMFD.objects.filter(url=url)[0].id))
            except IndexError:
                # 数据没有url获取他内容，不完整，不具备参考价值
                continue
        elif dbId == 'pc_CBBD':
            # 提取中国图书全文数据库
            try:
                for li in li_s:
                    all_info = li.css('li::text').extract_first().rsplit()
                    title = all_info[0]
                    if len(title) > 255:
                        title = title[:255]
                    authors = all_info[3]
                    if len(authors) > 255:
                        authors = authors[:255]
                    source = all_info[1]
                    issuing_time = all_info[4]
                    if not ReferencesCBBD.objects.filter(
                            Q(title=title) & Q(authors=authors) & Q(source=source) & Q(issuing_time=issuing_time)):
                        CBBD_item = ReferencesCBBDItem()
                        CBBD_item['title'] = title
                        CBBD_item['authors'] = authors
                        CBBD_item['source'] = source
                        CBBD_item['issuing_time'] = issuing_time
                        yield CBBD_item
                    CBBD_list.append(str(ReferencesCBBD.objects.filter(
                        Q(title=title) & Q(authors=authors) & Q(source=source) & Q(issuing_time=issuing_time))[
                                             0].id))
            except IndexError:
                # 数据没有url获取他内容，不完整，不具备参考价值
                continue
        elif dbId == 'pc_SSJD':
            # 提取国际期刊数据库
            for li in li_s:
                url = 'http://kns.cnki.net' + li.css('a::attr(href)').extract_first()
                title = li.css('a::text').extract_first()
                if len(title) > 255:
                    title = title[:255]
                all_info = li.css('li::text').extract_first().split('\r\n')
                info = all_info[1]
                if len(info) > 255:
                    info = info[:255]
                issuing_time = all_info[2]
                if not ReferencesSSJD.objects.filter(url=url):
                    SSJD_item = ReferencesSSJDItem()
                    SSJD_item['url'] = url
                    SSJD_item['title'] = title
                    SSJD_item['info'] = info
                    SSJD_item['issuing_time'] = issuing_time
                    yield SSJD_item
                SSJD_list.append(str(ReferencesSSJD.objects.filter(url=url)[0].id))
        elif dbId == 'pc_CRLDENG':
            # 提取外文题录数据库
            for li in li_s:
                try:
                    title = li.css('a::text').extract_first()
                    if len(title) > 255:
                        title = title[:255]
                    all_info = li.css('li::text').extract_first().split('\r\n')
                    if len(all_info) < 3:
                        # 数据个数不符
                        continue
                    info = all_info[1]
                    if len(info) > 255:
                        info = info[:255]
                    issuing_time = all_info[2]
                    if not ReferencesCRLDENG.objects.filter(
                            Q(title=title) & Q(info=info) & Q(issuing_time=issuing_time)):
                        CRLDENG_item = ReferencesCRLDENGItem()
                        CRLDENG_item['title'] = title
                        CRLDENG_item['info'] = info
                        CRLDENG_item['issuing_time'] = issuing_time
                        yield CRLDENG_item
                    CRLDENG_list.append(str(ReferencesCRLDENG.objects.filter(
                        Q(title=title) & Q(info=info) & Q(issuing_time=issuing_time))[0].id))
                except TypeError:
                    continue
        elif dbId == 'pc_CCND':
            # 中国重要报纸全文数据库
            for li in li_s:
                url = 'http://kns.cnki.net' + li.css('a::attr(href)').extract_first()
                title = li.css('a::text').extract_first()
                if len(title) > 255:
                    title = title[:255]
                all_info = li.css('li::text').extract_first().split('\r\n')
                authors = all_info[1].split('&nbsp&nbsp')[0]
                if len(authors) > 255:
                    authors = authors[:255]
                source = all_info[1].split('&nbsp&nbsp')[-1]
                issuing_time = all_info[2]
                if not ReferencesCCND.objects.filter(url=url):
                    # 在数据库中没有这条数据信息
                    CCND_item = ReferencesCCNDItem()
                    CCND_item['url'] = url
                    CCND_item['title'] = title
                    CCND_item['authors'] = authors
                    CCND_item['source'] = source
                    CCND_item['issuing_time'] = issuing_time
                    yield CCND_item
                CCND_list.append(str(ReferencesCCND.objects.filter(url=url)[0].id))
        elif dbId == 'pc_CPFD':
            for li in li_s:
                url = 'http://kns.cnki.net' + li.css('a::attr(href)').extract_first()
                title = li.css('a::text').extract_first()
                if len(title) > 255:
                    title = title[:255]
                all_info = li.css('li::text').extract_first().split('\r\n')
                info = all_info[1]
                if len(info) > 255:
                    info = info[:255]
                issuing_time = all_info[2]
                if not ReferencesCPFD.objects.filter(url=url):
                    CPFD_item = ReferencesCPFDItem()
                    CPFD_item['url'] = url
                    CPFD_item['title'] = title
                    CPFD_item['info'] = info
                    CPFD_item['issuing_time'] = issuing_time
                    yield CPFD_item
                CPFD_list.append(str(ReferencesCPFD.objects.filter(url=url)[0].id))
        else:
            print('当前块所属库dbId错误!url=', response.url)

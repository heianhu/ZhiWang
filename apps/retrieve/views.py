from django.shortcuts import render, redirect, render_to_response
from django.views.generic import View
from retrieve.models import SearchFilter
from crawl_data.models import Summary, Detail, Authors, Periodicals, References, ReferencesCBBD, ReferencesCCND, \
    ReferencesCDFD, ReferencesCJFQ, ReferencesCPFD, ReferencesCMFD, ReferencesCRLDENG, ReferencesSSJD, Organization
from django.db.models import Q
import jieba
import jieba.posseg
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, FileResponse, JsonResponse, HttpResponseRedirect
from django.utils.http import urlquote
from django.http import Http404
import json
import time, os
import datetime
from retrieve.utils import write_to_excel, compress_excel


# Create your views here.

class IndexView(View):
    def get(self, request):
        if not request.session.session_key:
            request.session.save()
        return render(request, 'index.html', {
        })


class Search(View):
    def post(self, request):
        """
            'txt_2_sel': $('#txt_2_sel').val(),{# 主题选择 #}
            'txt_2_value1': $('#txt_2_value1').val(),{# 主题输入框1 #}
            'txt_2_relation':  $('#txt_2_relation').val(),{# 并行条件选择 #}
            'txt_2_value2': $('#txt_2_value2').val(),{# 主题输入框2 #}
            'au_1_sel': $('#au_1_sel').val(), {# 作者选择 #}
            'au_1_value1': $('#au_1_value1').val(),   {# 作者输入框 #}
            'magazine_value1': $('#magazine_value1').val(),{# 文献来源输入框 #}
        :param request:
        :return:
        """

        para = dict(
            txt_2_sel=request.POST.get('txt_2_sel', ''),  # 主题选择
            txt_2_value1=request.POST.get('txt_2_value1', ''),  # 主题输入框1
            txt_2_relation=request.POST.get('txt_2_relation', ''),  # 并行条件选择
            txt_2_value2=request.POST.get('txt_2_value2', ''),  # 主题输入框2
            # au_1_sel = request.POST.get('au_1_sel', '') # 作者选择  暂时没用
            au_1_value1=request.POST.get('au_1_value1', ''),  # 作者输入框
            au_special=request.POST.get('au_special', ''),  # 作者模糊/精准
            org_1_value=request.POST.get('org_1_value', ''),  # 组织
            org_1_special2=request.POST.get('org_1_special2', ''),  # 组织模糊/精准
            publishdate_from=request.POST.get('publishdate_from', ''),  # 起始年
            publishdate_to=request.POST.get('publishdate_to', ''),  # 截止年
            magazine_value1=request.POST.get('magazine_value1', ''),  # 文献来源输入框
            magazine_special=request.POST.get('magazine_special', '')  # 文献模糊/精准
        )

        search_filter = SearchFilter()
        search_filter.session_id = request.session.session_key
        queryId = str(time.time()).replace('.', '')
        search_filter.time = queryId
        search_filter.filterPara = str(para)
        search_filter.save()
        return redirect('/retrieve?queryId={}'.format(queryId))

    def get(self, request):
        """
        搜索功能
        目前能根据标题和作者，在被标记的期刊中的文献进行搜索
        :param request:
        :return:
        """
        # 获取关键词和搜索类型
        queryId = request.GET.get('queryId', '')
        curr_page = request.GET.get('page', '1')
        session_id = request.session.session_key
        try:
            search_filter = SearchFilter.objects.get(time=queryId, session_id=session_id)
        except KeyError:
            return render(request, 'index.html')

        search_filter = eval(search_filter.filterPara)

        all_articles = Search.get_query_set(search_filter)

        result_count = all_articles.count()

        # 分页功能
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_articles, 12, request=request)
        articles = p.page(page)
        search_filter.update({
            'all_articles': articles,
            'result_count': result_count
        })

        return render(request, 'index.html', search_filter)

    @staticmethod
    def get_query_set(search_filter):
        """
        由搜索条件获取查询数据集
        :param search_filter:搜索条件 dict
        :return: 结果数据集 queryset
        """
        try:
            txt_2_sel = search_filter.get('txt_2_sel', '')
            txt_2_value1 = search_filter.get('txt_2_value1', '')
            txt_2_relation = search_filter.get('txt_2_relation', '')
            txt_2_value2 = search_filter.get('txt_2_value2', '')
            au_1_value1 = search_filter.get('au_1_value1', '')
            org_1_value = search_filter.get('org_1_value', '')
            publishdate_from = search_filter.get('publishdate_from', '')
            publishdate_to = search_filter.get('publishdate_to', '')
            magazine_value1 = search_filter.get('magazine_value1', '')

            txt_2_sel_dic = {  # CNKI_AND CNKI_OR
                "SU": (Q(title__icontains=txt_2_value1), Q(title__icontains=txt_2_value2)),  # 标题
                "KY": (Q(detail__detail_keywords__icontains=txt_2_value1),
                       Q(detail__detail_keywords__icontains=txt_2_value2)),  # 关键词
                "AB": (Q(detail__detail_abstract__icontains=txt_2_value1),
                       Q(detail__detail_abstract__icontains=txt_2_value2)),  # 摘要
                "CLC$=|?": (Q(source__issn_number=txt_2_value1), Q(source__issn_number=txt_2_value1))  # 中图分类号
            }
            org_id = Organization.objects.filter(organization_name__icontains=org_1_value)[0]
            org_id = str(org_id.id)

            if publishdate_from and publishdate_to:
                publishdate_from = publishdate_from.split('-')
                date_from = datetime.datetime(int(publishdate_from[0]), int(publishdate_from[1]),
                                              int(publishdate_from[2]), 0, 0)
                publishdate_to = publishdate_to.split('-')
                date_to = datetime.datetime(int(publishdate_to[0]), int(publishdate_to[1]), int(publishdate_to[2]),
                                            0, 0)
                date_filter = Q(issuing_time__range=(date_from, date_to))
            else:
                date_filter = Q()

            else_sel = Q(authors__icontains=au_1_value1) & \
                       (Q(source__issn_number__icontains=magazine_value1) | Q(source__name__icontains=magazine_value1)) \
                       & (Q(detail__organizations__icontains=org_1_value) | Q(detail__organizations__icontains=org_id)) \
                       & date_filter

            if txt_2_relation == 'CNKI_AND':
                all_articles = Summary.objects.filter(
                    (txt_2_sel_dic[txt_2_sel][0] & txt_2_sel_dic[txt_2_sel][1]) & else_sel, source__mark=True)
            elif txt_2_relation == 'CNKI_OR':
                all_articles = Summary.objects.filter(
                    (txt_2_sel_dic[txt_2_sel][0] | txt_2_sel_dic[txt_2_sel][1]) & else_sel, source__mark=True)
            elif txt_2_relation == 'CNKI_NOT':
                all_articles = Summary.objects.filter(
                    txt_2_sel_dic[txt_2_sel][0] & else_sel, source__mark=True
                ).exclude(txt_2_sel_dic[txt_2_sel][1])
            else:
                response = render_to_response('404.html', {})
                response.status_code = 404
                return response
        except KeyError:
            response = render_to_response('404.html', {})
            response.status_code = 404
            return response

        return all_articles


class GetDetailInfo(View):
    def get(self, request, getdetailinfo_id):
        """
        处理下载单个文章
        :param getdetailinfo_id: summary文章的id
        :return: excel文件流
        """
        filename = write_to_excel(getdetailinfo_id)
        if not filename:
            response = render_to_response('404.html', {})
            response.status_code = 404
            return response
        file = open('media/excel/single/{0}'.format(filename), 'rb')
        response = FileResponse(file)

        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(urlquote(filename))

        return response


class DownloadSel(View):

    def post(self, request):
        """
        处理下载选择的多篇文章，由前端ajax发起请求
        生成多个excel文件并压缩zip
        :return: 生成的zip文件前缀
        """
        ids = request.POST.get('ids', '')
        # 将id转为整形列表并去除空白项
        ids = [int(id) for id in ids.split(',') if id]

        zip_name = compress_excel(ids)

        return JsonResponse({'status': 'success',
                             # 返回的data值将成为前端js请求下载压缩文件的url的参数
                             'data': zip_name.replace('.zip', ''),
                             }, content_type='application/json')


class DownloadZip(View):
    def get(self, request, zip_name):
        """
        处理下载zip文件请求
        :param request:
        :param zip_name: 不带后缀的zip文件名
        :return: 文件流
        """

        # 将勾选下载的压缩包归档到select文件夹
        os.rename('media/excel/{0}.zip'.format(zip_name),'media/excel/select/{0}.zip'.format(zip_name))
        file = open('media/excel/select/{0}.zip'.format(zip_name), 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(urlquote('downloadfile.zip'))

        return response


class DownloadAll(View):
    def get(self, request, query_id):
        """
        处理"下载全部"按钮
        :param request:
        :param query_id: 由查询条件生成的queryid
        :return:
        """

        session_id = request.session.session_key

        try:
            search_filter = SearchFilter.objects.get(time=query_id, session_id=session_id)
            # 将搜索条件哈希，作为zip文件名
            hash_str = hash(search_filter.filterPara)

        except KeyError:
            response = render_to_response('404.html', {})
            response.status_code = 404
            return response

        search_filter = eval(search_filter.filterPara)

        hash_filename = '{0}.zip'.format(hash_str)

        # zip文件未生成过,如果生成过了直接返回该文件
        if not os.path.isfile('media/excel/all/{0}'.format(hash_filename)):
            all_articles = Search.get_query_set(search_filter)

            ids = all_articles.values_list("id")
            # values_list返回的是单元素的元组构成的列表:[(123,),(456,)]，对其每个元素取第一项
            ids = map(lambda x: x[0], ids)
            zip_name = compress_excel(ids)

            # 将按时间戳生成的zip文件名改为按searchfilter哈希结果的文件名,并归档到all文件夹中
            os.rename('media/excel/{0}'.format(zip_name), 'media/excel/all/{0}'.format(hash_filename))

        file = open('media/excel/all/{0}'.format(hash_filename), 'rb')
        response = FileResponse(file)

        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(urlquote('downloadfile.zip'))

        return response

from django.shortcuts import render
from django.views.generic import View
from crawl_data.models import Summary, Detail, Authors, Periodicals, References
from crawl_data.models import ReferencesCBBD, ReferencesCCND, ReferencesCDFD, ReferencesCJFQ
from crawl_data.models import ReferencesCPFD, ReferencesCMFD, ReferencesCRLDENG, ReferencesSSJD
import jieba

import jieba.posseg
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, FileResponse
from django.utils.http import urlquote
from openpyxl import Workbook


# Create your views here.

class IndexView(View):
    def get(self, request):
        return render(request, 'index.html', {

        })


class Search(View):
    def get(self, request):
        """
        尚未处理空字符串传入情况
        :param request:
        :return:
        """
        keywords = request.GET.get('keywords', '')
        search_type = request.GET.get('s_type', '')
        if keywords.rsplit():
            if search_type == 'title':
                temp_articles = Summary.objects.filter(title__icontains=keywords, source__mark=True)
                if temp_articles:
                    all_articles = temp_articles
                else:
                    all_articles = Summary.objects.all()
                    seg_list = jieba.posseg.cut(keywords)
                    for seg, seg_tpye in seg_list:
                        if 'n' in seg_tpye or 'v' in seg_tpye:
                            all_articles = all_articles & Summary.objects.filter(title__icontains=seg,
                                                                                 source__mark=True)
            elif search_type == 'author':
                all_articles = Summary.objects.filter(authors__icontains=keywords, source__mark=True)
            else:
                return render(request, 'index.html')
        else:
            return render(request, 'index.html')

        # 分页功能
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_articles, 12, request=request)
        articles = p.page(page)

        return render(request, 'result.html', {
            'all_articles': articles,
            'search_type': search_type,
            'keywords': keywords,
            'result_count': all_articles.count()
        })


class GetDetailInfo(View):
    def get(self, request, getdetailinfo_id):
        summary_id = int(getdetailinfo_id)
        # 在Excel中插入数据，文件名为detail_id字段

        fields = ['FN', 'VR', 'PT', 'AU', 'AF', 'BA', 'CA', 'GP', 'BE', 'TI', 'SO', 'SE', 'BS', 'LA', 'DT',
                  'CT', 'CY', 'CL', 'SP', 'HO', 'DE', 'ID', 'AB', 'C1', 'RP', 'EM', 'FU', 'FX', 'CR', 'NR',
                  'TC', 'Z9', 'PU', 'PI', 'PA', 'SN', 'BN', 'J9', 'JI', 'PD', 'PY', 'VL', 'IS', 'SI', 'PN',
                  'SU', 'BP', 'EP', 'AR', 'DI', 'D2', 'PG', 'P2', 'WC', 'SC', 'GA', 'UT', 'ER', 'EF']

        values = { field:[i,''] for i, field in enumerate(fields)}

        article_summary = Summary.objects.get(id=summary_id)
        article_detail = Detail.objects.get(id=article_summary.detail_id)
        # 文件名
        values['FN'][1] = article_detail.detail_id
        # 作者
        values['AU'][1] = article_summary.authors
        # 标题
        values['TI'][1] = article_summary.title
        # 出版日期
        values['PD'][1] = article_summary.issuing_time
        # issn号
        values['SN'][1] = Periodicals.objects.get(id=article_summary.source_id).issn_number
        # 出版物名称
        values['SO'][1] = Periodicals.objects.get(id=article_summary.source_id).name
        # 摘要
        values['AB'][1] = article_detail.detail_abstract
        # 参考文献
        article_reference =  References.objects.get(id=article_detail.references_id)
        str_refer = ['CBBD', 'CDFD','CJFQ','CMFD','CRLDENG','SSJD','CCND','CPFD']
        refers = [] # 参考于各个期刊的id，每个期刊的id以列表形式存在 [[1,2],[3,4]]
        for refer in str_refer:
            refers.append(getattr(article_reference, refer).split())

        all_refers = [] # 每一项是相应期刊的查询集
        all_refers.append( ReferencesCBBD.objects.filter(id__in=refers[0]) )
        all_refers.append( ReferencesCDFD.objects.filter(id__in=refers[1]) )
        all_refers.append( ReferencesCJFQ.objects.filter(id__in=refers[2]) )
        all_refers.append( ReferencesCMFD.objects.filter(id__in=refers[3]) )
        all_refers.append( ReferencesCRLDENG.objects.filter(id__in=refers[4]) )
        all_refers.append( ReferencesSSJD.objects.filter(id__in=refers[5]) )
        all_refers.append( ReferencesCCND.objects.filter(id__in=refers[6]) )
        all_refers.append( ReferencesCPFD.objects.filter(id__in=refers[7]) )

        # 对每一条结果取title值
        all_refers_title = [refer.title for queryset in all_refers for refer in queryset]
        # 合并所有title
        title = ';'.join(all_refers_title)
        values['CR'][1] = title


        wb = Workbook()
        sheet = wb.get_active_sheet()

        for k, [i, v] in values.items():
            sheet.cell(row=i + 1, column=1).value = k
            sheet.cell(row=i + 1, column=2).value = v

        # 保存并返回下载
        filename = '{0}.xlsx'.format(article_detail.detail_id)
        wb.save('media/' + filename)
        file = open('media/{0}'.format(filename), 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(urlquote(filename))

        return response



from django.shortcuts import render
from django.views.generic import View
from crawl_data.models import Summary
import jieba
import jieba.posseg
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, FileResponse
from django.utils.http import urlquote


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
    def get(self, request, summary_id):
        summary_id = int(summary_id)
        # 在Excel中插入数据，文件名为detail_id字段


        # 保存并返回下载
        filename = 'detail_id字段'
        # newWb.save('media/{}.xls'.format(filename))
        file = open('media/{}.xls'.format(filename), 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}.xls"'.format(urlquote(filename))

        return response

from django.shortcuts import render
from django.views.generic import View
from crawl_data.models import Summary
import jieba
import jieba.posseg
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.db.models.query import QuerySet


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

        result_count = all_articles.count()

        # 进行分页
        limit = 20  # 每页显示的记录数
        paginator = Paginator(all_articles, limit)  # 实例化一个分页对象

        page = request.GET.get('page')  # 获取页码
        try:
            all_articles = paginator.page(page)  # 获取某页对应的记录
        except PageNotAnInteger:  # 如果页码不是个整数
            all_articles = paginator.page(1)  # 取第一页的记录
        except EmptyPage:  # 如果页码太大，没有相应的记录
            all_articles = paginator.page(paginator.num_pages)  # 取最后一页的记录

        return render(request, 'result.html', {
            'all_articles': all_articles,
            'result_count': result_count,
            'search_type': search_type,
            'keywords': keywords

        })

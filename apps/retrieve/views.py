from django.shortcuts import render
from django.views.generic import View


# Create your views here.

class IndexView(View):
    def get(self, request):
        return render(request, 'index.html', {
        })


class Search(View):
    def get(self, request):
        print('dsf')

        search_keywords = request.GET.get('keywords', '')
        print(search_keywords)
        return render(request, 'index.html', {
        })

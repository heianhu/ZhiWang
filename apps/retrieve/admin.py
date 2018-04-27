from django.contrib import admin

from django.contrib import admin

from .models import SearchFilter


class SearchFilterAdmin(admin.ModelAdmin):

    list_display = ['username', 'filterPara', 'search_time']


admin.site.register(SearchFilter, SearchFilterAdmin)  # 将其注册

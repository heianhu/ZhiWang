#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'

from django.conf.urls import url, include
from .views import Search, GetDetailInfo, DownloadSel, DownloadZip, DownloadAll


urlpatterns = [
    url(r'^download/(?P<getdetailinfo_id>\d+)/$', GetDetailInfo.as_view(), name='getdetailinfo'),
    url(r'^downloadSel/$', DownloadSel.as_view(), name='downloadSel'),
    url(r'^downloadzip/(?P<zip_name>\d+)/$', DownloadZip.as_view(), name='downloadzip'),
    url(r'^downloadall/(?P<query_id>\d+)/$', DownloadAll.as_view(), name='downloadall'),

]
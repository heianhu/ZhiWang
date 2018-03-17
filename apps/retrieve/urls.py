#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'

from django.conf.urls import url, include
from .views import Search, GetDetailInfo


urlpatterns = [
    url(r'^$', Search.as_view(), name='retrieve'),

    url(r'^download/(?P<getdetailinfo_id>\d+)/$', GetDetailInfo.as_view(), name='getdetailinfo'),

]
# -*-coding=utf-8-*-
__author__ = 'Eeljiang'
__date__ = '2018/5/8 16:01'

from django import template
register = template.Library()


@register.filter
def multiply(value, num):
    # 自定义一个乘法过滤器以计算分页后搜索结果中文章的序号
    return (int(value)-1) * int(num)


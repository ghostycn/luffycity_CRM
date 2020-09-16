#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.urls import reverse
from django.http import QueryDict

def memory_reverse(request,name,*args,**kwargs):
    """
    反向生成URL
    :param request:
    :param name:
    :param args:
    :param kwargs:
    :return:
    """
    url = reverse(name,args=args,kwargs=kwargs)
    origin_params = request.GET.get('_filter')
    if origin_params:
        url = "%s?%s" % (url, origin_params)
    return url

def memory_url(request,name,*args,**kwargs):
    """
    生成带有原搜索条件的URL（替代了模版中的url）
    :param request:
    :param name:
    :return:
    """

    basic_url = reverse(name,args=args,kwargs=kwargs)
    if not request.GET:
        return basic_url

    query_dict = QueryDict(mutable=True)
    query_dict["_filter"] = request.GET.urlencode()
    return "%s?%s" % (basic_url,query_dict.urlencode())
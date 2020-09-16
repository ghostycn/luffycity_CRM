#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from django.urls.resolvers import URLResolver,URLPattern
from collections import OrderedDict
from django.conf import settings
from django.utils.module_loading import import_string

def check_url_exclude(url):
    """
    排除一些特定的url
    :param url:
    :return:
    """

    for regex in settings.AUTO_DISCOVER_EXCLUDE:
        if re.match(regex,url):
            return True

def recursion_urls(pre_namespace, pre_url, urlpatterns, url_ordered_dict):
    """
    递归的去获取URl
    :param pre_namespace: name前缀，以后用于拼接name
    :param pre_url: url前缀，以后用于拼接url
    :param urlpatterns: 路由关系列表
    :param url_ordered_dict: 用于保存递归中获取的所有的路由
    :return:
    """
    for item in urlpatterns:
        if isinstance(item,URLPattern): # 非路由分发，将路由添加到url_ordered_dict
            # print(item)
            if not item.name:
                continue

            if pre_namespace:
                name = "%s:%s" % (pre_namespace,item.name)
            else:
                name = item.name
            url = pre_url + item.pattern.regex.pattern.strip("^$")
            if check_url_exclude(url):
                continue
            url_ordered_dict[name] = {"name": name, "url":url}
        elif isinstance(item,URLResolver): # 路由分发，递归
            # print(item.namespace)
            if pre_namespace:
                if item.namespace:
                    namespace = "%s:%s" %(pre_namespace,item.namespace)
                else:
                    namespace = item.namespace
            else:
                if item.namespace:
                    namespace = item.namespace
                else:
                    namespace = None

            recursion_urls(namespace,  pre_url + item.pattern.regex.pattern.strip("^$"), item.url_patterns, url_ordered_dict)  # 递归去获取所有的路由


def get_all_url_dict():
    """
    获取项目中的所有URL
    :return:
    """
    url_ordered_dict = OrderedDict()
    md = import_string(settings.ROOT_URLCONF) # from luffy .. import urls

    recursion_urls(None, "/", md.urlpatterns, url_ordered_dict) # 递归去获取所有的路由

    return url_ordered_dict

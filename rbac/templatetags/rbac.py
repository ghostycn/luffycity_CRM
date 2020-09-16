#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.template import Library
from django.conf import settings
from collections import OrderedDict
from django.urls import reverse
from django.http import QueryDict
from rbac.service import urls
import re

register = Library()


@register.inclusion_tag('rbac/static_menu.html')
def static_menu(request):
    """
    创建一级菜单
    :return:
    """
    menu_list = request.session[settings.MENU_SESSION_KEY]
    for item in menu_list:
        regex = "^%s$" % (item['url'],)
        if re.match(regex, request.path_info):
            item['class'] = 'active'

    return {'menu_list': menu_list}

@register.inclusion_tag('rbac/multi_menu.html')
def multi_menu(request):
    """
    创建二级菜单
    :return:
    """
    """生成菜单"""

    menu_dict = request.session.get(settings.MENU_SESSION_KEY)
    key_list = sorted(menu_dict)

    ordered_dict = OrderedDict()
    for key in key_list:
        val = menu_dict[key]
        val['class'] = 'hide'
        for per in val['children']:
            if per["id"] == request.current_selected_permission:
                per['class'] = 'active'
                val['class'] = ''
        ordered_dict[key] = val
    return {
        'menu_dict': ordered_dict
    }

@register.inclusion_tag('rbac/url_record.html')
def url_record(request):
    return {"url_list":request.url_record}

@register.filter
def has_permission(request,name):
    """
    最多只能传递两个参数：request|has_permission:"customer_add"
    :param request:
    :param name:
    :return:
    """
    if name in request.session[settings.PERMISSION_SESSION_KEY]:
        return True

@register.simple_tag
def memory_url(request,name,*args,**kwargs):
    """
    生成带有原搜索条件的URL（替代了模版中的url）
    :param request:
    :param name:
    :return:
    """



    return urls.memory_url(request,name,*args,**kwargs)
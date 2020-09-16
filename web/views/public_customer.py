#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.utils.safestring import mark_safe
from django.shortcuts import HttpResponse,render
from django.urls import re_path
from django.db import transaction
from stark.service.v1 import StarkHander, get_choice_text, get_m2m_text, StarkModelForm
from web import models
from .base import PermissionHandler


class PublicCustomerModelForm(StarkModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant', ]


class PublicCustomerHandler(PermissionHandler,StarkHander):

    def display_record(self, obj=None, is_header=None):
        if is_header:
            return "跟进记录"
        record_url = self.reverse_commons_url(self.get_url_name('record_view'),pk=obj.pk)
        return mark_safe("<a href='%s'>查看跟进记录</a>" %record_url)

    def get_queryset(self, request, *args, **kwargs):
        return self.model_class.objects.filter(consultant__isnull=True)

    def extra_urls(self):
        patterns = [
            re_path(r'record/(?P<pk>\d+)/$', self.wapper(self.record_view), name=self.get_url_name("record_view"))
        ]
        return patterns

    def record_view(self, request, pk):
        """
        查看跟进记录的视图
        :param request:
        :param pk:
        :return:
        """
        record_list = models.ConsultRecord.objects.filter(customer_id=pk)
        return render(request, 'record_view.html', {'record_list': record_list})

    model_form_class = PublicCustomerModelForm

    list_display = [StarkHander.display_checkbox,'name', 'qq', get_m2m_text('咨询课程', 'course'), display_record, get_choice_text('状态', 'status')]

    def action_multi_apply(self,request,*args,**kwargs):
        """
        批量申请公户到私户
        :param request:
        :return:
        """
        current_user_id = request.session['user_info']['id']

        # 客户ID
        pk_list = request.POST.getlist("pk")

        # 将选中的客户更新到我的账户(consultant=当前自己)

        private_customer_count = models.Customer.objects.filter(consultant_id=current_user_id,status=2).count()

        # 私户个数限制
        if (private_customer_count + len(pk_list)) > models.Customer.MAX_PRIVATE_CUSTOMER_COUNT:
            return HttpResponse("私户中已有%s个客户，最多只能申请%s" %(private_customer_count, models.Customer.MAX_PRIVATE_CUSTOMER_COUNT - private_customer_count))

        # 数据库中加锁

        flag = False
        with transaction.atomic(): # 事务
            # 在数据库中加锁
            origin_queryset = models.Customer.objects.filter(id__in=pk_list,status=2,consultant__isnull=True).select_for_update()

            if len(origin_queryset) == len(pk_list):
                models.Customer.objects.filter(id__in=pk_list,status=2,consultant__isnull=True).update(consultant_id=current_user_id)
                flag = True
        if not flag:
            return HttpResponse("选中的客户已被其他人申请走，请重新选择")

    action_multi_apply.text = "申请到我的私户"

    action_list = [action_multi_apply]




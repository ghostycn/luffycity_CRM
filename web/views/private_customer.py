#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.utils.safestring import mark_safe
from django.urls import reverse
from stark.service.v1 import StarkHander,get_m2m_text,get_choice_text,StarkModelForm
from web import models
from .base import PermissionHandler

class PrivateCustomerModelForm(StarkModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant', ]

class PrivateHandler(PermissionHandler,StarkHander):

    model_form_class = PrivateCustomerModelForm

    def display_record(self, obj=None, is_header=None,*args,**kwargs):
        if is_header:
            return "跟进记录"
        record_url = reverse('stark:web_consultrecord_list',  kwargs={"customer_id":obj.pk})
        return mark_safe("<a target='_blank' href='%s'>跟进记录</a>" % record_url)

    def display_payment(self, obj=None, is_header=None,*args,**kwargs):
        if is_header:
            return "缴费记录"
        record_url = reverse('stark:web_paymentrecord_list',  kwargs={"customer_id":obj.pk})
        return mark_safe("<a target='_blank' href='%s'>缴费记录</a>" % record_url )

    list_display = [StarkHander.display_checkbox,'name', 'qq', get_m2m_text('咨询课程', 'course'), display_record,display_payment,get_choice_text('状态', 'status')]

    def get_queryset(self, request, *args, **kwargs):

        current_user_id = request.session['user_info']['id']

        return self.model_class.objects.filter(consultant_id=current_user_id)

    def save(self,request,form,is_update,*args,**kwargs):
        if not is_update:
            current_user_id = request.session['user_info']['id']
            form.instance.consultant_id = current_user_id
        form.save()

    def action_multi_apply(self,request,*args,**kwargs):
        """
        批量将私移除到公户
        :param request:
        :return:
        """
        current_user_id = request.session['user_info']['id']

        # 客户ID
        pk_list = request.POST.getlist("pk")

        self.model_class.objects.filter(id__in=pk_list,consultant_id=current_user_id).update(consultant=None)

    action_multi_apply.text = "移除到公户"

    action_list = [action_multi_apply]
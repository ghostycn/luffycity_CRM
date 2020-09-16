#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.urls import re_path
from django.utils.safestring import mark_safe
from django.shortcuts import HttpResponse
from stark.service.v1 import StarkHander,StarkModelForm
from web import models
from .base import PermissionHandler

class ConsultRecordModelForm(StarkModelForm):
    class Meta:
        model = models.ConsultRecord
        fields = ['note',]

class ConsultRecordHandler(PermissionHandler,StarkHander):

    model_form_class = ConsultRecordModelForm

    list_display = ['note','consultant','date']

    change_list_template = 'consult_record.html'

    def get_urls(self):

        patterns = [
            re_path(r'^list/(?P<customer_id>\d+)/$', self.wapper(self.changelist_view), name=self.get_list_url_name),
            re_path(r'^add/(?P<customer_id>\d+)/$', self.wapper(self.add_view), name=self.get_add_url_name),
            re_path(r'^change/(?P<customer_id>\d+)/(?P<pk>\d+)/$', self.wapper(self.change_view), name=self.get_change_url_name),
            re_path(r'^delete/(?P<customer_id>\d+)/(?P<pk>\d+)/$', self.wapper(self.delete_view), name=self.get_delete_url_name)
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def get_queryset(self, request, *args, **kwargs):

        customer_id = kwargs.get("customer_id")
        current_user_id = request.session['user_info']['id']

        return self.model_class.objects.filter(customer_id=customer_id,customer__consultant_id=current_user_id)

    def save(self,request,form,is_update,*args,**kwargs):
        customer_id = kwargs.get('customer_id')
        current_user_id = request.session['user_info']['id']
        object_exists = models.Customer.objects.filter(id=customer_id,
                                                       consultant_id=current_user_id).exists()
        if not object_exists:

            return HttpResponse("非法操作")

        if not is_update:
            form.instance.customer_id = customer_id
            form.instance.consultant_id = current_user_id
        form.save()

    def display_edit_del(self, obj=None, is_header=None,*args,**kwargs):
        customer_id = kwargs.get('customer_id')
        if is_header:
            return "操作"
        tpl = "<a href='%s'>编辑</a> | <a href='%s'>删除</a>" %(self.reverse_change_url(pk=obj.pk,customer_id=customer_id),self.reverse_delete_url(pk=obj.pk,customer_id=customer_id))
        return mark_safe(tpl)

    def get_change_object(self,request,pk,*args,**kwargs):


        customer_id = kwargs.get("customer_id")
        current_user_id = request.session['user_info']['id']

        return models.ConsultRecord.objects.filter(pk=pk,
                                                   customer_id=customer_id,
                                                   customer__consultant_id=current_user_id).first()

    def delete_object(self,request,pk,*args,**kwargs):
        customer_id = kwargs.get("customer_id")
        current_user_id = request.session['user_info']['id']
        print(customer_id,current_user_id)
        record_queryset = models.ConsultRecord.objects.filter(pk=pk,
                                           customer_id=customer_id,
                                           customer__consultant_id=current_user_id)
        print(record_queryset)
        if not record_queryset.exists():
            return HttpResponse("要删除的记录不存在，请重新选择")
        record_queryset.delete()
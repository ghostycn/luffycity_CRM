#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.urls import re_path
from django.utils.safestring import mark_safe
from django.urls import reverse
from stark.service.v1 import StarkHander,get_choice_text,get_m2m_text,StarkModelForm,SearchOption
from web import models
from .base import PermissionHandler

class StudentModelForm(StarkModelForm):
    class Meta:
        model = models.Student
        fields = ["qq","mobile","emergency_contract","memo"]


class StudentHandler(PermissionHandler,StarkHander):

    model_form_class = StudentModelForm

    def display_score(self, obj=None, is_header=None,*args,**kwargs):
        if is_header:
            return "积分管理"
        record_url = reverse('stark:web_scorerecord_list', kwargs={"student_id": obj.pk})
        return mark_safe("<a target='_blank' href='%s'>%s</a>" %(record_url,obj.score))


    list_display = ["customer","qq","mobile","emergency_contract",get_m2m_text("已报班级","class_list"),
                    display_score,get_choice_text("状态","student_status")]

    def get_add_btn(self,request,*args,**kwargs):

        return None

    def get_list_display(self):

        value = []

        if self.list_display:

            value.extend(self.list_display)
            # 设置默认添加编辑与删除按钮
            value.append(StarkHander.display_edit)

        return value

    def get_urls(self):

        patterns = [
            re_path(r'^list/$', self.wapper(self.changelist_view), name=self.get_list_url_name),
            re_path(r'^change/(?P<pk>\d+)/$', self.wapper(self.change_view), name=self.get_change_url_name)
        ]

        patterns.extend(self.extra_urls())
        return patterns

    search_list = ["customer__name","qq","monile"]

    search_group = [
        SearchOption("class_list",text_func=lambda x:'%s-%s' %(x.school.title,str(x)))
    ]

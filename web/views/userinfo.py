#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from stark.service.v1 import StarkModelForm,ModelForm,StarkHander,SearchOption,get_choice_text
from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import render,redirect
from django.urls import re_path
from django.utils.safestring import mark_safe
from web.utils.md5 import gen_md5
from web import models
from .base import PermissionHandler

class UserInfoAddModelForm(StarkModelForm):
    confirm_password = forms.CharField(label="确认密码")

    class Meta:
        model = models.UserInfo
        fields = ["name","password","confirm_password","nickname","gender","phone","email","depart","roles"]

    def clean_confirm_password(self):
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data["confirm_password"]

        if password != confirm_password:
            raise ValidationError("密码输入不一致")
        return confirm_password

    def clean(self):
        password = self.cleaned_data["password"]
        self.cleaned_data["password"] = gen_md5(password)
        return self.cleaned_data


class UserInfoChangeModelForm(PermissionHandler,StarkModelForm):

    class Meta:
        model = models.UserInfo
        fields = ["name","nickname","gender","phone","email","depart","roles"]

class ResetPasswordForm(ModelForm):

    password = forms.CharField(label="密码",widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="确认密码",widget=forms.PasswordInput)

    def clean_confirm_password(self):
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data["confirm_password"]

        if password != confirm_password:
            raise ValidationError("密码输入不一致")
        return confirm_password

    def clean(self):
        password = self.cleaned_data["password"]
        self.cleaned_data["password"] = gen_md5(password)
        return self.cleaned_data

class UserInfoHander(StarkHander):
    per_page_count = 2

    def display_reset_pwd(self, obj=None, is_header=None,*args,**kwargs):

        if is_header:
            return "重置密码"
        reset_url = self.reverse_reset_pwd_url(pk=obj.pk)
        return mark_safe("<a href='%s'>重置密码</a>" %reset_url)


    list_display = ['nickname',get_choice_text("性别",'gender'),'phone','email','depart',display_reset_pwd]

    def get_model_form_class(self,is_add,request,pk=None,*args,**kwargs):
        """
        定制添加和编辑页面的model_form的定制
        :param add_or_change:
        :return:
        """

        if is_add:
            return UserInfoAddModelForm
        return UserInfoChangeModelForm

    def reset_password(self,request,pk):

        userinfo_object = models.UserInfo.objects.filter(id=pk).first()

        if request.method == "GET":
            form = ResetPasswordForm()
            return render(request,'stark/change.html',{"form":form})
        form = ResetPasswordForm(data=request.POST)
        if form.is_valid():
            # 密码更新到数据库
            userinfo_object.password = form.cleaned_data["password"]
            userinfo_object.save()
            return redirect(self.reverse_list_url())
        return render(request, 'stark/change.html', {"form": form})
    @property
    def get_reset_pwd_url_name(self):
        return self.get_url_name("rest_pwd")

    def extra_urls(self):
        patterns = [
            re_path(r'^reset/password/(?P<pk>\d+)/$', self.wapper(self.reset_password), name=self.get_reset_pwd_url_name)
        ]
        return patterns

    def reverse_reset_pwd_url(self, *args, **kwargs):
        # # 生成带有原搜素条件的重置密码URL
        return self.reverse_commons_url(self.get_reset_pwd_url_name,*args,**kwargs)

    search_list = ["nickname__contains",'name__contains']

    search_group = [
        SearchOption("gender"),
        SearchOption("depart",is_multi=True)
    ]
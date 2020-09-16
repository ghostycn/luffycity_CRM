#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from rbac import models
from rbac.forms.base import BootStrapModelForm
class UserModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(label="确认密码")

    class Meta:
        model = models.UserInfo
        fields = ["name","email","password","confirm_password"]


    def clean_confirm_password(self):
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data["confirm_password"]
        if password != confirm_password:
            raise ValidationError("两次密码数据不一致")
        return confirm_password

    def clean_name(self):
        name = self.cleaned_data["name"]
        obj = models.UserInfo.objects.filter(name=name)
        if obj:
            raise ValidationError("用户名已经存在")
        return name

class UpdateUserModelForm(BootStrapModelForm):

    class Meta:
        model = models.UserInfo
        fields = ["name","email"]

    def clean_name(self):
        name = self.cleaned_data["name"]
        obj = models.UserInfo.objects.filter(name=name)
        if obj:
            raise ValidationError("用户名已经存在")
        return name

class ResetPasswordUserModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(label="确认密码")

    class Meta:
        model = models.UserInfo
        fields = ["password","confirm_password"]




    def clean_confirm_password(self):
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data["confirm_password"]
        if password != confirm_password:
            raise ValidationError("两次密码数据不一致")
        return confirm_password
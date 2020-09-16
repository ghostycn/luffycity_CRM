#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色管理
"""
from django.shortcuts import render,redirect,HttpResponse
from django.urls import reverse
from rbac import models
from rbac.forms.user import UserModelForm,UpdateUserModelForm,ResetPasswordUserModelForm

def user_list(request):
    """
    用户列表
    :param request:
    :return:
    """
    user_queryset = models.UserInfo.objects.all()

    return render(request,"rbac/user_list.html",{"users":user_queryset})

def user_add(request):
    """
    添加用户
    :param request:
    :return:
    """
    if request.method == "GET":
        form = UserModelForm()
        return render(request, 'rbac/change.html', {"form":form})
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse('user_list'))
    return render(request, 'rbac/change.html', {"form": form})

def user_edit(request,pk):
    """
    编辑用户
    :param request:
    :param pk:
    :return:
    """
    obj = models.UserInfo.objects.filter(id=pk).first()

    if not obj:
        return HttpResponse("用户不存在")
    if request.method == "GET":
        form = UpdateUserModelForm(instance=obj)
        return render(request, 'rbac/change.html', {"form":form})
    form = UpdateUserModelForm(instance=obj,data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse('user_list'))
    return render(request, 'rbac/change.html', {"form": form})

def user_del(request,pk):
    """
    删除用户
    :param request:
    :param pk:
    :return:
    """
    origin_url = reverse('user_list')
    if request.method == "GET":
        return render(request,'rbac/delete.html',{"cancel":origin_url})
    elif request.method == "POST":
        models.UserInfo.objects.filter(id=pk).delete()
        return redirect(origin_url)

def user_reset_pwd(request,pk):
    """
    重置密码
    :param request:
    :param pk:
    :return:
    """
    obj = models.UserInfo.objects.filter(id=pk).first()

    if not obj:
        return HttpResponse("用户不存在")
    if request.method == "GET":
        form = ResetPasswordUserModelForm()
        return render(request, 'rbac/change.html', {"form": form})
    form = ResetPasswordUserModelForm(instance=obj, data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse('user_list'))
    return render(request, 'rbac/change.html', {"form": form})


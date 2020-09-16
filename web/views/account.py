#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.shortcuts import render,redirect,HttpResponse,reverse
from web import models
from web.utils.md5 import gen_md5
from rbac.service.init_permission import init_permission
def login(request):
    """

    :param request:
    :return:
    """
    if request.method == "GET":
        return render(request,'login.html')

    user = request.POST.get("username")
    password = gen_md5(request.POST.get("password",""))
    user_object = models.UserInfo.objects.filter(name=user,password=password).first()
    if not user_object:
        return render(request,'login.html',{"error":"用户名或密码错误"})



    request.session["user_info"] = {"id":user_object.id, "nickname":user_object.nickname}

    # 用户权限信息初始化
    init_permission(user_object,request)

    return redirect('/index')


def logout(request):
    """

    :param request:
    :return:
    """
    request.session.delete()
    return redirect('/login/')

def index(request):
    """

    :param request:
    :return:
    """

    if request.method == "GET":
        return render(request,"index.html")

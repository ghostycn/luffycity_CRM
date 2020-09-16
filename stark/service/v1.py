#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.urls import path,re_path
from django.shortcuts import HttpResponse,render,redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import QueryDict
from django import forms
from django.db.models import ForeignKey,ManyToManyField
# Q 查询用于构造负责的ORM查询条件
from django.db.models import Q
from types import FunctionType
from stark.utils.pagination import Pagination
import functools

def get_choice_text(title,field):
    """
    对于Stark组件中定义列时，choice如果想要显示中文信息，调用此方法即可
    :param title: 页面显示的表头
    :param field: 字段名称
    :return:
    """
    def inner(self,obj=None,is_header=None,*args,**kwargs):

        if is_header:
            return title
        method = "get_%s_display" %field

        return getattr(obj,method)()
    return inner

def get_datetime_text(title,field,time_format='%Y-%m-%d'):
    """
    对于Stark组件中定义列时，获取格式化时间
    :param title: 页面显示的表头
    :param field: 字段名称
    :param time_format: 要格式化的时间格式
    :return:
    """
    def inner(self,obj=None,is_header=None,*args,**kwargs):

        if is_header:
            return title

        datatime_value = getattr(obj,field)
        return datatime_value.strftime(time_format)
    return inner

def get_m2m_text(title,field):
    """
    对于Stark组件中定义列时，显示manytomany文本信息
    :param title: 页面显示的表头
    :param field: 字段名称
    :param time_format: 要格式化的时间格式
    :return:
    """
    def inner(self,obj=None,is_header=None):

        if is_header:
            return title

        queryset = getattr(obj,field).all()
        text_list =  [str(row) for row in queryset]
        return '.'.join(text_list)
    return inner

class StarkModelForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        super(StarkModelForm,self).__init__(*args,**kwargs)
        # 统一给ModelForm生成字段添加样式
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

class ModelForm(forms.Form):

    def __init__(self,*args,**kwargs):
        super(ModelForm,self).__init__(*args,**kwargs)
        # 统一给ModelForm生成字段添加样式
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

class SearchGroupRow(object):

    def __init__(self,queryset_or_tuple,option,query_dict):
        """

        :param queryset_or_tuple: 组合搜索关联获取到的数据
        :param option: 配置
        :param query_dict: request.GET
        """
        self.queryset_or_tuple = queryset_or_tuple
        self.option = option
        self.query_dict = query_dict

    def __iter__(self):
        yield "<div class='whole'>"
        yield self.option.title
        yield "</div>"

        yield "<div class='others'>"
        total_query_dict = self.query_dict.copy()
        total_query_dict._mutable = True

        origin_value_list = self.query_dict.getlist(self.option.field)
        if not origin_value_list:
            yield "<a href='#' class='active'>全部</a>"
        else:
            total_query_dict.pop(self.option.field)

            yield "<a href='?%s'>全部</a>" % total_query_dict.urlencode()

        for item in self.queryset_or_tuple:
            text = self.option.get_text(item)
            value = str(self.option.get_value_func(item))
            # 需要request.GET
            # 获取组合搜索按钮文本背后对应的值
            query_dict = self.query_dict.copy()
            query_dict._mutable = True


            if not self.option.is_multi:
                query_dict[self.option.field] = value
                if value in origin_value_list:
                    query_dict.pop(self.option.field)
                    yield "<a href='?%s' class='active'>%s</a>" % (query_dict.urlencode(),text)
                else:
                    yield "<a href='?%s'>%s</a>" % (query_dict.urlencode(),text)

            else:
                multi_value_list = query_dict.getlist(self.option.field)

                if value in multi_value_list:
                    multi_value_list.remove(value)
                    query_dict.setlist(self.option.field,multi_value_list)
                    yield "<a href='?%s' class='active'>%s</a>" % (query_dict.urlencode(),text)

                else:
                    multi_value_list.append(value)
                    query_dict.setlist(self.option.field,multi_value_list)
                    yield "<a href='?%s'>%s</a>" % (query_dict.urlencode(),text)

        yield "</div>"

class SearchOption(object):

    def __init__(self,field,is_multi=None,db_condition=None,text_func=None,value_func=None):
        """

        :param field: 组合搜索关联的字段
        :param is_multi: 是否支持多选
        :param db_condition: 数据库关联查询时的条件
        :param text_func: 此函数用于显示组合搜索按钮页面文本
        :param value_func: 此函数用于显示组合搜索按钮值
        """
        self.field = field
        self.is_multi = is_multi
        if not db_condition:
            db_condition = {}
        self.db_condition = db_condition
        self.text_func = text_func
        self.is_choice = False
        self.value_func = value_func

    def get_db_condition(self,request,*args,**kwargs):
        return self.db_condition

    def get_queryset_or_tuple(self,model_class,request,*args,**kwargs):
        # 根据字符串，找到对应Model类中的字段对象
        field_object = model_class._meta.get_field(self.field)
        self.title = field_object.verbose_name

        # 再根据对象去获取关联对象
        if isinstance(field_object, ForeignKey) or isinstance(field_object, ManyToManyField):
            # ForeignKey 和 ManyToManyField，应该去获取关联表中的数据
            db_condition = self.get_db_condition(request)
            data = field_object.remote_field.model.objects.filter(**db_condition)
            return SearchGroupRow(data,self,request.GET)

        else:
            # 获取choice中的数据
            self.is_choice = True
            return SearchGroupRow(field_object.choices,self,request.GET)

    def get_text(self,field_object):
        """
        获取文本函数
        :param field_object:
        :return:
        """

        if self.text_func:
            return self.text_func(field_object)

        if self.is_choice:
            return field_object[1]
        return str(field_object)

    def get_value_func(self,field_object):

        if self.value_func:
            return self.value_func(field_object)

        if self.is_choice:
            return field_object[0]
        return field_object.pk

class StarkHander(object):

    list_display = []
    per_page_count = 10
    has_add_btn = True

    change_list_template = None
    change_template = None
    delete_template = None

    def __init__(self,site,model_class,prev):
        self.model_class = model_class
        self.prev = prev
        self.site = site
        self.request = None

    def action_multi_delete(self,request,*args,**kwargs):
        """
        批量删除
        :param request:
        :return:
        """
        pk_list = request.POST.getlist("pk")

        self.model_class.objects.filter(id__in=pk_list).delete()

    action_multi_delete.text = "批量删除"

    search_group = []

    def get_search_group(self):
        return self.search_group

    def get_search_group_condition(self,request):
        """
        获取组合搜索的条件
        :param request:
        :return:
        """
        condition = {}
        for option in self.get_search_group():
            if option.is_multi:
                values_list = request.GET.getlist(option.field)
                if not values_list:
                    continue
                condition["%s__in" %option.field] = values_list
            else:
                value = request.GET.get(option.field)
                if not value:
                    continue
                condition[option.field] = value
        return condition

    action_list = []

    def get_action_list(self):
        return self.action_list

    search_list = []

    def get_search_list(self):
        return self.search_list

    order_list = []

    def get_order_list(self):
        return self.order_list or ["id"]

    def reverse_commons_url(self,name,*args,**kwargs):
        # # 生成带有原搜素条件的URL
        name = "%s:%s" % (self.site.namespace, name)
        base_url = reverse(name,args=args,kwargs=kwargs)
        if not self.request.GET:
            add_url = base_url
        else:
            param = self.request.GET.urlencode()
            new_query_dict = QueryDict(mutable=True)
            new_query_dict['_filter'] = param
            add_url = "%s?%s" % (base_url, new_query_dict.urlencode())
        return add_url

    def reverse_add_url(self,*args,**kwargs):
        # 生成带有原搜素条件的添加URL
        return self.reverse_commons_url(self.get_add_url_name,*args,**kwargs)

    def reverse_change_url(self,*args,**kwargs):
        # # 生成带有原搜素条件的编辑URL
        return self.reverse_commons_url(self.get_change_url_name, *args, **kwargs)

    def reverse_delete_url(self,*args,**kwargs):
        # # 生成带有原搜素条件的删除URL
        return self.reverse_commons_url(self.get_delete_url_name, *args, **kwargs)

    def reverse_list_url(self,*args,**kwargs):

        """
        跳转回列表页面时，生成URl
        :return:
        """
        name = "%s:%s" % (self.site.namespace, self.get_list_url_name)
        base_url = reverse(name,args=args,kwargs=kwargs)
        param = self.request.GET.get('_filter')
        if not param:
            return base_url
        return "%s?%s" % (base_url, param)

    def get_add_btn(self,request,*args,**kwargs):
        if self.has_add_btn:
            add_url = self.reverse_add_url(*args,**kwargs)
            return "<a class='btn btn-primary' href='%s'>添加</a>" %add_url
        return None

    def display_checkbox(self, obj=None, is_header=None,*args,**kwargs):
        """
        自定义批量操作
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "选择"
        return mark_safe('<input type="checkbox" name="pk" value="%s" />' %obj.pk)

    def display_edit(self, obj=None, is_header=None,*args,**kwargs):
        """
        自定义页面显示的列 （表头和内容）
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "编辑"
        # name = "%s:%s" % (self.site.namespace, self.get_change_url_name)
        #
        # url = reverse(name, args=(obj.pk,))
        url = self.reverse_change_url(pk=obj.pk)
        return mark_safe("<a href='%s'>编辑</a>" % url)

    def display_del(self, obj=None, is_header=None,*args,**kwargs):
        """
        自定义页面显示的列 （表头和内容）
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "删除"

        url = self.reverse_delete_url(pk=obj.pk)
        return mark_safe("<a href='%s'>删除</a>" % url)

    def display_edit_del(self, obj=None, is_header=None,*args,**kwargs):
        if is_header:
            return "操作"
        tpl = "<a href='%s'>编辑</a> | <a href='%s'>删除</a>" %(self.reverse_change_url(pk=obj.pk),self.reverse_delete_url(pk=obj.pk))
        return mark_safe(tpl)

    def get_list_display(self,request,*args,**kwargs):

        value = []

        if self.list_display:

            value.extend(self.list_display)
            # 设置默认添加编辑与删除按钮
            # value.append(StarkHander.display_edit)
            # value.append(StarkHander.display_del)
            value.append(type(self).display_edit_del)


        return value

    model_form_class =None

    def get_model_form_class(self,is_add,request,pk=None,*args,**kwargs):

        if self.model_form_class:
            return self.model_form_class

        class DynamicModelForm(StarkModelForm):
            class Meta:
                model = self.model_class
                fields = "__all__"

        return DynamicModelForm

    def save(self,request,form,is_update,*args,**kwargs):
        """
        再使用ModelForm保存数据之前预留的钩子方法
        :param form:
        :param is_update:
        :return:
        """
        form.save()

    def get_queryset(self, request, *args, **kwargs):
        return self.model_class.objects

    def changelist_view(self,request,*args,**kwargs):
        """
        列表页面
        :param request:
        :return:
        """
        # start 组合搜索


        search_group = self.get_search_group()
        search_group_row_list = []
        for search_option_obj in search_group:
            row = search_option_obj.get_queryset_or_tuple(model_class=self.model_class,request=request,*args,**kwargs)
            search_group_row_list.append(row)
        # end 组合搜索


        # start 处理action

        action_list = self.get_action_list()


        action_dict = {i.__name__:i.text for i in action_list}

        if request.method == "POST":
            action_func_name = request.POST.get("action")
            if action_func_name and action_func_name in action_dict:
                action_response = getattr(self,action_func_name)(request,*args,**kwargs)
                if action_response:
                    return action_response

        # end 处理action


        # start search
        search_list = self.get_search_list()
        """
        1、如果search_list中没有值，则不显示搜索框
        2、获取用户提交的关键字
        3、构造条件
        """
        # 用户提交的关键字
        search_value = request.GET.get("q",'')

        conn = Q()
        conn.connector = "OR"
        if search_value:
            for item in search_list:
                conn.children.append((item,search_value))

        self.model_class.objects.filter(conn)

        # end search


        # 获取排序
        order_list = self.get_order_list()

        list_display = self.get_list_display(request,*args,**kwargs)

        # 1、处理表格的表头
        header_list = []

        if list_display:
            for key_or_fun in list_display:
                if isinstance(key_or_fun,FunctionType):
                    verbose_name = key_or_fun(self,obj=None,is_header=True,*args,**kwargs)

                else:
                    verbose_name = self.model_class._meta.get_field(key_or_fun).verbose_name
                header_list.append(verbose_name)

        else:
            header_list.append(self.model_class._meta.model_name)


        # 从数据库中获取所有的数据
        # 根据URL中获取的page = 3
        """
        # 1、根据用户访问的页面，计算处数据库索引的位置
            1 0：10
            2 10：20
            3 20：30
        # 2、生成HTML中的页码
        """
        # 获取组合搜索条件
        search_group_condition = self.get_search_group_condition(request)

        prev_queryset = self.get_queryset(request, *args, **kwargs)
        queryset = prev_queryset.filter(conn).filter(**search_group_condition).order_by(*order_list)

        all_count = queryset.count()
        query_params = request.GET.copy()
        query_params._mutable = True  # 允许内部数值可以修改


        pager = Pagination(
            current_page=request.GET.get('page'),
            all_count=all_count,
            base_url=request.path_info,
            query_params=query_params,
            per_page=self.per_page_count,

        )

        data_list = queryset[pager.start:pager.end]

        body_list = []

        for row in data_list:
            tr_list = []
            if list_display:
                for key_or_fun in list_display:
                    if isinstance(key_or_fun,FunctionType):
                        tr_list.append(key_or_fun(self,row,is_header=False,*args,**kwargs))

                    else:
                        tr_list.append(getattr(row,key_or_fun))
            else:
                tr_list.append(row)
            body_list.append(tr_list)

        # 3、添加按钮

        add_btn = self.get_add_btn(request,*args,**kwargs)

        return render(
            request,self.change_list_template or 'stark/change_list.html',
            {
                "body_list":body_list,
                "header_list":header_list,
                "pager":pager,
                "add_btn":add_btn,
                "search_list":search_list,
                "search_value":search_value,
                "action_dict":action_dict,
                "search_group_row_list":search_group_row_list
            }
        )

    def add_view(self, request,*args,**kwargs):
        """
        添加页面
        :param request:
        :return:
        """

        model_form_class = self.get_model_form_class(True,request,*args,**kwargs)

        if request.method == "GET":
            form = model_form_class()
            return render(request,'stark/change.html',{"form":form})

        form = model_form_class(data=request.POST)
        if form.is_valid():
            response = self.save(request,form,False,*args,**kwargs)
            # 在数据库保存成功后，跳转回列表页面

            return response or redirect(self.reverse_list_url(*args,**kwargs))

        return render(request, self.change_template or 'stark/change.html', {"form": form})

    def get_change_object(self,request,pk,*args,**kwargs):

        return self.model_class.objects.filter(pk=pk).first()

    def change_view(self,request,pk,*args,**kwargs):
        """
        编辑页面
        :param request:
        :param pk:
        :return:
        """

        current_change_object = self.get_change_object(request,pk,*args,**kwargs)
        # current_change_object = self.model_class.objects.filter(pk=pk).first()
        if not current_change_object:
            return HttpResponse("要修改的数据不存在，请重新选择！")

        model_form_class = self.get_model_form_class(False,request,pk,*args,**kwargs)

        if request.method == "GET":
            form = model_form_class(instance=current_change_object)
            return render(request, self.change_template or 'stark/change.html', {"form": form})

        form = model_form_class(data=request.POST,instance=current_change_object)
        if form.is_valid():
            response = self.save(request,form, True,*args,**kwargs)
            # 在数据库保存成功后，跳转回列表页面

            return response or redirect(self.reverse_list_url(*args,**kwargs))

        return render(request, self.change_template or 'stark/change.html', {"form": form})

    def delete_object(self,request,pk,*args,**kwargs):
        self.model_class.objects.filter(pk=pk).delete()

    def delete_view(self, request,pk,*args,**kwargs):
        """
        删除页面
        :param request:
        :param pk:
        :return:
        """

        origin_list_url = self.reverse_list_url(*args,**kwargs)
        if request.method == "GET":
            return render(request,self.delete_template or 'stark/delete.html',{"cancel":origin_list_url})

        response = self.delete_object(request,pk,*args,**kwargs)
        return response or redirect(origin_list_url)

    def get_url_name(self,param):
        app_lable, model_name = self.model_class._meta.app_label, self.model_class._meta.model_name
        if self.prev:
            return "%s_%s_%s_%s" %(app_lable,model_name,self.prev,param)
        return "%s_%s_%s" %(app_lable,model_name,param)

    @property
    def get_list_url_name(self):
        # 获取列表页面的URL的name
        return self.get_url_name('list')

    @property
    def get_add_url_name(self):
        # 获取添加页面的URL的name
        return self.get_url_name('add')

    @property
    def get_change_url_name(self):
        # 获取修改页面的URL的name
        return self.get_url_name('change')

    @property
    def get_delete_url_name(self):
        # 获取删除页面的URL的name
        return self.get_url_name('delete')

    def wapper(self,func):
        @functools.wraps(func)
        def inner(request,*args,**kwargs):
            self.request = request
            return func(request,*args,**kwargs)
        return inner

    def get_urls(self):

        patterns = [
            re_path(r'^list/$', self.wapper(self.changelist_view), name=self.get_list_url_name),
            re_path(r'^add/$', self.wapper(self.add_view), name=self.get_add_url_name),
            re_path(r'^change/(?P<pk>\d+)/$', self.wapper(self.change_view), name=self.get_change_url_name),
            re_path(r'^delete/(?P<pk>\d+)/$', self.wapper(self.delete_view), name=self.get_delete_url_name)
        ]
        """
        if self.prev:
            patterns = [
                re_path(r'^list/$', self.changelist_view, name='%s_%s_%s_list' % (app_lable, model_name,self.prev)),
                re_path(r'^add/$', self.add_view, name='%s_%s_%s_add' % (app_lable, model_name,self.prev)),
                re_path(r'^change/$', self.change_view, name='%s_%s_%s_change' % (app_lable, model_name,self.prev)),
                re_path(r'^delete/$', self.delete_view, name='%s_%s_%s_delete' % (app_lable, model_name,self.prev))
            ]
        else:
            patterns = [
                re_path(r'^list/$',self.changelist_view,name='%s_%s_list' %(app_lable,model_name)),
                re_path(r'^add/$',self.add_view,name='%s_%s_add' %(app_lable,model_name)),
                re_path(r'^change/$',self.change_view,name='%s_%s_change' %(app_lable,model_name)),
                re_path(r'^delete/$',self.delete_view,name='%s_%s_delete' %(app_lable,model_name))
            ]
        """

        patterns.extend(self.extra_urls())
        return patterns

    def extra_urls(self):
        return []

class StarkSite(object):

    def __init__(self):
        self._registry = []
        self.app_name = 'stark'
        self.namespace = 'stark'

    def register(self,model_class,handler_class=None,prev=None):
        """

        :param model_class: 是models中数据库表对应的类
        :param handler_class: 处理请求的试图函数所在的类
        :param prev: 生成URL的前缀
        :return:
        """

        if not handler_class:
            handler_class = StarkHander
        self._registry.append({"model_class":model_class,"handler":handler_class(self,model_class,prev),'prev':prev})
        """
        self._registry = [
            {"prev":Node,"model_class":model.Depart,"handler":DepartHander(models.Depart,prev)},
            {"prev":private,"model_class":model.UserInfo,"handler":UserInfoHandler(models.UserInfo,prev)},
            {"prev":Node,"model_class":model.Host,"handler":HostHander(models.Host,prev)},
        ]
        """

    def get_urls(self):
        patterns = []
        for item in self._registry:
            model_class = item["model_class"]
            handler = item["handler"]
            prev = item["prev"]
            app_lable, model_name = model_class._meta.app_label,model_class._meta.model_name
            if prev:
                # patterns.append(re_path(r'^%s/%s/%s/list/$' % (app_lable, model_name,prev), handler.changelist_view))
                # patterns.append(re_path(r'^%s/%s/%s/add/$' % (app_lable, model_name,prev), handler.add_view))
                # patterns.append(re_path(r'^%s/%s/%s/change/(\d+)/$' % (app_lable, model_name,prev), handler.change_view))
                # patterns.append(re_path(r'^%s/%s/%s/del/(\d+)/$' % (app_lable, model_name,prev), handler.delete_view))
                patterns.append(re_path(r'^%s/%s/%s/' % (app_lable, model_name,prev), (handler.get_urls(),None,None)))
            else:
                # patterns.append(re_path(r'^%s/%s/list/$' % (app_lable,model_name), handler.changelist_view))
                # patterns.append(re_path(r'^%s/%s/add/$' % (app_lable,model_name), handler.add_view))
                # patterns.append(re_path(r'^%s/%s/change/(\d+)/$' % (app_lable,model_name), handler.change_view))
                # patterns.append(re_path(r'^%s/%s/del/(\d+)/$' % (app_lable,model_name), handler.delete_view))
                patterns.append(
                    re_path(r'^%s/%s/' % (app_lable, model_name), (handler.get_urls(), None, None)))
        return patterns

    @property
    def urls(self):
        return self.get_urls(),self.app_name,self.namespace

site = StarkSite()
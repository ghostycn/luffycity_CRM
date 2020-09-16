#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.urls import re_path
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.shortcuts import HttpResponse,render
from django.forms.models import modelformset_factory
from stark.service.v1 import StarkHander,StarkModelForm,get_datetime_text
from web import models
from .base import PermissionHandler

class CourseRecordModelForm(StarkModelForm):
    class Meta:
        model = models.CourseRecord
        fields = ["day_num","teacher"]

class StudyRecordModelForm(StarkModelForm):
    class Meta:
        model= models.StudyRecord
        fields = ['record']

class CourseRecordHandler(PermissionHandler,StarkHander):

    def display_attendance(self, obj=None, is_header=None, *args, **kwargs):

        if is_header:
            return "考勤记录"

        record_url = reverse('stark:web_courserecord_attendance', kwargs={"course_record_id": obj.pk})
        return mark_safe("<a target='_blank' href='%s'>考勤记录</a>" % record_url)

    list_display = [StarkHander.display_checkbox,"class_object","day_num","teacher",get_datetime_text("时间","date"),display_attendance]

    model_form_class = CourseRecordModelForm

    def display_edit_del(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "操作"
        class_id = kwargs.get("class_id")
        tpl = "<a href='%s'>编辑</a> | <a href='%s'>删除</a>" % (
        self.reverse_change_url(pk=obj.pk,class_id=class_id),
        self.reverse_delete_url(pk=obj.pk,class_id=class_id))
        return mark_safe(tpl)

    def get_urls(self):

        patterns = [
            re_path(r'^list/(?P<class_id>\d+)/$', self.wapper(self.changelist_view), name=self.get_list_url_name),
            re_path(r'^add/(?P<class_id>\d+)/$', self.wapper(self.add_view), name=self.get_add_url_name),
            re_path(r'^change/(?P<class_id>\d+)/(?P<pk>\d+)/$', self.wapper(self.change_view), name=self.get_change_url_name),
            re_path(r'^delete/(?P<class_id>\d+)/(?P<pk>\d+)/$', self.wapper(self.delete_view), name=self.get_delete_url_name),
            re_path(r'^attendance/(?P<course_record_id>\d+)/$', self.wapper(self.attendance_view), name=self.get_attendance_url_name)
        ]

        patterns.extend(self.extra_urls())
        return patterns

    @property
    def get_attendance_url_name(self):
        # 获取删除页面的URL的name
        return self.get_url_name('attendance')

    def attendance_view(self,request,course_record_id,*args,**kwargs):
        """
        考勤的批量操作
        :param request:
        :param course_record_id:
        :param args:
        :param kwargs:
        :return:
        """
        study_record_object_list = models.StudyRecord.objects.filter(course_record_id=course_record_id)

        study_model_formset = modelformset_factory(models.StudyRecord, form=StudyRecordModelForm,extra=0)

        if request.method == "POST":
            formset = study_model_formset(queryset=study_record_object_list,data=request.POST)
            if formset.is_valid():
                formset.save()
            return render(request, "attendance.html", {"formset": formset})

        formset = study_model_formset(queryset=study_record_object_list)
        return render(request,"attendance.html",{"formset":formset})

    def get_queryset(self, request, *args, **kwargs):
        class_id = kwargs.get("class_id")
        return self.model_class.objects.filter(class_object_id=class_id)

    def save(self,request,form,is_update,*args,**kwargs):
        class_id = kwargs.get("class_id")

        if not is_update:
            form.instance.class_object_id = class_id

        form.save()

    def action_multi_init(self,request,*args,**kwargs):
        course_record_id_list = request.POST.getlist("pk")
        class_id = kwargs.get("class_id")
        class_object = models.ClassList.objects.filter(id=class_id).first()
        if not class_object:
            return HttpResponse("班级不存在")
        student_object_list = class_object.student_set.all()
        for course_record_id in course_record_id_list:
            # 判断上课记录是否合法
            course_record_object =models.CourseRecord.objects.filter(id=course_record_id,class_object_id=class_id).first()
            if not course_record_object:
                continue

            # 判断此上课记录的考勤记录是否存在
            study_record_exists = models.StudyRecord.objects.filter(course_record=course_record_object).exists()
            if study_record_exists:
                continue

            # 为每个学生在该天创建考勤记录  for循环次数过多不推荐
            # for stu in student_object_list:
            #     models.StudyRecord.objects.create(student_id=stu.id,course_record_id=course_record_id)

            # 批量生成对象
            study_record_object_list = [models.StudyRecord(student_id=stu.id,course_record_id=course_record_id)
                                        for stu in student_object_list]

            models.StudyRecord.objects.bulk_create(study_record_object_list,batch_size=50)

    action_multi_init.text = "批量初始化考勤"

    action_list = [action_multi_init]
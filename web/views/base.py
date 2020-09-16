#!/usr/bin/env python3
# -*- coding: utf-8 -*-
class PermissionHandler(object):

    def get_add_btn(self,request,*args,**kwargs):
        from django.conf import settings
        permission_dict = request.session[settings.PERMISSION_SESSION_KEY]
        if self.get_add_url_name not in permission_dict:
            return None
        return super().get_add_btn(request,*args,**kwargs)

    def get_list_display(self,request,*args,**kwargs):
        from django.conf import settings
        permission_dict = request.session[settings.PERMISSION_SESSION_KEY]
        value = []
        if self.list_display:
            value.extend(self.list_display)
            if self.get_change_url_name in permission_dict and self.get_delete_url_name in permission_dict:
                value.append(type(self).display_edit_del)
                return value
            # 如果客户有编辑权限
            if self.get_change_url_name in permission_dict:
                value.append(type(self).display_edit)
            # 如果客户有删除权限
            elif self.get_delete_url_name in permission_dict:
                value.append(type(self).display_del)
        return value
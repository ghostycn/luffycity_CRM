#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from stark.service.v1 import StarkHander
from .base import PermissionHandler

class CourseHandler(PermissionHandler,StarkHander):
    list_display = ["name"]


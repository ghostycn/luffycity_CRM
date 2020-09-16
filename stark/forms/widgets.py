#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms

class DateTimePickerInput(forms.TextInput):

    template_name = 'stark/forms/widgets/datetime_picker.html'
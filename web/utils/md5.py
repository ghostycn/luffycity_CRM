#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib

def gen_md5(origin):
    """
    买md5加密
    :param origin:
    :return:
    """

    ha = hashlib.md5(b'abc')
    # 字符串转换字节
    ha.update(origin.encode('utf-8'))
    return ha.hexdigest()
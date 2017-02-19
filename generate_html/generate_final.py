#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re
import json
import sys
import urllib
from urllib import urlencode
import webbrowser
import HTMLParser
import unicodedata
reload(sys)
sys.setdefaultencoding("utf-8")

dir = 'C:\Users\zpysky\Desktop\jtc_school_info\my_school_info'
dir2 = 'C:\Users\zpysky\Desktop\jtc_school_info\my_school_info2'
filenames = os.listdir(dir)


def get_yimusanfendi_school_info(filename):
    f = open(dir + '\\' + filename, 'r')
    res = []
    is_project = False
    while True:
        line = f.readline()
        if not line:
            break
        if is_project:
            line1 = line.replace('\n', '</br>')
            res.append(line1)
            continue
        if '项目列表' in line:
            is_project = True
            line1 = line.replace('\n', '</br>')
            res.append(line1.strip())
            continue
        else:
            res.append(line.strip())
    return res


for x in filenames:
    k = get_yimusanfendi_school_info(x)
    output_file = dir2 + '\\' + x
    sys.stdout = file(output_file, 'w')
    for y in k:
        print y
    #os.rename(dir+os.sep+x, dir+os.sep+str(a)+'.bmp')
    #os.rename(dir+os.sep+filenames[a],dir+os.sep+str(a)+'.bmp')

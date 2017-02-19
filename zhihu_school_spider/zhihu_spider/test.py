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
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest
reload(sys)
sys.setdefaultencoding("utf-8")

def get_all_target_urls():
    f = open('C:\Users\zpysky\PycharmProjects\zhihu_spider\Refined Top 100 School detail.txt', 'r')
    res = []
    while True:
        line = f.readline()
        line = line.strip('\n')
        if len(line) == 0:
            break
        detail = line.split(',')
        res.append(detail)
    return res

s = "波士顿大学".encode('utf8')
start_urls = get_all_target_urls()
names = start_urls[48]
for name in names:
    print type(s), type(name)
    print s, name
    if s in name:
        print 'haa'
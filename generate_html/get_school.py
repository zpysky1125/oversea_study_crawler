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


f = open('C:\Users\zpysky\PycharmProjects\yimusanfendi_spider\yimusanfendi_spider\Refined Top 100 School detail.txt', 'r')
while True:
    line = f.readline()
    if len(line) == 0:
        break
    line1 = line.split(',')[0]
    open(line1+".txt", 'w')

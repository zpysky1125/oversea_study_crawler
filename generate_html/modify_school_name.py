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

res = []
f = open('C:\Users\zpysky\PycharmProjects\yimusanfendi_spider\yimusanfendi_spider\Refined Top 100 School detail.txt', 'r')
while True:
    line = f.readline()
    if len(line) == 0:
        break
    line1 = line.split(',')[0]
    res.append(line1)


dir = 'C:\Users\zpysky\Desktop\combine\quora_school'
out = 'C:\Users\zpysky\Desktop\combine\output'
filenames = os.listdir(dir)
for x in filenames:
    s = int(x.replace('.txt', ''))
    #print dir + os.sep + res[s-1] + '.txt'
    print s
    os.rename(dir + os.sep + x, out + os.sep + res[s-1] + '.txt')
    #os.rename(dir+os.sep+x, dir+os.sep+str(a)+'.bmp')
    #os.rename(dir+os.sep+filenames[a],dir+os.sep+str(a)+'.bmp')
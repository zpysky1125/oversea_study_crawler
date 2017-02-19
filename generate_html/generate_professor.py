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


def get_all_target_urls():
    f = open('C:\Users\zpysky\PycharmProjects\zhihu_professor_spider\zhihu_professor_spider\Facultylist_modify.txt', 'r')
    res = []
    while True:
        line = f.readline()
        line = line.strip('\n')
        if line == '\n':
            continue
        if len(line) == 0:
            break
        res.append(line)
    return res

professor_names = get_all_target_urls()


def get_pages():
    f = open('C:\Users\zpysky\Desktop\Model\Model\professor.html', 'r')
    res = []
    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip()
        res.append(line)
    return res

pages = get_pages()


def get_zhihu_professor(professor_name, zhihu_anchor):
    filepath = 'C:\Users\zpysky\Desktop\combine\zhihu_professor\\' + professor_name + '.txt'
    if not os.path.exists(filepath):
        return []
    f = open(filepath , 'r')
    res = []
    while True:
        line = f.readline()
        line1 = line.replace('\n', '</br>')
        if not line:
            break
        if 'professor name: ' in line1:
            continue
        if "whitedot.jpg" in line1:
            continue
        if 'imgsrc: ' in line1:
            line1 = line1.replace('imgsrc: ', '<img src = "')
            line1 = line1.replace('</br>', '" />')
        if 'topic' in line1:
            url = res[-1]
            url = url.replace('url:', '').replace('</br>', '')
            del res[-1]
            zhihu_anchor.append(line1.replace('topic:', ''))
            line1 = '<a href = "' + url + '">' + line1 + "</a>"
            line1 = '<div class="para-title level-3"><h3 class="title-text"></br>' + line1 + '</h3></div>'
            line1 = '<div class="anchor-list"><a name="2_' + str(len(zhihu_anchor)) + '" class="lemma-anchor para-title"></a></div>' + line1
        res.append(line1)
    return res


def get_zhihu_anchor(zhihu_anchor):
    i = 1
    res = []
    for x in zhihu_anchor:
        l = 'zhuhu_topic' + str(i)
        s = '<li class="level2"><span class="index">▪</span><span class="text">' + '<a href="#2_' + str(i) + '">' + l + '</a></span></li>'
        res.append(s)
        i += 1
    return res


def get_rate_professor(professor_name):
    filepath = 'C:\Users\zpysky\Desktop\combine\\rate_professor\\' + professor_name + '.txt'
    if not os.path.exists(filepath):
        return []
    f = open(filepath, 'r')
    res = []
    while True:
        line = f.readline()
        line1 = line.replace('\n', '</br>')
        if not line:
            break
        res.append(line1)
    return res


def get_quora_professor(professor_name, quora_anchor):
    filepath = 'C:\Users\zpysky\Desktop\combine\quora_professor\\' + professor_name + '.txt'
    if not os.path.exists(filepath):
        return []
    f = open(filepath, 'r')
    res = []
    topic = ''
    while True:
        line = f.readline()
        line1 = line.replace('\n', '</br>')
        if not line:
            break
        if 'Topic: ' in line1:
            topic = line1.replace('Topic: ', '')
            continue
        if 'Url: ' in line1:
            url = 'https://www.quora.com' + line1.replace('Url: ', '')
            line1 = '<a href = "' + url + '">' + topic + "</a>"
            line1 = '<div class="para-title level-3"><h3 class="title-text"></br>' + line1 + '</h3></div>'
            line1 = '<div class="anchor-list"><a name="3_' + str(len(quora_anchor)) + '" class="lemma-anchor para-title"></a></div>' + line1
        res.append(line1)
    return res


def get_quora_anchor(quora_anchor):
    i = 1
    res = []
    for x in quora_anchor:
        l = 'quora_topic' + str(i)
        s = '<li class="level2"><span class="index">▪</span><span class="text">' + '<a href="#3_' + str(i) + '">' + l + '</a></span></li>'
        res.append(s)
        i += 1
    return res


def generate_page(professor_name, lines1, lines2, lines3, lines4, lines5):
    professor_html = []
    for page in pages:
        if 'title_name' in page:
            s = page.replace('title_name', professor_name)
            professor_html.append(s)
        elif 'professor_name' in page:
            s = page.replace('professor_name', professor_name)
            professor_html.append(s)
        elif '知乎话题' in page:
            for line in lines3:
                professor_html.append(line)
        elif 'quora话题' in page:
            for line in lines4:
                professor_html.append(line)
        elif 'zhihu_comment' in page:
            for line in lines1:
                professor_html.append(line)
        elif 'quora_comment' in page:
            for line in lines2:
                professor_html.append(line)
        elif 'rate_comment' in page:
            professor_html.append('</br>')
            for line in lines5:
                professor_html.append(line)
        else:
            professor_html.append(page)

    output_file = "C:\Users\zpysky\Desktop\Model\Model\output_professor\\" + professor_name + '.html'
    sys.stdout = file(output_file, 'w')
    for x in professor_html:
        print x

    """
        publications_name
        citations_name
        field_name
        homepage_name
    """
lines6 = []


def delete_html(professor_name):
    output_file = "C:\Users\zpysky\Desktop\Model\Model\output_professor\\" + professor_name + '.html'
    if os.path.exists(output_file):
        print 'yes'
        os.remove(output_file)


def generate_professor(professor_name):
    zhihu_anchor = []
    quora_anchor = []
    lines1 = get_zhihu_professor(professor_name, zhihu_anchor)
    lines2 = get_quora_professor(professor_name, quora_anchor)
    lines3 = get_zhihu_anchor(zhihu_anchor)
    lines4 = get_quora_anchor(quora_anchor)
    lines5 = get_rate_professor(professor_name)
    if lines1 == [] and lines2 == [] and lines5 == []:
        #delete_html(professor_name)
        print professor_name
    #generate_page(professor_name, lines1, lines2, lines3, lines4, lines5)


for name in professor_names:
    generate_professor(name)

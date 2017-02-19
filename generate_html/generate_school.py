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
import xlrd
reload(sys)
sys.setdefaultencoding("utf-8")

school_names = []
f = open('C:\Users\zpysky\PycharmProjects\yimusanfendi_spider\yimusanfendi_spider\Refined Top 100 School detail.txt', 'r')
while True:
    line = f.readline()
    if len(line) == 0:
        break
    line1 = line.split(',')[0]
    school_names.append(line1)

bk = xlrd.open_workbook(r"C:\Users\zpysky\Desktop\combine\rate_school.xls")
sh = bk.sheet_by_name("total_page")
nrows = sh.nrows
row_list = []
for i in range(1, nrows):
    row_data = sh.row_values(i)
    row_list.append(row_data)


def get_school_side_info(school_name):
    for row in row_list:
        if row[0] == school_name:
            return row


def get_pages():
    f = open('C:\Users\zpysky\Desktop\Model\Model\school.html', 'r')
    res = []
    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip()
        res.append(line)
    return res

pages = get_pages()


def get_zhihu_school(filename, zhihu_anchor):
    filepath = 'C:\Users\zpysky\Desktop\combine\zhihu_school\\' + filename + '.txt'
    if not os.path.exists(filepath):
        return []
    f = open(filepath, 'r')
    res = []
    while True:
        line = f.readline()
        line1 = line.replace('\n', '</br>')
        if not line:
            break
        if "school name:" in line1:
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


def get_1point3acres_school(filename, yimusanfendi_anchor):
    filepath = 'C:\Users\zpysky\Desktop\combine\yimusanfendi_school_comment\\' + filename + '.txt'
    if not os.path.exists(filepath):
        return []
    f = open(filepath, 'r')
    res = []
    while True:
        line = f.readline()
        line1 = line.replace('\n', '</br>')
        if not line:
            break
        if "学校名:" in line1:
            continue
        if '问题:' in line1:
            url = res[-1]
            url = url.replace('</br>', '')
            del res[-1]
            yimusanfendi_anchor.append(line1.replace('问题:', ''))
            line1 = '<a href = "' + url + '">' + line1 + "</a>"
            line1 = '<div class="para-title level-3"><h3 class="title-text"></br>' + line1 + '</h3></div>'
            line1 = '<div class="anchor-list"><a name="3_' + str(len(yimusanfendi_anchor)) + '" class="lemma-anchor para-title"></a></div>' + line1
        res.append(line1)
    return res


def get_quora_school(filename, quora_anchor):
    filepath = 'C:\Users\zpysky\Desktop\combine\quora_school\\' + filename + '.txt'
    if not os.path.exists(filepath):
        return []
    f = open(filepath, 'r')
    res = []
    if_question = False
    while True:
        line = f.readline()
        line1 = line.replace('\n', '</br>')
        if not line:
            break
        if if_question:
            if_question = False
            quora_anchor.append(line1)
        if "Question:" in line1:
            if_question = True
            line1 = '<div class="para-title level-3"><h3 class="title-text"></br>' + line1 + '</h3></div>'
            line1 = '<div class="anchor-list"><a name="4_' + str(len(quora_anchor)+1) + '" class="lemma-anchor para-title"></a></div>' + line1
        res.append(line1)
    return res


def get_zhihu_anchor(zhihu_anchor):
    i = 1
    res = []
    for x in zhihu_anchor:
        l = 'zhuhu_topic' + str(i)
        s = '<li class="level2"><span class="index">▪</span><span class="text">' + '<a href="#2_' + str(i) + '">' + x.replace('</br>', '') + '</a></span></li>'
        res.append(s)
        i += 1
    return res


def get_yimusanfendi_anchor(yimusanfendi_anchor):
    i = 1
    res = []
    for x in yimusanfendi_anchor:
        l = '1point3acres_topic' + str(i)
        s = '<li class="level2"><span class="index">▪</span><span class="text">' + '<a href="#3_' + str(i) + '">' + x.replace('</br>', '') + '</a></span></li>'
        res.append(s)
        i += 1
    return res


def get_quora_anchor(quora_anchor):
    i = 1
    res = []
    for x in quora_anchor:
        l = 'quora_topic' + str(i)
        s = '<li class="level2"><span class="index">▪</span><span class="text">' + '<a href="#4_' + str(i) + '">' + x.replace('</br>', '') + '</a></span></li>'
        res.append(s)
        i += 1
    return res


def get_yimusanfendi_school_info(filename):
    filepath = 'C:\Users\zpysky\Desktop\combine\yimusanfendi_school_info\\' + filename + '.txt'
    if not os.path.exists(filepath):
        return []
    f = open(filepath, 'r')
    res = []
    res1 = []
    is_project = False
    while True:
        line = f.readline()
        if not line:
            break
        if is_project:
            line1 = line.replace('\n', '</br>')
            res1.append(line1)
            continue
        if '城市:' in line:
            line1 = line.replace('城市:', '')
            line1 = line1.strip()
            res.append(line1)
        if '州:' in line:
            line1 = line.replace('州:', '')
            line1 = line1.strip()
            res.append(line1)
        if 'zipcode:' in line:
            line1 = line.replace('zipcode:', '')
            line1 = line1.strip()
            res.append(line1)
        if '地址:' in line:
            line1 = line.replace('地址:', '')
            line1 = line1.strip()
            res.append(line1)
        if '学费:' in line:
            line1 = line.replace('学费:', '')
            line1 = line1.strip()
            res.append(line1)
        if '生活费:' in line:
            line1 = line.replace('生活费:', '')
            line1 = line1.strip()
            res.append(line1)
        if 'US NEWS 排名:' in line:
            line1 = line.replace('US NEWS 排名:', '')
            line1 = line1.strip()
            res.append(line1)
        if 'TIMES 排名:' in line:
            line1 = line.replace('TIMES 排名:', '')
            line1 = line1.strip()
            res.append(line1)
        if 'QS 排名:' in line:
            line1 = line.replace('QS 排名:', '')
            line1 = line1.strip()
            res.append(line1)
        if '项目列表' in line:
            is_project = True
            line1 = line.replace('\n', '</br>')
            res1.append(line1.strip())
    while len(res) < 9:
        res.append('')
    res.append(res1)
    return res


def get_school_introduction(filename):
    f = open('C:\Users\zpysky\Desktop\combine\school_introduction\\' + filename + '.txt', 'r')
    res = []
    res.append('<img src = "https://maps.googleapis.com/maps/api/streetview?size=600x300&location=' + filename +
               '" />')
    res.append('</br>')
    while True:
        line = f.readline()
        line1 = line.replace('\n', '</br>')
        if not line:
            break
        for i in range(1,70):
            pattern = '[' + str(i) + ']'
            line1 = line1.replace(pattern, '')
        res.append(line1)
    res.append('</br>')
    return res


def generate_page(school_name, lines1, lines2, lines3, lines4, lines5, lines6, lines7, lines8, lines9):
    school_html = []
    for page in pages:
        if 'title_name' in page:
            s = page.replace('title_name', school_name)
            school_html.append(s)
        elif 'introdcution_overview' in page:
            for line in lines6:
                school_html.append(line)
        elif 'city_name' in page:
            if lines5 != []:
                s = page.replace('city_name', lines5[0])
            else:
                s = page.replace('city_name', '')
            school_html.append(s)
        elif 'state_name' in page:
            if lines5 != []:
                s = page.replace('state_name', lines5[1])
            else:
                s = page.replace('state_name', '')
            school_html.append(s)
        elif 'zipcode_name' in page:
            if lines5 != []:
                s = page.replace('zipcode_name', lines5[2])
            else:
                s = page.replace('zipcode_name', '')
            school_html.append(s)
        elif 'address_name' in page:
            if lines5 != []:
                s = page.replace('address_name', lines5[3])
            else:
                s = page.replace('address_name', '')
            school_html.append(s)
        elif 'school_fee' in page:
            if lines5 != []:
                s = page.replace('school_fee', lines5[4])
            else:
                s = page.replace('school_fee', '')
            school_html.append(s)
        elif 'live_fee' in page:
            if lines5 != []:
                s = page.replace('live_fee', lines5[5])
            else:
                s = page.replace('live_fee', '')
            school_html.append(s)
        elif 'US_NEWS_RANKING' in page:
            if lines5 != []:
                s = page.replace('US_NEWS_RANKING', str(lines5[6]))
            else:
                s = page.replace('US_NEWS_RANKING', '')
            school_html.append(s)
        elif 'TIMES_RANKING' in page:
            if lines5 != []:
                s = page.replace('TIMES_RANKING', str(lines5[7]))
            else:
                s = page.replace('TIMES_RANKING', '')
            school_html.append(s)
        elif 'QS_RANKING' in page:
            if lines5 != []:
                s = page.replace('QS_RANKING', str(lines5[8]))
            else:
                s = page.replace('QS_RANKING', '')
            school_html.append(s)
        elif '知乎话题' in page:
            for line in lines4:
                school_html.append(line)
        elif '一亩三分地话题' in page:
            for line in lines3:
                school_html.append(line)
        elif 'quora话题' in page:
            for line in lines8:
                school_html.append(line)
        elif 'school_project' in page:
            school_html.append('</br>')
            if lines5 != []:
                for line in lines5[9]:
                    school_html.append(line)
        elif 'zhihu_comment' in page:
            for line in lines1:
                school_html.append(line)
        elif 'yimusanfendi_comment' in page:
            school_html.append('</br>')
            for line in lines2:
                school_html.append(line)
        elif 'quora_comment' in page:
            for line in lines7:
                school_html.append(line)
        elif 'side_school_name' in page:
            s = page.replace('side_school_name', lines9[0].strip())
            school_html.append(s)
        elif 'side_location' in page:
            s = page.replace('side_location', lines9[2].strip())
            school_html.append(s)
        elif 'overall_quality_rate' in page:
            s = page.replace('overall_quality_rate', str(lines9[1]))
            school_html.append(s)
        elif 'side_reputation_rate' in page:
            s = page.replace('side_reputation_rate', str(lines9[3]))
            school_html.append(s)
        elif 'side_location_rate' in page:
            s = page.replace('side_location_rate', str(lines9[4]))
            school_html.append(s)
        elif 'side_internet_rate' in page:
            s = page.replace('side_internet_rate', str(lines9[5]))
            school_html.append(s)
        elif 'side_food_rate' in page:
            s = page.replace('side_food_rate', str(lines9[6]))
            school_html.append(s)
        elif 'side_opportunity_rate' in page:
            s = page.replace('side_opportunity_rate', str(lines9[7]))
            school_html.append(s)
        elif 'side_library_rate' in page:
            s = page.replace('side_library_rate', str(lines9[8]))
            school_html.append(s)
        elif 'side_campus_rate' in page:
            s = page.replace('side_campus_rate', str(lines9[9]))
            school_html.append(s)
        elif 'side_clubs_rate' in page:
            s = page.replace('side_clubs_rate', str(lines9[10]))
            school_html.append(s)
        elif 'side_social_rate' in page:
            s = page.replace('side_social_rate', str(lines9[11]))
            school_html.append(s)
        elif 'side_happiness_rate' in page:
            s = page.replace('side_happiness_rate', str(lines9[12]))
            school_html.append(s)
        else:
            school_html.append(page)
    output_file = "C:\Users\zpysky\Desktop\Model\Model\output_school2\\" + school_name + '.html'
    sys.stdout = file(output_file, 'w')
    for x in school_html:
        print x



def generate_school(school_name):
    zhihu_anchor = []
    yimusanfendi_anchor = []
    quora_anchor = []
    lines1 = get_zhihu_school(school_name, zhihu_anchor)
    lines2 = get_1point3acres_school(school_name, yimusanfendi_anchor)
    lines3 = get_yimusanfendi_anchor(yimusanfendi_anchor)
    lines4 = get_zhihu_anchor(zhihu_anchor)
    lines5 = get_yimusanfendi_school_info(school_name)
    lines6 = get_school_introduction(school_name)
    lines7 = get_quora_school(school_name, quora_anchor)
    lines8 = get_quora_anchor(quora_anchor)
    lines9 = get_school_side_info(school_name)
    generate_page(school_name, lines1, lines2, lines3, lines4, lines5, lines6, lines7, lines8, lines9)


for name in school_names:
    generate_school(name)

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

header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip,deflate",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
    "Referer": "https://instant.1point3acres.com/",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}
base = "https://instant.1point3acres.com/"
glob_base = "https://instant.1point3acres.com"
base_topic_url = "https://instant.1point3acres.com/thread/search?q="
filter_str = ['intern', '拒','rej', '交流群','rank','company','征友']
glob_urls = []


def get_all_target_urls():
    f = open("C:\Users\zpysky\PycharmProjects\yimusanfendi_spider\yimusanfendi_spider\Refined Top 100 School detail.txt", 'r')
    res = []
    while True:
        line = f.readline()
        line = line.strip('\n')
        if len(line) == 0:
            break
        detail = line.split(',')
        res.append(detail)
    return res


class yimusanfendi_answer(object):
    def __init__(self):
        self.answer_er = ''
        self.answer_content = None

    def answer_print(self):
        print self.answer_er.strip()
        for s in self.answer_content:
            if s == '\n\n':
                continue
            if s == '\n':
                continue
            print s.strip()
        print


class yimusanfendi_question_answer(object):
    def __init__(self):
        self.xsrf = ''
        self.question_title = ''
        self.question_content = []
        self.qa_number = 0
        self.answer_num = 0
        self.answers = []
        self.topic = None
        self.url = ''

    def deal_question_answer(self, response):
        self.url = response.url
        selector = Selector(response)
        if selector.xpath('//div[@class="module-body"]/h1[@class="seo_title"]/text()').extract() != []:
            self.question_title = selector.xpath('//div[@class="module-body"]/h1[@class="seo_title"]/text()').extract()[0]
        self.question_content = selector.xpath('//div[@class="description"]/text()').extract()
        in_topic = False
        in_question = False
        for x in self.topic.names:
            i = True
            for y in x.split(' '):
                line = self.question_title.encode('utf-8').strip()
                a = y.encode('utf-8').strip()
                if a.lower() not in line.lower():
                    i = False
                    break
            if i:
                in_topic = True
                break
        qc = ''
        for y in self.question_content:
            qc = qc + y.strip()
        for x in self.topic.names:
            i = True
            for y in x.split(' '):
                line = qc.encode('utf-8').strip()
                a = y.encode('utf-8').strip()
                if a.lower() not in line.lower():
                    i = False
                    break
            if i:
                in_topic = True
                break
        for filter_s in filter_str:
            line1 = self.question_title.encode('utf-8').strip()
            line2 = qc.encode('utf-8').strip()
            if filter_s.lower() in line1.lower() or filter_s.lower() in line2.lower():
                in_topic = False
                in_question = False
                break
        if not in_question and not in_topic:
            if self in self.topic.work_list:
                self.topic.work_list.remove(self)
            if self in self.topic.apply_list:
                self.topic.apply_list.remove(self)
            if self in self.topic.live_list:
                self.topic.live_list.remove(self)
            if self in self.topic.study_list:
                self.topic.study_list.remove(self)
            self.topic.finish_topic_num += 1
            #print self.topic.names[0], self.topic.finish_topic_num
            if self.topic.finish_topic_num == self.topic.work_topic_num + self.topic.apply_topic_num + self.topic.live_topic_num + self.topic.study_topic_num:
                self.topic.topic_print()
            return
        answer_num_path = selector.xpath('//div[@class="col-md-8 col-sm-8 col-xs-8 text-muted form-inline"]/text()').extract()
        answer_num = int(answer_num_path[0].split('个')[0].strip('\n'))
        self.answer_num = min(answer_num, 100)
        self.qa_number = response.url.split('thread/')[1]
        answer_str = glob_base + "/thread/" + self.qa_number + "/posts?ps=" + str(self.answer_num) + "&sort=vote&pg=1"
        yield Request(answer_str, method='GET', meta={'cookiejar': 1}, callback=self.deal_answer)

    def deal_answer(self, response):
        selector = Selector(response)
        for x in selector.xpath('//div[@class="thread_reply"]'):
            answer = yimusanfendi_answer()
            answer.answer_er = x.xpath('div[@class="content"]/div[@class="vertical_section"]'
                            '/div[@class="user_info text-muted vertical_section"]/div[@class="avatar-info"]'
                        '/a/span[@class="text-slight"]/text()').extract()[0]
            answer.answer_content = x.xpath('div[@class="content"]/div[@class="vertical_section user_saying"]'
                                    '/div[@class="post_plaintext"]/text()').extract()
            self.answers.append(answer)
        self.topic.finish_topic_num += 1
        #print self.topic.names[0],self.topic.finish_topic_num
        if self.topic.finish_topic_num == self.topic.work_topic_num + self.topic.apply_topic_num + self.topic.live_topic_num + self.topic.study_topic_num:
            self.topic.topic_print()

    def question_answer_print(self):
        print self.url
        print '问题:'+self.question_title.strip()
        print '问题内容:'
        for s in self.question_content:
            if s == '\n\n':
                continue
            if s == '\n':
                continue
            print s.strip()
        print '回答：'
        for q in self.answers:
            q.answer_print()
        print


class yimusanfendi_topic(object):
    def __init__(self):
        self.work_list = []
        self.apply_list = []
        self.live_list = []
        self.study_list = []
        self.finish_topic_num = 0
        self.work_topic_num = 0
        self.apply_topic_num = 0
        self.live_topic_num = 0
        self.study_topic_num = 0
        self.xsrf = ''
        self.school_name = ''
        self.names = []
        self.offset = 0
        self.urls = []
        self.start_urls = []

    def deal_work_topic(self, response):
        selector = Selector(response)
        topic_url = selector.xpath('//div[@class="col-md-10 verticalLine thread_list_entry_snippet"]/h4/a/@href').extract()
        self.work_topic_num += len(topic_url)
        for qa_str in topic_url:
            qa = yimusanfendi_question_answer()
            qa.topic = self
            qa.xsrf = self.xsrf
            qa_url = glob_base + qa_str
            """
            if qa_url in self.urls:
                self.finish_topic_num += 1
                #print self.finish_topic_num
                if self.finish_topic_num == self.work_topic_num + self.apply_topic_num + self.live_topic_num + self.study_topic_num:
                    self.topic_print()
                continue
            self.urls.append(qa_url)
            """
            if qa_url in glob_urls:
                self.finish_topic_num += 1
                #print self.names[0], self.finish_topic_num
                if self.finish_topic_num == self.work_topic_num + self.apply_topic_num + self.live_topic_num + self.study_topic_num:
                    self.topic_print()
                continue
            glob_urls.append(qa_url)
            self.work_list.append(qa)
            yield Request(qa_url, method='GET', meta={'cookiejar': 1}, callback=qa.deal_question_answer)


    def deal_apply_topic(self, response):
        selector = Selector(response)
        topic_url = selector.xpath('//div[@class="col-md-10 verticalLine thread_list_entry_snippet"]/h4/a/@href').extract()
        self.apply_topic_num += len(topic_url)
        for qa_str in topic_url:
            qa = yimusanfendi_question_answer()
            qa.topic = self
            qa.xsrf = self.xsrf
            qa_url = glob_base + qa_str
            """
            if qa_url in self.urls:
                self.finish_topic_num += 1
                #print self.finish_topic_num
                if self.finish_topic_num == self.work_topic_num + self.apply_topic_num + self.live_topic_num + self.study_topic_num:
                    self.topic_print()
                continue
            self.urls.append(qa_url)
            """
            if qa_url in glob_urls:
                self.finish_topic_num += 1
                #print self.names[0], self.finish_topic_num
                if self.finish_topic_num == self.work_topic_num + self.apply_topic_num + self.live_topic_num + self.study_topic_num:
                    self.topic_print()
                continue
            glob_urls.append(qa_url)
            self.apply_list.append(qa)
            yield Request(qa_url, method='GET', meta={'cookiejar': 1}, callback=qa.deal_question_answer)

    def deal_study_topic(self, response):
        selector = Selector(response)
        topic_url = selector.xpath('//div[@class="col-md-10 verticalLine thread_list_entry_snippet"]/h4/a/@href').extract()
        self.study_topic_num += len(topic_url)
        for qa_str in topic_url:
            qa = yimusanfendi_question_answer()
            qa.topic = self
            qa.xsrf = self.xsrf
            qa_url = glob_base + qa_str
            """
            if qa_url in self.urls:
                self.finish_topic_num += 1
                #print self.finish_topic_num
                if self.finish_topic_num == self.work_topic_num + self.apply_topic_num + self.live_topic_num + self.study_topic_num:
                    self.topic_print()
                continue
            self.urls.append(qa_url)
            """
            if qa_url in glob_urls:
                self.finish_topic_num += 1
                #print self.names[0], self.finish_topic_num
                if self.finish_topic_num == self.work_topic_num + self.apply_topic_num + self.live_topic_num + self.study_topic_num:
                    self.topic_print()
                continue
            glob_urls.append(qa_url)
            self.study_list.append(qa)
            yield Request(qa_url, method='GET', meta={'cookiejar': 1}, callback=qa.deal_question_answer)

    def deal_live_topic(self, response):
        selector = Selector(response)
        topic_url = selector.xpath('//div[@class="col-md-10 verticalLine thread_list_entry_snippet"]/h4/a/@href').extract()
        self.live_topic_num += len(topic_url)
        for qa_str in topic_url:
            qa = yimusanfendi_question_answer()
            qa.topic = self
            qa.xsrf = self.xsrf
            qa_url = glob_base + qa_str
            """
            if qa_url in self.urls:
                self.finish_topic_num += 1
                #print self.finish_topic_num
                if self.finish_topic_num == self.work_topic_num + self.apply_topic_num + self.live_topic_num + self.study_topic_num:
                    self.topic_print()
                continue

            self.urls.append(qa_url)
            """
            if qa_url in glob_urls:
                self.finish_topic_num += 1
                #print self.names[0], self.finish_topic_num
                if self.finish_topic_num == self.work_topic_num + self.apply_topic_num + self.live_topic_num + self.study_topic_num:
                    self.topic_print()
                continue
            glob_urls.append(qa_url)
            self.live_list.append(qa)
            yield Request(qa_url, method='GET', meta={'cookiejar': 1}, callback=qa.deal_question_answer)

    def topic_print(self):
        output_file = 'C:\Users\zpysky\PycharmProjects\yimusanfendi_spider\yimusanfendi_spider\output2\\' \
                      + self.names[0] + '.txt'
        sys.stdout = open(output_file, 'w')
        print '学校名：' + self.names[0]
        print '工作话题：'
        for x in self.work_list:
            x.question_answer_print()
        print '申请话题：'
        for x in self.apply_list:
            x.question_answer_print()
        print '学习话题：'
        for x in self.study_list:
            x.question_answer_print()
        print '生活话题：'
        for x in self.live_list:
            x.question_answer_print()

    def get_topic(self, response):
        urls = []
        for x in self.names:
            str1 = base_topic_url + x + "&ch=" + '1' + "&pg=" + str(1)
            str2 = base_topic_url + x + "&ch=" + '2' + "&pg=" + str(1)
            str3 = base_topic_url + x + "&ch=" + '3' + "&pg=" + str(1)
            str4 = base_topic_url + x + "&ch=" + '5' + "&pg=" + str(1)
            url = []
            url.append(str1)
            url.append(str2)
            url.append(str3)
            url.append(str4)
            urls.append(url)
        for url in urls:
            yield Request(url[0], method='GET', meta={'cookiejar': 1}, callback=self.deal_work_topic)
            yield Request(url[1], method='GET', meta={'cookiejar': 1}, callback=self.deal_apply_topic)
            yield Request(url[2], method='GET', meta={'cookiejar': 1}, callback=self.deal_study_topic)
            yield Request(url[3], method='GET', meta={'cookiejar': 1}, callback=self.deal_live_topic)

    def get_topics(self):
        urls = []
        for x in self.names:
            str1 = base_topic_url + x + "&ch=" + '1' + "&pg=" + str(1)
            str2 = base_topic_url + x + "&ch=" + '2' + "&pg=" + str(1)
            str3 = base_topic_url + x + "&ch=" + '3' + "&pg=" + str(1)
            str4 = base_topic_url + x + "&ch=" + '5' + "&pg=" + str(1)
            url = []
            url.append(str1)
            url.append(str2)
            url.append(str3)
            url.append(str4)
            urls.append(url)
        for url in urls:
            yield Request(url[0], method='GET', meta={'cookiejar': 1}, callback=self.deal_work_topic)
            yield Request(url[1], method='GET', meta={'cookiejar': 1}, callback=self.deal_apply_topic)
            yield Request(url[2], method='GET', meta={'cookiejar': 1}, callback=self.deal_study_topic)
            yield Request(url[3], method='GET', meta={'cookiejar': 1}, callback=self.deal_live_topic)
            """
        for y in self.start_urls:
            urls = []
            for x in y:
                str1 = base_topic_url + x + "&ch=" + '1' + "&pg=" + str(i)
                str2 = base_topic_url + x + "&ch=" + '2' + "&pg=" + str(i)
                str3 = base_topic_url + x + "&ch=" + '3' + "&pg=" + str(i)
                str4 = base_topic_url + x + "&ch=" + '5' + "&pg=" + str(i)
                url = []
                url.append(str1)
                url.append(str2)
                url.append(str3)
                url.append(str4)
                urls.append(url)
            for url in urls:
                yield Request(url[0], method='GET', meta={'cookiejar': 1}, callback=self.deal_work_topic)
                yield Request(url[1], method='GET', meta={'cookiejar': 1}, callback=self.deal_apply_topic)
                yield Request(url[2], method='GET', meta={'cookiejar': 1}, callback=self.deal_study_topic)
                yield Request(url[3], method='GET', meta={'cookiejar': 1}, callback=self.deal_live_topic)
            """

class yimusanfendi_spider(CrawlSpider):
    name = "yimusanfendi"
    allowed_domains = ["1point3acres.com"]
    start_urls = []
    base = "https://instant.1point3acres.com/"

    def __init__(self, *args, **kwargs):
        super(yimusanfendi_spider, self).__init__(*args, **kwargs)
        self.request_answer_param = None
        self.xsrf = ''
        self.start_urls = get_all_target_urls()

    def start_requests(self):
        return [Request("https://instant.1point3acres.com/",
                        meta={'cookiejar': 1},
                        callback=self.post_topic)]

    def post_topic(self, response):
        for x in self.start_urls:
            topic = yimusanfendi_topic()
            topic.names = x
            urls = []
            for y in x:
                str1 = base_topic_url + y + "&ch=" + '1' + "&pg=" + str(1)
                str2 = base_topic_url + y + "&ch=" + '2' + "&pg=" + str(1)
                str3 = base_topic_url + y + "&ch=" + '3' + "&pg=" + str(1)
                str4 = base_topic_url + y + "&ch=" + '5' + "&pg=" + str(1)
                url = []
                url.append(str1)
                url.append(str2)
                url.append(str3)
                url.append(str4)
                urls.append(url)
            for url in urls:
                yield Request(url[0], method='GET', meta={'cookiejar': 1}, callback=topic.deal_work_topic)
                yield Request(url[1], method='GET', meta={'cookiejar': 1}, callback=topic.deal_apply_topic)
                yield Request(url[2], method='GET', meta={'cookiejar': 1}, callback=topic.deal_study_topic)
                yield Request(url[3], method='GET', meta={'cookiejar': 1}, callback=topic.deal_live_topic)
            """
        topic = yimusanfendi_topic()
        topic.start_urls = self.start_urls
        topic.names = self.start_urls[99]
        topic.xsrf = Selector(response).xpath('//input[@name="_xsrf"]/@value').extract()[0]
        str1 = self.base + "search?_xsrf=" + topic.xsrf + "&q=" + topic.names[0]
        return [Request(str1, meta={'cookiejar': 1}, callback=topic.get_topic)]
        """




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
    "Referer": "http://www.zhihu.com/",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}


xsrf = ''
base = 'https://www.zhihu.com/search?type=content&q='
glob_base = "https://www.zhihu.com"


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


def my_print(str="", str1=""):
        my_str = '' + str
        my_str = my_str.strip('\n')
        my_str = str1 + my_str
        print my_str


class MyParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.level = ''
        self.before_level = ''
        self.str = ''

    def handle_starttag(self, tag, attrs):
        self.before_level = self.level
        self.level = tag
        if tag == 'a':
            if self.before_level != 'a_end':
                pass
            for name, value in attrs:
                if name == 'href':
                    my_print('link: ' + value + "  ")

        if tag == 'img':
            if self.level != self.before_level:
                pass
            for name, value in attrs:
                if name == 'src':
                    my_print('imgsrc: ' + value + "  ")

    def handle_data(self, data):
        if self.before_level == 'a_end':
            pass
        my_print(data)

    def handle_endtag(self, tag):
        self.level = tag + '_end'

    def close(self):
        print

global_parser = MyParser()


class zhihu_answer(object):
    def __init__(self):
        self.answer = ''
        self.answer_field = ''
        self.answer_content = ''
        self.qa = None

    def zhihu_answer_print(self):
        print self.answer + self.answer_field
        for ans in self.answer_content:
            global_parser.feed(ans)
            global_parser.close()


class zhihu_question_answer(object):
    def __init__(self):
        self.url = ''
        self.topic = ''
        self.question = ''
        self.answer_num = ''
        self.max_answer = 0
        self.current_answer = 0
        self.answers = []
        self.xsrf = ''
        self.request_answer_param = None
        self.school = None

    def zhihu_question_answer_print(self):
        my_print(self.url, "url:")
        my_print(self.topic, "topic:")
        my_print(self.question, "question:")
        my_print(self.answer_num, "answer_num:")
        my_print('', 'answers:')
        for ans in self.answers:
            ans.zhihu_answer_print()

    def response_more_answer(self, response):
        res = json.loads(response.body)
        for x in res['msg']:
            for y in Selector(text=x).xpath('//div[@class="zm-item-answer  zm-item-expanded"]'):
                zhihu_ans = zhihu_answer()
                zhihu_ans.qa = self
                answer_er = y.xpath('div[@class="answer-head"]/div[@class="zm-item-answer-author-info"]'
                                '/a[@class="author-link"]/text()').extract()
                answerer_field = y.xpath('div[@class="answer-head"]/div[@class="zm-item-answer-author-info"]'
                                '/span[@class="bio"]/text()').extract()
                if(answer_er == []):
                    zhihu_ans.answer = "unknown anthor"
                elif(answerer_field == []):
                    zhihu_ans.answer = answer_er[0]
                    zhihu_ans.answer_field = ""
                else:
                    zhihu_ans.answer = answer_er[0]
                    zhihu_ans.answer_field = answerer_field[0]
                answer = y.xpath('div[@class="zm-item-rich-text js-collapse-body"]/div[@class="zm-editable-content clearfix"]').extract()
                zhihu_ans.answer_content = answer
                self.current_answer += 1
                self.answers.append(zhihu_ans)
        if self.current_answer < self.max_answer:
            yield self.request_more_answer(response)
        else:
            self.school.finish_topic += 1
            #print self.school.finish_topic, self.school.offset
            if self.school.finish_topic == self.school.final_topic:
                self.school.zhihu_school_print()

    def request_more_answer(self, response):
        if self.current_answer >= self.max_answer:
            return None
        more_buf = self.get_more_answer(response)
        return FormRequest('https://www.zhihu.com/node/QuestionAnswerListV2', method='POST',
                            meta={'cookiejar': response.meta['cookiejar']},
                            headers=header,
                            formdata = {
                                '_xsrf': self.xsrf,
                                'params': more_buf,
                                'method': 'next'},
                            callback=self.response_more_answer,
                            dont_filter=True)

    def get_more_answer(self, response):
        if self.request_answer_param == None:
            data_init = Selector(response).xpath('//div[@id="zh-question-answer-wrap"]/@data-init').extract()[0]
            dc = json.loads(data_init)
            dc['params']['offset'] = self.current_answer
            self.request_answer_param = json.dumps(dc['params'])
            return self.request_answer_param
        else:
            self.request_answer_param = json.loads(self.request_answer_param)
            self.request_answer_param['offset'] = self.current_answer
            self.request_answer_param = json.dumps(self.request_answer_param)
            return self.request_answer_param


class zhihu_school(object):
    def __init__(self):
        self.offset = 0
        self.finish_topic = 0
        self.topic_list = []
        self.question_answers = []
        self.names = []
        self.final_topic = 0

    def get_topics(self, response):
        selector = Selector(response)
        topic_list = selector.xpath('//div[@class="title"]/a/@href').extract()
        for topic in topic_list:
            top = glob_base + topic
            if 'question' not in top:
                self.finish_topic += 1
                #print self.finish_topic, self.offset
                if self.finish_topic == self.offset:
                    self.zhihu_school_print()
                continue
            if top in self.topic_list:
                self.finish_topic += 1
                #print self.finish_topic, self.offset
                if self.finish_topic == self.offset:
                    self.zhihu_school_print()
                continue
            self.topic_list.append(top)
        #print self.finish_topic, len(self.topic_list)
        if self.offset - self.finish_topic - len(self.topic_list) < 8:
            self.final_topic = self.finish_topic + len(self.topic_list)
            for topic in self.topic_list:
                yield Request(topic, meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse_topic)

    def get_more_topics(self, response):
        htmls = eval(response.body)['htmls']
        for x in htmls:
            topic = Selector(text=x).xpath('//div[@class="title"]/a/@href').extract()
            topic[0] = topic[0].replace('\\', '')
            if 'question' not in topic[0]:
                self.finish_topic += 1
                #print self.finish_topic, self.offset
                if self.finish_topic == self.offset:
                    self.zhihu_school_print()
                continue
            topic[0] = glob_base + topic[0]
            if topic[0] in self.topic_list:
                self.finish_topic += 1
                #print self.finish_topic, self.offset
                if self.finish_topic == self.offset:
                    self.zhihu_school_print()
                continue
            self.topic_list.append(topic[0])
        #print self.finish_topic, len(self.topic_list)
        if self.offset - self.finish_topic - len(self.topic_list) < 8:
            self.final_topic = self.finish_topic + len(self.topic_list)
            for topic in self.topic_list:
                yield Request(topic, meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse_topic)
            #yield Request(topic[0], meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse_topic)

    def parse_topic(self, response):
        selector = Selector(response)
        url = response.url
        zhihu_qa = zhihu_question_answer()
        zhihu_qa.school = self
        topic = selector.xpath('//h2[@class="zm-item-title zm-editable-content"]/text()').extract()[0]
        ques = selector.xpath('//div[@class="zm-editable-content"]/text()').extract()
        if(ques == []):
            ques = selector.xpath('//textarea[@class="content hidden"]/text()').extract()
        if(ques != []):
            question = ques[0]
        else:
            question = ""
        if(selector.xpath('//h3[@id="zh-question-answer-num"]/@data-num').extract() != []):
            answer_num = selector.xpath('//h3[@id="zh-question-answer-num"]/@data-num').extract()[0]
        else:
            answer_num = '0'
        in_question = False
        in_topic = False
        for x in self.names:
            i = True
            for y in x.split('|'):
                line = question.encode('utf-8').strip()
                a = y.encode('utf-8').strip()
                if a.lower() not in line.lower() and a not in line:
                    i = False
                    break
            if i:
                in_question = True
                break
        for x in self.names:
            i = True
            for y in x.split('|'):
                line = topic.encode('utf-8').strip()
                a = y.encode('utf-8').strip()
                if a.lower() not in line.lower() and a not in line:
                    i = False
                    break
            if i:
                in_topic = True
                break
        if (not in_topic and not in_question) or answer_num == '0':
            self.finish_topic += 1
            #print self.finish_topic, self.offset
            if self.finish_topic == self.final_topic:
                self.zhihu_school_print()
            return
        self.question_answers.append(zhihu_qa)

        zhihu_qa.url = url;
        zhihu_qa.topic = topic;
        zhihu_qa.question = question
        zhihu_qa.answer_num = answer_num
        zhihu_qa.max_answer = min(int(answer_num), 40)

        for x in selector.xpath('//div[@class="zm-item-answer  zm-item-expanded"]'):
            zhihu_ans = zhihu_answer()
            zhihu_ans.qa = zhihu_qa
            answer_er = x.xpath('div[@class="answer-head"]/div[@class="zm-item-answer-author-info"]'
                               '/a[@class="author-link"]/text()').extract()
            answerer_field = x.xpath('div[@class="answer-head"]/div[@class="zm-item-answer-author-info"]'
                               '/span[@class="bio"]/text()').extract()
            if(answer_er == []):
                zhihu_ans.answer = "unknown anthor"
            elif(answerer_field == []):
                zhihu_ans.answer = answer_er[0]
                zhihu_ans.answer_field = ""
            else:
                zhihu_ans.answer = answer_er[0]
                zhihu_ans.answer_field = answerer_field[0]
            answer = x.xpath('div[@class="zm-item-rich-text js-collapse-body"]/div[@class="zm-editable-content clearfix"]').extract()
            zhihu_ans.answer_content = answer
            zhihu_qa.current_answer += 1
            zhihu_qa.answers.append(zhihu_ans)
        if zhihu_qa.max_answer - zhihu_qa.current_answer > 10:
            yield zhihu_qa.request_more_answer(response)
        else:
            self.finish_topic += 1
            #print self.finish_topic, self.offset
            if self.finish_topic == self.final_topic:
                self.zhihu_school_print()


    def zhihu_school_print(self):
        if self.question_answers == []:
            return
        output_file = "C:\Users\zpysky\PycharmProjects\zhihu_spider\zhihu_spider\output\\" + "bina" + '.txt'
        sys.stdout = file(output_file, 'w')
        my_print(self.names[0], "school name:")
        for qa in self.question_answers:
            qa.zhihu_question_answer_print()


class zhihu_spider(CrawlSpider):
    name = "zhihu"
    allowed_domains = ["zhihu.com"]
    start_urls = []
    base = "https://www.zhihu.com"
    myparser = MyParser()

    def __init__(self, *args, **kwargs):
        super(zhihu_spider, self).__init__(*args, **kwargs)
        self.request_answer_param = None
        self.xsrf = ''
        #self.start_urls = get_all_target_urls()
        #self.start_urls.append(["CMU", "Carnegie Mellon University", "卡耐基梅隆"])
        #self.start_urls.append(["Massachusetts Institute of Technology","MIT","麻省理工"])
        self.start_urls.append(["宾夕法尼亚大学"])
        self.school = None

    def start_requests(self):
        return [Request("https://www.zhihu.com/#signin",
                        meta={'cookiejar': 1},
                        callback=self.post_login)]

    def post_login(self, response):
        self.xsrf = Selector(response).xpath('//input[@name="_xsrf"]/@value').extract()[0]
        return [FormRequest('https://www.zhihu.com/login/email', method='POST',
                            meta={'cookiejar': response.meta['cookiejar']},
                            headers=header,
                            formdata={
                                '_xsrf': self.xsrf,
                                'email': 'zpysky1125@sina.com',
                                'password': 'zpysky1125~@#',
                                'remember_me': 'true'},
                            callback=self.after_login,
                            dont_filter=True
                            )]

    def after_login(self, response):
        school = zhihu_school()
        school.names = self.start_urls[0]
        school.offset = len(school.names) * 20
        for name in school.names:
            url = base + name
            url2 = "https://www.zhihu.com/r/search?q=" + name + "&type=content&offset=10"
            yield Request(url, meta={'cookiejar': response.meta['cookiejar']}, callback=school.get_topics)
            yield Request(url2, meta={'cookiejar': response.meta['cookiejar']}, callback=school.get_more_topics)

        """
        for school_name in self.start_urls:
            school = zhihu_school()
            school.names = school_name
            school.offset = len(school_name) * 20
            for name in school_name:
                url = base + name
                url2 = "https://www.zhihu.com/r/search?q=" + name + "&type=content&offset=10"
                yield Request(url, meta={'cookiejar': response.meta['cookiejar']}, callback=school.get_topics)
                yield Request(url2, meta={'cookiejar': response.meta['cookiejar']}, callback=school.get_more_topics)
        """







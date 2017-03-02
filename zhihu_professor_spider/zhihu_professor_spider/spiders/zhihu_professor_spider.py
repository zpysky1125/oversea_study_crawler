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

#sys.stdout = file('new.txt', 'w')

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


def my_print(str="", str1=""):
        my_str = '' + str
        my_str = my_str.strip('\n').replace('<br>', '\n').replace('\n\n', '\n')
        my_str = str1 + my_str
        if my_str != '\n':
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
        self.answers = []
        self.xsrf = ''
        self.professor = None

    def parse_topic(self, response):
        selector = Selector(response)
        url = response.url
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
            answer_num = 0
        judge_question = True
        judge_topic = True
        for x in self.professor.key_words:
            if x.lower() not in question.lower():
                judge_topic = False
                break
        for x in self.professor.key_words:
            if x.lower() not in question.lower():
                judge_question = False
                break
        if judge_question or judge_topic:
            self.professor.key_in_answer = False
            if answer_num != 0:
                self.url = url;
                self.topic = topic;
                self.question = question
                for x in selector.xpath('//div[@class="zm-item-answer  zm-item-expanded"]'):
                    zhihu_ans = zhihu_answer()
                    zhihu_ans.qa = self
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
                    self.answers.append(zhihu_ans)
        else:
            self.url = url;
            self.topic = topic;
            self.question = question
            for x in selector.xpath('//div[@class="zm-item-answer  zm-item-expanded"]'):
                answer = x.xpath('div[@class="zm-item-rich-text js-collapse-body"]/div[@class="zm-editable-content clearfix"]').extract()
                judge_answer = True
                for key_word in self.professor.key_words:
                    if key_word.lower() not in answer[0].lower():
                        judge_answer = False
                        break
                if not judge_answer:
                    continue
                zhihu_ans = zhihu_answer()
                zhihu_ans.qa = self
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
                zhihu_ans.answer_content = answer
                self.answers.append(zhihu_ans)
        self.professor.finish_topic += 1
        if self.professor.finish_topic == 10:
            self.professor.zhihu_professor_print()

    def zhihu_question_answer_print(self):
        my_print(self.url, "url: ")
        my_print(self.topic, "topic: ")
        my_print(self.question, "question: ")
        print
        my_print('', 'answers: ')
        for ans in self.answers:
            ans.zhihu_answer_print()


class zhihu_prof(object):
    def __init__(self):
        self.prof_url = ''
        self.prof_name = ''
        self.xsrf = ''
        self.question_answers = []
        self.key_words = []
        self.finish_topic = 0
        self.key_in_answer = True

    def get_topics(self, response):
        selector = Selector(response)
        self.prof_url = response.url
        self.key_words = self.prof_name.split(' ')
        topics = selector.xpath('//li[@class="item clearfix"]')
        for topic in topics:
            summarys = topic.xpath('div[@class="content"]/ul[@class="answers"]/li/div/div[@class="entry-body"]'
                                    '/div[@class="entry-content js-collapse-body"]/div[@class="summary hidden-expanded"]'
                                    '/em/text()').extract()
            if summarys == []:
                self.finish_topic += 1
                continue
            judge_summary = True
            for key_word in self.key_words:
                judge = False
                for em in summarys:
                    if em.lower() in key_word.lower():
                        judge = True
                        break
                if not judge:
                    judge_summary = False
                    break
            if not judge_summary:
                self.finish_topic += 1
                continue
            qa = topic.xpath('div[@class="title"]/a/@href').extract()[0]
            new_topic = glob_base + qa
            zhihu_qa = zhihu_question_answer()
            zhihu_qa.professor = self
            self.question_answers.append(zhihu_qa)
            yield Request(new_topic, meta={'cookiejar': response.meta['cookiejar']}, callback=zhihu_qa.parse_topic)

    def zhihu_professor_print(self):
        if self.question_answers == []:
            return
        output_file = self.prof_name + '.txt'
        sys.stdout = file(output_file, 'w')
        my_print(self.prof_name, "professor name: ")
        for qa in self.question_answers:
            qa.zhihu_question_answer_print()


class zhihu_professor_spider(CrawlSpider):
    name = "zhihu_professor"
    allowed_domains = ["zhihu.com"]
    start_urls = []
    base = "https://www.zhihu.com"

    def __init__(self, *args, **kwargs):
        super(zhihu_professor_spider, self).__init__(*args, **kwargs)
        self.xsrf = ''
        self.start_urls = get_all_target_urls()
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
                                'email': 'xxx@yy.com',
                                'password': 'zzzz',
                                'remember_me': 'true'},
                            callback=self.after_login,
                            dont_filter=True
                            )]

    def after_login(self, response):
        for prof_name in self.start_urls:
            url = base + prof_name
            zhihu_professor = zhihu_prof()
            zhihu_professor.xsrf = self.xsrf
            zhihu_professor.prof_name = prof_name
            yield Request(url, meta={'cookiejar': response.meta['cookiejar']}, callback=zhihu_professor.get_topics)




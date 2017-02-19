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
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
    "Referer": "https://www.quora.com/",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "www.quora.com",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive"
}
base_url = "https://www.quora.com"
request_url = "https://www.quora.com/search?q="

def get_all_target_urls():
    f = open("C:\Users\zpysky\PycharmProjects\quora_spider\quora_spider\Facultylist_modify.txt", 'r')
    res = []
    while True:
        line = f.readline()
        line = line.strip('\n')
        if len(line) == 0:
            break
        res.append(line)
    return res


class quora_question_answer(object):
    def __init__(self):
        self.url = ''

    def get_question_answer(self, response):
        selector = Selector(response)
        pass


class quora_professor(object):
    def __init__(self):
        self.name = ''
        self.key_words = []
        self.finish = 0
        self.request_topic_urls = []
        self.topic_num = 0
        self.structure = []

    def get_questions(self, response):
        selector = Selector(response)
        topics = selector.xpath('//div[@class="pagedlist_item"]/div/div/div[@class="e_col w4_5"]')
        for topic in topics:
            title_url = topic.xpath('div[@class="title "]/div/a[@class="question_link"]/@href').extract()[0]
            title_name = topic.xpath('descendant::*[@class="rendered_qtext"]/text()').extract()[0]
            row_content = topic.xpath('div[@class="row content"]/div/div/div/div[@class="feed_card"]/span'
                                      '/div/div/span/span[@class="rendered_qtext"]/span[@class="matched_term"]/text()').extract()

            str = ''
            count = 0
            for x in topic.xpath('descendant::*[@class="rendered_qtext"]/text()').extract():
                if count == 0:
                    count += 1
                    continue
                str = str + x
            title_abstract = str
            in_key = True
            for key in self.key_words:
                i = False
                for y in row_content:
                    if key.lower() in y.lower():
                        i = True
                        break
                if not i:
                    in_key = False
                    break
            if in_key:
                topic_url = base_url + title_url
                if topic_url not in self.request_topic_urls:
                    self.request_topic_urls.append(topic_url)
                    self.structure.append([title_name, title_url, title_abstract])
        self.finish += 1
        if self.finish == 2:
            self.quora_prof_print()

    def quora_prof_print(self):
        if self.request_topic_urls == []:
            return
        output_file = 'C:\Users\zpysky\PycharmProjects\quora_spider\quora_spider\output\\' + self.name + '.txt'
        sys.stdout = open(output_file, 'w')
        for structure in self.structure:
            print 'Topic: ' + structure[0].strip()
            print 'Url: ' + structure[1].strip()
            print 'Abstract: '
            print structure[2].strip()
            print


class quora_spider(CrawlSpider):
    name = "quora_spider"
    allowed_domains = ["quora.com"]
    start_urls = []

    def __init__(self, *args, **kwargs):
        super(quora_spider, self).__init__(*args, **kwargs)
        self.start_urls = get_all_target_urls()
        #self.start_urls.append("David Patterson")

    def start_requests(self):
        return [Request("https://www.quora.com",
                        meta={'cookiejar': 1},
                        callback=self.get_prof)]

    def get_prof(self, response):
        for url in self.start_urls:
            quora_prof = quora_professor()
            quora_prof.name = url
            modify_url = url.replace('-', ' ')
            key = modify_url.split(' ')
            for k in key:
                if '.' in k:
                    key.remove(k)
            quora_prof.key_words = key
            url1 = request_url + url + "&type=answer"
            url2 = request_url + url + "&type=question"
            yield Request(url1, meta={'cookiejar': response.meta['cookiejar']}, callback=quora_prof.get_questions)
            yield Request(url2, meta={'cookiejar': response.meta['cookiejar']}, callback=quora_prof.get_questions)




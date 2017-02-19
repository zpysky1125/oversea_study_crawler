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
base = 'http://www.ratemyprofessors.com'
glob_base = 'http://www.ratemyprofessors.com/search.jsp?query='


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


class rate_professor_information(object):
    def __init__(self):
        self.school = ''
        self.work = ''
        self.overall_quality = ''
        self.average_grade = ''
        self.helpfulness = ''
        self.clarity = ''
        self.easiness = ''
        self.tags = []
        self.comments = []
        self.topic = None

    def get_info(self, response):
        selector = Selector(response)
        if selector.xpath('//div[@class="result-title"]/text()').extract() == []:
            self.topic.prof_infos.remove(self)
            self.topic.query -= 1
            if self.topic.finish_query == self.topic.query:
                self.topic.prof_print()
            return
        self.work = selector.xpath('//div[@class="result-title"]/text()').extract()[0]
        self.school = selector.xpath('//div[@class="result-title"]/h2/a/text()').extract()[0]
        self.overall_quality = selector.xpath('//div[@class="breakdown-wrapper"]/div[@class="breakdown-header"][1]'
                                              '/div[@class="grade"]/text()').extract()[0]
        self.average_grade = selector.xpath('//div[@class="breakdown-wrapper"]/div[@class="breakdown-header"][2]'
                                              '/div[@class="grade"]/text()').extract()[0]
        self.helpfulness = selector.xpath('//div[@class="faux-slides"]/div[@class="rating-slider"][1]'
                                          '/div[@class="rating"]/text()').extract()[0]
        self.clarity = selector.xpath('//div[@class="faux-slides"]/div[@class="rating-slider"][2]'
                                          '/div[@class="rating"]/text()').extract()[0]
        self.easiness = selector.xpath('//div[@class="faux-slides"]/div[@class="rating-slider"][3]'
                                          '/div[@class="rating"]/text()').extract()[0]
        tags = selector.xpath('//div[@class="tag-box"]/span[@class="tag-box-choosetags"]')
        for tag in tags:
            self.tags.append(tag.xpath('text()').extract()[0] + tag.xpath('b/text()').extract()[0])
        comments = selector.xpath('//tr[@class=""]')
        for comment in comments:
            comm = []
            helpfulness = comment.xpath('td[@class="rating"]/div/div[@class="breakdown"]'
                          '/div[@class="break"][1]/span[1]/text()').extract()[0]
            clarity = comment.xpath('td[@class="rating"]/div/div[@class="breakdown"]'
                          '/div[@class="break"][2]/span[1]/text()').extract()[0]
            easiness = comment.xpath('td[@class="rating"]/div/div[@class="breakdown"]'
                          '/div[@class="break"][3]/span[1]/text()').extract()[0]
            class_name = comment.xpath('td[@class="class"]/span[1]/span/text()').extract()[0]
            comment_content = comment.xpath('td[@class="comments"]/p[@class="commentsParagraph"]/text()').extract()[0]
            comm.append(helpfulness)
            comm.append(clarity)
            comm.append(easiness)
            comm.append(class_name)
            comm.append(comment_content.strip())
            self.comments.append(comm)
        self.topic.finish_query += 1
        if self.topic.finish_query == self.topic.query:
            self.topic.prof_print()

    def prof_info_print(self):
        print 'school: ' + self.school.strip()
        print 'work: ' + self.work.strip()
        print 'overall_quality: ' + self.overall_quality
        print 'average_grade: ' + self.average_grade
        print 'helpfulness: '+ self.helpfulness
        print 'clarity: ' + self.clarity
        print 'easiness: ' + self.easiness
        print 'tags:',
        for tag in self.tags:
            print tag + ' ',
        print '\n'
        print 'comments: '
        for comment in self.comments:
            print 'helpfulness: ' + comment[0] + '  ',
            print 'clarity: ' + comment[1] + '  ',
            print 'easiness: ' + comment[2] + '  ',
            print 'class_name: ' + comment[3]
            print 'comment: ' + comment[4]
            print

class rate_professor_topic(object):
    def __init__(self):
        self.name = ''
        self.relative_result = 0
        self.query = 0
        self.finish_query = 0
        self.prof_infos = []
        self.key = []

    def get_prof_topic(self, response):
        selector = Selector(response)
        prof_list = selector.xpath('//li[@class="listing PROFESSOR"]/a')
        self.relative_result = len(prof_list)
        if self.relative_result >= 1:
            urls = []
            for x in prof_list:
                name = x.xpath('span[@class="listing-name"]/span[@class="main"]/text()').extract()[0]
                key_in = True
                for key in self.key:
                    if key.lower() not in name.lower():
                        key_in = False
                        continue
                if not key_in:
                    continue
                self.query += 1
                prof_info = rate_professor_information()
                prof_info.topic = self
                self.prof_infos.append(prof_info)
                url = base + x.xpath('@href').extract()[0]
                peer = [url, prof_info]
                urls.append(peer)
            for peer in urls:
                yield Request(peer[0], meta={'cookiejar': response.meta['cookiejar']}, callback=peer[1].get_info)

    def prof_print(self):
        if self.query == 0:
            return
        if self.query == 1:
            output_file = "C:\Users\zpysky\PycharmProjects\\" + "rate_professor_spider\\" + "rate_professor_spider\output\\" \
                          + self.name + '.txt'
        else:
            output_file = "C:\Users\zpysky\PycharmProjects\\" + "rate_professor_spider\\" + "rate_professor_spider\output\\" \
                          + self.name + "__" + str(self.query) + '.txt'
        sys.stdout = file(output_file, 'w')
        print 'professor_name: ' + self.name
        for prof_info in self.prof_infos:
            prof_info.prof_info_print()


class rate_professor_spider(CrawlSpider):
    name = "rate_professor"
    allowed_domains = ["www.ratemyprofessors.com"]
    start_urls = []

    def __init__(self, *args, **kwargs):
        super(rate_professor_spider, self).__init__(*args, **kwargs)
        self.start_urls = get_all_target_urls()

    def start_requests(self):
        return [Request("http://www.ratemyprofessors.com",
                        meta={'cookiejar': 1},
                        callback=self.post_request)]

    def post_request(self, response):
        for prof_name in self.start_urls:
            url = glob_base + prof_name
            prof = rate_professor_topic()
            prof.name = prof_name
            prof.key = prof_name.replace('.', '').split(' ')
            yield Request(url, meta={'cookiejar': response.meta['cookiejar']}, callback=prof.get_prof_topic)






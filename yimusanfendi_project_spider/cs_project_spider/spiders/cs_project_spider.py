#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re
import json
import sys
import time
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
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
    "Host": "instant.1point3acres.com",
    "Referer": "https://instant.1point3acres.com/signin?next=%2F",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}

header2 = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
    "Host": "en.wikipedia.org",
    "Content": "keep-alive",
    "Cache-Control": "max-age=0"
}


class school_project(object):
    def __init__(self):
        self.project_url = ''
        self.project_name = ''
        self.enrollment_time = ''
        self.deadline = 'deadline: '
        self.apply_fee = ''
        self.degree = ''
        self.offered_by = ''
        self.contact = ''
        self.school = None

    def get_project_info(self, response):
        selector = Selector(response)
        self.apply_fee = selector.xpath('//div[@class="col-md-3"][2]/p[3]/text()').extract()[0]
        self.enrollment_time = selector.xpath('//div[@class="col-md-3"][3]/p[1]/text()').extract()[0]
        if selector.xpath('//div[@class="col-md-3"][3]/p[2]/text()').extract() != []:
            self.deadline = selector.xpath('//div[@class="col-md-3"][3]/p[2]/text()').extract()[0]
        intro = selector.xpath('//div[@class="col-xs-12 col-sm-8"]/div[@class="panel panel-default"]/div[@class="panel-body"]'
                       '/table[@class="table"]')
        self.degree = intro.xpath('tr[1]/td/text()').extract()[0] + intro.xpath('tr[1]/td/a/text()').extract()[0]
        self.offered_by = intro.xpath('tr[2]/td/text()').extract()[0]
        self.contact = intro.xpath('tr[3]/td/text()').extract()[0]
        self.school.finish_project += 1
        if self.school.finish_project == self.school.project_num and self.school.finish == 1:
            self.school.school_info_print()

    def project_print(self):
        print '项目名称：' + self.project_name.strip()
        print self.enrollment_time.strip()
        print self.deadline.strip()
        print self.apply_fee.strip()
        print '学位: ' + self.degree
        print 'offered_by: ' + self.offered_by
        print '联系方式: ' + self.contact.strip()
        print

class cs_school(object):
    def __init__(self):
        self.project_list = []
        self.school_url = ''
        self.school_name = ''
        self.school_image = ''
        self.school_intro = ''
        self.school_intro_url = ''
        self.school_position_image = ''
        self.school_city = ''
        self.school_state = ''
        self.school_zipcode = ''
        self.school_address = ''
        self.school_study_cost = ''
        self.school_live_cost = ''
        self.cs_rank = ''
        self.rank_usnews = ''
        self.rank_times = ''
        self.rank_qs = ''
        self.project_num = 0
        self.finish_project = 0
        self.finish = 0

    def get_school_info(self, response):
        selector = Selector(response)
        self.school_image = (((selector.xpath('//script[@type="text/javascript"]/text()').extract()[0])
                              .split("google_view = ")[1]).split(";")[0]).strip('"')
        self.school_intro_url = (((selector.xpath('//script[@type="text/javascript"]/text()').extract()[0])
                              .split("wiki_url = ")[1]).split(";")[0]).strip('"')
        table = selector.xpath('//div[@class="panel-body"]/table[@class="table"]')
        rank_table = selector.xpath('//div[@class="panel panel-default"]/table[@class="table"]')
        self.school_position_image = table.xpath('tr[1]/td/a/@href').extract()[0]
        self.school_city = table.xpath('tr[2]/td[2]/text()').extract()[0]
        self.school_state = table.xpath('tr[3]/td[2]/text()').extract()[0]
        self.school_zipcode = table.xpath('tr[4]/td[2]/text()').extract()[0]
        self.school_address = table.xpath('tr[5]/td[2]/text()').extract()[0]
        self.school_study_cost = table.xpath('tr[6]/td[2]/text()').extract()[0].strip('\n').replace(' ', '')
        self.school_live_cost = table.xpath('tr[7]/td[2]/text()').extract()[0].strip('\n').replace(' ', '')
        self.rank_usnews = rank_table.xpath('tr[2]/td[1]/text()').extract()[0]
        self.rank_times = rank_table.xpath('tr[3]/td[1]/text()').extract()[0]
        self.rank_qs = rank_table.xpath('tr[4]/td[1]/text()').extract()[0]
        yield FormRequest(self.school_intro_url, method='GET', headers=header2, callback=self.get_school_intro)

    def get_school_intro(self, response):
        self.school_intro = response.body.split('extract":')[1].strip(')').strip('}').strip('"')
        self.finish = 1
        if self.finish_project == self.project_num:
            self.school_info_print()

    def school_info_print(self):
        output_file = self.school_name + '.txt'
        sys.stdout = file(output_file, 'w')
        print '学校：' + self.school_name
        print '学校图片：'+ self.school_image
        print '简介：' + self.school_intro
        print '学校位置：' + self.school_position_image
        print '城市: ' + self.school_city
        print '州: ' + self.school_state
        print 'zipcode: ' + self.school_zipcode
        print '地址: ' + self.school_address
        print '学费：' + self.school_study_cost
        print '生活费：' + self.school_live_cost
        print 'US NEWS 排名：' + self.rank_usnews
        print 'TIMES 排名：' + self.rank_times
        print 'QS 排名：' + self.rank_qs
        print '项目列表：\n'
        for x in self.project_list:
            x.project_print()


class cs_project_spider(CrawlSpider):
    name = "cs_project"
    #allowed_domains = ["1point3acres.com"]
    start_urls = ["https://instant.1point3acres.com/program/rank/cs"]
    base = "https://instant.1point3acres.com"

    def __init__(self, *args, **kwargs):
        super(cs_project_spider, self).__init__(*args, **kwargs)
        self.request_answer_param = None
        self.xsrf = ''

    def start_requests(self):
        return [Request("https://instant.1point3acres.com/signin",
                        meta={'cookiejar': 1},
                        callback=self.post_login)]

    def post_login(self, response):
        self.xsrf = Selector(response).xpath('//input[@name="_xsrf"]/@value').extract()[0]
        return [FormRequest('https://instant.1point3acres.com/signin', method='POST',
                            meta={'cookiejar': response.meta['cookiejar']},
                            headers=header,
                            formdata={
                                '_xsrf': self.xsrf,
                                'name_or_email': 'zpysky1125@sina.com',
                                'password': 'zpysky1125~@#',
                                'question_id': '0',
                                'remember_me': '1'},
                            callback=self.after_login,
                            )]

    def after_login(self, response):
        yield Request(self.start_urls[0], meta={'cookiejar': response.meta['cookiejar']}, callback=self.get_program_list)

    def get_program_list(self, response):
        selector = Selector(response)
        i = 0
        while i < 7:
            i += 1
            url = "https://instant.1point3acres.com/program/rank/cs?ajax=true&pg=" + str(i)
            yield Request(url, method='GET', meta={'cookiejar': 1}, callback=self.get_program)

    def get_program(self, response):
        selector = Selector(response)
        #print response.body
        program_list = selector.xpath('//div[@class="row"]/div[@class="col-xs-10 col-sm-10 no-right-padding"]')
        for node in program_list:
            school = cs_school()
            school.school_url = node.xpath('div[@class="institute_intro"]/h4/a/@href').extract()[0]
            school.school_name = node.xpath('div[@class="institute_intro"]/h4/a/span/text()').extract()[0]
            school_projects = node.xpath('div[@class="row"]/div[@class="col-xs-6 col-sm-6"]'
                                            '/div[@class="institute_intro"]/p/a[@target="_blank"]')
            school.cs_rank = node.xpath('div[@class="institute_intro"]/h4/span[@class="institute_rank"]/text()').extract()[0].replace('#', '')
            school.project_num = len(school_projects)
            yield Request(self.base+school.school_url, meta={'cookiejar': 1}, callback=school.get_school_info)
            for project_node in school_projects:
                project = school_project()
                project.school = school
                project.project_url = "https://instant.1point3acres.com" + project_node.xpath('@href').extract()[0]
                project.project_name = project_node.xpath('text()').extract()[0]
                school.project_list.append(project)
                yield Request(project.project_url, meta={'cookiejar': 1}, callback=project.get_project_info)



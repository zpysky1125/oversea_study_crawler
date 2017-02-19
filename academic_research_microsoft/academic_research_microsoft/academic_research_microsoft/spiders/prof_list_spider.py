import scrapy
from scrapy.http import HtmlResponse
from scrapy.selector import Selector
import urlparse
import xlwt

count = 0
file = open("C:\Users\zpysky\PycharmProjects\\academic_research_microsoft\\academic_research_microsoft\\facultylist.txt","r")
list = []
for line in file:
    name = line.strip("\n").strip(" ")
    list.append(name)

#print list
profs_table = xlwt.Workbook()
profs_sheet = profs_table.add_sheet("total_page")

class acaspider(scrapy.Spider):
    name = "profspider"
    download_delay = 0.10
    start_urls = [
        'https://www.baidu.com/' ,
    ]

    def parse(self,response):
        global list
        #yield scrapy.Request("http://academic.research.microsoft.com/Author/622916/omead-amidi", callback=self.third_parse)

        for name in list:
            yield scrapy.Request("http://academic.research.microsoft.com/Detail?query=" + name + "&searchtype=1&s=0&SearchDomain=2", callback=self.second_parse)
            #scrapy.Request("http://academic.research.microsoft.com/Detail?query=" + name + "&searchtype=1&s=0&SearchDomain=2",callback = self.second_parse )

    def second_parse(self,response):
        link = response.xpath("//div[@id='ctl00_MainContent_ObjectList_ctl00_divContent']/div[@class='title']/h3/a/@href")
        if ( len(link) == 0 ):
            return
        #print link[0].extract()
        yield scrapy.Request(urlparse.urljoin(response.url,link[0].extract()),callback = self.third_parse )

    def third_parse(self,response):
        global count
        print response.url
        name = response.xpath("//span[@id='ctl00_MainContent_AuthorItem_authorName']/text()")
        if ( len (name) == 0 ):
            name = ""
        else:
            name = name.extract()[0]
        print name
        org  = response.xpath("//a[@id='ctl00_MainContent_AuthorItem_affiliation']/text()")
        if ( len(org) > 0 ):
            org = org[0].extract()
        else:
            org = ""
        cit  = response.xpath("//a[@id='ctl00_MainContent_AuthorItem_citedBy']/span/text()")
        if ( len(cit) == 0 ):
            cit = ""
        else:
            cit = cit.extract()[0]
        print cit
        pub  = response.xpath("//a[@id='ctl00_MainContent_AuthorItem_divAffiliation']/span/text()")
        if ( len(pub) == 0 ):
            pub = ""
        else:
            pub = pub.extract()[0]
        fld  = response.xpath("//div[@class='line-height-small']")[0].xpath(".//a/text()").extract()
        homepage = response.xpath("//a[@id='ctl00_MainContent_AuthorItem_imgHomePageLink']/@href")
        if ( len(homepage) > 0 ):
            homepage =  urlparse.urljoin(response.url , homepage[0].extract() )
        else:
            homepage = ""
        link = response.url
        profs_sheet.write( count , 0 , name )
        profs_sheet.write( count , 1 , org )
        profs_sheet.write( count , 2 , cit )
        profs_sheet.write( count , 3 , pub )
        profs_sheet.write( count , 4 , fld )
        profs_sheet.write( count , 5 , homepage)
        profs_sheet.write( count , 6 , link )
        profs_table.save("porfs_list.xls")
        count = count + 1

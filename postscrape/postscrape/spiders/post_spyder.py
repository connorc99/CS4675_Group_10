import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import *
from scrapy.item import Item, Field

from scrapy import signals
from pydispatch import dispatcher

import datetime
import csv
import time
 
class SuperSpider(CrawlSpider):
    name = 'extractor'
    allowed_domains = ['www.cc.gatech.edu']
    start_urls = ['https://www.cc.gatech.edu']
    base_url = 'https://www.cc.gatech.edu'
    rules = [Rule(LinkExtractor(), callback='parse_item', follow=True)]
    keywords = {
        "computing" : [],
        "undergraduate": [],
        "research": [],
        "online": []
    }

    custom_settings = {
        "DEPTH_LIMIT": 10
    }


    pages_crawled = 0

    def __init__(self, name = "default", allowed_suffix = None, max_depth = 20, filter_depth = 10):
        super(SuperSpider, self).__init__()
        self.name = name
        self.suffix_list = allowed_suffix
        self.max_depth = max_depth
        self.filter_depth = filter_depth
        '''
        custom_settings = {
            "DEPTH_LIMIT": max_depth #not currently working :(
        }
        '''

    def parse_item(self, response):
        self.log("scraper {}".format(self.name))
        self.log('crawling {}'.format(response.url))
        self.log('current depth: {}'.format(response.meta['depth']))

        #time.sleep(1) #delete after testing

        suffix = response.url.split("edu")[1][0]

        if response.meta['depth'] > self.filter_depth and False and suffix not in self.suffix_list: #once past certain level, must meet prefix
            self.log('filtered out suffix past depth')
            return
        if self.pages_crawled % 100 == 0:
            stats = self.crawler.stats.get_stats()
            with open('test_stats_{}.csv'.format(self.pages_crawled), 'w') as csv_file:  
                writer = csv.writer(csv_file)
                for key, value in stats.items():
                    writer.writerow([key, value])
                for key, value in self.keywords.items():
                    writer.writerow([key, len(value)])
                    print([key, len(value)])
                writer.writerow(["current_time", datetime.datetime.now()])

            with open('keyword_current_output.csv', 'w') as csv_file:  
                writer = csv.writer(csv_file)
                for key, value in self.keywords.items():
                    writer.writerow([key, value])
    
        self.pages_crawled += 1
        for keyword in self.keywords:
            if keyword in response.text.lower():
                self.keywords[keyword].append(response.url)
            else:
                pass
        #print(self.crawler.stats.get_stats())

    def close(self, spider):
        self.log("KEYWORDS:::::")
        stats = self.crawler.stats.get_stats()

        print(stats)
        with open('stats_final_output.csv', 'w') as csv_file:  
            writer = csv.writer(csv_file)
            for key, value in stats.items():
                writer.writerow([key, value])


        with open('keyword_final_output.csv', 'w') as csv_file:  
            writer = csv.writer(csv_file)
            for key, value in self.keywords.items():
                writer.writerow([key, value])

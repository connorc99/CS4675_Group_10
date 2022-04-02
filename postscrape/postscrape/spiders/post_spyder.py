import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import *
from scrapy.item import Item, Field

from scrapy import signals
from pydispatch import dispatcher

import datetime
import csv
import time

import sqlite3
from sqlite3 import Error
 
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
        self.connection = self.create_connection("db/urldatabase.db")
        self.cur = self.connection.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS urls (scraper_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, url VARCHAR(255) NOT NULL, `creation_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

    def parse_item(self, response):
        self.log("scraper {}".format(self.name))
        self.log('crawling {}'.format(response.url))
        self.log('current depth: {}'.format(response.meta['depth']))

        #check and see if already in database, if so do not parse the item
        if self.check_in_db(response.url):
            return

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
        
        #add to persistent memory storage
        self.add_to_db(response.url)

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

    def check_in_db(self, url):
        print("checking in database...")
        # with open("scraped_urls.json", "r") as json_file:
        #     data = json.load(json_file)
        #     return url in data["url"]
        self.cur.execute("select * from urls where url='{}'".format(url))
        output = self.cur.fetchall()
        print("Checking if already in database- output from DB is {}".format(output))
        return output != []
        

    def add_to_db(self, url):
        print("adding to db...")
        # with open("scraped_urls.json", "w") as json_file:
        #     data = json.load(json_file)
        #     return url in data["url"]
        print("Adding new url to database of {}".format(url))
        self.cur.execute("insert into urls values ('{}', '{}')".format(self.name, url))
        self.connection.commit()

    def create_connection(self, db_file):
        """ create a database connection to a SQLite database """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            print(sqlite3.version)
            return conn
        except Error as e:
            print("Could not connect, resting, error will pop up in ~5 seconds")
            time.sleep(4)
            print(e)

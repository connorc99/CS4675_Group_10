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

'''
Change these between runs
filter_depth: when to start checking URLs that have been added for appropriate suffix, we MANUALLY check this w/ suffix list
max_depth: the deepest inside a suffix the scraper can go, scrapy checks this for us AUTOMATICALLY

Issue: we DO want to scrape an already scraped page if we are on or past filter_depth, but just add the new links
    -Alternative is we DONT scrape the page

2 Implementations:
    1. We scrape already scraped pages in each scraper, and only check to see if that specific scraper has scraped that URL yet
    2. We don't scrape pages already scraped, which will be quicker and discover less pages

We can talk about the tradeoffs in the writeup of each

This file will be doing option 2- we will NOT scrape a page if another scraper has already scraped it

I think this still parses every page, but only scrapes keywords from ones between filter and max depth. 
We can discuss a limitation in knowing how to implement not having the follow=True workaround
'''
filter_depth = 10
max_depth = filter_depth + 5

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
        "DEPTH_LIMIT": max_depth 
    }
    pages_crawled = 0

    '''
    name: name of the scraper for table
    allowed_suffix: list of letters we will allow as the suffix
    '''
    def __init__(self, name = "default", allowed_suffix = None, table_name = None):
        super(SuperSpider, self).__init__()
        self.name = name
        self.table_name = table_name
        self.suffix_list = allowed_suffix
        self.max_depth = max_depth
        self.filter_depth = filter_depth
        self.connection = self.create_connection(".\\db\\urldatabase.db")
        self.duplicates_from_other_scraper = 0
        self.last_dequeue_value = -9999
        self.cur = self.connection.cursor()
        try:
            '''
            self.cur.execute("CREATE TABLE IF NOT EXISTS scraper (scraper_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, name VARCHAR(255), max_depth INT, filter_depth INT, creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
            self.cur.execute("CREATE TABLE IF NOT EXISTS url (url_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, scraper_id INT NOT NULL, url VARCHAR(255) NOT NULL, creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

            self.cur.execute("INSERT INTO scraper (name, max_depth, filter_depth) VALUES ('{}', {}, {})".format(self.name, self.max_depth, self.filter_depth));
            '''
            self.scraper_id = self.cur.lastrowid
            self.connection.commit()
            print(self.scraper_id)
            
        except Error as e:
            print(e)
            time.sleep(4)

    def parse_item(self, response):
        self.log("scraper {}".format(self.name))
        self.log('crawling {}'.format(response.url))
        self.log('current depth: {}'.format(response.meta['depth']))

        #check and see if already in database, if so do not parse the item
        if self.check_in_db(response.url):
            self.duplicates_from_other_scraper += 1
            return

        #get the letter for suffix
        suffix = response.url.split("edu")[1][0]

        if (response.meta['depth'] > self.filter_depth) and (suffix not in self.suffix_list): #once past certain level, must meet prefix
            self.log('filtered out suffix past depth')
            return
        

        #adds persistent stats- should probably convert this to SQL
        print("stats check!!")
        print(self.crawler.stats.get_stats())
        if self.crawler.stats.get_stats()["scheduler/dequeued"] - self.last_dequeue_value > 500:
            self.last_dequeue_value = self.crawler.stats.get_stats()["scheduler/dequeued"] 
            self.write_stats()



        for keyword in self.keywords:
            if keyword in response.text.lower():
                self.keywords[keyword].append(response.url)
            else:
                pass

        #add to persistent memory storage
        self.add_to_db(response.url)



        #print(self.crawler.stats.get_stats())

    '''
    def write_stats_old(self):
        print("-------------------\nWriting stats! We are at {}".format(self.pages_crawled))
        time.sleep(2)
        try:
                stats = self.crawler.stats.get_stats()
                stats_path = "output_stats/{}/{}/".format(self.table_name, self.name)
                with open('{}/stats_{}.csv'.format(stats_path, self.pages_crawled), 'w') as csv_file:
                    writer = csv.writer(csv_file)
                    for key, value in stats.items():
                        writer.writerow([key, value])
                    for key, value in self.keywords.items():
                        writer.writerow([key, len(value)])
                        print([key, len(value)])
                    writer.writerow(["current_time", datetime.datetime.now()])

                with open('{}/keword_stats.csv'.format(stats_path), 'w') as csv_file:
                    writer = csv.writer(csv_file)
                    for key, value in self.keywords.items():
                        writer.writerow([key, value])
                print("Added stats!")
                time.sleep(2)
        except Exception as e:
            print("stats error!")
            print(e)
            time.sleep(3)
    '''

    def write_stats(self):
        '''
        - Create the table for this configuration if one does not exist
        - Drop all old records from the table
        - So just drop and then create I guess

        - Insert into the table the current scraper name, start time, currently enqueued, currently dequeued, request count, response count, 
        duplicates in this scraper filtered, DUPES OVERALL FILTERED- NEED TO TRACK, offsite requests filtered, current keyword stats and current time

        '''
        try:
            stats = self.crawler.stats.get_stats()
            print(stats)
            insert_query = f'''
            INSERT INTO {self.table_name} 
            (
                scraper_name,
                enqueued,
                dequeued,
                request_count,
                response_count,
                duplicates_filtered_internal,
                duplicates_filtered_from_others,
                offsites_filtered,
                computing_count,
                undergrad_count,
                research_count,
                online_count,
                current_time
            )
            VALUES
            (
                '{self.name}',
                {stats["scheduler/enqueued"]}, 
                {stats["scheduler/dequeued"]},
                {stats["downloader/request_count"]},
                {stats["downloader/response_count"]},
                {stats["dupefilter/filtered"]},
                {self.duplicates_from_other_scraper},
                {stats["offsite/filtered"]},
                {len(self.keywords["computing"])},
                {len(self.keywords["undergraduate"])},
                {len(self.keywords["research"])},
                {len(self.keywords["online"])},
                CURRENT_TIMESTAMP
            )
            '''
            print(insert_query)
            self.cur.execute(insert_query)
            self.connection.commit()
            print("SUCCESS IN INSERTION")
        except Exception as e:
            print("ERROR INSERTING: {}".format(e))
            print("Sleeping for 3...")
        finally:
            time.sleep(3)


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
        try:
            print("checking in database...")
            # with open("scraped_urls.json", "r") as json_file:
            #     data = json.load(json_file)
            #     return url in data["url"]
            self.cur.execute("select * from url where url='{}'".format(url))
            output = self.cur.fetchall()
            print("Checking if already in database- output from DB is {}".format(output))
        except Exception as e:
            print("Error checking database: {}".format(e))
            time.sleep(3)
            return False

        return output != []


    def add_to_db(self, url):
        print("adding to db...")
        # with open("scraped_urls.json", "w") as json_file:
        #     data = json.load(json_file)
        #     return url in data["url"]
        print("Adding new url to database of {}".format(url))
        self.cur.execute("insert into url (scraper_id, url) values ('{}', '{}')".format(self.scraper_id, url))
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
            print(e)
            time.sleep(4)

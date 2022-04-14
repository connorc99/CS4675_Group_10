
initial_depth = 3
filter_depth = 8
max_depth = 15

'''
- Adds all links in depth to initial depth
- Only adds links past inital depth if link is not in database
- Only adds links past filter depth if above is true and suffix condition is met

'''

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
    #rules = [Rule(LinkExtractor(), callback='parse_item', follow=True)]
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
    @name: name of the scraper for table
    @allowed_suffix: list of letters we will allow as the suffix
    '''
    def __init__(self, name = "default", allowed_suffix = None, table_name = None):
        super(SuperSpider, self).__init__()
        self.name = name
        self.table_name = table_name
        self.suffix_list = allowed_suffix
        self.max_depth = max_depth
        self.filter_depth = filter_depth
        self.initial_depth = initial_depth
        self.connection = self.create_connection(".\\db\\urldatabase.db")
        self.duplicates_from_other_scraper = 0 #a value we set ourselves for the stats output, where we query the DB and the URL was already in it. Scrapy filters them out for us if the same scraper was the one who discovered the page
        self.last_dequeue_value = -9999
        self.cur = self.connection.cursor()

        self.link_extractor = LinkExtractor()


    def start_requests(self):
        yield scrapy.Request('https://www.cc.gatech.edu', self.parse)

    def parse(self, response):
        self.log("scraper {}".format(self.name))
        self.log('crawling {}'.format(response.url))
        self.log('current depth: {}'.format(response.meta['depth']))

        already_in_db = self.check_in_db(response.url)
        suffix = self.get_suffix

        #If we already have the link in DB, only consider it if its in the inital sweep
        if already_in_db:
            self.duplicates_from_other_scraper += 1
            #If we are deeper than the 
            #if response.meta['depth'] < filter_depth or suffix in self.suffix_list:
            if response.meta['depth'] <= self.initial_depth:
                pass
            else:
                return

        #Periodically add stats to DB
        if self.crawler.stats.get_stats()["scheduler/dequeued"] - self.last_dequeue_value > 500:
            self.last_dequeue_value = self.crawler.stats.get_stats()["scheduler/dequeued"] 
            self.write_stats()

        #Only add keyword info if this is a new page- else, just extract links!
        if not already_in_db:
            for keyword in self.keywords:
                if keyword in response.text.lower():
                    self.keywords[keyword].append(response.url)
                else:
                    pass
            self.add_to_db(response.url)

        #This part adds any new links we want to consider
        for link in self.link_extractor.extract_links(response):
            suffix = self.get_suffix(link)
            if (response.meta['depth'] > self.filter_depth) and (suffix not in self.suffix_list):
                print("Filtered out non matching suffix!")
            else:
                #print("Adding in link {}".format(link))
                yield scrapy.Request(link.url, callback=self.parse)


    
    def get_suffix(self, link):
        try:
            suffix = link.split("edu")[1][0]
        except:
            suffix = ""

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
        print("Writing stats...")
        try:
            stats = self.crawler.stats.get_stats()
            print(stats)
            #These are problematic on first run, so just manually set these
            try:
                duplicates_start = stats["dupefilter/filtered"]
                offsite_start = stats["offsite/filtered"]
                dups_from_others = self.duplicates_from_other_scraper #note- this is not currently working/ telling us anything
            except:
                duplicates_start = 0
                offsite_start = 0
                dups_from_others = 0
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
                {duplicates_start},
                {dups_from_others},
                {offsite_start},
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
            #time.sleep(3)
            print("Done with insertion function...\n\n")


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
        self.cur.execute("insert into url (scraper_id, url) values ('{}', '{}')".format(self.name, url))
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

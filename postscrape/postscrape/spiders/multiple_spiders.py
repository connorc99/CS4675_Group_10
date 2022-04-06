'''
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from post_spyder import SuperSpider 


configure_logging()
runner = CrawlerRunner()

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(SuperSpider, allowed_suffix= ["a", "b", "c"], name="first", max_depth = 2)
    yield runner.crawl(SuperSpider, allowed_suffix = ["d", "e", "f"], name="second")
    reactor.stop()



crawl()
reactor.run() # the script will block here until the last crawl call is finished
'''

import scrapy
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from post_spyder import SuperSpider 

import sqlite3
from sqlite3 import Error

import time

configure_logging();
settings = get_project_settings()
runner = CrawlerRunner(settings)

subprocesses = 2
filter_depth = 3
max_depth = 5

table_name = "subprocesses_{}_filterdepth_{}_maxdepth_{}".format(subprocesses, filter_depth, max_depth) 
conn = sqlite3.connect(".\\db\\urldatabase.db")
print(sqlite3.version)
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS {}".format(table_name))
cur.execute('''
    CREATE TABLE {} (
    insertion_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    scraper_name VARCHAR(100),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount_scraped_rough INT,
    enqueued INT,
    dequeued INT,
    request_count INT,
    response_count INT,
    duplicates_filtered_internal INT,
    duplicates_filtered_from_others INT,
    offsites_filtered INT,
    computing_count INT,
    undergrad_count INT,
    research_count INT,
    online_count INT,
    current_time TIMESTAMP, 
    subprocesses INT DEFAULT {},
    filter_depth INT DEFAULT {},
    max_depth INT DEFAULT {}
    )
    
    '''.format(table_name, subprocesses, filter_depth, max_depth))
conn.commit()
conn.close()


time.sleep(3)

#scraper_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
# name VARCHAR(255), max_depth INT, filter_depth INT, creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP

runner.crawl(SuperSpider, allowed_suffix= ["a", "b", "c"], name="scraper_1", table_name = table_name)
runner.crawl(SuperSpider, allowed_suffix = ["d", "e", "f"], name="scraper_2",  table_name = table_name)
#ideally work on persistance of scraped files

d = runner.join()
d.addBoth(lambda _: reactor.stop())

reactor.run() # the script will block here until all crawling jobs are finished
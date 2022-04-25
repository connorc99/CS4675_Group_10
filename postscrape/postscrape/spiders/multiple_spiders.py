'''
Between runs for analysis:
- Change filter_depth and max_depth both here AND in post_spyder, custom_settings causes problems if I pass it in for some reason

Subprocesses: 1/2/4

Initial depth:  2/3
Filter depth:   5/8
Max depth:     10/15

'''

subprocesses = 2
initial_depth = 2
filter_depth = 3
max_depth = 5

import scrapy
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from post_spyder import SuperSpider
import sqlite3
from sqlite3 import Error
import time

iteration = 0
print("\n\n---------------------\nRUNNING MAIN FILE: {}\n\n\n------------------------------".format(iteration))
iteration += 1
#time.sleep(3)

configure_logging()
settings = get_project_settings()
runner = CrawlerRunner()


table_name = "subprocesses_{}_initialdepth_{}_filterdepth_{}_maxdepth_{}".format(subprocesses, initial_depth, filter_depth, max_depth)
conn = sqlite3.connect(".\\db\\urldatabase.db")
print(sqlite3.version)
cur = conn.cursor()


try:
    cur.execute("CREATE TABLE IF NOT EXISTS url (url_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, scraper_id INT NOT NULL, url VARCHAR(255) NOT NULL, creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
except Error as e:
    print(e)
    time.sleep(4)

#Clear out table of URLs for new scrapers to write to
try:
    cur.execute("delete from url")
except:
    pass

#Create fresh table to track stats with
cur.execute("DROP TABLE IF EXISTS {}".format(table_name))
cur.execute('''
    CREATE TABLE {} (
    insertion_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    scraper_name VARCHAR(100),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    initial_depth INT DEFAULT {},
    filter_depth INT DEFAULT {},
    max_depth INT DEFAULT {}
    )

    '''.format(table_name, subprocesses, initial_depth, filter_depth, max_depth))
conn.commit()
conn.close()

print("Created table, about to start...")
time.sleep(3)

import string
alphabet_list = list(string.ascii_lowercase)

if subprocesses == 1:
    runner.crawl(SuperSpider, allowed_suffix= alphabet_list, name="scraper_1", table_name = table_name)
elif subprocesses == 2:
    runner.crawl(SuperSpider, allowed_suffix= alphabet_list[:13], name="scraper_1", table_name = table_name)
    runner.crawl(SuperSpider, allowed_suffix = alphabet_list[13:], name="scraper_2",  table_name = table_name)
elif subprocesses == 4:
    runner.crawl(SuperSpider, allowed_suffix= alphabet_list[:6], name="scraper_1", table_name = table_name)
    runner.crawl(SuperSpider, allowed_suffix = alphabet_list[6:13], name="scraper_2",  table_name = table_name)
    runner.crawl(SuperSpider, allowed_suffix = alphabet_list[13:19], name="scraper_3",  table_name = table_name)
    runner.crawl(SuperSpider, allowed_suffix = alphabet_list[19:], name="scraper_4",  table_name = table_name)


d = runner.join()
d.addBoth(lambda _: reactor.stop())

reactor.run() # the script will block here until all crawling jobs are finished

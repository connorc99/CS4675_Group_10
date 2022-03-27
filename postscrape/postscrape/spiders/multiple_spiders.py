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

configure_logging();
settings = get_project_settings()
runner = CrawlerRunner(settings)
runner.crawl(SuperSpider, allowed_suffix= ["a", "b", "c"], name="first")
runner.crawl(SuperSpider, allowed_suffix = ["d", "e", "f"], name="second")
#ideally work on persistance of scraped files

d = runner.join()
d.addBoth(lambda _: reactor.stop())

reactor.run() # the script will block here until all crawling jobs are finished
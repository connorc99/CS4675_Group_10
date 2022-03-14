from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from post_spyder import SuperSpider 


configure_logging()
runner = CrawlerRunner()

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(SuperSpider, allowed_suffix= ["a", "b", "c"])
    yield runner.crawl(SuperSpider, allowed_suffix = ["d", "e", "f"])
    reactor.stop()

crawl()
reactor.run() # the script will block here until the last crawl call is finished
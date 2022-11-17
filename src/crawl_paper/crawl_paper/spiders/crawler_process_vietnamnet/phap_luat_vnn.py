import sys
import os
sys.path.append(os.path.abspath(os.path.join('.', 'crawl_paper')))

from vietnamnet import VietnamnetSpider
from scrapy.crawler import CrawlerProcess

def main():
    process = CrawlerProcess()
    process.crawl(VietnamnetSpider, category='phap-luat', limit=100)
    process.start()

if __name__ == '__main__':
    main()

import sys
import os
sys.path.append(os.path.abspath(os.path.join('.', 'crawl_paper')))

from crawl_paper.spiders.dantri import DantriSpider
from scrapy.crawler import CrawlerProcess

def main():
    process = CrawlerProcess()
    process.crawl(DantriSpider, category='bat-dong-san')
    process.start()

if __name__ == '__main__':
    main()
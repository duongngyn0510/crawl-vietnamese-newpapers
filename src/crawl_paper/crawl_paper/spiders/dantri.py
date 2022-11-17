import json
import os
import time
import scrapy


URL = 'http://dantri.com.vn/'

CATEGORIES = {
    'xa-hoi': 'xa-hoi',
    'the-gioi': 'the-gioi',
    'kinh-doanh': 'kinh-doanh',
    'bat-dong-san': 'bat-dong-san',
    'the-thao': 'the-thao',
    'lao-dong-viec-lam': 'lao-dong-viec-lam',
    'tam-long-nhan-ai': 'tam-long-nhan-ai',
    'suc-khoe': 'suc-khoe',
    'van-hoa': 'van-hoa',
    'giai-tri': 'giai-tri',
    'o-to-xe-may': 'o-to-xe-may',
    'suc-manh-so': 'suc-manh-so',
    'giao-duc-huong-nghiep': 'giao-duc-huong-nghiep',
    'an-sinh': 'an-sinh',
    'phap-luat': 'phap-luat',
    'du-lich': 'du-lich',
    'doi-song': 'doi-song',
    'tinh-yeu-gioi-tinh': 'tinh-yeu-gioi-tinh'
}

CATEGORIES_COUNTER = {
    'xa-hoi': 0,
    'the-gioi': 0,
    'kinh-doanh': 0,
    'bat-dong-san': 0,
    'the-thao': 0,
    'lao-dong-viec-lam': 0,
    'tam-long-nhan-ai': 0,
    'suc-khoe': 0,
    'van-hoa': 0,
    'giai-tri': 0,
    'o-to-xe-may': 0,
    'suc-manh-so': 0,
    'giao-duc-huong-nghiep': 0,
    'an-sinh': 0,
    'phap-luat': 0,
    'du-lich': 0,
    'doi-song': 0,
    'tinh-yeu-gioi-tinh': 0
}


class DantriSpider(scrapy.Spider):
    name = 'dantri'
    allowed_domains = ['dantri.com.vn']
    folder_path = './raw_data/raw_dantri'
    start_urls = []

    def __init__(self, category, *args, **kwargs):
        super(DantriSpider, self).__init__(*args, **kwargs)
        
        # make folder
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
            
        if category in CATEGORIES: # highly recommend 
            category_path = os.path.join(self.folder_path, CATEGORIES[category])
            if not os.path.exists(category_path):
                os.makedirs(category_path)
            self.start_urls = [URL + category + '.htm']

        elif category == 'get_all': # a lot of requests are coming to the server so this value of argument is not highly recommended
            for CATEGORIE in CATEGORIES:
                category_path = os.path.join(self.folder_path, CATEGORIES[CATEGORIE])
                if not os.path.exists(category_path):
                    os.makedirs(category_path)
                self.start_urls.append(URL + CATEGORIE + '.htm')  

        else:
            raise ValueError(f'{category} is not a valid value for category')

    def start_requests(self):
        for url in self.start_urls:
            time.sleep(0.5) # add time sleep to avoid 429 response code (too many requests)
            yield scrapy.Request(url=url, callback=self.parse)   

    def parse(self, response):
        articles = response.xpath("//div[@class='main']//article")
        for article in articles:
            time.sleep(0.5) 
            url = "https://dantri.com.vn" + article.xpath(".//div/a/@href").get()
            yield scrapy.Request(url=url, callback=self.parse_news)
        try:
            next_page = response.xpath("//a[@class='page-item next']/@href").get()
            time.sleep(0.2)
            yield scrapy.Request(url="https://dantri.com.vn" + next_page, callback=self.parse)
        except:
            pass
        
    def parse_news(self, response):
        json_data = self.extract_news(response)
        yield json_data

        category = response.url.split('/')[-2]
        CATEGORIES_COUNTER[category] = CATEGORIES_COUNTER[category] + 1
        filename = '%s/%s-%s.json' % (CATEGORIES[category], CATEGORIES[category], CATEGORIES_COUNTER[category])
        with open(self.folder_path + "/" + filename, 'w', encoding='utf-8') as fp:
            json.dump(json_data, fp, ensure_ascii=False)
            self.log('Saved file %s' % filename)

    def extract_news(self, response):
        url = response.url
        json_data = {
            'url': url,
            'title': response.xpath("//h1[@class='title-page detail']/text()").get(),
            'abstract': response.xpath("//h2[@class='singular-sapo']/text()").get(),
            'content_html': response.xpath("//div[@class='singular-content']").get()
        }

        return json_data
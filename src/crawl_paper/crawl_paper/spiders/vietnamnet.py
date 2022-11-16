import json
import os
import time
import scrapy

URL = 'https://vietnamnet.vn/'

CATEGORIES = {
    'thoi-su': 'thoi-su',
    'kinh-doanh': 'kinh-doanh',
    'the-gioi': 'the-gioi',
    'giai-tri': 'giai-tri',
    'the-thao': 'the-thao',
    'suc-khoe': 'suc-khoe',
    'doi-song': 'doi-song',
    'giao-duc': 'giao-duc',
    'phap-luat': 'phap-luat',
    'oto-xe-may': 'oto-xe-may',
    'bat-dong-san': 'bat-dong-san',
    'tuan-viet-nam': 'tuan-viet-nam',
    'du-lich': 'du-lich',
    'ban-doc': 'ban-doc'
}

CATEGORIES_COUNTER = {
    'thoi-su': 0,
    'kinh-doanh': 0,
    'the-gioi': 0,
    'giai-tri': 0,
    'the-thao': 0,
    'suc-khoe': 0,
    'doi-song': 0,
    'giao-duc': 0,
    'phap-luat': 0,
    'oto-xe-may': 0,
    'bat-dong-san': 0,
    'tuan-viet-nam': 0,
    'du-lich': 0,
    'ban-doc': 0
}

class VietnamnetSpider(scrapy.Spider):
    name = 'vietnamnet'
    allowed_domains = ['vietnamnet.vn']
    folder_path = 'raw_vietnamnet'
    start_urls = []

    def __init__(self, category, *args, **kwargs):
        super(VietnamnetSpider, self).__init__(*args, **kwargs)
        
        # make folder
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
            
        if category in CATEGORIES: # highly recommend 
            category_path = os.path.join(self.folder_path, CATEGORIES[category])
            if not os.path.exists(category_path):
                os.makedirs(category_path)
            self.start_urls = [URL + category]
        elif category == 'get_all': # a lot of requests are coming to the server so this value of argument is not highly recommended
            for CATEGORIE in CATEGORIES:
                category_path = os.path.join(self.folder_path, CATEGORIES[CATEGORIE])
                if not os.path.exists(category_path):
                    os.makedirs(category_path)
                self.start_urls.append(URL + CATEGORIE)  
        else:
            raise ValueError(f'{category} is not a valid value for category')

    def start_requests(self):
        for url in self.start_urls:
            time.sleep(0.5) # add time sleep to avoid 429 response code (too many requests)
            yield scrapy.Request(url=url, callback=self.parse, meta={'category': url.split('/')[-1]})   

    def parse(self, response):
        category = response.request.meta['category']      
        articles = response.xpath("//div[@class='feature-box__content']")
        for article in articles:
            time.sleep(0.4) 
            url = "https://vietnamnet.vn" + article.xpath(".//h3/a[1]/@href").get()
            title = article.xpath("normalize-space(.//a[1]/text())").get()
            abstract = article.xpath('normalize-space(.//div[2]/text())').get()
            yield scrapy.Request(url=url, callback=self.parse_news, meta={'title': title, 'abstract': abstract, 'category': category})
    
    def parse_news(self, response):
        category = response.request.meta['category']    
        abstract = response.request.meta['abstract']
        title = response.request.meta['title']
        json_data = self.extract_news(response, abstract, title)
        yield json_data

        CATEGORIES_COUNTER[category] = CATEGORIES_COUNTER[category] + 1
        filename = '%s/%s-%s.json' % (CATEGORIES[category], CATEGORIES[category], CATEGORIES_COUNTER[category])
        with open(self.folder_path + "/" + filename, 'w', encoding='utf-8') as fp:
            json.dump(json_data, fp, ensure_ascii=False)
            self.log('Saved file %s' % filename)

    def extract_news(self, response, abstract, title):
        url = response.url
        json_data = {
            'url': url,
            'title': title,
            'abstract': abstract,
            'content_html': response.xpath("//div[@class='maincontent ']/div").get()
        }

        return json_data
    
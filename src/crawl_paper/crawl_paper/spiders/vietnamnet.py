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
    'thoi-su': [0, 0],
    'kinh-doanh': [0, 0],
    'the-gioi': [0, 0],
    'giai-tri': [0, 0],
    'the-thao': [0, 0],
    'suc-khoe': [0, 0],
    'doi-song': [0, 0],
    'giao-duc': [0, 0],
    'phap-luat': [0, 0],
    'oto-xe-may': [0, 0],
    'bat-dong-san': [0, 0],
    'tuan-viet-nam': [0, 0],
    'du-lich': [0, 0],
    'ban-doc': [0, 0]
}

class VietnamnetSpider(scrapy.Spider):
    name = 'vietnamnet'
    allowed_domains = ['vietnamnet.vn']
    folder_path = './raw_data/raw_vietnamnet'
    page_limit = None
    crr_page = 0
    start_urls = []

    def __init__(self, category, limit=None, *args, **kwargs):
        super(VietnamnetSpider, self).__init__(*args, **kwargs)
        if limit != None:
            self.page_limit = int(limit)

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
            time.sleep(0.4) # add time sleep to avoid 429 response code (too many requests)
            yield scrapy.Request(url=url, callback=self.parse, meta={'category': url.split('/')[-1]})   

    def parse(self, response):
        category = response.request.meta['category']      
        articles = response.xpath("//div[@class='feature-box__content']")
        for article in articles:
            time.sleep(0.1) 
            url = "https://vietnamnet.vn" + article.xpath(".//h3/a[1]/@href").get()
            title = article.xpath("normalize-space(.//h3/a[1]/text())").get()
            abstract = article.xpath('normalize-space(.//div[2]/text())').get()
            yield scrapy.Request(url=url, callback=self.parse_news, meta={'title': title, 'abstract': abstract, 'category': category})
       
        if CATEGORIES_COUNTER[category][1] == 0:
            vertical_articles = response.xpath("//div[@class='verticalHighlight-box']")
            for vertical_article in vertical_articles:
                time.sleep(0.1)
                url = "https://vietnamnet.vn" + vertical_article.xpath(".//div[1]/a/@href").get()
                title = vertical_article.xpath("normalize-space(.//div[3]//a/text())").get()
                yield scrapy.Request(url=url, callback=self.parse_vertical_news, meta={'title': title, 'category': category})

        # crawl until limit-page
        if CATEGORIES_COUNTER[category][1] >= self.page_limit and self.page_limit is not None:
            return
        
        try:
            next_page = response.xpath("//div[@class='panination__content']/a[last()]/@href").get()
            time.sleep(0.1)
            if next_page is not None:
                CATEGORIES_COUNTER[category][1] = CATEGORIES_COUNTER[category][1] + 1
                if 'https://vietnamnet.vn' in next_page:
                    yield scrapy.Request(url=next_page, callback=self.parse, meta={'category': category})
                else:
                    yield scrapy.Request(url="https://vietnamnet.vn" + next_page, callback=self.parse, meta={'category': category})     
        except:
            pass

        # category = response.request.meta['category']      
        # articles = response.xpath("//div[@class='feature-box__content']")
        # for article in articles:
        #     time.sleep(0.1) 
        #     url = "https://vietnamnet.vn" + article.xpath(".//h3/a[1]/@href").get()
        #     title = article.xpath("normalize-space(.//h3/a[1]/text())").get()
        #     abstract = article.xpath('normalize-space(.//div[2]/text())').get()
        #     yield response.follow(url=url, callback=self.parse_news, meta={'title': title, 'category': category, 'abstract': abstract})
       
        # try:
        #     next_page = response.xpath("//div[@class='panination__content']/a[last()]/@href").get()
        #     time.sleep(0.1)
        #     if next_page is not None:
        # #       CATEGORIES_COUNTER[category][1] = CATEGORIES_COUNTER[category][1] + 1
        #         if 'https://vietnamnet.vn' in next_page:
        #             yield scrapy.Request(url=next_page, callback=self.parse, meta={'category': category})
        #         else:
        #             yield scrapy.Request(url="https://vietnamnet.vn" + next_page, callback=self.parse, meta={'category': category}, dont_filter=True)     
        # except:
        #     pass


    def parse_news(self, response):
        category = response.request.meta['category']    
        abstract = response.request.meta['abstract']
        title = response.request.meta['title']
        json_data = self.extract_news(response, title, abstract)
        yield json_data

        CATEGORIES_COUNTER[category][0] = CATEGORIES_COUNTER[category][0] + 1
        filename = '%s/%s-%s.json' % (CATEGORIES[category], CATEGORIES[category], CATEGORIES_COUNTER[category][0])
        with open(self.folder_path + "/" + filename, 'w', encoding='utf-8') as fp:
            json.dump(json_data, fp, ensure_ascii=False)
            self.log('Saved file %s' % filename)

    def parse_vertical_news(self, response):
        category = response.request.meta['category']    
        title = response.request.meta['title']
        json_data = self.extract_news(response, title)
        yield json_data

        CATEGORIES_COUNTER[category][0] = CATEGORIES_COUNTER[category][0] + 1
        filename = '%s/%s-%s.json' % (CATEGORIES[category], CATEGORIES[category], CATEGORIES_COUNTER[category][0])
        with open(self.folder_path + "/" + filename, 'w', encoding='utf-8') as fp:
            json.dump(json_data, fp, ensure_ascii=False)
            self.log('Saved file %s' % filename)

    def extract_news(self, response, title, abstract=None):
        url = response.url
        content_html = response.xpath("//div[@class='maincontent ']/div").get()
        if abstract is not None:
            json_data = {
                'url': url,
                'title': title,
                'abstract': abstract,
                'content_html': content_html
            }
            return json_data
        else:
            url = response.url
            content_html = response.xpath("//div[@class='maincontent ']/div").get()
            abstract = response.xpath("//div[@class='newFeature__main-textBold']/text()").get()
            json_data = {
                'url': url,
                'title': title,
                'abstract': abstract,
                'content_html': content_html
            }
            return json_data

        
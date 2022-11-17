# Text-Summarization-for-Vietnamese-Newpapers

## 1. Data Collection

Using **[Scrapy](https://scrapy.org/)** for crawling data from [dantri](https://dantri.com.vn/), [vietnamnet](https://vietnamnet.vn/)...

Using git bash or linux terminal for running `bash pipe_crawl_vnn.bash` and `bash pipe_crawl_dantri.bash` (in a folder `src/crawl_paper`). After running these commands we have a new folder `src/crawl_paper/raw_data` containing the raw dataset

Articles in [dantri](https://dantri.com.vn/) include 18 categories

Articles in [vietnamnet](https://vietnamnet.vn/) include 14 categoriesS

Each article is saved as json file and includes 4 features (url, title, abstract and html_content)

**Note that all collected data has not been preprocessed**

## 2. Preprocessing
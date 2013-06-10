import urllib.request
from bs4 import BeautifulSoup

import wc_naver.category
from wc_naver.naver_crawler import NaverSingleWebtoonCrawler

import wc_daum.category
from wc_daum.daum_crawler import DaumSingleWebtoonCrawler

# put (category, titleId) tuple of Naver webtoons
naver_title_infos = {
    #(wc_naver.category.BEST_CHALLENGE, '477644'), #천지해
    #(wc_naver.category.BEST_CHALLENGE, '247478'), #Nihil Dant
    #(wc_naver.category.WEBTOON, '471286')         #키드갱 시즌 2
}

daum_title_infos = {
    #(wc_daum.category.WEBTOON, 'jebijeon')
    (wc_daum.category.LEAGUE, '3670')
}
    

for info in naver_title_infos:
    crawler = NaverSingleWebtoonCrawler()
    crawler.crawl(info)

for info in daum_title_infos:
    crawler = DaumSingleWebtoonCrawler()
    crawler.crawl(info)
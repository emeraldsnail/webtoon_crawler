﻿import wc_naver.category as naver
from wc_naver.naver_single_webtoon_crawler import NaverSingleWebtoonCrawler

import wc_daum.category as daum
from wc_daum.daum_crawler import DaumSingleWebtoonCrawler

from wc_nate.nate_crawler import NateWebtoonCrawler

import wc_util

# put (category, titleId) tuple of Naver webtoons
# titleId can be obtained from the URL of the webtoon list page
# ex) URL is 'http://comic.naver.com/webtoon/list.nhn?titleId=123456'
#    => titleId is '123456'
naver_title_infos = [
    #(naver.CHALLENGE, ''),
    #(naver.CHALLENGE, ''),
    #(naver.BEST_CHALLENGE, ''),
    #(naver.BEST_CHALLENGE, ''),
    #(naver.WEBTOON, ''),
    #(naver.WEBTOON, ''),
    #(naver.WEBTOON, ''),
]

# put (category, titleId) tuple of Daum webtoons
# titleId can be obtained from the URL of the webtoon list page.
# ex) URL is 'http://cartoon.media.daum.net/webtoon/view/thisiswebtoon'
#    => titleId is 'thisiswebtoon'
# ex) URL is 'http://cartoon.media.daum.net/league/view/1234'
#    => titleId is '1234'
daum_title_infos = [
    #(daum.LEAGUE, ''),
    #(daum.LEAGUE, ''),
    #(daum.LEAGUE, ''),
    #(daum.WEBTOON, ''),
    #(daum.WEBTOON, ''),
    #(daum.WEBTOON, ''),
    #(daum.WEBTOON, ''),
    #(daum.WEBTOON, ''),
]

# put btno of Nate webtoons
# bsno can be obtained from the URL of the webtoon list page.
# ex) URL is 'http://comics.nate.com/webtoon/detail.php?btno=12345'
#     => titleId is '12345'
nate_title_infos = [
    #'12345',
    #'55200',
]

if __name__ == '__main__':
    crawl_type = wc_util.get_crawl_type()
    """
    for info in naver_title_infos:
        crawler = NaverSingleWebtoonCrawler(info)
        crawler.crawl()

    for info in daum_title_infos:
        crawler = DaumSingleWebtoonCrawler(info)
        crawler.crawl()
    """     
    for info in nate_title_infos:
        crawler = NateWebtoonCrawler(info, crawl_type)
        crawler.crawl()

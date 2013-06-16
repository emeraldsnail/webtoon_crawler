import wc_naver.category as naver
from wc_naver.naver_single_webtoon_crawler import NaverSingleWebtoonCrawler

import wc_daum.category as daum
from wc_daum.daum_crawler import DaumSingleWebtoonCrawler

# put (category, titleId) tuple of Naver webtoons
# titleId can be obtained from the URL of the webtoon list page
# ex) URL is 'http://comic.naver.com/webtoon/list.nhn?titleId=123456' => titleId is '123456'
naver_title_infos = [
    #(naver.CHALLENGE, ''),
    #(naver.CHALLENGE, ''),
    #(naver.BEST_CHALLENGE, ''),
    (naver.BEST_CHALLENGE, '392615'),
    #(naver.WEBTOON, ''),
    #(naver.WEBTOON, ''),
    #(naver.WEBTOON, '497180'),
]

# put (category, titleId) tuple of Daum webtoons
# titleId can be obtained from the URL of the webtoon list page.
# ex) URL is 'http://cartoon.media.daum.net/webtoon/view/thisiswebtoon' => titleId is 'thisiswebtoon'
# ex) URL is 'http://cartoon.media.daum.net/league/view/1234' => titleId is '1234'
daum_title_infos = [
    #(daum.LEAGUE, ''),
    #(daum.LEAGUE, ''),
    #(daum.LEAGUE, ''),
    #(daum.WEBTOON, ''),
    #(daum.WEBTOON, 'acoustic'),
    #(daum.WEBTOON, ''),
    #(daum.WEBTOON, ''),
    #(daum.WEBTOON, ''),
]

if __name__ == '__main__':
    for info in naver_title_infos:
        crawler = NaverSingleWebtoonCrawler(info)
        crawler.crawl()

    for info in daum_title_infos:
        crawler = DaumSingleWebtoonCrawler(info)
        crawler.crawl()
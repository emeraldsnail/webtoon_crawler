import wc_util

from wc_daum import category as daum_category
from wc_daum import daum_crawler
from wc_naver import category as naver_category
from wc_naver import naver_crawler
from wc_nate import nate_crawler


# put (category, titleId) tuple of Naver webtoons
# titleId can be obtained from the URL of the webtoon list page
# ex) URL is 'http://comic.naver.com/webtoon/list.nhn?titleId=123456'
#    => titleId is '123456'
naver_title_infos = [
    (naver_category.CHALLENGE, '582948'),
    #(naver_category.CHALLENGE, ''),
    (naver_category.BEST_CHALLENGE, '555616'),
    #(naver_category.BEST_CHALLENGE, ''),
    (naver_category.WEBTOON, '568986'),
    #(naver_category.WEBTOON, ''),
]

# put (category, titleId) tuple of Daum webtoons
# titleId can be obtained from the URL of the webtoon list page.
# ex) URL is 'http://cartoon.media.daum.net/webtoon/view/thisiswebtoon'
#    => titleId is 'thisiswebtoon'
# ex) URL is 'http://cartoon.media.daum.net/league/view/1234'
#    => titleId is '1234'
daum_title_infos = [
    #(daum_category.LEAGUE, ''),
    #(daum_category.LEAGUE, ''),
    #(daum_category.WEBTOON, ''),
    #(daum_category.WEBTOON, ''),
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
    
    for info in naver_title_infos:
        crawler = naver_crawler.NaverSingleWebtoonCrawler(info, crawl_type)
        crawler.crawl()
    """
    for info in daum_title_infos:
        crawler = daum_crawler.DaumSingleWebtoonCrawler(info)
        crawler.crawl()
    """
    for info in nate_title_infos:
        crawler = nate_crawler.NateWebtoonCrawler(info, crawl_type)
        crawler.crawl()

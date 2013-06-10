from bs4 import BeautifulSoup

import urllib.request
import urllib.parse
import wc_util
import os.path
import wc_daum.category
import httplib2
from json import JSONDecoder


base_url = 'http://cartoon.media.daum.net'
# Daum supports RSS feed, in which all episodes are shown
list_url = base_url + '/{category}/rss/{title_id}'

webtoon_json_url = base_url + '/webtoon/viewer_images.js?webtoon_episode_id={episode_id}'
league_json_url = base_url + '/data/leaguetoon/viewer_images/{episode_id}'

json_decoder = JSONDecoder()

# Daum requires cookie to access json of webtoon image urls
# Not sure if this cookie value is identical for all users
# 'MTAuMTA%3D' is urlencoded & base64-encoded '10.10' without quotes
# TODO: automatically fetch cookie value from viewer url once, rather than using hardcoded value
cookiestring = 'WEBTOON_VIEW=MTAuMTA%3D'

save_path = 'daum/{category}/{title_id}/{episode_id}/'
filename_pattern = '{original_filename}.jpg'

class DaumSingleWebtoonCrawler:

    #webtoon_info is a tuple of (category, title_id)
    def __init__(self, webtoon_info):
        self.category = webtoon_info[0]
        self.title_id = webtoon_info[1]
        self.headers = {'Cookie': cookiestring}
        
        if self.category == wc_daum.category.WEBTOON:
            self.json_url = webtoon_json_url
            self.json_result_key = 'images'
        else:
            self.json_url = league_json_url
            self.json_result_key = 'data'

    def extract_episode_id(self, url):
        path = os.path.split(urllib.parse.urlparse(url)[2])[-1]
        return path
        
    def extract_filename(self, url):
        return os.path.split(urllib.parse.urlparse(url)[2])[-1]

    def build_list_url(self):
        # assume that the category is correct
        return list_url.format(category = self.category, title_id = self.title_id)
        
    def get_json_data(self, json_url):
        # for some reason, going through a common method does not work with httplib2
        # Also, in httplib2 the types of key/value in headers are not consistent: sometimes bytes, sometimes str.
        # think it's a bug in httplib2...?
        http = httplib2.Http()
        response, content = http.request(json_url, 'GET', headers = self.headers)
        return json_decoder.decode(content.decode('utf8'))
        
    def crawl_episode(self, episode_info):
        print('crawling single episode', episode_info[1])
        
        episode_id = self.extract_episode_id(episode_info[0])
        json_url = self.json_url.format(episode_id = episode_id)
        json_data = self.get_json_data(json_url)
        
        urls = []
        for image in json_data[self.json_result_key]:
            urls.append(image['url'])
        
        for url in urls:
            print(url)
            directory = save_path.format(category = self.category, title_id = self.title_id,
                episode_id = episode_id)
            filename = filename_pattern.format(original_filename = self.extract_filename(url))
            print(directory, filename)
            wc_util.save_to_binary_file(url, directory, filename)
        
    def crawl(self):
        rss_url = self.build_list_url()
        content = wc_util.get_text_from_url(rss_url)
        content_soup = BeautifulSoup(content)
        channel = content_soup.find('rss').find('channel')
        items = channel.find_all('item')
        
        for item in items:
            episode_url = item.find('link').string
            episode_title = item.find('title').string
            self.crawl_episode((episode_url, episode_title))
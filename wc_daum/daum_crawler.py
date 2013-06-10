from bs4 import BeautifulSoup

import urllib.request
import urllib.parse
import wc_util
import os.path
import wc_daum.category
import httplib2
from json import JSONDecoder

base_url = 'http://cartoon.media.daum.net'
list_url = base_url + '/{category}/rss/{title_id}'
viewer_url = base_url + '/{category}/viewer/{episode_id}'

webtoon_image_json = '/webtoon/viewer_images.js?webtoon_episode_id={episode_id}'
league_image_json = '/data/leaguetoon/viewer_images/{episode_id}'

class DaumSingleWebtoonCrawler:

    def extract_episode_id(self, url):
        path = os.path.split(urllib.parse.urlparse(url)[2])[-1]
        return path

    def build_list_url(self, title_info):
        # assume that the category is correct
        self.category  = title_info[0]
        return list_url.format(category = title_info[0], title_id = title_info[1])
        
        
    def crawl_episode(self, episode_info):
        print('crawling single episode', episode_info[1])
        
        if self.category == wc_daum.category.WEBTOON:
            image_json = webtoon_image_json
        else:
            image_json = league_image_json

        image_json = image_json.format(episode_id = self.extract_episode_id(episode_info[0]))
        
        viewer = viewer_url.format(category = self.category, episode_id = self.extract_episode_id(episode_info[0]))
        json_url = urllib.parse.urljoin(base_url, image_json)
        
        # To use cookie
        http = httplib2.Http()
        response, content = http.request(viewer, 'GET')
        cookie = {'Cookie': response['set-cookie']}
        response, content = http.request(json_url, 'GET', headers = cookie)
        
        json_content = content.decode('utf8') 
        decoder = JSONDecoder()
        decoded = decoder.decode(json_content)
        images = decoded['images']
        for image in images:
            print(image['url'])
        
        
    def crawl(self, title_info):
        url = self.build_list_url(title_info)
        print ('page url', url)
        
        content = wc_util.get_text_from_url(url)
        content_soup = BeautifulSoup(content)
        channel = content_soup.find('rss').find('channel')
        items = channel.find_all('item')
        
        for item in items:
            episode_url = item.find('link').string
            episode_title = item.find('title').string
            self.crawl_episode((episode_url, episode_title))
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

save_path = 'daum/{category}/{title_name}/{episode_id} {episode_name}/'
filename_pattern = '{original_filename}.jpg'
thumbnail_filename = '{original_filename}.jpg'

class DaumSingleWebtoonCrawler:

    #title_info is a tuple of (category, title_id)
    def __init__(self, title_info):
        self.category = title_info[0]
        self.title_id = title_info[1]
        
    def build_episode_info(self, item):
        episode_url = item.find('link').string.strip()
        episode_id = wc_util.extract_last(episode_url)
        episode_name = item.find('title').string.strip()
        # format of yyyy-MM-dd HH:mm:ss
        episode_date = item.find('pubdate').string.strip().split(' ')[0]
        thumbnail_url = BeautifulSoup(item.find('description').string).find('img')['src']
        
        return {
            'episode_id' : episode_id,
            'episode_name' : episode_name,
            'episode_url' : episode_url,
            'episode_date' : episode_date,
            'thumbnail_url' : thumbnail_url,
        }
        
    def crawl_episode(self, title_info, episode_info):
        crawler = DaumSingleEpisodeCrawler(title_info, episode_info)
        crawler.crawl()      
        
    def crawl(self):
        rss_url = list_url.format(category = self.category, title_id = self.title_id)
        content = wc_util.get_text_from_url(rss_url)
        content_soup = BeautifulSoup(content)
        channel = content_soup.find('rss').find('channel')
        title_name = channel.find('title').string.strip()
        items = channel.find_all('item')
        
        title_info = {
            'category' : self.category,
            'title_id' : self.title_id,
            'title_name' : title_name,
        }

        for item in items:
            episode_info = self.build_episode_info(item)
            self.crawl_episode(title_info, episode_info)


class DaumSingleEpisodeCrawler:

    def __init__(self, title_info, episode_info):
        self.headers = dict(title_info)
        self.headers.update(episode_info)
        self.http_headers = {'Cookie': cookiestring}
        
        
        if title_info['category'] == wc_daum.category.WEBTOON:
            self.json_url = webtoon_json_url
            self.json_result_key = 'images'
        else:
            self.json_url = league_json_url
            self.json_result_key = 'data'

        title_name = self.headers['title_name']
        self.headers['title_name'] = wc_util.remove_invalid_filename_chars(title_name)
        
        episode_name = self.headers['episode_name']
        self.headers['episode_name'] = wc_util.remove_invalid_filename_chars(episode_name)
    
    
    def get_json_data(self, json_url):
        # for some reason, going through a common method does not work with httplib2
        # Also, in httplib2 the types of key/value in http_headers are not consistent: sometimes bytes, sometimes str.
        # think it's a bug in httplib2...?
        http = httplib2.Http()
        response, content = http.request(json_url, 'GET', headers = self.http_headers)
        return json_decoder.decode(content.decode('utf8'))    
        
        
    def crawl(self):
        print('crawling single episode', self.headers['episode_name'])
        
        episode_id = wc_util.extract_last(self.headers['episode_url'])
        json_url = self.json_url.format(**self.headers)
        json_data = self.get_json_data(json_url)
        
        urls = []
        for image in json_data[self.json_result_key]:
            urls.append(image['url'])
        
        directory = save_path.format(**self.headers)
        
        for url in urls:
            print(url)
            
            headers = self.headers.copy()
            headers['original_filename'] = wc_util.extract_last(url)
            
            filename = filename_pattern.format(**headers)
            wc_util.save_to_binary_file(url, directory, filename)
            
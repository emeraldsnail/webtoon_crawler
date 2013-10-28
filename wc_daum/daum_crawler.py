import bs4
import httplib2
import json
import wc_util

from os import path
from urllib import request
from urllib import parse

from wc_base import base_crawler
from wc_daum import category
from wc_util import logger


BASE_URL = 'http://cartoon.media.daum.net'
# Daum supports RSS feed, in which all episodes are shown
LIST_URL = BASE_URL + '/{category}/rss/{title_id}'

WEBTOON_JSON_URL = BASE_URL + '/webtoon/viewer_images.js?webtoon_episode_id={episode_id}'
LEAGUE_JSON_URL = BASE_URL + '/data/leaguetoon/viewer_images/{episode_id}'

JSON_DECODER = json.JSONDecoder()

# Daum requires cookie to access json of webtoon image urls
# Not sure if this cookie value is identical for all users
# 'MTAuMTA%3D' is urlencoded & base64-encoded '10.10' without quotes
# TODO: automatically fetch cookie value from viewer url once, rather than using hardcoded value
COOKIESTRING = 'WEBTOON_VIEW=MTAuMTA%3D'

SAVE_PATH = 'daum/{category}/{title_id} {title_name}/{episode_id} {episode_name}/'
IMAGE_FILENAME_PATTERN = '{prefix}_{original_filename}.jpg'
THUMBNAIL_FILENAME_PATTERN = '{prefix}_{original_filename}.jpg'

class DaumWebtoonCrawler(base_crawler.BaseWebtoonCrawler):
    #title_info is a tuple of (category, title_id)
    def __init__(self, title_info, crawl_type):
        super().__init__(title_info, crawl_type)

    def get_episode_crawler(self, title_info, episode_info):
        return DaumEpisodeCrawler(title_info, episode_info, self.crawl_type)
        
    def get_title_and_episode_info(self):
        rss_url = LIST_URL.format(category = self.title_info[0],
                title_id = self.title_info[1])
        content = wc_util.get_text_from_url(rss_url)
        content_soup = bs4.BeautifulSoup(content)
        channel = content_soup.find('rss').find('channel')
        title_name = channel.find('title').string.strip()
        items = channel.find_all('item')
        
        title_info = {
            'category' : self.title_info[0],
            'title_id' : self.title_info[1],
            'title_name' : title_name,
        }

        episode_infos = []
        for item in items:
            episode_infos.append(self.build_episode_info(item))
        
        # In RSS, the episodes are sorted in reverse chronological order.
        return title_info, reversed(episode_infos)
        
    def build_episode_info(self, item):
        episode_url = item.find('link').string.strip()
        episode_id = wc_util.extract_last(episode_url)
        episode_name = item.find('title').string.strip()
        # format of yyyy-MM-dd HH:mm:ss
        episode_date = item.find('pubdate').string.strip().split(' ')[0]
        
        content_soup = bs4.BeautifulSoup(item.find('description').string)
        thumbnail_url = content_soup.find('img')['src']
        
        return {
            'episode_id' : episode_id,
            'episode_name' : episode_name,
            'episode_url' : episode_url,
            'episode_date' : episode_date,
            'thumbnail_url' : thumbnail_url,
        }   

class DaumEpisodeCrawler(base_crawler.BaseEpisodeCrawler):

    # title_info is (category, title_id, title_name)
    # episode_info is (episode_id, episode_name, episode_url, episode_date,
    #        thumbnail_url)
    def __init__(self, title_info, episode_info, crawl_type):
        headers = dict(title_info)
        headers.update(episode_info)
        self.http_headers = {'Cookie': COOKIESTRING}
        
        if title_info['category'] == category.WEBTOON:
            self.json_url = WEBTOON_JSON_URL
            self.json_result_key = 'images'
        else:
            self.json_url = LEAGUE_JSON_URL
            self.json_result_key = 'data'

        title_name = headers['title_name']
        headers['title_name'] = wc_util.remove_invalid_filename_chars(
                title_name)
        
        episode_name = headers['episode_name']
        headers['episode_name'] = wc_util.remove_invalid_filename_chars(
                episode_name)
                
        directory = SAVE_PATH.format(**headers)
        super().__init__(directory, headers, crawl_type)
      
    def get_json_data(self, json_url):
        # For some reason, going through a common method does not work with
        # httplib2l Also, in httplib2 the types of key/value in http_headers are
        # not consistent: sometimes bytes, sometimes str. think it's a bug in
        # httplib2...?
        http = httplib2.Http()
        response, content = http.request(json_url, 'GET',
                headers = self.http_headers)
        return JSON_DECODER.decode(content.decode('utf8'))    
                
    def populate_episode_info(self):
        json_url = self.json_url.format(**self.headers)
        json_data = self.get_json_data(json_url)
        
        image_urls = []
        for image in json_data[self.json_result_key]:
            image_urls.append(image['url'])
        
        info_writer = logger.InfoWriter(self.directory)
        info_writer.write_webtoon_title(self.headers['title_name'])
        info_writer.write_episode_title(self.headers['episode_name'])
        info_writer.write_episode_thumbnail_url(self.headers['thumbnail_url'])
        for image_url in image_urls:
            info_writer.write_episode_image_url(image_url)
        info_writer.write_complete()
        info_writer.close()

    def thumbnail_filename_from_url(self, prefix, url):
        headers = wc_util.copy_headers_with_filename_and_prefix(self.headers,
                prefix, url)
        return THUMBNAIL_FILENAME_PATTERN.format(**headers)
        
    def image_filename_from_url(self, prefix, url):
        headers = wc_util.copy_headers_with_filename_and_prefix(self.headers,
                prefix, url)
        return IMAGE_FILENAME_PATTERN.format(**headers) 
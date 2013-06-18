from bs4 import BeautifulSoup
from wc_naver import thumbnail_filename
from wc_naver import filename_pattern
from wc_naver import save_path
import wc_util
import os.path
import urllib.parse

class NaverSingleEpisodeCrawler:
    
    # title_info is (category, title_id, title_name)
    # episode_info is (episode_id, episode_name, episode_url, thumbnail_url)
    def __init__(self, title_info, episode_info):        
        self.headers = dict(title_info)
        self.headers.update(episode_info)
        
        title_name = self.headers['title_name']
        self.headers['title_name'] = wc_util.remove_invalid_filename_chars(title_name)
        
        episode_name = self.headers['episode_name']
        self.headers['episode_name'] = wc_util.remove_invalid_filename_chars(episode_name)
    
    def crawl(self):
        print('crawling single episode', self.headers['episode_name'])      
        directory = save_path.format(**self.headers)
        
        # save the thumbnail
        headers = self.headers.copy()
        thumbnail_url = self.headers['thumbnail_url']
        headers['original_filename'] = wc_util.extract_last(thumbnail_url)
        t_filename = thumbnail_filename.format(**headers)
        wc_util.save_to_binary_file(thumbnail_url, directory, t_filename)
        
        # save main images
        content = BeautifulSoup(wc_util.get_text_from_url(self.headers['episode_url']))
        images = content.find('div', class_ = 'wt_viewer').find_all('img')
        for image in images:
            src = image['src']
            print ('image:', src)
            headers = self.headers.copy()
            headers['original_filename'] = wc_util.extract_last(src)
            filename = filename_pattern.format(**headers)
            wc_util.save_to_binary_file(src, directory, filename)
            
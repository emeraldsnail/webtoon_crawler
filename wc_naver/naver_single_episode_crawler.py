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
        self.category = title_info[0]
        self.title_id = title_info[1]
        self.title_name = title_info[2]
        self.episode_id = episode_info[0]
        self.episode_name = episode_info[1]
        self.episode_url = episode_info[2]
        self.thumbnail_url = episode_info[3]
        
        self.headers = dict(
            category = self.category,
            title_id = self.title_id,
            title_name = wc_util.remove_invalid_filename_chars(self.title_name),
            episode_id = self.episode_id,
            episode_name = wc_util.remove_invalid_filename_chars(self.episode_name),
        )
        
    def extract_filename(self, url):
        return os.path.split(urllib.parse.urlparse(url)[2])[-1]
    
    def crawl(self):
        print('crawling single episode', self.episode_name)      
        directory = save_path.format(**self.headers)
        
        # save the thumbnail
        headers = self.headers.copy()
        headers['original_filename'] = self.extract_filename(self.thumbnail_url)
        t_filename = thumbnail_filename.format(**headers)
        wc_util.save_to_binary_file(self.thumbnail_url, directory, t_filename)
        
        # save main images
        content = BeautifulSoup(wc_util.get_text_from_url(self.episode_url))
        images = content.find('div', class_ = 'wt_viewer').find_all('img')
        for image in images:
            src = image['src']
            print ('image:', src)
            headers = self.headers.copy()
            headers['original_filename'] = self.extract_filename(src)
            filename = filename_pattern.format(**headers)
            wc_util.save_to_binary_file(src, directory, filename)
            
import time

from wc_base import base_crawler
import wc_util
from wc_util import logger

from bs4 import BeautifulSoup

base_url = 'http://comics.nate.com'
list_url = base_url + '/webtoon/detail.php?btno={title_id}'
viewer_url = list_url + '&bsno={episode_id}'

save_path = 'nate/{title_id}_{title_name}/{episode_id}_{episode_name}/'
image_filename_pattern = '{prefix}_{timestamp}_{original_filename}'
thumbnail_filename_pattern = '{prefix}_{original_filename}'

class NateWebtoonCrawler:

    # title_id is btno
    def __init__(self, title_id, crawl_type):
        self.title_id = title_id
        self.crawl_type = crawl_type
    
    def get_title_name(self, content_soup):
        webtIntro = content_soup.find('dl', class_ = 'webtIntro')
        title_em = webtIntro.find('dt', class_ = 'f_clear').find('em')
        return title_em.string.strip()
        
    def get_episode_infos(self, content_soup):
        webtView  = content_soup.find('div', class_ = 'webtView')
        episodes = webtView.find('select').find_all('option')
       
        infos = []
        for episode in episodes:
            episode_info = {
                'episode_id': episode['value'],
                'episode_name': episode.string.strip(),
            }
            infos.append(episode_info)
        return infos
        
    def crawl_episode(self, title_info, episode_info):
        crawler = NateEpisodeCrawler(title_info, episode_info,
                self.crawl_type)
        crawler.crawl()
        
    def crawl(self):
        url = list_url.format(title_id = self.title_id)
        content = wc_util.get_text_from_url(url)
        content_soup = BeautifulSoup(content)
        
        title_name = self.get_title_name(content_soup) 
        title_info = {
            'title_id': self.title_id,
            'title_name': title_name,
        }
        
        episode_infos = self.get_episode_infos(content_soup)
        
        for episode_info in episode_infos:
            self.crawl_episode(title_info, episode_info)    
        
        
class NateEpisodeCrawler(base_crawler.BaseEpisodeCrawler):

    # title_info contains {title_id, title_name} as keys
    # episode_info contains {episode_id, episode_name} as keys 
    def __init__(self, title_info, episode_info, crawl_type):
        self.title_info = title_info
        self.episode_info = episode_info
        headers = dict(title_info)
        headers.update(episode_info)
        
        title_name = headers['title_name']
        headers['title_name'] = wc_util.remove_invalid_filename_chars(
                title_name)
        
        episode_name = headers['episode_name']
        headers['episode_name'] = wc_util.remove_invalid_filename_chars(
                episode_name)
                
        self.directory = self.get_save_path(headers)
        super().__init__(self.directory, headers, crawl_type)
        
    def get_image_url(self, content_soup):
        # Nate webtoons have only one image for each episode, '001.jpg'
        webtView = content_soup.find('div', class_ = 'webtView')
        img = webtView.find('img', alt = self.headers['title_name'])
        return img['src']
        
    def get_thumbnail_url(self, content_soup):
        thumbSet = content_soup.find('div', class_ = 'thumbSet')
        selected_dl = thumbSet.find('dl', class_ = 'selected')
        image = selected_dl.find('img')
        return image['src']
    
    def copy_headers_with_filename_and_prefix(self, file_url, prefix):
        headers = self.headers.copy()
        filename = wc_util.extract_last(file_url)
        headers['original_filename'] = filename
        headers['prefix'] = prefix
        return headers
        
    def populate_episode_info(self):
        url = viewer_url.format(**self.headers)
        content = wc_util.get_text_from_url(url)
        content_soup = BeautifulSoup(content)
        
        # get thumbnail url
        t_url = self.get_thumbnail_url(content_soup)
        # get image url
        image_url = self.get_image_url(content_soup)
        
        info_writer = logger.InfoWriter(self.directory)
        info_writer.write_webtoon_title(self.title_info['title_name'])
        info_writer.write_episode_title(self.episode_info['episode_name'])
        info_writer.write_episode_thumbnail_url(t_url)
        info_writer.write_episode_image_url(image_url)
        info_writer.write_complete()
        info_writer.close()
        
    
    def get_save_path(self, headers):
        return save_path.format(**headers)

    def thumbnail_filename_from_url(self, prefix, url):
        headers = self.copy_headers_with_filename_and_prefix(url, prefix)
        return thumbnail_filename_pattern.format(**headers)
        
    def image_filename_from_url(self, prefix, url): 
        headers = self.copy_headers_with_filename_and_prefix(url, prefix)
        # Nate only has one image file per episode, with the same name.
        # Need to use timestamp to distinguish them.
        headers['timestamp'] = str(int(time.time() * 10.0))
        return image_filename_pattern.format(**headers)
import bs4
import time
import wc_nate
import wc_util

from wc_base import base_crawler
from wc_util import logger


class NateWebtoonCrawler(base_crawler.BaseWebtoonCrawler):
    # title_info is (btno)
    def __init__(self, title_info, crawl_type):
        super().__init__(title_info, crawl_type)
        
    def get_episode_crawler(self, title_info, episode_info):
        return NateEpisodeCrawler(title_info, episode_info, self.crawl_type)
        
    def get_title_and_episode_info(self):
        url = wc_nate.LIST_URL.format(title_id = self.title_info)
        content = wc_util.get_text_from_url(url)
        content_soup = bs4.BeautifulSoup(content)
        
        title_name = self.get_title_name(content_soup) 
        title_info = {
            'title_id': self.title_info,
            'title_name': title_name,
        }
        
        episode_infos = self.get_episode_infos(content_soup)
        return title_info, episode_infos
    
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
                
        directory = wc_nate.SAVE_PATH.format(**headers)
        super().__init__(directory, headers, crawl_type)
        
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

    def populate_episode_info(self):
        url = wc_nate.VIEWER_URL.format(**self.headers)
        content = wc_util.get_text_from_url(url)
        content_soup = bs4.BeautifulSoup(content)
        
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

    def thumbnail_filename_from_url(self, prefix, url):
        headers = wc_util.copy_headers_with_filename_and_prefix(self.headers,
                prefix, url)
        return wc_nate.THUMBNAIL_FILENAME_PATTERN.format(**headers)
        
    def image_filename_from_url(self, prefix, url): 
        headers = wc_util.copy_headers_with_filename_and_prefix(self.headers,
                prefix, url)
        # Nate only has one image file per episode, with the same name.
        # Need to use timestamp to distinguish them.
        headers['timestamp'] = str(int(time.time() * 10.0))
        return wc_nate.IMAGE_FILENAME_PATTERN.format(**headers)
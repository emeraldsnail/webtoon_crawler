from bs4 import BeautifulSoup

import urllib.request
import urllib.parse
import wc_util
import os.path

from wc_naver import list_url
from wc_naver import base_url
from wc_naver.naver_single_episode_crawler import NaverSingleEpisodeCrawler

class NaverSingleWebtoonCrawler:

    # title_info is tuple of (category, title_id)
    def __init__(self, title_info):
        self.category = title_info[0]
        self.title_id = title_info[1]
    
    def build_list_url(self, page = 1):
        # assume that the category is correct
        return list_url.format(category = self.category, title_id = self.title_id, page_id = page)
        
    def extract_episode_id(self, url):
        q = urllib.parse.urlparse(url).query
        qsl = urllib.parse.parse_qsl(q)
        dic = dict(qsl)
        if 'no' in dic:
            return dic['no']
        else:
            return dic['seq']
        
    def get_episode_infos(self, content_soup):
        title_results = content_soup.find('table', class_ = 'viewList').find_all('tr')
        infos = []
        
        if title_results != None:
            for result in title_results:
                try:
                    title_cell = result.find('td', class_ = 'title')
                    if title_cell != None:
                        anchor = title_cell.find('a')
                        episode_url = urllib.parse.urljoin(base_url, anchor['href'])
                        episode_id = self.extract_episode_id(episode_url)
                        episode_name = anchor.string.strip()
                        episode_date = result.find('td', class_ = 'num').string.strip()
                        thumbnail_url = result.find('img')['src']
                        
                        infos.append({
                            'episode_id' : episode_id, 
                            'episode_name' : episode_name,
                            'episode_url' : episode_url,
                            'episode_date' : episode_date,
                            'thumbnail_url' : thumbnail_url,
                        })
                except:
                    #pass malformed pages
                    print ('malformed page found')
                    
        return infos
        
    def crawl_episode(self, title_info, episode_info):
        episode_crawler = NaverSingleEpisodeCrawler(title_info, episode_info)
        episode_crawler.crawl()
        
    def is_last_page(self, content_soup):
        try:
            page_navigation = content_soup.find('div', class_ = 'pagenavigation')
            has_next_page_button = page_navigation.find('a', class_ = 'next')
            return has_next_page_button == None
        except:
            #return True if malfo-rmed page. This prevents further process
            return True
            
    def get_title_name(self, content_soup):
        return content_soup.find('div', class_ = 'comicinfo').find('div', class_ = 'detail').find('h2').string.strip()
    
    def crawl(self):
        current_page = 1
        while True:
            url = self.build_list_url(current_page)
            print ('page url', url)
            content = wc_util.get_text_from_url(url)
            
            content_soup = BeautifulSoup(content)
            title_name = self.get_title_name(content_soup)
            title_info = {
                'category' : self.category,
                'title_id' : self.title_id, 
                'title_name' : title_name,
            }
            
            episode_infos = self.get_episode_infos(content_soup) 
            for episode_info in episode_infos:
                self.crawl_episode(title_info, episode_info)
            
            if self.is_last_page(content_soup):
                break
            else:
                current_page = current_page + 1

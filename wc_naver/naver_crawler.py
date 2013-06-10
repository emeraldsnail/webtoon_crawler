from bs4 import BeautifulSoup

import urllib.request
import urllib.parse
import wc_util
import os.path

base_url = 'http://comic.naver.com'
list_url = base_url + '/{category}/list.nhn?titleId={title_id}&page={page_id}'
viewer_url = base_url + '/{category}/detail.nhn?titleId={titleId}&no={episode_id}'

save_path = 'naver/{category}/{title_id}/{episode_id}/'
filename_pattern = '{original_filename}'

class NaverSingleWebtoonCrawler:

    # title_info is tuple of (category, title_id)
    def __init__(self, title_info):
        self.category = title_info[0]
        self.title_id = title_info[1]
    
    def build_list_url(self, page = 1):
        # assume that the category is correct
        return list_url.format(category = self.category, title_id = self.title_id, page_id = page)
        
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
                        episode_title = anchor.string
                        infos.append((episode_url, episode_title))
                except:
                    #pass malformed pages
                    print ('malformed page found')
                    
        return infos
        
    def extract_episode_id(self, url):
        q = urllib.parse.urlparse(url).query
        qsl = urllib.parse.parse_qsl(q)
        dic = dict(qsl)
        if 'no' in dic:
            return dic['no']
        else:
            return dic['seq']
        
    def extract_filename(self, url):
        return os.path.split(urllib.parse.urlparse(url)[2])[-1]
        
    def crawl_episode(self, episode_info):
        print('crawling single episode', episode_info[1])
        content = BeautifulSoup(wc_util.get_text_from_url(episode_info[0]))
        images = content.find('div', class_ = 'wt_viewer').find_all('img')
        for image in images:
            src = image['src']
            print ('image:', src)
            
            directory = save_path.format(category = self.category, title_id = self.title_id,
                episode_id = self.extract_episode_id(episode_info[0]))
            filename = filename_pattern.format(original_filename = self.extract_filename(src))
            print(directory, filename)
            wc_util.save_to_binary_file(src, directory, filename)
        
        
    def is_last_page(self, content_soup):
        try:
            page_navigation = content_soup.find('div', class_ = 'pagenavigation')
            has_next_page_button = page_navigation.find('a', class_ = 'next')
            return has_next_page_button == None
        except:
            #return True if malformed page. This prevents further process
            return True
    
    def crawl(self):
        current_page = 1
        while True:
            url = self.build_list_url(current_page)
            print ('page url', url)
            content = wc_util.get_text_from_url(url)
            content_soup = BeautifulSoup(content)
            episode_infos = self.get_episode_infos(content_soup)
            
            for episode_info in episode_infos:
                self.crawl_episode(episode_info)
            
            if self.is_last_page(content_soup):
                break
            else:
                current_page = current_page + 1
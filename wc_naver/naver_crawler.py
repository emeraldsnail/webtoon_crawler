import bs4
import urllib
import wc_naver
import wc_util

from os import path

from wc_base import base_crawler
from wc_util import logger


class NaverWebtoonCrawler(base_crawler.BaseWebtoonCrawler):
    # title_info is tuple of (category, title_id)
    def __init__(self, title_info, crawl_type):
        super().__init__(title_info, crawl_type)
        
    def get_episode_crawler(self, title_info, episode_info):
        return NaverEpisodeCrawler(title_info, episode_info, self.crawl_type)
        
    def get_title_and_episode_info(self):
        episode_infos = []
        title_info = None
        current_page = 1
        while True:
            url = self.build_list_url(current_page)
            content_text = wc_util.get_text_from_url(url)

            content_soup = bs4.BeautifulSoup(content_text)
            if not title_info:
                title_name = self.get_title_name(content_soup)
                title_info = {
                    'category' : self.title_info[0],
                    'title_id' : self.title_info[1],
                    'title_name' : title_name,
                }
            episode_infos.extend(self.get_episode_infos(content_soup))

            if self.is_last_page(content_soup):
                break
            else:
                current_page = current_page + 1
                
        return title_info, reversed(episode_infos)

    def build_list_url(self, page = 1):
        # assume that the category is correct
        return wc_naver.LIST_URL.format(category = self.title_info[0],
                title_id = self.title_info[1], page_id = page)

    def extract_episode_id(self, url):
        q = urllib.parse.urlparse(url).query
        qsl = urllib.parse.parse_qsl(q)
        dic = dict(qsl)
        if 'no' in dic:
            return dic['no']
        else:
            return dic['seq']

    def get_episode_infos(self, content_soup):
        title_results = content_soup.find('table',
                class_ = 'viewList').find_all('tr')
        infos = []

        if title_results != None:
            for result in title_results:
                try:
                    title_cell = result.find('td', class_ = 'title')
                    if title_cell != None:
                        anchor = title_cell.find('a')
                        episode_url = urllib.parse.urljoin(wc_naver.BASE_URL,
                                anchor['href'])
                        episode_id = self.extract_episode_id(episode_url)
                        episode_name = anchor.string.strip()
                        episode_date = result.find('td',
                                class_ = 'num').string.strip()
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
                    print ('Malformed page. Check if HTML structure changed')

        return infos

    def is_last_page(self, content_soup):
        try:
            page_nav = content_soup.find('div', class_ = 'pagenavigation')
            has_next_page_button = page_nav.find('a', class_ = 'next')
            return has_next_page_button == None
        except:
            #return True if malformed page. This prevents further process
            return True

    def get_title_name(self, content_soup):
        return content_soup.find('div', class_ = 'comicinfo').find('div',
                class_ = 'detail').find('h2').contents[0].strip()

                
class NaverEpisodeCrawler(base_crawler.BaseEpisodeCrawler):
    
    # title_info is (category, title_id, title_name)
    # episode_info is (episode_id, episode_name, episode_url, thumbnail_url)
    def __init__(self, title_info, episode_info, crawl_type):        
        headers = dict(title_info)
        headers.update(episode_info)
        
        headers['title_name'] = wc_util.remove_invalid_filename_chars(
                headers['title_name'])
        
        headers['episode_name'] = wc_util.remove_invalid_filename_chars(
                headers['episode_name'])
        directory = wc_naver.SAVE_PATH.format(**headers)
        super().__init__(directory, headers, crawl_type)
    
    def populate_episode_info(self):
        content_text = wc_util.get_text_from_url(self.headers['episode_url'])
        content = bs4.BeautifulSoup(content_text)
        image_soups = content.find('div', class_ = 'wt_viewer').find_all('img')
        image_urls = []
        for image in image_soups:
            image_urls.append(image['src'])
        
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
        return wc_naver.THUMBNAIL_FILENAME_PATTERN.format(**headers)
        
    def image_filename_from_url(self, prefix, url):
        headers = wc_util.copy_headers_with_filename_and_prefix(self.headers,
                prefix, url)
        return wc_naver.IMAGE_FILENAME_PATTERN.format(**headers)    
        
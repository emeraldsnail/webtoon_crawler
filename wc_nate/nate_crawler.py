from bs4 import BeautifulSoup

import wc_util

base_url = 'http://comics.nate.com'
list_url = base_url + '/webtoon/detail.php?btno={title_id}'
viewer_url = list_url + '&bsno={episode_id}'

save_path = 'nate/{title_name}/{episode_name}/'
filename_pattern = '{original_filename}'
thumbnail_filename = '{original_filename}'

class NateSingleWebtoonCrawler:

    # title_ic is btno
    def __init__(self, title_id):
        self.title_id = title_id
    
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
        crawler = NateSingleEpisodeCrawler(title_info, episode_info)
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
        
        
class NateSingleEpisodeCrawler:

    # title_info contains {title_id, title_name} as keys
    # episode_info contains {episode_id, episode_name} as keys 
    def __init__(self, title_info, episode_info):
        self.headers = dict(title_info)
        self.headers.update(episode_info)
        
        title_name = self.headers['title_name']
        self.headers['title_name'] = wc_util.remove_invalid_filename_chars(title_name)
        
        episode_name = self.headers['episode_name']
        self.headers['episode_name'] = wc_util.remove_invalid_filename_chars(episode_name)
        
    def get_image_url(self, content_soup):
        webtView = content_soup.find('div', class_ = 'webtView')
        img = webtView.find('img', alt = self.headers['title_name'])
        return img['src']
        
    def get_thumbnail_url(self, content_soup):
        thumbSet = content_soup.find('div', class_ = 'thumbSet')
        selected_dl = thumbSet.find('dl', class_ = 'selected')
        image = selected_dl.find('img')
        return image['src']
    
    def copy_headers_with_filename(self, file_url):
        headers = self.headers.copy()
        filename = wc_util.extract_last(file_url)
        headers['original_filename'] = filename
        return headers
    
    def crawl(self):
        print('crawling single episode', self.headers['episode_name'])
        
        url = viewer_url.format(**self.headers)
        content = wc_util.get_text_from_url(url)
        content_soup = BeautifulSoup(content)
        directory = save_path.format(**self.headers)
        
        # save thumbnail
        t_url = self.get_thumbnail_url(content_soup)
        t_headers = self.copy_headers_with_filename(t_url)
        t_filename = thumbnail_filename.format(**t_headers)
        wc_util.save_to_binary_file(t_url, directory, t_filename)
        
        # Nate webtoons have only one image for each episode
        image_url = self.get_image_url(content_soup)
        headers = self.copy_headers_with_filename(image_url)
        filename = filename_pattern.format(**headers)
        wc_util.save_to_binary_file(image_url, directory, filename)
        
        
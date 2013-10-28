import wc_util
from wc_util import logger

THUMBNAIL_PREFIX = 'thumbnail'

class CrawlTypeNotFoundException(Exception):
    pass

# Base class for all title (webtoon) crawlers
class BaseWebtoonCrawler:
    def __init__(self, title_info, crawl_type):
        self.crawl_type = crawl_type
        self.title_info = title_info
    
    def crawl(self):
        title_info , episode_infos = self.get_title_and_episode_info()
        for episode_info in episode_infos:
            episode_crawler = self.get_episode_crawler(title_info, episode_info)
            episode_crawler.crawl()
        
    def get_episode_crawler(self, title_info, episode_info):
        raise NotImplementedError('Subclass should override this method')
        
    def get_title_and_episode_info(self):
        raise NotImplementedError('Subclass should override this method')
    
    
# Base class for all episode crawlers
class BaseEpisodeCrawler:
    
    def __init__(self, directory, headers, crawl_type):
        self.directory = directory
        self.headers = headers
        self.crawl_type = crawl_type
        self.info_reader = None
        self.log_reader = logger.LogReader(self.directory)
        self.info_writer = None
        self.log_writer = None
    
    # Determine thumbnail filename to save from the file url
    def thumbnail_filename_from_url(self, prefix, url):
        raise NotImplementedError('Subclass should override this method')
    
    # Determine image filename to save from the file url
    def image_filename_from_url(self, prefix, url):
        raise NotImplementedError('Subclass should override this method')
     
    # Save an file from url and log the download
    def save_file(self, file_url, filename):
        if wc_util.save_to_binary_file(file_url, self.directory, filename):
            print ('Successfully saved file from', file_url)
            # log if file is successfully downloaded
            if not self.log_writer:
                self.log_writer = logger.LogWriter(self.directory)
            self.log_writer.write_downloaded_file_url(file_url)
        else:
            print ('Failed to save file from ', file_url)
        
    def crawl(self):
        episode_title = self.headers['episode_name']
    
        if self.crawl_type == wc_util.CrawlType.FULL:
            print('Starts full crawling ', episode_title)
            self.full_crawl()
        elif self.crawl_type == wc_util.CrawlType.UPDATE:
            print('Starts update crawling ', episode_title)
            self.update_crawl()
        elif self.crawl_type == wc_util.CrawlType.SHALLOW:
            print('Starts shallow crawling ', episode_title)
            self.shallow_crawl()
        else:
            raise CrawlTypeNotFoundException('Crawl type is incorrect!')
        
        print('Finished crawling ', episode_title)
        
        # cleanup
        if self.info_writer:
            self.info_writer.close()
        if self.log_writer:
            self.log_writer.close()
        
    # Crawl from scratch, overriding any existing files
    def full_crawl(self):
        self.populate_episode_info()
        self.info_reader = logger.InfoReader(self.directory)

        # download thumbnails
        thumbnail_urls = self.info_reader.get_episode_thumbnail_urls()
        for thumbnail_url in thumbnail_urls:
            filename = self.thumbnail_filename_from_url(THUMBNAIL_PREFIX,
                    thumbnail_url)
            self.save_file(thumbnail_url, filename)
        
        # download images
        image_urls = self.info_reader.get_episode_image_urls()
        for index, image_url in enumerate(image_urls):
            prefix = '{0:03d}'.format(index+1)
            filename = self.image_filename_from_url(prefix, image_url)
            self.save_file(image_url, filename)
        
    # Check info file and download missing ones.
    def shallow_crawl(self):
        if not self.info_reader:
            self.info_reader = logger.InfoReader(self.directory)

        if self.info_reader.is_complete():
            # Shallowly crawl thumbnails
            thumbnail_urls = self.info_reader.get_episode_thumbnail_urls()
            for thumbnail_url in thumbnail_urls:
                if not self.log_reader.file_url_exists(thumbnail_url):
                    filename = self.thumbnail_filename_from_url(
                            THUMBNAIL_PREFIX, thumbnail_url)
                    self.save_file(thumbnail_url, filename)
                    
            # Shallowly crawl image files
            image_urls = self.info_reader.get_episode_image_urls()
            # TODO: make this for loop faster than this O(n**2)
            for index, image_url in enumerate(image_urls):
                prefix = '{0:03d}'.format(index+1)
                filename = self.image_filename_from_url(prefix, image_url)
                self.save_file(image_url, filename)
        else: 
            # Info file is populated before any actual downloading.
            # If info file is incomplete, we need to do full crawl.
            self.full_crawl()

    # Check episode webpage for update, and if there are new image files,
    # download them and update info file.
    def update_crawl(self):
        # update crawl is identical to (1) update info.txt (2) do shallow crawl
        self.populate_episode_info()
        self.info_reader = logger.InfoReader(self.directory) # need new reader
        self.shallow_crawl()
    
    # fetch episode info from webpage and (over)write to info file
    def populate_episode_info(self):
        raise NotImplementedError('Subclass should override this method')
       
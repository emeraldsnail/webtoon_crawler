import wc_util
from wc_util import logger

thumbnail_prefix = 'thumbnail'

class CrawlTypeNotFoundException(Exception):
    pass

# Base class for all single episode crawlers
class BaseEpisodeCrawler:
    
    def __init__(self, directory, crawl_type):
        self.directory = directory
        self.crawl_type = crawl_type
        self.info_reader = logger.InfoReader(self.directory)
        self.log_reader = logger.LogReader(self.directory)
    
    # Determine filename to save from the file url
    def filename_from_file_url(self, prefix, file_url):
        raise NotImplementedError('Subclass should override this method')
     
    # Save an file from url
    def save_file(self, prefix, file_url):
        filename = filename_from_file_url(prefix, file_url)
        if wc_util.save_to_binary_file(file_url, self.directory, filename):
            # log if file is successfully downloaded
            if not self.log_writer:
                self.log_writer = logger.LogWriter(self.directory)
            self.log_writer.write_downloaded_file_url(file_url)
        
    def crawl(self):
        if self.crawl_type == CrawlType.FULL:
            self.full_crawl()
        elif self.crawlers == CrawlType.UPDATE:
            self.update_crawl()
        elif self.crawlers == CrawlType.SHALLOW:
            self.shallow_crawl()
        else:
            raise CrawlTypeNotFoundException('Crawl type is incorrect!')
            
        # cleanup
        if self.info_writer:
            self.info_writer.close()
        if self.log_writer:
            self.log_writer.close()
        
    # Crawl from scratch
    def full_crawl(self):
        raise NotImplementedError('Subclass should override this method')
        
    # Check info file and download missing ones.
    def shallow_crawl(self):
        if self.info_reader.is_episode_complete():
            # Shallowly crawl thumbnails
            thumbnail_urls = info_reader.get_episode_thumbnail_urls()
            for thumbnail_url in thumbnail_urls:
                if not self.log_reader.file_url_exists(thumbnail_url):
                    self.save_file(thumbnail_prefix, thumbnail_url)
                    
            # Shallowly crawl image files
            image_urls = info_reader.get_episode_image_urls()
            # TODO: make this for loop faster than this O(n**2)
            for index, image_url in enumerate(image_urls):
                if not self.log_reader.file_url_exists(image_url):
                    self.save_file(index, image_url)
        else: 
            # Info file is populated before any actual downloading.
            # If info file is incomplete, we need to do full crawl.
            self.full_crawl()

    # Check episode webpage for update, and if there are new image files,
    # download them and update info file.
    def update_crawl(self):
        # update crawl is identical to (1) update info.txt (2) do shallow crawl
        self.fetch_episode_info()
        self.info_reader = logger.InfoReader(self.directory) # need new reader
        self.shallow_crawl()
       
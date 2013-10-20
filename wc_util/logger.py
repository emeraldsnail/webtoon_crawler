import os.path
import time


INFO_FILENAME = 'info.txt'
LOG_FILENAME = 'download.log'
TIMESTAMP = 'TIMESTAMP'
DELIMETER = ':'
STR_FORMAT = '{0}' + DELIMETER + '{1}\n'

WEBTOON_TITLE = 'WEBTOON_TITLE'
WEBTOON_AUTHOR = 'WEBTOON_AUTHOR'
WEBTOON_THUMBNAIL = 'WEBTOON_THUMBNAIL'

EPISODE_TITLE = 'EPISODE_TITLE'
EPISODE_AUTHOR = 'EPISODE_AUTHOR'
EPISODE_DATE = 'DATE'
EPISODE_FILECOUNT = 'FILECOUNT'
EPISODE_THUMBNAIL_URL = 'THUMBNAIL_URL'
EPISODE_IMAGE_URL = 'FILE_URL'

DOWNLOADED = 'DOWNLOADED'
INFO_COMPLETE = 'INFO_COMPLETE'

# TODO: improve the atomicity of writer classes.

# Base class of all writers
class BaseWriter:
    def __init__(self, directory, filename, option = 'a'):
        if not os.path.exists(directory):
            os.makedirs(directory)
        path = os.path.join(directory, filename)
        self.output = open(path, option)

    def write_TIMESTAMP(self):
        self.write_in_format(TIMESTAMP, str(time.localtime()))

    def write_in_format(self, head, content, should_flush = True):
        head = (head or '').strip()
        content = (content or '').strip()
        self.output.write(STR_FORMAT.format(head, content))
        if should_flush:
            self.output.flush() # flush every time

    def close(self):
        self.output.close()


# Base class of all readers
class BaseReader:
    #line_data = {}

    def __init__(self, directory, filename):
        self.directory = directory
        self.line_data = {}
        path = os.path.join(directory, filename)
        if os.path.isfile(path):
            file = open(path, 'r')
            lines = file.readlines()
            self.expand(lines)
            file.close()
        #print('base reader content: ', str(self.line_data))

    def is_empty(self):
        return not self.line_data

    def expand(self, lines):
        for line in lines:       
            try:
                line = line.strip()
                if not line: continue
                split = line.split(DELIMETER, 1)
                key = split[0]
                values = self.line_data.get(key, [])
                values.append(split[1])
                self.line_data[key] = values
            except Exception as e:
                pass # malformed line. Silently continue

    def read_first(self, key):
        values = self.read_all(key)
        if values:
            return values[0]
        else:
            return None

    # return the last value of the key, if exists
    def read_last(self, key):
        values = self.read_all(key)
        if values:
            return values[-1]
        else:
            return None

    # return all values of the key, if exists
    def read_all(self, key):
        return self.line_data.get(key, [])

    def print_content(self):
        print (self.line_data)

class InfoWriter(BaseWriter):
    def __init__(self, directory):
        super().__init__(directory, INFO_FILENAME, 'w')

    def write_webtoon_title(self, title):
        self.write_in_format(WEBTOON_TITLE, title)

    def write_webtoon_author(self, author):
        self.write_in_format(WEBTOON_AUTHOR, author)

    def write_episode_title(self, title):
        self.write_in_format(EPISODE_TITLE, title)

    def write_episode_date(self, date):
        self.write_in_format(EPISODE_DATE, date)

    def write_episode_filecount(self, filecount):
        self.write_in_format(EPISODE_FILECOUNT, filecount)

    def write_episode_image_url(self, image_url):
        self.write_in_format(EPISODE_IMAGE_URL, image_url)

    def write_episode_thumbnail_url(self, thumbnail_url):
        self.write_in_format(EPISODE_THUMBNAIL_URL, thumbnail_url)
        
    def write_complete(self):
        self.write_in_format(INFO_COMPLETE, 'True')


class InfoReader(BaseReader):
    def __init__(self, directory):
        super().__init__(directory, INFO_FILENAME)
        
    def get_episode_filecount(self):
        return self.read_last(EPISODE_FILECOUNT)
        
    def get_episode_thumbnail_urls(self):
        return self.read_all(EPISODE_THUMBNAIL_URL)
    
    def get_episode_image_urls(self):
        return self.read_all(EPISODE_IMAGE_URL)
        
    def get_episode_title(self):
        return self.read_first(EPISODE_TITLE)
        
    def is_complete(self):  
        return self.read_all(INFO_COMPLETE)


class LogWriter(BaseWriter):
    def __init__(self, directory):
        super().__init__(directory, LOG_FILENAME)

    def write_downloaded_file_url(self, file_url):
        self.write_in_format(DOWNLOADED, file_url)


class LogReader(BaseReader):
    def __init__(self, directory):
        super().__init__(directory, LOG_FILENAME)
        
    def file_url_exists(self, file_url):
        return file_url in self.read_all(DOWNLOADED)

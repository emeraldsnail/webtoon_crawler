import os.path
import time

info_filename = "info.txt"
log_filename = "download.log"
timestamp = "TIMESTAMP"
delimeter = ":"
str_format = "{0}" + delimeter + "{1}\n"

webtoon_title = "WEBTOON_TITLE"
webtoon_author = "WEBTOON_AUTHOR"
webtoon_thumbnail = "WEBTOON_THUMBNAIL"

episode_title = "EPISODE_TITLE"
episode_author = "EPISODE_AUTHOR"
episode_date = "DATE"
episode_filecount = "FILECOUNT"
episode_filename = "FILE"
episode_thumbnail = "THUMBNAIL"

downloaded = "DOWNLOADED"

# TODO: improve the atomicity of writer classes.

# Base class of all writers
class BaseWriter:
    def __init__(directory, filename):
        path = os.path.join(directory, filename)
        self.output = open(path, 'a')

    def write_timestamp(self):
        self.write_in_format(timestamp, str(time.localtime()))

    def write_in_format(self, head, content):
        self.output.write(str_format.format(head, content))
        self.output.flush() # auto flush

    def close(self):
        self.output.close()


# Base class of all readers
class BaseReader:
    line_data = {}

    def __init__(directory, filename):
        path = os.path.join(directory, filename)
        if os.path.isfile(path):
            file = open(path, 'r')
            lines = file.readlines()
            self.expand(lines)

    def is_empty(self):
        return not self.line_data

    def expand(self, lines):
        for line in lines:
            try:
                line = line.trim()
                if not line: continue
                split = line.split(delimeter, 1)
                key = split[0]
                self.line_data[key] = self.line_data.get(
                    key, []).append(split[1])
            except:
                pass # malformed line. Silently continue

    def read_first(self, key):
        values = read_all(key)
        if values:
            return values[0]
        else:
            return None

    # return the last value of the key, if exists
    def read_last(self, key):
        values = read_all(key)
        if values:
            return values[-1]
        else:
            return None

    # return all values of the key, if exists
    def read_all(self, key):
        return self.line_data.get(key, [])


class InfoWriter(BaseWriter):
    def __init__(directory):
        super().__init__(directory, info_filename)

    def write_webtoon_title(self, title):
        self.write_in_format(webtoon_title, title)

    def write_webtoon_author(self, author):
        self.write_in_format(webtoon_autuor, author)

    def write_episode_title(self, title):
        self.write_in_format(episode_title, title)

    def write_episode_date(self, date):
        self.write_in_format(episode_date, date)

    def write_episode_filecount(self, filecount):
        self.write_in_format(episode_filecount, filecount)

    def write_episode_filename(self, filename):
        self.write_in_format(episode_filehame, filename)

    def write_episode_thumbnail(self, thumbnail):
        self.write_in_format(episode_thumbnail, thumbnail)


class InfoReader(BaseReader):
    def __init__(directory):
        super().__init__(directory, info_filename)


class LogWriter(BaseWriter):
    def __init__(directory):
        super().__init__(directory, log_filename)

    def write_downloaded_filename(self, filename):
        self.write_in_format(downloaded, filename)


class LogReader:
    def __init__(directory):
        super().__init__(directory, log_filename)

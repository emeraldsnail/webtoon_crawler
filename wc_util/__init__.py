import urllib.request
import httplib2
import os.path
import re
import argparse

httpclient = httplib2.Http()

class CrawlType:
    FULL = 'full'
    SHALLOW = 'shallow'
    UPDATE = 'update'
    
all_crawl_types = [CrawlType.FULL, CrawlType.SHALLOW, CrawlType.UPDATE]

crawl_type_help_str = """
    Specify crawling type.
    full: download the entire episodes, overwriting existing files
    shallow: check the logs and download missing ones and newer episodes only. Do not check for updates in already downloaded episodes'
    update: identical to shallow, except that all episodes (including already downloaded ones) are checked again for updates, and download if new images exist'
"""

parser = argparse.ArgumentParser(description = crawl_type_help_str)
parser.add_argument('-t', '--crawl-type', choices = all_crawl_types,
        default = CrawlType.SHALLOW, help = 'specify crawl type')

def getdata(url, headers = {}, method = 'GET'):
    return httpclient.request(url, method, headers)

def get_binary_from_url(url, headers = {}):
    try:
        req = urllib.request.Request(url, headers=headers)
        fp = urllib.request.urlopen(req)
        binary = fp.read()
        fp.close()
        return binary
    except:
        return None
    
def get_text_from_url(url, encoding = 'utf8'):
    return get_binary_from_url(url).decode(encoding)
    
def save_to_binary_file(url, directory, filename, headers={}):
    binary_content = get_binary_from_url(url, headers)
    
    if binary_content:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            path = os.path.join(directory, filename)
            
            file = open(path, 'wb')
            file.write(binary_content)
            file.close()
            return True
        except:
            return False
    else:
        return False
    
def extract_last(url):
    return os.path.split(urllib.parse.urlparse(url)[2])[-1]
    
def remove_invalid_filename_chars(name):
    return re.sub(r'[/:\\*?"<>|]', '', name)
    
def get_crawl_type():
    options = parser.parse_args()
    return options.crawl_type

def copy_headers_with_filename_and_prefix(original_headers, prefix, file_url):
    headers = original_headers.copy()
    filename = extract_last(file_url)
    headers['original_filename'] = filename
    headers['prefix'] = prefix
    return headers
    
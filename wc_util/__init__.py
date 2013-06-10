import urllib.request

def get_binary_from_url(url):
    try:
        fp = urllib.request.urlopen(url)
        binary = fp.read()
        fp.close()
        return binary
    except:
        return None
    
def get_text_from_url(url, encoding = 'utf8'):
    return get_binary_from_url(url).decode(encoding)
    
def save_to_binary_file(url, filename):
    binary_content = get_binary_from_url(url)
    file = open(filename, 'wb')
    file.write(binary_content)
    file.close()
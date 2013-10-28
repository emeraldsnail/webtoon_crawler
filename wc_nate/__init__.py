BASE_URL = 'http://comics.nate.com'
LIST_URL = BASE_URL + '/webtoon/detail.php?btno={title_id}'
VIEWER_URL = LIST_URL + '&bsno={episode_id}'

SAVE_PATH = 'nate/{title_id}_{title_name}/{episode_id}_{episode_name}/'
IMAGE_FILENAME_PATTERN = '{prefix}_{timestamp}_{original_filename}'
THUMBNAIL_FILENAME_PATTERN = '{prefix}_{original_filename}'
BASE_URL = 'http://comic.naver.com'
LIST_URL = BASE_URL + '/{category}/list.nhn?titleId={title_id}&page={page_id}'
VIEWER_URL = BASE_URL + '/{category}/detail.nhn?titleId={titleId}&no={episode_id}'

# Changing any of the values below may result in re-crawling of downloaded files
SAVE_PATH = 'naver/{category}/{title_id} {title_name}/{episode_id} {episode_name}/'
IMAGE_FILENAME_PATTERN = '{prefix}_{original_filename}'
THUMBNAIL_FILENAME_PATTERN = '{prefix}_{original_filename}'
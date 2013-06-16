base_url = 'http://comic.naver.com'
list_url = base_url + '/{category}/list.nhn?titleId={title_id}&page={page_id}'
viewer_url = base_url + '/{category}/detail.nhn?titleId={titleId}&no={episode_id}'

save_path = 'naver/{category}/{title_name}/{episode_id} {episode_name}/'
filename_pattern = '{original_filename}'
thumbnail_filename = '{original_filename}'
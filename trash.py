def set_result_rating(uuid, rating):
    # api_route = '/api/demo/description/rating'
    url = settings.url
    url = url + settings.rating_api
    payload = {'image_uuid': uuid,
                'rating': rating}
    try:
        response = requests.post(url, json=payload, timeout=settings.ml_models_timeout)
        result = response.json()
    except  (ConnectionError, HTTPError, Timeout):
        result = {'error': 'server unavailable'}

def get_desc_and_tags(path_url=None, lang='en', url_method=False):
    path_url = 'https://cdn.motor1.com/images/mgl/3PMJX/s3/car-for-whole-life.webp'
    if url_method:
        api_route = settings.url_api
        payload = {'json': {'imageUrl': path_url,
                    'lang': lang}}
    else:
        api_route = settings.file_api
        payload = {'files': {'image_file': open(path_url, 'rb')},
                    'data': {'lang': lang}}
    url = settings.url
    url = url + api_route
    try:
        response = requests.post(url, **payload, timeout=settings.ml_models_timeout)
        result = response.json()
    except  (ConnectionError, HTTPError, Timeout):
        result = {'error': 'server unavailable'}
    answer, uuid = make_desc_tags_answer(result, 'list')
    return answer, uuid

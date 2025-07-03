from validators import url as check_url


def validate_url(url):
    url_max_length = 255

    if len(url) == 0:
        return 'URL обязателен'

    if len(url) > url_max_length:
        return 'URL превышает 255 символов'

    if not check_url(url):
        return 'Некорректный URL'

    return None
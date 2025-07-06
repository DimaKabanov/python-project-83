from urllib.parse import urlparse

from bs4 import BeautifulSoup
from validators import url as check_url


def normalize_url(url):
    result = urlparse(url)
    return f'{result.scheme}://{result.netloc}'


def validate_url(url):
    url_max_length = 255

    if len(url) == 0:
        return 'URL обязателен'

    if len(url) > url_max_length:
        return 'URL превышает 255 символов'

    if not check_url(url):
        return 'Некорректный URL'

    return None


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    h1 = '' if soup.h1 is None else soup.h1.string
    title = '' if soup.title is None else soup.title.string
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    description = '' if meta_tag is None else meta_tag.get('content')

    return h1, title, description
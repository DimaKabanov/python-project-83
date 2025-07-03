import os
from datetime import datetime
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.models import Url
from page_analyzer.repositories.url_repository import UrlRepository
from page_analyzer.validators import validate_url

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


conn = psycopg2.connect(app.config['DATABASE_URL'])
repo = UrlRepository(conn)


@app.get('/')
def index():
    return render_template('index.html', form_url='', error=None)


@app.get('/urls')
def urls_index():
    urls = repo.get_content()
    return render_template('urls/index.html', urls=urls)


@app.post('/urls')
def urls_create():
    form_url = request.form.get('url')
    error = validate_url(form_url)

    if error:
        return render_template(
            'index.html',
            form_url=form_url,
            error=error), 422

    normalized_url = normalize_url(form_url)
    url = Url(name=normalized_url, created_at=datetime.now())

    existing_url = repo.find_by_name(url.name)

    if existing_url:
        flash('Страница уже существует', 'info')
        return redirect(url_for('urls_show', id=existing_url.id), code=302)

    id = repo.save(url)
    flash('Сайт успешно добавлен', 'success')

    return redirect(url_for('urls_show', id=id), code=302)


@app.get('/urls/<id>')
def urls_show(id):
    messages = get_flashed_messages(with_categories=True)
    url = repo.find(id)

    if not url:
        return abort(404)

    return render_template('urls/show.html', url=url, messages=messages)


@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


def normalize_url(url):
    result = urlparse(url)
    return f'{result.scheme}://{result.netloc}'
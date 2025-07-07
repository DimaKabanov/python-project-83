import os
from datetime import datetime

import psycopg2
import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    g,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)
from requests import RequestException

from page_analyzer.models import Check, Url
from page_analyzer.repositories.check_repository import CheckRepository
from page_analyzer.repositories.url_repository import UrlRepository
from page_analyzer.utils import normalize_url, parse_html, validate_url

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(app.config['DATABASE_URL'])
    return g.db


def get_url_repo():
    return UrlRepository(get_db())


def get_check_repo():
    return CheckRepository(get_db())


@app.get('/')
def index():
    return render_template('index.html', form_url='', error=None)


@app.get('/urls')
def urls_index():
    urls = get_url_repo().get_all()
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

    existing_url = get_url_repo().find_by({'name': url.name})

    if existing_url:
        flash('Страница уже существует', 'info')
        return redirect(url_for('urls_show', id=existing_url.id), code=302)

    url_id = get_url_repo().save(url)
    flash('Страница успешно добавлена', 'success')

    return redirect(url_for('urls_show', id=url_id), code=302)


@app.get('/urls/<id>')
def urls_show(id):
    messages = get_flashed_messages(with_categories=True)
    url = get_url_repo().find(id)
    checks = get_check_repo().find_all_by({'url_id': id})

    if not url:
        return abort(404)

    return render_template(
        'urls/show.html',
        url=url,
        checks=checks,
        messages=messages)


@app.post('/urls/<id>/checks')
def urls_check_create(id):
    url = get_url_repo().find(id)

    if not url:
        return abort(404)

    try:
        response = requests.get(url.name)
        response.raise_for_status()

        h1, title, description = parse_html(response.content)

        check = Check(
            url_id=id,
            status_code=response.status_code,
            h1=h1,
            title=title,
            description=description,
            created_at=datetime.now()
        )

        get_check_repo().save(check)
        flash('Страница успешно проверена', 'success')
    except RequestException:
        flash('Произошла ошибка при проверке', 'danger')

    return redirect(url_for('urls_show', id=id), code=302)


@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@app.template_filter('format_date')
def format_date_filter(date):
    if date is None:
        return ''
    return date.strftime('%Y-%m-%d')

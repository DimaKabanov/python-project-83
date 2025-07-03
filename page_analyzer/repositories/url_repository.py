from psycopg2.extras import RealDictCursor

from page_analyzer.models import Url


class UrlRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_content(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT * FROM urls ORDER BY created_at DESC')
            return cur.fetchall()

    def find(self, id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            sql = 'SELECT * FROM urls WHERE id = %s'
            cur.execute(sql, (id,))
            url = cur.fetchone()
            return Url(**url) if url else None

    def find_by_name(self, name):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            sql = 'SELECT * FROM urls WHERE name = %s'
            cur.execute(sql, (name,))
            url = cur.fetchone()
            return Url(**url) if url else None

    def save(self, url):
        if url.id is None:
            id = self._create(url)
        else:
            id = self._update(url)

        return id

    def _create(self, url):
        with self.conn.cursor() as cur:
            sql = '''
                INSERT INTO urls (name, created_at)
                VALUES (%s, %s)
                RETURNING id
            '''
            cur.execute(sql, (url.name, url.created_at))
            url.id = cur.fetchone()[0]

        self.conn.commit()
        return url.id

    def _update(self, url):
        with self.conn.cursor() as cur:
            sql = 'UPDATE urls SET name = %s, created_at = %s WHERE id = %s'
            cur.execute(sql, (url.name, url.created_at, url.id))

        self.conn.commit()
        return url.id
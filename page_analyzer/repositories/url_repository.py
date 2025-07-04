from psycopg2.extras import RealDictCursor

from page_analyzer.models import Url


class UrlRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_all(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            sql = '''
                SELECT
                    u.id,
                    u.name,
                    max(uc.created_at) AS last_check_date,
                    (
                        SELECT status_code 
                        FROM url_checks 
                        WHERE url_id = u.id 
                        ORDER BY created_at DESC 
                        LIMIT 1
                    ) AS status_code
                FROM urls AS u
                LEFT JOIN url_checks AS uc ON u.id = uc.url_id
                GROUP BY u.id, u.name
                ORDER BY u.created_at DESC;
            '''
            cur.execute(sql)
            return cur.fetchall()

    def find(self, id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            sql = 'SELECT * FROM urls WHERE id = %s'
            cur.execute(sql, (id,))
            url = cur.fetchone()
            return Url(**url) if url else None

    def find_by(self, query):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            field, value = next(iter(query.items()))
            sql = f'SELECT * FROM urls WHERE {field} = %s'
            cur.execute(sql, (value,))
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
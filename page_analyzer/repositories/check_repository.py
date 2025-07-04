from psycopg2.extras import RealDictCursor


class CheckRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_all(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT * FROM url_checks ORDER BY created_at DESC')
            return cur.fetchall()

    def find_all_by(self, query):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            field, value = next(iter(query.items()))
            sql = f'''
                SELECT * FROM url_checks
                WHERE {field} = %s
                ORDER BY created_at DESC
            '''
            cur.execute(sql, (value,))
            return cur.fetchall()

    def save(self, check):
        with self.conn.cursor() as cur:
            sql = '''
                INSERT INTO url_checks
                    (url_id, status_code, h1, title, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            '''

            values = (
                check.url_id,
                check.status_code,
                check.h1,
                check.title,
                check.description,
                check.created_at
            )

            cur.execute(sql, values)
            check.id = cur.fetchone()[0]

        self.conn.commit()
        return check.id
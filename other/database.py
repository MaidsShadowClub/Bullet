from psycopg2 import pool, extensions
from scrapy.utils.project import get_project_settings


class Database:
    def __init__(self):
        cfg = get_project_settings()
        self.pool = pool.SimpleConnectionPool(
            1, 20,
            dbname=cfg.get("PG_BASE"),
            user=cfg.get("PG_USER"),
            password=cfg.get("PG_PASS"),
            host=cfg.get("PG_HOST"),
            port=cfg.get("PG_PORT")
        )

    def open(self) -> tuple[extensions.connection, extensions.cursor]:
        conn = self.pool.getconn()
        curs = conn.cursor()
        return conn, curs

    def close(self, conn, curs):
        curs.close()
        self.pool.putconn(conn)
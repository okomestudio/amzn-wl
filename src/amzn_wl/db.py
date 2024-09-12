"""Database access layer."""

import contextlib
import sqlite3

from .configs import config
from .entities import products


@contextlib.contextmanager
def get_conn():
    database = config["sqlite"]["database"]
    conn = sqlite3.connect(database)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


sql_ensure_product = """-- sql
INSERT INTO
  product (asin, title, byline)
VALUES
  (?, ?, ?)
ON CONFLICT (asin) DO
UPDATE
SET
  title = excluded.title,
  byline = excluded.byline
WHERE
  title != excluded.title
  OR byline != excluded.byline;
"""


def ensure_product(product: products.Product):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql_ensure_product, (product.asin, product.title, product.byline))

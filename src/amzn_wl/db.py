"""Database access layer."""

import contextlib
import sqlite3

from .configs import config
from .entities import prices, products, sites, wishlists


@contextlib.contextmanager
def get_conn():
    database = config["sqlite"]["database"]
    conn = sqlite3.connect(database)
    conn.execute("PRAGMA foreign_keys = 1")
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()


sql_insert_price = """
INSERT INTO
  price (asin, hostname, value, currency)
VALUES
  (?, ?, ?, ?)
"""


def insert_price(price: prices.Price):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            sql_insert_price,
            (price.asin, price.hostname, str(price.value), price.currency),
        )


sql_ensure_product = """
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


sql_ensure_site = """
INSERT INTO
  site (hostname)
VALUES
  (?)
ON CONFLICT (hostname) DO NOTHING;
"""


def ensure_site(site: sites.Site):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql_ensure_site, (site.hostname,))


sql_ensure_wishlist = """
INSERT INTO
  wishlist (wishlist_id, name)
VALUES
  (?, ?)
ON CONFLICT (wishlist_id)
UPDATE
SET
  name = excluded.name
WHERE
  name != excluded.name;
"""


def ensure_wishlist(wishlist: wishlists.Wishlist):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql_ensure_wishlist, (wishlist.wishlist_id, wishlist.name))

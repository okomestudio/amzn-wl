"""Database access layer."""

import contextlib
import logging
import sqlite3
from decimal import Decimal

from .configs import config
from .entities.loyalty import Loyalty
from .entities.price_drop import PriceDrop
from .entities.product import Product
from .entities.product_price import ProductPrice
from .entities.site import Site
from .entities.wishlist import Wishlist

sqlite3.register_adapter(Decimal, lambda d: str(d))
sqlite3.register_converter("decimal", lambda s: Decimal(s.decode()))

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def get_conn():
    database = config["sqlite"]["database"]
    conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    # Uncomment for query logging:
    # conn.set_trace_callback(logger.info)

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


sql_insert_product_price = """
INSERT INTO
  product_price (asin, hostname, value, currency_id)
SELECT
  ?, ?, ?, currency_id
FROM currency WHERE code = ?
RETURNING product_price_id
"""


def insert_product_price(product_price: ProductPrice) -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            sql_insert_product_price,
            (
                product_price.product.asin,
                product_price.site.hostname,
                product_price.price.value,
                product_price.price.currency_code,
            ),
        )
        row = cur.fetchone()
        product_price_id = row[0]

    if product_price.price_drop:
        insert_product_price_drop(product_price_id, product_price.price_drop)
    if product_price.loyalty:
        insert_product_price_loyalty(product_price_id, product_price.loyalty)

    return product_price_id


sql_insert_product_price_drop = """
INSERT INTO
  product_price_drop (product_price_id, value, currency_id, original_value, original_currency_id, percentage)
SELECT
  ?, ?, currency_id, ?, currency_id, ?
FROM currency WHERE code = ?
"""


def insert_product_price_drop(product_price_id: int, price_drop: PriceDrop):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            sql_insert_product_price_drop,
            (
                product_price_id,
                price_drop.price.value if price_drop.price else None,
                price_drop.original_price.value,
                price_drop.percentage.value if price_drop.percentage else None,
                price_drop.original_price.currency_code,
            ),
        )


sql_insert_product_price_loyalty = """
INSERT INTO
  product_price_loyalty (product_price_id, point, percentage)
VALUES
  (?, ?, ?)
"""


def insert_product_price_loyalty(product_price_id: int, loyalty: Loyalty):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            sql_insert_product_price_loyalty,
            (
                product_price_id,
                loyalty.point,
                loyalty.percentage.value,
            ),
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


def ensure_product(product: Product):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql_ensure_product, (product.asin, product.title, product.byline))


sql_ensure_product_wishlist = """
INSERT INTO
  product_wishlist (asin, wishlist_id)
VALUES
  (?, ?)
ON CONFLICT (asin, wishlist_id) DO
UPDATE
SET
  updated = DATETIME('now')
"""


def ensure_product_wishlist(product: Product, wishlist: Wishlist):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql_ensure_product_wishlist, (product.asin, wishlist.wishlist_id))


sql_ensure_site = """
INSERT INTO
  site (hostname)
VALUES
  (?)
ON CONFLICT (hostname) DO NOTHING;
"""


def ensure_site(site: Site):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql_ensure_site, (site.hostname,))


sql_ensure_wishlist = """
INSERT INTO
  wishlist (wishlist_id, hostname, name)
VALUES
  (?, ?, ?)
ON CONFLICT (wishlist_id) DO
UPDATE
SET
  hostname = excluded.hostname,
  name = excluded.name
WHERE
  hostname != excluded.hostname OR
  name != excluded.name;
"""


def ensure_wishlist(wishlist: Wishlist):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            sql_ensure_wishlist,
            (wishlist.wishlist_id, wishlist.site.hostname, wishlist.name),
        )

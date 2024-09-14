import pathlib
from decimal import Decimal

import pytest

from alembic.command import upgrade
from alembic.config import Config as AlembicCfg
from amzn_wl import db
from amzn_wl.configs import config
from amzn_wl.entities.prices import Price
from amzn_wl.entities.products import Product
from amzn_wl.entities.sites import Site
from amzn_wl.entities.wishlists import Wishlist


@pytest.fixture(scope="session", autouse=True)
def alembic_cfg():
    database = "amzn-wl-test.db"

    config["sqlite"]["database"] = database

    alembic_cfg = AlembicCfg("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{ database }")
    upgrade(alembic_cfg, "head")

    yield alembic_cfg

    pathlib.Path(database).unlink()


def select_fetch_all(sql: str, params: tuple | None = None) -> list:
    with db.get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        return cur.fetchall()


def delete_table(table: str) -> None:
    with db.get_conn() as conn:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table}")


@pytest.fixture(scope="function")
def price_table():
    yield
    delete_table("price")


@pytest.fixture(scope="function")
def product_table():
    yield
    delete_table("product")


@pytest.fixture(scope="function")
def product_wishlist_table():
    yield
    delete_table("product_wishlist")


@pytest.fixture(scope="function")
def site_table():
    yield
    delete_table("site")

@pytest.fixture(scope="function")
def wishlist_table():
    yield
    delete_table("wishlist")


class TestInsertPrice:
    def test_insert(self, product_table, site_table, price_table):
        product = Product(asin="foo", title="bar", byline="baz")
        site = Site(hostname="en")
        value = Decimal("1.99")
        currency = "$"
        price = Price(
            asin=product.asin, hostname=site.hostname, value=value, currency=currency
        )
        db.ensure_product(product)
        db.ensure_site(site)

        db.insert_price(price)

        rows = select_fetch_all("SELECT asin, hostname, value, currency FROM price")
        assert rows == [(product.asin, site.hostname, str(value), currency)]

    def test_insert_multiple(self, product_table, site_table, price_table):
        product = Product(asin="foo", title="bar", byline="baz")
        site = Site(hostname="en")
        value = Decimal("1.99")
        currency = "$"
        price = Price(
            asin=product.asin, hostname=site.hostname, value=value, currency=currency
        )
        db.ensure_product(product)
        db.ensure_site(site)

        db.insert_price(price)
        db.insert_price(price)

        rows = select_fetch_all(
            "SELECT price_id, asin, hostname, value, currency FROM price"
        )
        assert len(rows) == 2


class TestEnsureProduct:
    def test_insert(self, product_table):
        product = Product(asin="foo", title="bar", byline="baz")

        db.ensure_product(product)

        rows = select_fetch_all("SELECT asin, title, byline FROM product")
        assert rows == [("foo", "bar", "baz")]

    def test_upsert(self, product_table):
        products = [
            Product(asin="foo", title="bar", byline="baz"),
            Product(asin="foo", title="qux", byline="baz"),
        ]

        for product in products:
            db.ensure_product(product)

        rows = select_fetch_all("SELECT asin, title, byline FROM product")
        assert len(rows) == 1
        assert rows == [("foo", "qux", "baz")]


class TestEnsureProductWishlist:
    def test_insert(self, product_table, wishlist_table, product_wishlist_table):
        product = Product(asin="foo", title="bar", byline="baz")
        wishlist = Wishlist(wishlist_id='qux', url='https://foo.bar',name='wl')
        db.ensure_product(product)
        db.ensure_wishlist(wishlist)

        db.ensure_product_wishlist(product, wishlist)

        rows = select_fetch_all("SELECT * FROM product_wishlist")
        assert len(rows) == 1

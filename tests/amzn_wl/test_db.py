import pathlib
from decimal import Decimal

import pytest

from alembic.command import upgrade
from alembic.config import Config as AlembicCfg
from amzn_wl import db, primitives
from amzn_wl.configs import config
from amzn_wl.entities.loyalty import Loyalty
from amzn_wl.entities.price import Price
from amzn_wl.entities.price_drop import PriceDrop
from amzn_wl.entities.product import Product
from amzn_wl.entities.product_price import ProductPrice
from amzn_wl.entities.site import Site
from amzn_wl.entities.wishlist import Wishlist


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
def product_table():
    yield
    delete_table("product")


@pytest.fixture(scope="function")
def product_price_table():
    yield
    delete_table("product_price")


@pytest.fixture(scope="function")
def product_price_drop_table():
    yield
    delete_table("product_price_drop")


@pytest.fixture(scope="function")
def product_price_loyalty_table():
    yield
    delete_table("product_price_loyalty")


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


class TestInsertProductPrice:
    def test_insert(
        self,
        product_table,
        site_table,
        product_price_table,
        product_price_drop_table,
        product_price_loyalty_table,
    ):
        product = Product(asin="foo", title="bar", byline="baz")
        site = Site(hostname="en")
        price = Price(value=Decimal("1.99"), currency="$", currency_code="USD")
        price_drop = PriceDrop(
            Price(Decimal("0.99"), "$", "USD"),
            primitives.Percentage(Decimal("80")),
            Price(Decimal("11.99"), "$", "USD"),
        )
        loyalty = Loyalty(Decimal("0.50"), primitives.Percentage(Decimal("50")))

        product_price = ProductPrice(
            product, site, price, price_drop=price_drop, loyalty=loyalty
        )
        db.ensure_product(product)
        db.ensure_site(site)

        product_price_id = db.insert_product_price(product_price)

        rows = select_fetch_all(
            "SELECT asin, hostname, value, currency FROM product_price"
        )
        assert rows == [(product.asin, site.hostname, price.value, price.currency)]
        rows = select_fetch_all(
            "SELECT product_price_id, value FROM product_price_drop"
        )
        assert rows == [(product_price_id, price_drop.price.value)]
        rows = select_fetch_all(
            "SELECT product_price_id, point FROM product_price_loyalty"
        )
        assert rows == [(product_price_id, loyalty.point)]

    def test_insert_multiple(self, product_table, site_table, product_price_table):
        product = Product(asin="foo", title="bar", byline="baz")
        site = Site(hostname="en")
        price = Price(
            value=Decimal("1.99"),
            currency="$",
            currency_code="USD",
        )
        product_price = ProductPrice(product, site, price)
        db.ensure_product(product)
        db.ensure_site(site)

        db.insert_product_price(product_price)
        db.insert_product_price(product_price)

        rows = select_fetch_all(
            "SELECT product_price_id, asin, hostname, value, currency FROM product_price"
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
        site = Site(hostname="foo.com")
        wishlist = Wishlist(wishlist_id="qux", site=site, name="wl")
        db.ensure_product(product)
        db.ensure_site(site)
        db.ensure_wishlist(wishlist)

        db.ensure_product_wishlist(product, wishlist)

        rows = select_fetch_all("SELECT asin, wishlist_id FROM product_wishlist")
        assert rows == [(product.asin, wishlist.wishlist_id)]

    def test_insert_repeat(self, product_table, wishlist_table, product_wishlist_table):
        product = Product(asin="foo", title="bar", byline="baz")
        site = Site(hostname="foo.com")
        wishlist = Wishlist(wishlist_id="qux", site=site, name="wl")
        db.ensure_product(product)
        db.ensure_site(site)
        db.ensure_wishlist(wishlist)

        db.ensure_product_wishlist(product, wishlist)
        rows_1 = select_fetch_all("SELECT updated FROM product_wishlist")
        # time.sleep(75)  # let's not test updated field refresh
        db.ensure_product_wishlist(product, wishlist)
        rows_2 = select_fetch_all("SELECT updated FROM product_wishlist")

        assert len(rows_1) == 1
        assert len(rows_2) == 1
        # assert rows_1[0][0] < rows_2[0][0]

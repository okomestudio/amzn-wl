import pathlib

import pytest

from alembic.command import upgrade
from alembic.config import Config as AlembicCfg
from amzn_wl import db
from amzn_wl.configs import config
from amzn_wl.entities.products import Product


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

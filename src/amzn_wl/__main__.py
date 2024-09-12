"""Amazon Wishlist dumper."""

import logging
from argparse import ArgumentParser, BooleanOptionalAction

from .drivers import create_driver
from .signin import signin
from .wishlists import Product, get_all_wishlist_items

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def dump_wishlist_products(
    region: str, dump: str, wishlist: str, headless: bool
) -> None:
    """Dump items from all wishlists to JSONL."""
    landing_urls = {
        "jp": "https://www.amazon.co.jp/?language=ja_JP",
        "us": "https://www.amazon.com/",
    }
    url = landing_urls[region]

    driver = create_driver(headless=headless)

    items: list[Product] = []
    try:
        signin(driver, url)
        items = get_all_wishlist_items(driver, url, wishlist)

    except Exception as exc:
        logger.exception(exc)

    finally:
        if items:
            with open(dump, "a") as f:
                for item in items:
                    f.write(item.to_json(ensure_ascii=False) + "\n")


def main() -> None:
    p = ArgumentParser(description=__doc__)
    p.add_argument(
        "--region",
        "-r",
        type=str,
        default="us",
        choices=("jp", "us"),
        help="region (default: 'us')",
    )
    p.add_argument(
        "--dump",
        "-d",
        type=str,
        default="dump.jsonl",
        help="output dump JSONL file (default: 'dump.jsonl')",
    )
    p.add_argument("--wishlist", "-l", type=str, help="wishlist key")
    p.add_argument("--headless", action=BooleanOptionalAction, help="use headless mode")

    args = p.parse_args()

    dump_wishlist_products(**vars(args))


if __name__ == "__main__":
    raise SystemExit(main())

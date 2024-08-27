"""Amazon Wishlist dumper."""
import logging
import time
from argparse import ArgumentParser, BooleanOptionalAction

from .drivers import create_driver
from .signin import signin
from .wishlists import get_all_wishlist_items

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def dump_wishlist_items(region, dump, wishlist, headless):
    """Dump items from all wishlists to JSONL."""
    landing_urls = {
        "jp": "https://www.amazon.co.jp/?language=ja_JP",
        "us": "https://www.amazon.com/",
    }
    url = landing_urls[region]

    driver = create_driver(headless=headless)

    items = []
    try:
        signin(driver, url)
        get_all_wishlist_items(driver, items, url, wishlist)

    except Exception as exc:
        logger.exception(exc)
        while True:
            time.sleep(10)

    finally:
        if items:
            with open(dump, "a") as f:
                for item in items:
                    f.write(item.to_json(ensure_ascii=False) + "\n")


def main():  # noqa
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

    dump_wishlist_items(**vars(args))


if __name__ == "__main__":
    raise SystemExit(main())

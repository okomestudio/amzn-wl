import logging
import time
from argparse import ArgumentParser

from .drivers import create_driver
from .signin import signin
from .wishlists import get_all_wishlist_items

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def dump_wishlist_items(region, dump):
    landing_urls = {
        "jp": "https://www.amazon.co.jp/?language=ja_JP",
        "us": "https://www.amazon.com/",
    }
    url = landing_urls[region]

    driver = create_driver()

    items = []
    try:
        signin(driver, url)
        get_all_wishlist_items(driver, items, url)

    except Exception as exc:
        logger.exception(exc)
        while True:
            time.sleep(10)

    finally:
        with open(dump, "a") as f:
            for item in items:
                f.write(item.to_json(ensure_ascii=False) + "\n")


def main():
    p = ArgumentParser()
    p.add_argument("--region", "-r", type=str, default="us", choices=("jp", "us"))
    p.add_argument("--dump", "-d", type=str, default="dump.jsonl")

    args = p.parse_args()

    dump_wishlist_items(**vars(args))


if __name__ == "__main__":
    raise SystemExit(main())

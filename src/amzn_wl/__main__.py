"""Amazon Wishlist dumper."""

import logging
from argparse import ArgumentParser, BooleanOptionalAction

from .drivers import create_driver
from .entities.wishlist_item import WishlistItem
from .extractors import get_all_wishlist_items
from .signin import signin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def dump_wishlist_products(
    region: str, dump: str, wishlist_ids: list[str] | None, headless: bool
) -> None:
    """Dump items from all wishlists to JSONL."""
    landing_urls = {
        "jp": "https://www.amazon.co.jp/?language=ja_JP",
        "us": "https://www.amazon.com/",
    }
    url = landing_urls[region]

    driver = create_driver(headless=headless)

    items: list[WishlistItem] = []
    try:
        signin(driver, url)
        items = get_all_wishlist_items(driver, url, wishlist_ids)

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
    p.add_argument("--wishlist-id", "-l", action="append", type=str, help="wishlist ID")
    p.add_argument("--headless", action=BooleanOptionalAction, help="use headless mode")

    args = p.parse_args()

    args = vars(args)
    args["wishlist_ids"] = args.pop("wishlist_id")

    dump_wishlist_products(**args)


if __name__ == "__main__":
    raise SystemExit(main())

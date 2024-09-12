"""Wishlists."""

import logging
import time
import urllib.parse
from dataclasses import dataclass
from decimal import Decimal

from dataclasses_json import dataclass_json
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from . import primitives, products
from .utils import get, gets, new_window, sanitize_url

logger = logging.getLogger(__name__)


@dataclass_json
@dataclass
class Wishlist:
    """Wishlist."""

    url: str
    name: str


@dataclass_json
@dataclass
class Price(products.Price):
    """Price extracted from wishlist."""

    @classmethod
    def extract_from_wishlist_item(cls, elmt) -> "Price":
        """Extract Price from given wishlist product element."""
        price_range_elmt = get(elmt, ".//span[contains(@class, 'a-price-range')]")
        if price_range_elmt:
            # for a price range, take the higher one
            price_elmt = gets(price_range_elmt, ".//span[@class='a-price']")[1]
            logger.info("Price range found: %s", price_range_elmt.text)
        else:
            price_elmt = get(elmt, ".//span[contains(@class, 'a-price')]")

        if not price_elmt:
            logger.info("Price element not found")
            return

        price_symbol = get(
            price_elmt, ".//span[contains(@class, 'a-price-symbol')]", "text"
        )
        price_whole = get(price_elmt, ".//span[contains(@class, 'a-price-whole')]")
        if not (price_symbol and price_whole):
            logger.info(
                "Price symbol and/or price whole elements not found: %s, %s",
                price_symbol,
                price_whole,
            )
            return

        price_integer = price_whole.text  # this includes decimal point if exists
        price_fraction = get(
            price_elmt, ".//span[contains(@class, 'a-price-fraction')]", "text"
        )

        price = cls.parse(
            price_symbol
            + price_integer
            + (price_fraction if price_fraction is not None else "")
        )
        return price


@dataclass_json
@dataclass
class PriceDrop:
    """Price drop info."""

    value: Decimal = None
    percentage: primitives.Percentage = None
    original_price: products.Price = None


@dataclass_json
@dataclass
class Product(products.Product):
    """Product info found in wishlist."""

    wishlist: Wishlist = None
    price_drop: dict = None
    effective_price: products.Price = None

    def __post_init__(self):  # noqa
        if self.loyalty:
            self.effective_price = products.Price(
                self.price.value - self.loyalty.point, self.price.currency
            )
        else:
            self.effective_price = self.price


def extract_wishlist_product(
    driver: webdriver.Chrome, wishlist: Wishlist, elmt: WebElement
) -> Product:
    """Extract a product from a wishlist entry."""
    link = get(elmt, ".//a[@title]")
    if not link:
        # Likely "This title is no longer available"
        return

    title = link.get_attribute("title")

    url = sanitize_url(link.get_attribute("href"))

    loyalty = None
    if "amazon.co.jp" in driver.current_url:
        with new_window(driver, lambda: link.send_keys(Keys.CONTROL + Keys.ENTER)):
            loyalty = products.extract_loyalty(driver)

    byline = get(elmt, ".//span[starts-with(@id, 'item-byline-')]", "text")

    stars = get(
        elmt,
        ".//a[contains(@class, 'g-visible-js')]",
        lambda e: e.get_attribute("aria_label"),
    )

    price = Price.extract_from_wishlist_item(elmt)
    if not price:
        return

    price_drop_elmt = get(elmt, ".//div[contains(@class, 'itemPriceDrop')]")
    if price_drop_elmt:
        price_drop_value = get(price_drop_elmt, ".//span[1]", "text")
        if "%" in price_drop_value:
            logger.info("price_drop_value %s", price_drop_value)
            price_drop_percentage = primitives.Percentage.parse(price_drop_value)
            price_drop_value = None
        else:
            price_drop_value = products.Price.parse(price_drop_value)
            price_drop_percentage = None

        price_drop_original_price = products.Price.parse(
            get(price_drop_elmt, ".//span[3]", "text")
        )
        price_drop = PriceDrop(
            price_drop_value, price_drop_percentage, price_drop_original_price
        )
    else:
        price_drop = None

    item = Product(
        price=price,
        price_drop=price_drop,
        title=title,
        byline=byline,
        stars=stars,
        url=url,
        wishlist=wishlist,
        loyalty=loyalty,
    )
    logger.info(item.to_json(ensure_ascii=False, indent=4))
    return item


def scroll_till_fully_loaded(
    driver: webdriver.Chrome, stop_condition: str, max_try: int = 40, wait: int = 1
):
    """Scroll down a wishlist page till the end."""
    for _ in range(max_try):
        try:
            WebDriverWait(driver, wait).until(
                EC.presence_of_element_located((By.ID, stop_condition))
            )
        except exceptions.TimeoutException:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            continue
        else:
            break


def get_products_from_wishlist(
    driver: webdriver.Chrome, wishlist: Wishlist
) -> list[Product]:
    """Get items from given wishlist."""
    driver.get(wishlist.url)
    scroll_till_fully_loaded(driver, "endOfListMarker")

    items = []

    elmts = driver.find_elements(
        By.XPATH, "//ul[@id='g-items']//li[contains(@class, 'g-item-sortable')]"
    )
    for elmt in elmts:
        item = extract_wishlist_product(driver, wishlist, elmt)
        if item:
            items.append(item)

    return items


def get_all_wishlist_products(
    driver: webdriver.Chrome, url: str, wishlist: str | None = None
) -> list[Product]:
    """Entry point for getting items from all wishlists."""
    url = urllib.parse.urljoin(url, "/hz/wishlist/ls")

    driver.get(url)

    elmt = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "your-lists-nav"))
    )

    wishlists = []
    for link in elmt.find_elements(By.XPATH, './/div[contains(@class, "wl-list")]//a'):
        url = link.get_attribute("href")
        name = link.find_elements(
            By.XPATH, ".//span[starts-with(@id, 'wl-list-entry-title-')]"
        )[0].text

        # If a target wishlist is given, skip other wishlists
        if wishlist and wishlist not in url:
            continue

        wishlists.append(Wishlist(sanitize_url(url), name))

    items = []
    for wishlist in wishlists:
        items.extend(get_products_from_wishlist(driver, items, wishlist))

    return items

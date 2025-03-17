import logging
import urllib.parse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from . import db, primitives
from .entities.loyalty import compute_effective_price, extract_loyalty
from .entities.price import Price
from .entities.price_drop import PriceDrop
from .entities.product import Product, extract_asin
from .entities.product_price import ProductPrice
from .entities.site import Site
from .entities.wishlist import Wishlist, extract_wishlist_id
from .entities.wishlist_item import WishlistItem
from .utils import get, gets, new_window, sanitize_url
from .utils.selenium import scroll_till_fully_loaded

logger = logging.getLogger(__name__)


def extract_price(elmt) -> Price | None:
    """Extract Price from a wishlist product element."""
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

    price = Price.parse(
        price_symbol
        + price_integer
        + (price_fraction if price_fraction is not None else "")
    )
    return price


def extract_price_drop(elmt: WebElement) -> PriceDrop | None:
    price_drop_elmt = get(elmt, ".//div[contains(@class, 'itemPriceDrop')]")
    if not price_drop_elmt:
        return

    price_drop_value = get(price_drop_elmt, ".//span[1]", "text")
    if "%" in price_drop_value:
        logger.info("price_drop_value %s", price_drop_value)
        price = None
        percentage = primitives.Percentage.parse(price_drop_value)
    else:
        price = Price.parse(price_drop_value)
        percentage = None

    original_price = Price.parse(get(price_drop_elmt, ".//span[3]", "text"))
    price_drop = PriceDrop(
        price,
        percentage,
        original_price,
    )
    return price_drop


def extract_wishlist_item(
    driver: webdriver.Chrome, wishlist: Wishlist, elmt: WebElement
) -> WishlistItem | None:
    """Extract a product from a wishlist entry."""
    link = get(elmt, ".//a[@title]")
    if not link:
        # Likely "This title is no longer available"
        return

    loyalty = None
    if "amazon.co.jp" in driver.current_url:
        with new_window(driver, lambda: link.send_keys(Keys.CONTROL + Keys.ENTER)):
            loyalty = extract_loyalty(driver)

    price = extract_price(elmt)
    if not price:
        return

    url = sanitize_url(link.get_attribute("href"))
    effective_price = compute_effective_price(price, loyalty)

    title = link.get_attribute("title")
    asin = extract_asin(url)
    byline = get(elmt, ".//span[starts-with(@id, 'item-byline-')]", "text")
    stars = get(
        elmt,
        ".//a[contains(@class, 'g-visible-js')]",
        lambda e: e.get_attribute("aria_label"),
    )

    product = Product(
        asin=asin,
        title=title,
        byline=byline,
        url=url,
        stars=stars,
    )
    db.ensure_product(product)

    price_drop = extract_price_drop(elmt)
    product_price = ProductPrice(
        product, wishlist.site, price, price_drop, loyalty, effective_price
    )
    db.insert_product_price(product_price)

    item = WishlistItem(
        product=product,
        product_price=product_price,
        wishlist=wishlist,
    )
    db.ensure_product_wishlist(item.product, item.wishlist)

    logger.info(item.to_json(ensure_ascii=False, indent=4))
    return item


def extract_wishlist_items(
    driver: webdriver.Chrome, wishlist: Wishlist
) -> list[WishlistItem]:
    """Get items from the given wishlist."""
    driver.get(wishlist.url)
    scroll_till_fully_loaded(driver, "endOfListMarker")

    elmts = driver.find_elements(
        By.XPATH, "//ul[@id='g-items']//li[contains(@class, 'g-item-sortable')]"
    )
    items = [extract_wishlist_item(driver, wishlist, elmt) for elmt in elmts]
    return [item for item in items if item]


def extract_wishlist(elmt: WebElement) -> Wishlist | None:
    url = elmt.get_attribute("href")

    site = Site.from_url(url)
    db.ensure_site(site)

    name = elmt.find_elements(
        By.XPATH, ".//span[starts-with(@id, 'wl-list-entry-title-')]"
    )[0].text
    wishlist_id = extract_wishlist_id(url)
    if not wishlist_id:
        return

    wishlist = Wishlist(wishlist_id, site, name)
    db.ensure_wishlist(wishlist)

    return wishlist


def get_all_wishlist_items(
    driver: webdriver.Chrome, url: str, wishlist_ids: list[str] | None = None
) -> list[WishlistItem]:
    """Entry point for getting items from all wishlists."""
    url = urllib.parse.urljoin(url, "/hz/wishlist/ls")

    driver.get(url)

    elmt = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "your-lists-nav"))
    )

    wishlists = [
        extract_wishlist(link)
        for link in elmt.find_elements(
            By.XPATH, './/div[contains(@class, "wl-list")]//a'
        )
    ]

    items = []
    for wishlist in [wishlist for wishlist in wishlists if wishlist]:
        if wishlist_ids and (wishlist.wishlist_id not in wishlist_ids):
            continue
        items.extend(extract_wishlist_items(driver, wishlist))

    return items

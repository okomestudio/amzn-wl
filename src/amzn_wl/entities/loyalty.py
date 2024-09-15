import re
from dataclasses import dataclass
from decimal import Decimal

from dataclasses_json import dataclass_json
from selenium.webdriver.common.by import By

from .. import primitives
from .price import Price


@dataclass_json
@dataclass
class Loyalty:
    point: Decimal
    percentage: primitives.Percentage


def extract_loyalty(driver):
    elmts = driver.find_elements(
        By.ID, "Ebooks-desktop-KINDLE_ALC-prices-loyaltyPoints"
    )
    if not elmts:
        return

    elmts = elmts[0].find_elements(By.XPATH, ".//span/span")
    if not elmts:
        return

    m = re.match(r".*(\d+).*", elmts[0].text)
    point = Decimal(m.group(1)) if m else None

    percentage = primitives.Percentage.parse(elmts[1].text)

    return Loyalty(point, percentage) if point or percentage else None


def compute_effective_price(price: Price, loyalty: Loyalty) -> Price:
    if loyalty:
        effective_price = Price(price.value - loyalty.point, price.currency)
    else:
        effective_price = price
    return effective_price

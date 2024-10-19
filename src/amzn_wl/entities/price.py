from __future__ import annotations

import locale
import logging
import re
from dataclasses import dataclass
from decimal import Decimal

from dataclasses_json import dataclass_json

from ..utils import switch_locale

logger = logging.getLogger(__name__)


@dataclass_json
@dataclass
class Price:
    """Price object."""

    value: Decimal
    currency: str
    currency_code: str

    def __post_init__(self):
        self.value = Decimal(self.value)

    @classmethod
    def parse(cls, s: str) -> Price:
        value, currency, currency_code = _parse_value_and_currency(s)
        return cls(value, currency, currency_code)


def _detect_locale(s: str) -> str:
    if "￥" in s:
        loc = "ja_JP.UTF-8"
    else:
        loc = "en_US.UTF-8"
    return loc


def _parse_value_and_currency(s: str) -> tuple[str, str, str]:
    """Parse price value and currency from string."""
    logger.info("Parsing %s as price...", s)
    loc = _detect_locale(s)

    with switch_locale((locale.LC_MONETARY, locale.LC_NUMERIC), loc):
        d = locale.localeconv()
        symbol = d["currency_symbol"]
        decimal_point = d["mon_decimal_point"]
        thousands_sep = d["mon_thousands_sep"]

        re_str = r".*"
        if symbol in ("$",):
            re_str += f"\\{ symbol }"
        else:
            re_str += symbol
        re_str += r"\s*([\d" + thousands_sep + r"]+(" + decimal_point + r"\d+)?).*"

        value = re.match(re_str, s).group(1)
        value = locale.delocalize(value)

    currency_code = None
    if loc == "en_US.UTF-8" and symbol == "$":
        currency_code = "USD"
    elif loc == "ja_JP.UTF-8" and symbol == "￥":
        currency_code = "JPY"
    if not currency_code:
        raise RuntimeError(f"Currency cannot be determined: '{s}'")

    return value, symbol, currency_code

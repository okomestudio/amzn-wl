from dataclasses import dataclass

from dataclasses_json import dataclass_json

from .. import primitives
from . import prices


@dataclass_json
@dataclass
class PriceDrop:
    """Price drop info."""

    value: Decimal = None
    percentage: primitives.Percentage = None
    original_price: prices.Price = None

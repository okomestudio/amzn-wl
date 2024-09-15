from dataclasses import dataclass

from dataclasses_json import dataclass_json

from .. import primitives
from .price import Price


@dataclass_json
@dataclass
class PriceDrop:
    """Price drop info."""

    price: Price = None
    percentage: primitives.Percentage = None
    original_price: Price = None

from dataclasses import dataclass

from dataclasses_json import dataclass_json

from .loyalty import Loyalty
from .price import Price
from .price_drop import PriceDrop
from .product import Product
from .site import Site


@dataclass_json
@dataclass
class ProductPrice:
    product: Product
    site: Site
    price: Price
    price_drop: PriceDrop = None
    loyalty: Loyalty = None
    effective_price: Price = None

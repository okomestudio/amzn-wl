from dataclasses import dataclass

from dataclasses_json import dataclass_json

from .product import Product
from .product_price import ProductPrice
from .wishlist import Wishlist


@dataclass_json
@dataclass
class WishlistItem:
    """Wishlist item."""

    product: Product
    product_price: ProductPrice
    wishlist: Wishlist

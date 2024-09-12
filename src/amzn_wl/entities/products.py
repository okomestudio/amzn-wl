from dataclasses import dataclass

from dataclasses_json import dataclass_json

from .loyalties import Loyalty
from .prices import Price


@dataclass_json
@dataclass
class Product:
    url: str
    title: str
    byline: str
    stars: str
    price: Price
    loyalty: Loyalty = None

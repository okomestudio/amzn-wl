from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Product:
    title: str
    byline: str
    asin: str = None
    url: str = None
    stars: str = None

from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Product:
    url: str
    title: str
    byline: str
    stars: str

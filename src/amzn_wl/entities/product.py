import re
from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Product:
    asin: str
    title: str
    byline: str
    url: str = None
    stars: str = None


def extract_asin(url: str) -> str:
    """Extract ASIN from the URL."""
    m = re.match(r".+/dp/(\w+)/?$", url)
    asin = m.group(1) if m else None
    return asin

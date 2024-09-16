import re
import urllib.parse
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
    p = urllib.parse.urlparse(url)
    m = re.match(r".*/dp/(\w+)/?$", p.path)
    asin = m.group(1) if m else None
    return asin

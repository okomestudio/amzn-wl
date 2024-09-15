from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from dataclasses_json import dataclass_json

from .site import Site

logger = logging.getLogger(__name__)


@dataclass_json
@dataclass
class Wishlist:
    """Wishlist."""

    wishlist_id: str
    site: Site
    name: str
    url: str = None  # set automatically by the class

    def __post_init__(self):
        self.url = f"https://{ self.site.hostname }/hz/wishlist/ls/{ self.wishlist_id }"


def extract_wishlist_id(url: str) -> str | None:
    """Extract wishlist_id from the URL."""
    m = re.match(r".+/wishlist/ls/(\w+)/?$", url)
    wishlist_id = m.group(1) if m else None
    return wishlist_id

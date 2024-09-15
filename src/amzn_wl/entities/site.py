"""Amazon site objects."""

from __future__ import annotations

import logging
import urllib.parse
from dataclasses import dataclass

from dataclasses_json import dataclass_json

logger = logging.getLogger(__name__)


@dataclass_json
@dataclass
class Site:
    """Amazon site object."""

    hostname: str

    @classmethod
    def from_url(cls, url: str) -> Site:
        p = urllib.parse.urlparse(url)
        hostname = p.netloc
        return cls(hostname)

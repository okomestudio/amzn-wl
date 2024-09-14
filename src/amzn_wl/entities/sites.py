"""Amazon site objects."""

import logging
from dataclasses import dataclass

from dataclasses_json import dataclass_json

logger = logging.getLogger(__name__)


@dataclass_json
@dataclass
class Site:
    """Amazon site object."""

    hostname: str

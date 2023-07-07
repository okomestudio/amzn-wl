"""Primitives."""
import re
from dataclasses import dataclass
from typing import Union
from decimal import Decimal

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Percentage:
    """Precentage object."""

    value: Decimal
    unit: str = "%"

    @classmethod
    def parse(cls, s: str) -> Union["Percentage", None]:
        """Parse percentage from string."""
        m = re.match(r".*(\d+(.\d*)?)\s*%.*", s)
        return cls(Decimal(m.group(1))) if m else None

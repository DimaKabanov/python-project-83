from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Url:
    name: str
    created_at: datetime
    id: Optional[int] = None
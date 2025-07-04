from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Url:
    name: str
    created_at: datetime
    id: Optional[int] = None


@dataclass
class Check:
    url_id: int
    status_code: int
    h1: str
    title: str
    description: str
    created_at: datetime
    id: Optional[int] = None
from dataclasses import dataclass, field
from typing import Generic, TypeVar

ContentType = TypeVar("ContentType")
@dataclass
class SiteContent(Generic[ContentType]):
    url: str
    alias: str
    content: ContentType = field(default_factory=str)

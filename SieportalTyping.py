from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


@dataclass
class Product:
    article: str
    price: Optional[str] = None
    url: Optional[str] = None


@dataclass
class PageResult(Generic[T]):
    items: List[T]  # Более универсальное название (вместо products)
    total_count: int  # Более ясное название

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)  # Проще и правильнее

    def __len__(self) -> int:
        return len(self.items)


@dataclass
class Child:
    id: int
    link_node_id: int  # PEP8: snake_case для атрибутов
    title: str  # Было int, но title обычно str
    english_title: str
    has_child: bool
    url: str
    contains_product_variants: bool

"""Type definitions for Sieportal parser."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from collections.abc import Iterator

T = TypeVar("T")


@dataclass
class Product:
    """Product data class."""

    article: str
    price: str | None = None
    url: str | None = None


@dataclass
class PageResult(Generic[T]):
    """Paged result container."""

    items: list[T]  # Более универсальное название (вместо products)
    total_count: int  # Более ясное название

    def __iter__(self) -> Iterator[T]:
        """Iterate over items."""
        return iter(self.items)  # Проще и правильнее

    def __len__(self) -> int:
        """Return number of items."""
        return len(self.items)


@dataclass
class Child:
    """Child node data class."""

    id: int
    link_node_id: int  # PEP8: snake_case для атрибутов
    title: str  # Было int, но title обычно str
    english_title: str
    has_child: bool
    url: str
    contains_product_variants: bool

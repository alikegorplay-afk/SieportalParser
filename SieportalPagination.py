from math import ceil
from typing import Callable, Any, Optional, AsyncGenerator

from SieportalGetTreeApi import SieportalTreeAPI, PageResult


class Pagination:
    def __init__(
        self,
        id: str | int,
        API: SieportalTreeAPI,
        product_count: int = -1,
        func: Callable = SieportalTreeAPI.get_products,
    ):
        self.func = func
        self.max_page: int = ceil(product_count / 50) if product_count > 0 else 1
        self.page_now: int = 1
        self.product_count: int = product_count

        self._api = API
        self._id = id
        self.cache: dict[int, Any] = {}

    def __str__(self):
        return f"ID: {self._id} - [{self.page_now}/{self.max_page}]"

    @property
    def page(self) -> Any:
        if self.page_now - 1 in self.cache:  # Страницы начинаются с нуля
            return self.cache[self.page_now - 1]
        return None

    @classmethod
    async def create(
        cls,
        id: str | int,
        API: SieportalTreeAPI,
        func: Callable = SieportalTreeAPI.get_products,
    ) -> Optional["Pagination"]:
        result = await func(API, id)
        if result is None:
            return None

        total_product = result.total_count
        instance = cls(id, API, total_product)
        instance.cache[0] = result

        return instance

    async def next_page(self) -> Any:
        return await self.select_page(self.page_now + 1)

    async def back_page(self) -> Any:
        return await self.select_page(self.page_now - 1)

    async def select_page(self, page_num: int) -> Any:
        if not (1 <= page_num <= self.max_page):
            raise ValueError(
                f"Страница {page_num} не существует. Доступные страницы: от 1 до {self.max_page}"
            )

        # Если страница уже в кэше, возвращаем её
        if page_num - 1 in self.cache:
            self.page_now = page_num
            return self.cache[page_num - 1]

        # Если страницы нет в кэше, загружаем её
        result = await self.func(self._api, self._id, page_num - 1)
        if result:
            self.cache[page_num - 1] = result
            self.page_now = page_num

        return result

    async def fetch_all(self) -> AsyncGenerator[PageResult, None]:
        """Загружает все страницы и возращает гереатором"""
        for page_num in range(self.max_page):
            if page_num in self.cache:
                yield self.cache[page_num]
            else:
                yield await self.func(self._api, self._id, page_num)

    def get_cached_page(self, page_num: int) -> Optional[Any]:
        """Возвращает страницу из кэша, если она существует"""
        return self.cache.get(page_num)

    def clear_cache(self) -> None:
        """Очищает кэш, оставляя только текущую страницу"""
        current_page = self.page_now - 1
        if current_page in self.cache:
            current_data = self.cache[current_page]
            self.cache.clear()
            self.cache[current_page] = current_data
        else:
            self.cache.clear()

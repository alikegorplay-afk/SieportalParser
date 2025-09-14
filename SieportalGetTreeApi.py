import logging
import asyncio
import random

from typing import List, Dict, Optional
from dataclasses import dataclass

import aiohttp

from SieportalTyping import PageResult, Product, Child

@dataclass
class Config:
    sleep_time: int = 3
    proxy_list: List[str] = None
    client_data: Dict[str, str] = None
    
    def __post_init__(self):
        if self.proxy_list is None:
            self.proxy_list = ["http://xnuERA:whBHjy@77.73.133.196:8000"]
        if self.client_data is None:
            self.client_data = {
                'client_id': 'Siemens.SiePortal.UI',
                'client_secret': '7Ym0djaxvwbktNAnRABzu6ohqsxtIfpJuZwsWBXAydT79cCRvRAMfv1OWfKjdy0B',
                'grant_type': 'client_credentials',
            }

class SieportalAPI:
    TOKEN_URL = "https://auth.sieportal.siemens.com/connect/token"
    def __init__(self, session: aiohttp.ClientSession, language: str, region_id: str, *, max_try: int = 3, config: Config = Config()):
        self.max_try = max_try
        self.config = config
        self._session = session
        self.language = language
        self.region = region_id

        self._token = None
    
    async def fetch(self, method: str, url: str, *args, **kwargs) -> Dict:
        for try_num in range(1, self.max_try + 1):

            headers = kwargs.get('headers', {})
            headers['authorization'] = self._token or await self._get_token()
            kwargs['headers'] = headers

            try:
                async with self._session.request(method, url, *args, **kwargs) as response:
                    response.raise_for_status()
                    logging.debug(f"Status 200 для - {url}")
                    return await response.json()
            except aiohttp.ClientResponseError as error:
                if error.status == 401:
                    logging.info("Устаревший/Нерабочий токен обновляем...")
                    async with self._session.post(self.TOKEN_URL, data=self.config.client_data) as response:
                        response.raise_for_status()
                        self._token = await self._get_token()
                    await asyncio.sleep(self.config.sleep_time * try_num) 
                    continue
            
                elif error.status == 403:
                    kwargs['proxy'] = random.choice(self.config.proxy_list)
                    logging.warning(f"Недоступный сид! Использую прокси - {kwargs['proxy']}")
                    await asyncio.sleep(self.config.sleep_time * try_num)

                    continue

                elif 500 < error.status < 600:
                    logging.info(f"Проблема сервера ждём... - попытка {try_num} - {error.status}")
                    await asyncio.sleep(self.config.sleep_time)
                    continue

                elif error.status == 400:
                    logging.info("Неизвестный тип данных для ")
                    return None
                
                elif error.status == 500:
                    logging.info("Нету данных...")
                    return None

                else:
                    logging.error(f"Неиожиданный статус: {error.status}")
                    return None
            except Exception as error:
                logging.exception(f"НЕИЗВЕСТНАЯ ОШИБКА: {error}")

        logging.warning(f"Не смогли достучаться до сервера за {self.max_try} попыток")
        return None

    async def _get_token(self) -> str:
        """Получение токена авторизации"""
        while True:
            try:
                async with self._session.post(self.TOKEN_URL, data=self.config.client_data) as response:
                    response.raise_for_status()
                    token_data = await response.json()
                    return f"Bearer {token_data['access_token']}"
            except Exception as e:
                logging.error(f"Ошибка получения токена: {e}")

class SieportalTreeAPI(SieportalAPI):
    GET_TREE_CHILDREN = 'https://sieportal.siemens.com/api/mall/CatalogTreeApi/GetTreeChildren'
    GET_PRODUCTS = 'https://sieportal.siemens.com/api/mall/CatalogTreeApi/GetNodeProducts'
    GET_ACCESORIES = 'https://sieportal.siemens.com/api/mall/CatalogTreeApi/GetProductAccessories'
    GET_INFORMATION = 'https://sieportal.siemens.com/api/mall/CatalogTreeApi/GetNodeInformation'

    def __init__(self, session, language, region_id, *, max_try = 3):
        super().__init__(session, language, region_id, max_try=max_try)

    async def get_tree_children(self, id: int | str) -> Optional[PageResult[Child]]:
        params = {
            'ClassificationScheme': 'CatalogTree',
            'NodeId': id,
            'IsCatalogPage': 'true',
            'RegionId': self.region,
            'CountryCode': self.region,
            'Language': self.language,
        }
        response = (await self.fetch("GET", self.GET_TREE_CHILDREN, params = params))['catalogTreeChildNodes']
        if response is None:
            return None
        
        table = [Child(*data.values()) for data in response]
        return PageResult(table, len(table))

    async def get_tree_information(self, id: int | str) -> Optional[Dict[str, bool]]:
        params = {
            'NodeId': id,
            'RegionId': self.region,
            'TreeName': 'CatalogTree',
            'Language': self.language,
        }
        response = await self.fetch("GET", self.GET_INFORMATION, params=params)
        if response is None:
            return
        
        return {
            'info': response.get('containsProductInformation', False),
            'variants': response.get('containsProductVariants', False),
            'product': response.get('containsRelatedProducts', False)
        }

    async def get_products(self, id: int | str, page: int = 0):
        json_data = {
            'technicalSelectionFilters': [],
            'nodeId': id,
            'treeName': 'CatalogTree',
            'pageNumberIndex': page,
            'limit': 50,
            'checkStockAvailability': False,
            'keywordFilter': None,
            'regionId': self.region,
            'language': self.language,
            'sortCategory': 'Newest',
        }

        response = await self.fetch("POST", self.GET_PRODUCTS, json = json_data)
        if response is None:
            return
        product_count = response['productCount']

        return PageResult([Product(article=product['articleNumber'], url=product.get('url')) for product in response.get('products', [])], product_count)
    
    async def get_accesories(self, id: int, page: int = 0):
        json_data = {
            'regionId': self.region,
            'language': self.language,
            'nodeId': id,
            'treeName': 'CatalogTree',
            'pageNumberIndex': page,
            'limit': 50,
            'technicalSelectionFilters': [],
        }
        
        response = await self.fetch("POST", self.GET_ACCESORIES, json = json_data)
        if response is None:
            return
        product_count = response['productCount']
        result = PageResult([Product(article=product['articleNumber'], url=product.get('url')) for product in response.get('products', [])], product_count)

        return result
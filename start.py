from __future__ import annotations

import argparse
import asyncio
import logging
import os

import aiocsv
import aiofiles
import aiohttp

from SieportalGetTreeApi import SieportalTreeAPI
from SieportalPagination import Pagination


def parse_args():
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(description="Sieportal data extraction tool")

    parser.add_argument(
        "--input", "-i", default="files/key.csv", help="Input CSV file with node IDs",
    )

    parser.add_argument(
        "--language", "-l", default="en", help="Language code (e.g., en, de, fr)",
    )

    parser.add_argument(
        "--region", "-r", default="kr", help="Region code (e.g., kr, us, de)",
    )

    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=0.1,
        help="Delay between requests in seconds",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    return parser.parse_args()


async def read(fp: str):
    async with aiofiles.open(fp, newline="") as file:
        reader = aiocsv.AsyncReader(file)

        async for line in reader:
            yield line[0]


async def main():
    args = parse_args()
    logging.basicConfig(
        filename=f"logs\\log-{args.language}-{args.region}.log",
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    output_dir = os.path.dirname(f"files\\{args.language}-{args.region}.csv")
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    async with aiofiles.open(
        f"files\\{args.language}-{args.region}.csv", "a", newline="",
    ) as file:
        writer = aiocsv.AsyncWriter(file)
        async with aiohttp.ClientSession() as session:
            # Аномалия 10000083, 10000800
            sie = SieportalTreeAPI(session, args.language, args.region)

            async for node_id in read(args.input):
                data = await sie.get_tree_information(node_id)
                if data is None:
                    continue

                logging.info(
                    f"Найдены продукты: {data['variants']}, аксесуары {data['product']} - [{node_id}]",
                )
                if data["variants"]:
                    pagination = await Pagination.create(
                        node_id, sie, SieportalTreeAPI.get_products,
                    )
                    if pagination is None:
                        continue
                    async for page in pagination.fetch_all():
                        if page is None:
                            continue
                        await writer.writerows(
                            [[x.article, x.url] for x in page.items],
                        )

                if data["product"]:
                    pagination = await Pagination.create(
                        node_id, sie, SieportalTreeAPI.get_accesories,
                    )
                    if pagination is None:
                        continue
                    async for page in pagination.fetch_all():
                        if page is None:
                            continue
                        await writer.writerows(
                            [[x.article, x.url] for x in page.items],
                        )


asyncio.run(main())

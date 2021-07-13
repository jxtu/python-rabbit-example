#! /usr/bin/env python

from typing import List, Dict, Union, Iterator
import time
import click
import logging
from es_service.index import ESIndex
from utils import parse_cord_meta

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


class IndexLoader:
    """
    load document index to Elasticsearch
    """

    def __init__(self, index, docs):

        self.index_name = index
        self.docs: Union[Iterator[Dict], List[Dict]] = docs

    def load(self) -> None:
        st = time.time()
        logger.info(f"Building index ...")
        ESIndex(self.index_name, self.docs)
        logger.info(
            f"=== Built {self.index_name} in {round(time.time() - st, 2)} seconds ==="
        )

    @classmethod
    def from_csv(cls, index_name: str, data_dir, csv_file: str) -> "IndexLoader":
        try:
            return IndexLoader(index_name, parse_cord_meta(data_dir, csv_file))
        except FileNotFoundError:
            raise Exception(f"Cannot find {csv_file}!")


@click.command()
@click.argument("data_dir", type=click.Path(exists=True))
@click.argument("csv_path", type=click.Path(exists=True))
@click.argument("index_name", type=click.STRING, default="cord_askme_idx")
def main(data_dir: str, csv_path: str, index_name: str = "cord_askme_idx"):
    idx_loader = IndexLoader.from_csv(index_name, data_dir, csv_path)
    idx_loader.load()


if __name__ == "__main__":
    main()

#! /usr/bin/env python
import json
from typing import List, Dict, Union, Iterator
import time
import click
import logging
from es_service.index import ESIndex
# from utils import parse_cord_meta

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
    def from_json(cls, index_name: str, json_file: str):
        with open(json_file, "r") as f:
            json_dict = json.loads(f.read())
        docs = json_dict["body"]["documents"]
        return IndexLoader(index_name, docs)


@click.command()
@click.argument("json_path", type=click.Path(exists=True))
@click.argument("index_name", type=click.STRING, default="test_rabbitmq_idx")
def main(json_path: str, index_name: str = "test_rabbitmq_idx"):
    idx_loader = IndexLoader.from_json(index_name, json_path)
    idx_loader.load()


if __name__ == "__main__":
    main()

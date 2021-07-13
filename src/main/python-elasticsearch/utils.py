import os
from typing import Generator, Dict, Union
from pathlib import Path
import json

import pandas as pd  # type: ignore


def _get_publish_year(date: str) -> str:
    """
    :param date: format of "yyyy-mm-dd"
    :return:
    """
    return date.split("-")[0]


def get_body_from_pdf_json(json_file: Union[os.PathLike, str]):
    try:
        pdf_json = json.load(open(json_file, "r"))
    except FileNotFoundError:
        return ""
    body_text_lst = pdf_json.get("body_text", [])
    body_text = " ".join([block.get("text", "") for block in body_text_lst])
    return body_text


def parse_cord_meta(data_dir: str, csv_file: str) -> Generator[Dict, None, None]:
    csv_df = pd.read_csv(csv_file)
    csv_df = csv_df.astype({"pubmed_id": "int32"}).astype({"pubmed_id": "str"})
    for i, item in enumerate(csv_df.iloc):
        item = item.fillna("")
        item_dict = item.to_dict()
        item_dict["year"] = _get_publish_year(item_dict.get("publish_time", ""))
        if item_dict["pdf_json_files"]:
            item_dict["body"] = get_body_from_pdf_json(
                Path(data_dir).joinpath(item_dict["pdf_json_files"])
            )
        yield item_dict


if __name__ == "__main__":
    a = next(parse_cord_meta("raw_data/cord19/", "raw_data/cord19/metadata_subset.csv"))
    print(a)

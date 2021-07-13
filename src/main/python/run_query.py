#! /usr/bin/env python
from typing import Dict

from elasticsearch_dsl import Search  # type: ignore
from elasticsearch_dsl.query import MultiMatch, Ids  # type: ignore


def search(
    query: str, index: str = "docker_test_index", top_k: int = 5
) -> Dict[int, Dict[str, str]]:
    q_multi = MultiMatch(query=query, fields=["title", "abstract"])

    s = Search(using="default", index=index).query(q_multi)[
        :top_k
    ]  # initialize a query and return top k results
    response = s.execute()
    res_keys = ("Id", "Score", "PMC", "Title")
    result = {}
    for i, hit in enumerate(response):
        content = (hit.meta.id, round(hit.meta.score, 2), hit.pmc, hit.title)
        result[i] = {k: v for k, v in zip(res_keys, content)}
    return result

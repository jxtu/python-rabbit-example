#! /usr/bin/env python
from typing import Dict, List

from elasticsearch_dsl import Search  # type: ignore
from elasticsearch_dsl.query import MultiMatch, Ids, Query  # type: ignore
from elasticsearch_dsl.connections import connections  # type: ignore


def search(index: str, query: Query) -> List[Dict]:
    s = Search(using="default", index=index).query(query)[
        :5
        ]  # initialize a query and return top five results
    response = s.execute()
    docs = [hit.to_dict() for hit in response]
    print(f"retrieved {len(docs)} documents from Elasticsearch...")
    return docs


def run_query(msg_body_dict: Dict, index: str) -> Dict:
    query = " ".join(msg_body_dict["query"]["terms"])
    q_multi = MultiMatch(
        query=query, fields=["title_str", "abstract_str"]
    )
    docs = search(index, q_multi)
    for i, doc in enumerate(docs):
        doc.pop("title_str", None)
        doc.pop("abstract_str", None)
    msg_body_dict["documents"] = docs
    return msg_body_dict


if __name__ == '__main__':
    connections.create_connection(
        hosts=["localhost:9200"], timeout=100, alias="default"
    )
    qd = {
        "core": "cord_2020_06_12",
        "query": {
            "question": "How do fluid flow and transport affect the human environment?",
            "query": "body:fluid AND body:flow AND body:transport AND body:affect AND body:human AND body:environment",
            "terms": [
                "human",
                "expiratory",
                "droplets-A",
                "modeling",
            ],
            "count": 1000
        }
    }
    run_query(qd, "test_rabbitmq_idx")

from elasticsearch_dsl import Search  # type: ignore
from elasticsearch_dsl.query import Match, MatchAll, Ids, Query, MultiMatch, Nested  # type: ignore
from elasticsearch_dsl.connections import connections  # type: ignore


def search(index: str, query: Query) -> None:
    s = Search(using="default", index=index).query(query)[
        :5
    ]  # initialize a query and return top five results
    response = s.execute()
    for hit in response:
        print(
            hit.meta.id, hit.meta.score, hit.pmc, hit.title_str, sep="\t"
        )  # print the document id that is assigned by ES index, score and title


if __name__ == "__main__":
    connections.create_connection(
        hosts=["localhost:9200"], timeout=100, alias="default"
    )

    q_match_all = MatchAll()  # a query that matches all documents
    q_basic = Match(
        title={"query": "clinical gene cells"}
    )  # a query that matches "clinical" in the title field of the index, using BM25 as default
    q_multi = MultiMatch(
        query="hand-hygiene, and personal protective equipment", fields=["title_str", "abstract_str"]
    )
    q_match_ids = Ids(values=[0, 1, 2, 3, 4])  # a query that matches ids

    search(
        "test_rabbitmq_idx", q_multi
    )  # search, change the query object to see different results

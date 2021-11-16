from typing import Iterator, Dict, Union, Sequence, Generator

from elasticsearch_dsl import Index  # type: ignore

from elasticsearch_dsl.connections import connections  # type: ignore
from elasticsearch.helpers import bulk

from es_service.doc_template import BaseDoc


class ESIndex(object):
    def __init__(
        self, index_name: str, docs: Union[Iterator[Dict], Sequence[Dict]],
    ):
        """
        ES index structure
        :param index_name: the name of your index
        :param docs: wapo docs to be loaded
        """
        # set an elasticsearch connection to your localhost
        connections.create_connection(hosts=["localhost:9200"], timeout=100, alias="default")
        self.index = index_name
        es_index = Index(self.index)  # initialize the index

        # delete existing index that has the same name
        if es_index.exists():
            es_index.delete()

        es_index.document(BaseDoc)  # link document mapping to the index
        es_index.create()  # create the index
        if docs is not None:
            self.load(docs)

    @staticmethod
    def _populate_doc(
        docs: Union[Iterator[Dict], Sequence[Dict]]
    ) -> Generator[BaseDoc, None, None]:
        """
        populate the BaseDoc
        :param docs: wapo docs
        :return:
        """
        for i, doc in enumerate(docs):
            es_doc = BaseDoc(_id=i)
            es_doc.id = doc["id"]
            es_doc.pmid = doc.get("pmid")
            es_doc.pmc = doc.get("pmc")
            es_doc.doi = doc.get("doi")
            es_doc.year = doc.get("year")

            es_doc.title = doc.get("title")
            es_doc.articleAbstract = doc.get("articleAbstract")
            es_doc.title_str = doc.get("title")["text"]
            es_doc.abstract_str = doc.get("articleAbstract")["text"]

            es_doc.path = doc.get("path")
            es_doc.url = doc.get("url")
            es_doc.score = doc.get("score")
            es_doc.scores = doc.get("scores", {})

            yield es_doc

    def load(self, docs: Union[Iterator[Dict], Sequence[Dict]]):
        # bulk insertion
        bulk(
            connections.get_connection(),
            (
                d.to_dict(
                    include_meta=True, skip_empty=False
                )  # serialize the BaseDoc instance (include meta information and not skip empty documents)
                for d in self._populate_doc(docs)
            ),
        )

from elasticsearch_dsl import (  # type: ignore
    Document,
    Text,
    Keyword,
    DenseVector,
    Date,
    token_filter,
    analyzer,
)


class BaseDoc(Document):
    """
    CORD-19 document mapping structure
    """

    doc_id = Keyword()
    pmid = Keyword()
    pmc = Keyword()
    doi = Keyword()
    year = Date(format="strict_year")

    title = Text()
    abstract = Text()
    body = Text()

    path = Keyword()
    url = Keyword()
    license = Keyword()

    def save(self, *args, **kwargs):
        """
        save an instance of this document mapping in the index
        this function is not called because we are doing bulk insertion to the index in the index.py
        """
        return super(BaseDoc, self).save(*args, **kwargs)


if __name__ == "__main__":
    pass

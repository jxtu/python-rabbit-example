from elasticsearch_dsl import (  # type: ignore
    Document,
    Text,
    Keyword,
    DenseVector,
    Date,
    token_filter,
    Float,
    InnerDoc,
    Nested,
    analyzer,
)


class BaseDoc(Document):
    """
    CORD-19 document mapping structure
    """

    id = Keyword()
    pmid = Keyword()
    pmc = Keyword()
    doi = Keyword()
    year = Date(format="strict_year")
    title_str = Text()
    abstract_str = Text()

    title = Nested()
    articleAbstract = Nested()

    path = Keyword()
    url = Keyword()
    score = Float()
    scores = Nested()

    def save(self, *args, **kwargs):
        """
        save an instance of this document mapping in the index
        this function is not called because we are doing bulk insertion to the index in the index.py
        """
        return super(BaseDoc, self).save(*args, **kwargs)


if __name__ == "__main__":
    pass

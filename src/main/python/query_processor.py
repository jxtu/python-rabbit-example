#! src/bin/python
from typing import List
import click


class SimpleQueryProcessor(object):
    def __init__(self, stopwords_path: str) -> None:
        self.stopwords = set(open(stopwords_path, "r").read().strip().split("\n"))
        covid_terms = "coronavirus covid sars-cov-2"
        self.covid_mapping = {k: covid_terms for k in covid_terms.split()}

    def transform(self, query_question: str) -> str:
        query_question = query_question.strip()
        if query_question.endswith("?"):
            query_question = query_question[:-1]
        tokens = query_question.lower().split()
        terms = self.remove_stopwords(tokens)
        query = " ".join([self.expand(term) for term in terms])
        return query

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        return [tok for tok in tokens if tok not in self.stopwords]

    def expand(self, term: str) -> str:
        return self.covid_mapping.get(term, term)

    def __call__(self, query_question: str) -> str:
        return self.transform(query_question)


@click.command()
@click.argument("question", type=click.STRING)
@click.option(
    "--stopwords_path", "-s", default="stopwords.txt", type=click.Path(exists=True)
)
def main(question: str, stopwords_path):
    sqp = SimpleQueryProcessor(stopwords_path)
    print(f"original: {question}")
    print(f"new: {sqp(question)}")


if __name__ == "__main__":
    main()

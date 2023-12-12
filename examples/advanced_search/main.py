""" This example shows how to use the advanced search feature of PubMed. """

from pymed import PubMed
from pymed.article import Book

# Create a PubMed object that GraphQL can use to query
# Note that the parameters are not required but kindly requested by PubMed Central
# https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
pubmed = PubMed(tool="MyTool", email="my@email.address")

# Create a GraphQL query in plain text
QUERY = '(("2018/05/01"[Date - Create] : "3000"[Date - Create])) AND (Xiaoying Xian[Author] OR diabetes)'

# Execute the query against the API
results = pubmed.query(QUERY, skip="book", start_year=2018)

# Loop over the retrieved articles
for article in results:
    # Extract and format information from the article
    article_id = article.pubmed_id
    title = article.title

    if isinstance(article, Book):
        continue

    if article.keywords:
        keywords = '", "'.join(
            [keyword for keyword in article.keywords if keyword is not None]
        )

        publication_date = article.publication_date
        abstract = article.abstract

        # Show information about the article
        print(
            f'{article_id} - {publication_date} - {title}\nKeywords: "{keywords}"\n{abstract}\n'
        )

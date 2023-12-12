""" This script shows how to use pymed to query the PubMed API. """

from pymed import PubMed


# Create a PubMed object that GraphQL can use to query
# Note that the parameters are not required but kindly requested by PubMed Central
# https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
pubmed = PubMed(tool="MyTool", email="my@email.address")

# Create a GraphQL query in plain text
QUERY = "occupational health[Title]"


# Execute the query against the API
results = pubmed.query(QUERY, max_results=500)

# Loop over the retrieved articles
for article in results:
    # Print the type of object we've found (can be either PubMedBookArticle or PubMedArticle)
    print(type(article))

    # Print a JSON representation of the object
    print(article.to_json())

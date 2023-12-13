# Example - Simple search
This example shows how to perform a simple search on the PubMed database and retrieve information about the relevant articles.


```python
from pymed import PubMed


# Create a PubMed object that GraphQL can use to query
# Note that the parameters are not required but kindly requested by PubMed Central
# https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
pubmed = PubMed(tool="MyTool", email="my@email.address")

# Create a GraphQL query in plain text
QUERY = "occupational health[Title]"

# Execute the query against the API
results = pubmed.query(QUERY, max_results=250)

# Loop over the retrieved articles and print three of them
for article in list(results)[:3]:
    # Print the type of object we've found (can be either PubMedBookArticle or PubMedArticle)
    print(type(article))

    # Print a JSON representation of the object
    print(article.to_json())

```

    <class 'pymed.article.Paper'>
    {
        "conclusions": "",
        "copyrights": "\u00a9 The Author(s) 2023. Published by Oxford University Press on behalf of the Society of Occupational Medicine.",
        "journal": "Occupational medicine (Oxford, England)",
        "keywords": [],
        "methods": "",
        "results": "Fifteen focus groups were conducted with OSH/HR professionals (n\u2005=\u200560) from various occupational settings. Three levels of organizational preparedness were identified: 'early awareness and preparation'; 'unaware and not ready' and 'aware, but not ready'. Most organizations were aware of the COVID-19 severity, but not fully prepared for the pandemic, especially stand-alone enterprises that may not have sufficient resources to cope with an unanticipated crisis. The experiences shared by OSH professionals illustrate their agility in applying risk management and control skills to unanticipated public/occupational health crises that arise.",
        "xml": "<Element 'PubmedArticle' at 0x114b6f470>"
    }
    <class 'pymed.article.Paper'>
    {
        "conclusions": "",
        "copyrights": "",
        "journal": "Frontiers in public health",
        "keywords": [
            "burnout",
            "healthcare",
            "healthcare professional (HCP)",
            "occupational health",
            "organizational culture",
            "safety culture",
            "staff wellbeing",
            "wellbeing"
        ],
        "methods": "",
        "results": "",
        "xml": "<Element 'PubmedArticle' at 0x114b78040>"
    }
    <class 'pymed.article.Paper'>
    {
        "conclusions": "",
        "copyrights": "",
        "journal": "Problemy sotsial'noi gigieny, zdravookhraneniia i istorii meditsiny",
        "keywords": [
            "SciVal",
            "collaboration",
            "field weighted citation impact",
            "keywords",
            "medical science",
            "publication activity Scopus",
            "ranking",
            "relevance",
            "scholarly output",
            "scientometrics",
            "subject area"
        ],
        "methods": "",
        "results": "",
        "xml": "<Element 'PubmedArticle' at 0x114b7b3d0>"
    }


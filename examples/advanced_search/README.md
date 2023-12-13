# Example - Advanced search
This example shows how to perform an advanced search on the PubMed database and retrieve information about the relevant articles.

You can use [PubMed query builder](https://www.ncbi.nlm.nih.gov/pubmed/advanced) for creating the query syntax.


```python
from pymed import PubMed
from pymed.article import Book

# Create a PubMed object that GraphQL can use to query
# Note that the parameters are not required but kindly requested by PubMed Central
# https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
pubmed = PubMed(tool="MyTool", email="my@email.address")

# Create a GraphQL query in plain text (You can also used MeSH terms here)
QUERY = 'Xiaoying Xian[Author] AND Diabetes[MeSH Terms]'

# Execute the query against the API starting from the year 2018, and skip articles from books. 
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

# Save the PMIDs to a file
with open("pmids.txt", "w") as file:
    for article in results:
        file.write(article.pubmed_id + "\n")
```

    29969779 - 2018-07-04 - A Novel Mutation of SLC19A2 in a Chinese Zhuang Ethnic Family with Thiamine-Responsive Megaloblastic Anemia.
    Keywords: "Diabetes mellitus", "Megaloblastic anemia", "SLC19A2 mutation", "Trma", "Visual impairment"
    Thiamine-responsive megaloblastic anemia syndrome is a rare autosomal recessive disorder resulting from mutations in SLC19A2, and is mainly characterized by megaloblastic anemia, diabetes, and progressive sensorineural hearing loss.
    We study a Chinese Zhuang ethnicity family with thiamine-responsive megaloblastic anemia. The proband of the study presented with anemia and diabetes, similar to his late brother, as well as visual impairment. All clinical manifestations were corrected with thiamine (30 mg/d) supplementation for 1-3 months, except for visual impairment, which was irreversible. The presence of mutations in all exons and the flanking sequences of the SLC19A2 gene were analyzed in this family based on the proband's and his brother's clinical data. Computer analysis and prediction of the protein conformation of mutant THTR-1. The relative concentration of thiamine pyrophosphate in the proband's whole blood before and after initiation of thiamine supplement was measured by high performance liquid chromatography (HPLC).
    Gene sequencing showed a homozygous mutation in exon 6 of the SLC19A2 gene (c.1409insT) in the proband. His parents and sister were diagnosed as heterozygous carriers of the c.1409insT mutation. Computer simulation showed that the mutations caused a change in protein conformation. HPLC results suggested that the relative concentration of thiamine pyrophosphate in the proband's whole blood after thiamine supplement was significantly different (P=0.016) from that at baseline.
    This novel homozygous mutation (c.1409insT) caused the onset of thiamine-responsive megaloblastic anemia in the proband.
    
    27771724 - 2016-10-25 - Association between Recreational Physical Activity and the Risk of Upper Urinary Calculi.
    Keywords: "Physical activity", "Upper urinary calculi", "Water intake"
    Upper urinary calculi (UUC) is considered to be a comprehensive disease associated with many risk factors, but the role of physical activity (PA) is undefined. Here, we conducted a cross-sectional study to investigate this relationship in Asian populations.
    Patients diagnosed with UUC were the subjects of study and those who participated in a health examination in local medical center were included as controls. Information was collected through the same standard questionnaire. A metabolic equivalent score (METs) was measured for each kind of activity. OR of UUC in categories of PA were determined by logistic regression.
    A total of 1,782 controls and 1,517 cases were enrolled. People who took higher PA (5-9.9, 10-19.9, 20-29.9 and >30 METs/wk) weekly were associated with lower risks of UUC than those took lower PA (<4.9 METs/wk) after adjusting for age, ethnicity, body mass index, systolic blood pressure, water intake, history of gout, history of diabetes mellitus, history of supplemental calcium use and history of hypertension (adjusted OR 0.11, 0.32, 0.24, 0.34; 95% CI 0.08-0.15, 0.23-0.43, 0.15-0.40, 0.22-0.53, respectively; p value <0.001).
    In our cross-sectional study, PA was associated with UUC.
    


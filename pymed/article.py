""" This module contains the Article and Book classes, which is used to represent a PubMed articles. """

import json
import datetime

from xml.etree.ElementTree import Element
from typing import Dict, List, Optional

from .utils import get_content


class PubMedBaseArticle:
    """Base class for PubMed articles."""

    __slots__ = ("pubmed_id", "title", "abstract", "publication_date", "authors", "doi")

    def __init__(self, xml_element: Optional[Element] = None, **kwargs: dict) -> None:
        # If an XML element is provided, use it for initialization
        if xml_element is not None:
            self.initialize_from_xml(xml_element=xml_element)

        # If no XML element was provided, try to parse the input parameters
        else:
            for field in self.__slots__:
                self.__setattr__(field, kwargs.get(field, None))

    def initialize_from_xml(self, xml_element: Element) -> None:
        """
        Initializes the article object by parsing an XML element.

        Args:
            xml_element (Element): The XML element to parse.

        Returns:
            None
        """
        raise NotImplementedError

    def to_dict(self) -> dict:
        """Helper method to convert the parsed information to a Python dict.

        Returns:
            dict: A dictionary containing the parsed information.
        """

        return {key: self.__getattribute__(key) for key in self.__slots__}

    def to_json(self) -> str:
        """Converts the object to a JSON string representation.

        Returns:
            str: The JSON string representation of the object.
        """
        return json.dumps(
            {
                key: (
                    value
                    if not isinstance(value, (datetime.date, Element))
                    else str(value)
                )
                for key, value in self.to_dict().items()
            },
            sort_keys=True,
            indent=4,
        )


class Paper(PubMedBaseArticle):
    """Data class that contains a PubMed article."""

    __slots__ = (
        "keywords",
        "journal",
        "methods",
        "conclusions",
        "results",
        "copyrights",
        "xml",
    )

    def extract_pubmed_id(self, xml_element: Element) -> str:
        """Extracts the PubMed ID from the XML element.

        Args:
            xml_element (Element): XML element to extract the PubMed ID from.

        Returns:
            str: PubMed ID of the article.
        """
        path = "MedlineCitation/PMID"
        return get_content(element=xml_element, path=path)

    def extract_title(self, xml_element: Element) -> str:
        """Extracts the PubMed title from the XML element.

        Args:
            xml_element (Element): XML element to extract the title from.

        Returns:
            str: Title of the article.
        """
        path = ".//ArticleTitle"
        return get_content(element=xml_element, path=path)

    def extract_keywords(self, xml_element: Element) -> List[str | None]:
        """Extracts the Keywords from the XML element of a PubMed Article.

        Args:
            xml_element (Element): XML element to extract the keywords from.

        Returns:
            str: Keywords of the article.
        """
        path = ".//Keyword"
        return [
            keyword.text for keyword in xml_element.findall(path) if keyword is not None
        ]

    def extract_journal(self, xml_element: Element) -> str:
        """Extracts the journal title from the XML element of a PubMed Article.

        Args:
            xml_element (Element): XML element to extract the journal title from.

        Returns:
            str: Journal of the article.
        """
        path = ".//Journal/Title"
        return get_content(element=xml_element, path=path)

    def extract_abstract(self, xml_element: Element) -> str:
        """Extracts the abstract from the XML element of a PubMed Article.

        Args:
            xml_element (Element): XML element to extract the abstract from.

        Returns:
            str: Abstract of the article.
        """
        path = ".//AbstractText"
        return get_content(element=xml_element, path=path)

    def extract_conclusions(self, xml_element: Element) -> str:
        """Extracts the conclusions from the XML element of a PubMed Article.

        Args:
            xml_element (Element): XML element to extract the conclusions from.

        Returns:
            str: Conclusions of the article.
        """
        path = ".//AbstractText[@Label='CONCLUSION']"
        return get_content(element=xml_element, path=path)

    def extract_methods(self, xml_element: Element) -> str:
        """Extracts the methods from the XML element of a PubMed Article.

        Args:
            xml_element (Element): XML element to extract the methods from.

        Returns:
            str: Methods of the article.
        """
        path = ".//AbstractText[@Label='METHOD']"
        return get_content(element=xml_element, path=path)

    def extract_results(self, xml_element: Element) -> str:
        """Extracts the results from the XML element of a PubMed Article.

        Args:
            xml_element (Element): XML element to extract the results from.

        Returns:
            str: Results of the article.
        """
        path = ".//AbstractText[@Label='RESULTS']"
        return get_content(element=xml_element, path=path)

    def extract_copyrights(self, xml_element: Element) -> str:
        """Extracts the copyrights from the XML element of a PubMed Article.

        Args:
            xml_element (Element): XML element to extract the copyrights from.

        Returns:
            str: Copyrights of the article.
        """
        path = ".//CopyrightInformation"
        return get_content(element=xml_element, path=path)

    def extract_doi(self, xml_element: Element) -> str:
        """Extracts the DOI from the XML element of a PubMed Article.

        Args:
            xml_element (Element): XML element to extract the DOI from.

        Returns:
            str: DOI of the article.
        """
        path = ".//ArticleId[@IdType='doi']"
        return get_content(element=xml_element, path=path)

    def extract_publication_date(self, xml_element: Element) -> datetime.date | None:
        """
        Extracts the publication date from the given XML element.

        Args:
            xml_element (Element): The XML element containing the publication date.

        Returns:
            datetime.date | None: The extracted publication date as a `datetime.date` object,
            or `None` if the publication date cannot be parsed.
        """
        try:
            # Get the publication elements
            publication_date = xml_element.find(".//PubMedPubDate[@PubStatus='pubmed']")
            publication_year = int(get_content(publication_date, ".//Year", ""))
            publication_month = int(get_content(publication_date, ".//Month", ""))
            publication_day = int(get_content(publication_date, ".//Day", ""))

            # Construct a datetime object from the info
            return datetime.date(
                year=publication_year, month=publication_month, day=publication_day
            )

        except ValueError as e:
            print(e)
            return None

    def extract_authors(self, xml_element: Element) -> List[Dict[str, str]]:
        """
        Extracts author information from an XML element.

        Args:
            xml_element (Element): The XML element containing author information.

        Returns:
            list: A list of dictionaries, where each dictionary represents an author and contains the following keys:
                - "lastname": The last name of the author.
                - "firstname": The first name of the author.
                - "initials": The initials of the author.
                - "affiliation": The affiliation of the author.
        """
        return [
            {
                "lastname": get_content(author, ".//LastName", ""),
                "firstname": get_content(author, ".//ForeName", ""),
                "initials": get_content(author, ".//Initials", ""),
                "affiliation": get_content(
                    author, ".//AffiliationInfo/Affiliation", ""
                ),
            }
            for author in xml_element.findall(".//Author")
        ]

    def initialize_from_xml(self, xml_element: Element) -> None:
        """
        Initializes the article object by parsing an XML element.

        Args:
            xml_element (Element): The XML element to parse.

        Returns:
            None
        """
        # Parse the different fields of the article
        self.pubmed_id = self.extract_pubmed_id(xml_element)
        self.title = self.extract_title(xml_element)
        self.keywords = self.extract_keywords(xml_element)
        self.journal = self.extract_journal(xml_element)
        self.abstract = self.extract_abstract(xml_element)
        self.conclusions = self.extract_conclusions(xml_element)
        self.methods = self.extract_methods(xml_element)
        self.results = self.extract_results(xml_element)
        self.copyrights = self.extract_copyrights(xml_element)
        self.doi = self.extract_doi(xml_element)
        self.publication_date = self.extract_publication_date(xml_element)
        self.authors = self.extract_authors(xml_element)
        self.xml = xml_element


class Book(PubMedBaseArticle):
    """Data class that contains a PubMed article."""

    __slots__ = (
        "copyrights",
        "isbn",
        "language",
        "publication_type",
        "sections",
        "publisher",
        "publisher_location",
    )

    def extract_pubmed_id(self, xml_element: Element) -> str:
        """
        Extracts the PubMed ID from the XML element.

        Args:
            xml_element (Element): The XML element to extract the PubMed ID from.

        Returns:
            str: The PubMed ID.
        """
        path = ".//ArticleId[@IdType='pubmed']"
        return get_content(element=xml_element, path=path)

    def extract_title(self, xml_element: Element) -> str:
        """
        Extracts the title from the XML element.

        Args:
            xml_element (Element): The XML element to extract the title from.

        Returns:
            str: The title.
        """
        path = ".//BookTitle"
        return get_content(element=xml_element, path=path)

    def extract_abstract(self, xml_element: Element) -> str:
        """
        Extracts the abstract from the XML element.

        Args:
            xml_element (Element): The XML element to extract the abstract from.

        Returns:
            str: The abstract.
        """
        path = ".//AbstractText"
        return get_content(element=xml_element, path=path)

    def extract_copyrights(self, xml_element: Element) -> str:
        """
        Extracts the copyrights from the XML element.

        Args:
            xml_element (Element): The XML element to extract the copyrights from.

        Returns:
            str: The copyrights.
        """
        path = ".//CopyrightInformation"
        return get_content(element=xml_element, path=path)

    def extract_doi(self, xml_element: Element) -> str:
        """
        Extracts the DOI from the XML element.

        Args:
            xml_element (Element): The XML element to extract the DOI from.

        Returns:
            str: The DOI.
        """
        path = ".//ArticleId[@IdType='doi']"
        return get_content(element=xml_element, path=path)

    def extract_isbn(self, xml_element: Element) -> str:
        """
        Extracts the ISBN from the XML element.

        Args:
            xml_element (Element): The XML element to extract the ISBN from.

        Returns:
            str: The ISBN.
        """
        path = ".//Isbn"
        return get_content(element=xml_element, path=path)

    def extract_language(self, xml_element: Element) -> str:
        """
        Extracts the language from the XML element.

        Args:
            xml_element (Element): The XML element to extract the language from.

        Returns:
            str: The language.
        """
        path = ".//Language"
        return get_content(element=xml_element, path=path)

    def extract_publication_type(self, xml_element: Element) -> str:
        """
        Extracts the publication type from the XML element.

        Args:
            xml_element (Element): The XML element to extract the publication type from.

        Returns:
            str: The publication type.
        """
        path = ".//PublicationType"
        return get_content(element=xml_element, path=path)

    def extract_publication_date(self, xml_element: Element) -> str:
        """
        Extracts the publication date from the XML element.

        Args:
            xml_element (Element): The XML element to extract the publication date from.

        Returns:
            str: The publication date.
        """
        path = ".//PubDate/Year"
        return get_content(element=xml_element, path=path)

    def extract_publisher(self, xml_element: Element) -> str:
        """
        Extracts the publisher from the XML element.

        Args:
            xml_element (Element): The XML element to extract the publisher from.

        Returns:
            str: The publisher.
        """
        path = ".//Publisher/PublisherName"
        return get_content(element=xml_element, path=path)

    def extract_publisher_location(self, xml_element: Element) -> str:
        """
        Extracts the publisher location from the XML element.

        Args:
            xml_element (Element): The XML element to extract the publisher location from.

        Returns:
            str: The publisher location.
        """
        path = ".//Publisher/PublisherLocation"
        return get_content(element=xml_element, path=path)

    def extract_authors(self, xml_element: Element) -> List[Dict[str, str]]:
        """
        Extracts the authors from the XML element.

        Args:
            xml_element (Element): The XML element to extract the authors from.

        Returns:
            List[Dict[str, str]]: The list of authors, where each author is represented as a dictionary with keys:
                - "collective": The collective name of the author (if available).
                - "lastname": The last name of the author.
                - "firstname": The first name of the author.
                - "initials": The initials of the author.
        """
        return [
            {
                "collective": get_content(author, path=".//CollectiveName"),
                "lastname": get_content(element=author, path=".//LastName"),
                "firstname": get_content(element=author, path=".//ForeName"),
                "initials": get_content(element=author, path=".//Initials"),
            }
            for author in xml_element.findall(".//Author")
        ]

    def extract_sections(self, xml_element: Element) -> List[Dict[str, str]]:
        """
        Extracts the sections from the XML element.

        Args:
            xml_element (Element): The XML element to extract the sections from.

        Returns:
            List[Dict[str, str]]: The list of sections, where each section is represented as a dictionary with keys:
                - "title": The title of the section.
                - "chapter": The chapter or location label of the section.
        """
        return [
            {
                "title": get_content(section, path=".//SectionTitle"),
                "chapter": get_content(element=section, path=".//LocationLabel"),
            }
            for section in xml_element.findall(".//Section")
        ]

    def initialize_from_xml(self, xml_element: Element) -> None:
        """Helper method that parses an XML element into an article object.

        Args:
            xml_element (Element): The XML element to parse.

        Returns:
            None
        """

        # Parse the different fields of the article
        self.pubmed_id = self.extract_pubmed_id(xml_element)
        self.title = self.extract_title(xml_element)
        self.abstract = self.extract_abstract(xml_element)
        self.copyrights = self.extract_copyrights(xml_element)
        self.doi = self.extract_doi(xml_element)
        self.isbn = self.extract_isbn(xml_element)
        self.language = self.extract_language(xml_element)
        self.publication_date = self.extract_publication_date(xml_element)
        self.authors = self.extract_authors(xml_element)
        self.publication_type = self.extract_publication_type(xml_element)
        self.publisher = self.extract_publisher(xml_element)
        self.publisher_location = self.extract_publisher_location(xml_element)
        self.sections = self.extract_sections(xml_element)

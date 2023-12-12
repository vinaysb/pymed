""" This module contains the PubMed class that is used to interact with the PubMed API. """

import datetime
import itertools
import json
import xml.etree.ElementTree as xml
from typing import Any, Dict, Union, List, Generator

import requests

from .article import Paper, Book
from .utils import batches, make_date_bins

# Base url for all queries
BASE_URL = "https://eutils.ncbi.nlm.nih.gov"


class PubMed(object):
    """Wrapper around the PubMed API."""

    def __init__(
        self,
        tool: str = "my_tool",
        email: str = "my_email@example.com",
        timeout: int = 60,
        api_key: Union[str, None] = None,
    ) -> None:
        """Initialize the PubMed object.

        Args:
            tool (str, optional): Name of the tool that is executing the query.
                Defaults to "my_tool".
            email (str, optional): Email of the user of the tool.
                Defaults to "my_email@example.com".
            timeout (int, optional): Timeout in seconds for the requests to PubMed.
                Defaults to 10.
            api_key (str or None, optional): API key to use for the requests to PubMed.
                Defaults to None.

        Returns:
            None
        """

        # Store the input parameters
        self.tool = tool
        self.email = email
        self.timeout = timeout

        # Keep track of the rate limit
        self.rate_limit = 10 if api_key is not None else 3
        self.max_retriveable_results = 10000
        self.requests_made: List[datetime.datetime] = []

        # Define the standard / default query parameters
        self.parameters: Dict[str, Any] = {
            "tool": tool,
            "email": email,
            "db": "pubmed",
            "api_key": api_key,
        }

    def query(
        self,
        query: str,
        max_results: int = -1,
        skip: Union[str, None] = None,
        start_year: int = 1900,
    ):
        """
        Method that executes a query against the GraphQL schema, automatically
        inserting the PubMed data loader.

        Args:
            query (str): The GraphQL query to execute against the schema.
            max_results (int, optional): The maximum number of results to retrieve.
                Defaults to -1 (Retrieve all results).
            skip (str, optional): Option to skip either books or papers.
                Options - "book", "paper", None (default).
            start_year (int, optional): The year to start the search from.
                Defaults to 1900.

        Returns:
            itertools.chain: An iterator that contains the articles matching the query.
        """

        # Retrieve the article IDs for the query
        article_ids = self.get_article_ids(
            query=query, max_results=max_results, start_year=start_year
        )

        # Get the articles themselves
        articles = list(
            [
                self.get_articles(article_ids=batch, skip=skip)
                for batch in batches(article_ids, 250)
            ]
        )

        # Chain the batches back together and return the list
        return itertools.chain.from_iterable(articles)

    def get_total_results_count(self, query: str) -> int:
        """
        Helper method that returns the total number of results that match the query.

        Args:
            query (str): The query to send to PubMed.

        Returns:
            int: The total number of results for the query in PubMed.
        """
        # Get the default parameters
        parameters = self.parameters.copy()

        # Add specific query parameters
        parameters["term"] = query
        parameters["retmax"] = 1

        # Make the request (request a single article ID for this search)
        response = json.loads(
            self.get(
                url="/entrez/eutils/esearch.fcgi", parameters=parameters, retmode="json"
            )
        )
        total_results_count = int(response.get("esearchresult", {}).get("count"))

        # Return the total number of results (without retrieving them)
        return total_results_count

    def exceeded_rate_limit(self) -> bool:
        """Helper method to check if the rate limit has been exceeded.

        Returns:
            bool: True if the rate limit has been exceeded, False otherwise.
        """
        # Remove requests from the list that are longer than 1 second ago
        self.requests_made = [
            requestTime
            for requestTime in self.requests_made
            if requestTime > datetime.datetime.now() - datetime.timedelta(seconds=1)
        ]

        # Return whether we've made more requests in the last second, than the rate limit
        return len(self.requests_made) > self.rate_limit

    def get(self, url: str, parameters: dict, retmode: str = "json") -> str:
        """Generic helper method that makes a request to PubMed.

        Args:
            url (str): Last part of the URL that is requested (will be combined with the base url).
            parameters (dict): Parameters to use for the request.
            retmode (str, optional): Type of output that is requested (defaults to JSON but can be used to retrieve XML).

        Returns:
            str: If the response is valid JSON it will be parsed before returning, otherwise a string is returned.
        """

        # Make sure the rate limit is not exceeded
        while self.exceeded_rate_limit():
            pass

        # Set the response mode
        parameters["retmode"] = retmode

        # Make the request to PubMed
        response = requests.get(
            f"{BASE_URL}{url}", params=parameters, timeout=self.timeout
        )

        # Check for any errors
        response.raise_for_status()

        # Add this request to the list of requests made
        self.requests_made.append(datetime.datetime.now())

        return response.text

    def get_articles(
        self, article_ids: list, skip: Union[str, None] = None
    ) -> Generator[Union[Paper, Book], None, None]:
        """Helper method that batches a list of article IDs and retrieves the content.

        Args:
            article_ids (list): List of article IDs.
            skip (str, optional): Option to skip either books or papers.
                Options - "book", "paper", None (default).
            start_year (int, optional): The year to start the search from.
                Defaults to 1900.

        Yields:
            Union[Paper, Book]: Article objects.

        """
        # Get the default parameters
        parameters = self.parameters.copy()
        parameters["id"] = article_ids

        # Make the request
        response = self.get(
            url="/entrez/eutils/efetch.fcgi", parameters=parameters, retmode="xml"
        )

        # Parse as XML
        root = xml.fromstring(response)

        # Loop over the articles and construct article objects
        if skip != "paper":
            for article in root.iter("PubmedArticle"):
                yield Paper(xml_element=article)
        if skip != "book":
            for book in root.iter("PubmedBookArticle"):
                yield Book(xml_element=book)

    def get_article_ids(
        self,
        query: str,
        max_results: int,
        start_year: int = 1900,
    ) -> list:
        """Helper method to retrieve the article IDs for a query.

        Args:
            query (str): Query to be executed against the PubMed database.
            max_results (int): The maximum number of results to retrieve.
            start_year (int, optional): The year to start the search from.
                Defaults to 1900.

        Returns:
            list: Article IDs as a list.
        """

        # Get the default parameters
        parameters = self.parameters.copy()

        # Add specific query parameters
        parameters["term"] = query
        parameters["retmax"] = self.max_retriveable_results

        # If no max is provided (-1) we'll try to retrieve everything
        total_result_count = self.get_total_results_count(query)
        if max_results == -1:
            max_results = total_result_count

        # Calculate a cut off point based on the max_results parameter
        if max_results < parameters["retmax"]:
            parameters["retmax"] = max_results

        # Check if the total number of results is larger than the maximum number of results that can be retrieved (10000)
        if total_result_count <= self.max_retriveable_results:
            response = json.loads(
                self.get(
                    url="/entrez/eutils/esearch.fcgi",
                    parameters=parameters,
                    retmode="json",
                )
            )

            # Add the retrieved IDs to the list
            article_ids = response.get("esearchresult", {}).get("idlist", [])
        else:
            article_ids = self.recurse_bin_processing(
                start_date=datetime.date(start_year, 1, 1),
                end_date=datetime.date.today(),
                parameters=parameters,
                max_results=max_results,
            )

        # Return the response
        return article_ids

    def recurse_bin_processing(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        parameters: Dict[str, Any],
        max_results: int,
    ) -> List[str]:
        """Helper method that recursively processes date bins.

        Args:
            start_date (datetime.date): The start date of the range.
            end_date (datetime.date): The end date of the range.
            parameters (dict): Parameters to use for the request.
            max_results (int): The maximum number of results to retrieve.

        Returns:
            list: List of article IDs.
        """
        # Create a placeholder for the retrieved IDs
        article_ids = []

        date_bins = make_date_bins(start_date=start_date, end_date=end_date)

        for date_bin in date_bins:
            parameters["mindate"] = date_bin[0]
            parameters["maxdate"] = date_bin[1]

            # Calculate a cut off point based on the max_results parameter
            if max_results < parameters["retmax"]:
                parameters["retmax"] = max_results

            # Make the request
            response = json.loads(
                self.get(
                    url="/entrez/eutils/esearch.fcgi",
                    parameters=parameters,
                    retmode="json",
                )
            )

            # Add the retrieved IDs to the list
            article_ids += response.get("esearchresult", {}).get("idlist", [])

            # Get information from the response
            total_result_count = int(response.get("esearchresult", {}).get("count"))

            if total_result_count > self.max_retriveable_results:
                article_ids += self.recurse_bin_processing(
                    start_date=datetime.datetime.strptime(
                        date_bin[0], "%Y/%m/%d"
                    ).date(),
                    end_date=datetime.datetime.strptime(date_bin[1], "%Y/%m/%d").date(),
                    parameters=parameters,
                    max_results=max_results,
                )

        return article_ids

""" Unit tests for the PubMed class. """

from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock
from pymed import PubMed


class TestPubMed(unittest.TestCase):
    """Unit tests for the PubMed class."""

    def setUp(self):
        self.pubmed = PubMed(
            tool="test_tool", email="test_email@example.com", timeout=5
        )

    def test_init(self):
        """
        Test case for initializing the PubMed object.

        This test verifies that the PubMed object is initialized correctly with the specified tool, email, and timeout values.

        """
        self.assertEqual(self.pubmed.tool, "test_tool")
        self.assertEqual(self.pubmed.email, "test_email@example.com")
        self.assertEqual(self.pubmed.timeout, 5)

    @patch.object(PubMed, "get_article_ids")
    @patch.object(PubMed, "get_articles")
    def test_query(self, mock_get_articles, mock_get_article_ids):
        """
        Test case for the query method of the Pubmed class.

        Args:
            mock_get_articles (Mock): Mock object for the get_articles method.
            mock_get_article_ids (Mock): Mock object for the get_article_ids method.
        """
        mock_get_article_ids.return_value = [1, 2, 3]
        self.pubmed.query("test_query", max_results=3)
        mock_get_article_ids.assert_called_once_with(
            query="test_query", max_results=3, start_year=1900
        )
        mock_get_articles.assert_called()

    @patch.object(PubMed, "get")
    def test_get_total_results_count(self, mock_get):
        """
        Test case for the get_total_results_count method of the Pubmed class.

        Args:
            mock_get (Mock): Mock object for the get method.
        """
        mock_get.return_value = '{"esearchresult": {"count": "5"}}'
        result = self.pubmed.get_total_results_count("test_query")
        self.assertEqual(result, 5)

    def test_exceeded_rate_limit(self):
        """
        Test case for the exceeded_rate_limit method of the Pubmed class.
        """
        self.pubmed.requests_made = [
            datetime.now(),
        ] * 4
        self.pubmed.rate_limit = 3
        self.assertTrue(self.pubmed.exceeded_rate_limit())

    @patch("requests.get")
    def test_get(self, mock_get):
        """
        Test case for the get method of the Pubmed class.

        Args:
            mock_get (Mock): Mock object for the requests.get method.
        """
        mock_response = MagicMock()
        mock_response.text = "test_response"
        mock_get.return_value = mock_response
        result = self.pubmed.get("/test_url", {"param": "value"})
        self.assertEqual(result, "test_response")


if __name__ == "__main__":
    unittest.main()

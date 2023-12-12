""" Helper functions for the pymed package. """

from datetime import date, timedelta
from typing import Generator, List, Tuple, Union
from xml.etree.ElementTree import Element


def batches(iterable: list, n: int = 1) -> Generator[list, None, None]:
    """Helper method that creates batches from an iterable.

    Args:
        iterable (list): The iterable to batch.
        n (int, optional): The batch size. Defaults to 1.

    Yields:
        list: Batches of n objects taken from the iterable.
    """

    # Get the length of the iterable
    length = len(iterable)

    # Start a loop over the iterable
    for index in range(0, length, n):
        # Create a new iterable by slicing the original
        yield iterable[index : min(index + n, length)]


def get_content(
    element: Union[Element, None], path: str, default: str = "", separator: str = "\n"
) -> str:
    """
    Internal helper method that retrieves the text content of an XML element.

    Args:
        element (Element or None): The XML element to parse.
        path (str): Nested path in the XML element.
        default (str, optional): Default value to return when no text is found. Defaults to "".
        separator (str, optional): Separator to join multiple text values. Defaults to "\n".

    Returns:
        str: Text in the XML node.
    """

    # Find the path in the element
    if element is None:
        result = None
    else:
        result = element.findall(path)

    # Return the default if there is no such element
    if result is None or len(result) == 0:
        return default

    return separator.join([sub.text for sub in result if sub.text is not None])


def make_date_bins(
    start_date: date,
    end_date: date,
) -> List[Tuple[str, str]]:
    """Helper method that creates a list of bins for a given date range.

    Args:
        start_date (datetime.date): The start date of the range.
        end_date (datetime.date): The end date of the range.

    Returns:
        List[Tuple[str, str]]: A list of bins for the given date range in the format (upper bound, lower bound).
    """

    if start_date > end_date:
        raise ValueError("Start date must be before end date.")

    if (end_date - start_date).days > 366:
        return [
            (
                (end_date - timedelta(days=i)).strftime("%Y/%m/%d"),
                (end_date - timedelta(days=i - 365)).strftime("%Y/%m/%d"),
            )
            for i in range(1, (end_date.year - start_date.year) * 365, 365)
            if i > 1
        ]

    if (end_date - start_date).days > 31:
        return [
            (
                (end_date - timedelta(days=i)).strftime("%Y/%m/%d"),
                (end_date - timedelta(days=i - 28)).strftime("%Y/%m/%d"),
            )
            for i in range(1, 365, 28)
            if i > 1
        ]

    if (end_date - start_date).days > 7:
        return [
            (
                (end_date - timedelta(days=i)).strftime("%Y/%m/%d"),
                (end_date - timedelta(days=i - 7)).strftime("%Y/%m/%d"),
            )
            for i in range(1, 31, 7)
            if i > 1
        ]

    if (end_date - start_date).days > 1:
        return [
            (
                (end_date - timedelta(days=i)).strftime("%Y/%m/%d"),
                (end_date - timedelta(days=i - 1)).strftime("%Y/%m/%d"),
            )
            for i in range(1, 7)
            if i > 1
        ]

    return [
        (
            f"{end_date.year}/{end_date.month}/{end_date.day}",
            f"{end_date.year}/{end_date.month}/{end_date.day - 1}",
        )
    ]

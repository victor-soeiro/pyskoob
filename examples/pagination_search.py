"""Demonstrates fetching multiple pages of search results.

This example performs a search query and iterates over all available
pages until ``has_next_page`` is False. The title of each book is printed
along with the page number from which it came.
"""

from pyskoob import SkoobClient
from pyskoob.models.enums import BookSearch


def main() -> None:
    """Fetch a search query until no more pages are available."""
    query = "Python"
    page = 1

    with SkoobClient() as client:
        while True:
            results = client.books.search(query, BookSearch.TITLE, page=page)
            for book in results.results:
                print(f"[{page}] {book.title}")

            if not results.has_next_page:
                break
            page += 1


if __name__ == "__main__":
    main()

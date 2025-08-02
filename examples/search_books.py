"""Example script to search for books by title or author.

Run this script directly to perform a search using ``SkoobClient`` and
print the resulting book titles. Adjust the ``query`` variable to change
the search term or switch ``search_by`` to ``BookSearch.AUTHOR`` to search
by an author's name instead.
"""

from pyskoob import SkoobClient
from pyskoob.models.enums import BookSearch


def main() -> None:
    """Search for books with a simple query."""
    query = "Dom Casmurro"
    search_by = BookSearch.TITLE  # use BookSearch.AUTHOR to search by author

    with SkoobClient() as client:
        results = client.books.search(query, search_by)
        for book in results.results:
            print(f"{book.title} (id={book.book_id})")


if __name__ == "__main__":
    main()

"""Example script to search for authors by name.

Run this script directly to perform an author search using ``SkoobClient`` and
print the resulting author names. Adjust the ``query`` variable to change the
search term.
"""

from pyskoob.client import SkoobClient


def main() -> None:
    """Search for authors and print basic information."""
    query = "Leticia"
    page = 1

    with SkoobClient() as client:
        results = client.authors.search(query, page=page)
        for author in results.results:
            print(f"{author.name} - {author.books} books")


if __name__ == "__main__":
    main()

"""Example script to search for authors by name.

Run this module directly to perform an author search using :class:`~pyskoob.client.SkoobClient`.
You can pass the search term and page number via the command line. By default
the script searches for the name ``Leticia`` on page ``1``.
"""

from __future__ import annotations

import argparse

from pyskoob.client import SkoobClient


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", default="Leticia", help="Author name to search")
    parser.add_argument("--page", type=int, default=1, help="Page number for pagination")
    return parser.parse_args()


def main() -> None:
    """Search for authors and print basic information."""
    args = parse_args()

    with SkoobClient() as client:
        results = client.authors.search(args.query, page=args.page)
        for author in results.results:
            print(f"{author.name} - {author.books} books")


if __name__ == "__main__":
    main()

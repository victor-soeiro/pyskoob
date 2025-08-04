"""Example usage of the PublisherService."""

from pyskoob import SkoobClient


def main() -> None:
    """Fetch a publisher and display basic information."""
    publisher_id = 21

    with SkoobClient() as client:
        publisher = client.publishers.get_by_id(publisher_id)
        print(f"{publisher.name} (id={publisher.id})")
        if publisher.website:
            print(f"Website: {publisher.website}")

        authors = client.publishers.get_authors(publisher_id)
        print("Authors:")
        for author in authors.results:
            print(f" - {author.name}")

        books = client.publishers.get_books(publisher_id)
        print("Books:")
        for book in books.results:
            print(f" - {book.title}")


if __name__ == "__main__":
    main()

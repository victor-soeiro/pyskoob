import logging
from typing import cast

from bs4 import Tag

from pyskoob.exceptions import ParsingError
from pyskoob.http.client import AsyncHTTPClient
from pyskoob.internal.async_base import AsyncBaseSkoobService
from pyskoob.internal.base import BaseSkoobService
from pyskoob.models.pagination import Pagination
from pyskoob.models.publisher import (
    Publisher,
    PublisherAuthor,
    PublisherItem,
)
from pyskoob.parsers.publishers import parse_author, parse_book, parse_stats
from pyskoob.utils.bs4_utils import (
    get_tag_attr,
    get_tag_text,
    safe_find,
    safe_find_all,
)

logger = logging.getLogger(__name__)


class PublisherService(BaseSkoobService):
    """High level operations for retrieving publishers."""

    def get_by_id(self, publisher_id: int) -> Publisher:
        """Retrieve detailed information about a publisher.

        Parameters
        ----------
        publisher_id : int
            The identifier of the publisher on Skoob.

        Returns
        -------
        Publisher
            An object containing information about the publisher, including
            statistics and recently released books.

        Raises
        ------
        ParsingError
            If the expected elements cannot be parsed from the page.

        Examples
        --------
        >>> service.get_by_id(1).name
        'Editora Exemplo'
        """
        url = f"{self.base_url}/editora/{publisher_id}"
        logger.info("Fetching publisher page: %s", url)
        try:
            response = self.client.get(url)
            response.raise_for_status()
            soup = self.parse_html(response.text)
            name = get_tag_text(safe_find(soup, "h2")) or get_tag_text(soup.title)
            description = get_tag_text(safe_find(soup, "div", {"id": "historico"}))
            site_link = cast(Tag | None, soup.find("a", string="Site oficial"))
            website = get_tag_attr(site_link, "href")
            stats = parse_stats(safe_find(soup, "div", {"id": "vt_estatisticas"}))
            releases_div = safe_find(soup, "div", {"id": "livros_lancamentos"})
            releases = [parse_book(div, self.base_url) for div in safe_find_all(releases_div, "div", {"class": "livro-capa-mini"})]
            return Publisher(
                id=publisher_id,
                name=name,
                description=description,
                website=website,
                stats=stats,
                last_releases=releases,
            )
        except (AttributeError, TypeError, ValueError) as exc:
            logger.error("Failed to parse publisher page: %s", exc, exc_info=True)
            raise ParsingError("Failed to parse publisher page.") from exc
        except Exception as exc:  # pragma: no cover - unexpected
            logger.error(
                "An unexpected error occurred while parsing publisher page: %s",
                exc,
                exc_info=True,
            )
            raise ParsingError("An unexpected error occurred while parsing publisher page.") from exc

    def get_authors(self, publisher_id: int, page: int = 1) -> Pagination[PublisherAuthor]:
        """Retrieve authors associated with a publisher.

        Parameters
        ----------
        publisher_id : int
            The identifier of the publisher on Skoob.
        page : int, optional
            The pagination page to retrieve, by default 1.

        Returns
        -------
        Pagination[PublisherAuthor]
            A paginated list of authors published by the publisher.

        Raises
        ------
        ParsingError
            If the HTML structure for authors cannot be parsed.

        Examples
        --------
        >>> service.get_authors(1).results[0].name
        'Autor Exemplo'
        """
        url = f"{self.base_url}/editora/autores/{publisher_id}/mpage:{page}"
        logger.info("Fetching publisher authors: %s", url)
        try:
            response = self.client.get(url)
            response.raise_for_status()
            soup = self.parse_html(response.text)
            authors = [parse_author(div, self.base_url) for div in safe_find_all(soup, "div", {"class": "box_autor"})]
            next_page = bool(safe_find(soup, "div", {"class": "proximo"}))
            return Pagination(
                results=authors,
                limit=len(authors),
                page=page,
                total=len(authors),
                has_next_page=next_page,
            )
        except (AttributeError, TypeError, ValueError) as exc:
            logger.error("Failed to parse publisher authors: %s", exc, exc_info=True)
            raise ParsingError("Failed to parse publisher authors.") from exc
        except Exception as exc:  # pragma: no cover - unexpected
            logger.error(
                "An unexpected error occurred while parsing publisher authors: %s",
                exc,
                exc_info=True,
            )
            raise ParsingError("An unexpected error occurred while parsing publisher authors.") from exc

    def get_books(self, publisher_id: int, page: int = 1) -> Pagination[PublisherItem]:
        """Retrieve books published by the publisher.

        Parameters
        ----------
        publisher_id : int
            The identifier of the publisher on Skoob.
        page : int, optional
            The pagination page to retrieve, by default 1.

        Returns
        -------
        Pagination[PublisherItem]
            A paginated list of books released by the publisher.

        Raises
        ------
        ParsingError
            If book elements cannot be parsed from the page.

        Examples
        --------
        >>> service.get_books(1).results[0].title
        'Livro Exemplo'
        """
        url = f"{self.base_url}/editora/livros/{publisher_id}/mpage:{page}"
        logger.info("Fetching publisher books: %s", url)
        try:
            response = self.client.get(url)
            response.raise_for_status()
            soup = self.parse_html(response.text)
            books = [parse_book(div, self.base_url) for div in safe_find_all(soup, "div", {"class": "box_livro"})]
            next_page = bool(safe_find(soup, "div", {"class": "proximo"}))
            return Pagination(
                results=books,
                limit=len(books),
                page=page,
                total=len(books),
                has_next_page=next_page,
            )
        except (AttributeError, TypeError, ValueError) as exc:
            logger.error("Failed to parse publisher books: %s", exc, exc_info=True)
            raise ParsingError("Failed to parse publisher books.") from exc
        except Exception as exc:  # pragma: no cover - unexpected
            logger.error(
                "An unexpected error occurred while parsing publisher books: %s",
                exc,
                exc_info=True,
            )
            raise ParsingError("An unexpected error occurred while parsing publisher books.") from exc


class AsyncPublisherService(AsyncBaseSkoobService):
    """Asynchronous variant of :class:`PublisherService`."""

    def __init__(self, client: AsyncHTTPClient):
        super().__init__(client)

    async def get_by_id(self, publisher_id: int) -> Publisher:
        url = f"{self.base_url}/editora/{publisher_id}"
        logger.info("Fetching publisher page: %s", url)
        response = await self.client.get(url)
        response.raise_for_status()
        soup = self.parse_html(response.text)
        name = get_tag_text(safe_find(soup, "h2")) or get_tag_text(soup.title)
        description = get_tag_text(safe_find(soup, "div", {"id": "historico"}))
        site_link = cast(Tag | None, soup.find("a", string="Site oficial"))
        website = get_tag_attr(site_link, "href")
        stats = parse_stats(safe_find(soup, "div", {"id": "vt_estatisticas"}))
        releases_div = safe_find(soup, "div", {"id": "livros_lancamentos"})
        releases = [parse_book(div, self.base_url) for div in safe_find_all(releases_div, "div", {"class": "livro-capa-mini"})]
        return Publisher(
            id=publisher_id,
            name=name,
            description=description,
            website=website,
            stats=stats,
            last_releases=releases,
        )

    async def get_authors(self, publisher_id: int, page: int = 1) -> Pagination[PublisherAuthor]:
        url = f"{self.base_url}/editora/autores/{publisher_id}/mpage:{page}"
        logger.info("Fetching publisher authors: %s", url)
        response = await self.client.get(url)
        response.raise_for_status()
        soup = self.parse_html(response.text)
        authors = [parse_author(div, self.base_url) for div in safe_find_all(soup, "div", {"class": "box_autor"})]
        next_page = bool(safe_find(soup, "div", {"class": "proximo"}))
        return Pagination(
            results=authors,
            limit=len(authors),
            page=page,
            total=len(authors),
            has_next_page=next_page,
        )

    async def get_books(self, publisher_id: int, page: int = 1) -> Pagination[PublisherItem]:
        url = f"{self.base_url}/editora/livros/{publisher_id}/mpage:{page}"
        logger.info("Fetching publisher books: %s", url)
        response = await self.client.get(url)
        response.raise_for_status()
        soup = self.parse_html(response.text)
        books = [parse_book(div, self.base_url) for div in safe_find_all(soup, "div", {"class": "box_livro"})]
        next_page = bool(safe_find(soup, "div", {"class": "proximo"}))
        return Pagination(
            results=books,
            limit=len(books),
            page=page,
            total=len(books),
            has_next_page=next_page,
        )

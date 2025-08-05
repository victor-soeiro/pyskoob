"""Services for retrieving authors and their works from Skoob."""

import logging

from pyskoob.exceptions import ParsingError
from pyskoob.http.client import AsyncHTTPClient
from pyskoob.internal.async_base import AsyncBaseSkoobService
from pyskoob.internal.base import BaseSkoobService
from pyskoob.models.author import AuthorProfile, AuthorSearchResult
from pyskoob.models.book import BookSearchResult
from pyskoob.models.pagination import Pagination
from pyskoob.parsers.authors import (
    extract_total_results,
    parse_author_block,
    parse_author_book_div,
    parse_author_profile,
)
from pyskoob.utils.bs4_utils import (
    get_tag_text,
    safe_find,
    safe_find_all,
)

logger = logging.getLogger(__name__)


class AuthorService(BaseSkoobService):
    """High level operations for retrieving authors.

    The service scrapes HTML pages from Skoob to return author search results.

    Examples
    --------
    >>> service = AuthorService(None)
    >>> service.search("john").results
    []
    """

    def search(self, query: str, page: int = 1) -> Pagination[AuthorSearchResult]:
        """Search for authors by name.

        Parameters
        ----------
        query : str
            Term to look for.
        page : int, optional
            Page number for pagination, by default ``1``.

        Returns
        -------
        Pagination[AuthorSearchResult]
            Paginated list of authors matching the query.

        Examples
        --------
        >>> service.search("john").total
        0
        """
        url = f"{self.base_url}/autor/lista/busca:{query}/mpage:{page}"
        logger.info("Searching authors with query '%s' page %s", query, page)
        response = self.client.get(url)
        response.raise_for_status()
        soup = self.parse_html(response.text)

        author_blocks = []
        for div in safe_find_all(soup, "div"):
            style = str(div.get("style") or "")
            if "border-bottom:#ccc" in style and "margin-bottom:10px" in style:
                author_blocks.append(div)

        results = [r for div in author_blocks if (r := parse_author_block(div, self.base_url))]
        total = extract_total_results(soup)
        has_next = bool(safe_find(soup, "div", {"class": "proximo"}))
        return Pagination(
            results=results,
            limit=len(results),
            page=page,
            total=total,
            has_next_page=has_next,
        )

    # ------------------------------------------------------------------
    # Author profile
    def get_by_id(self, author_id: int) -> AuthorProfile:
        """Retrieve detailed information about an author.

        Parameters
        ----------
        author_id : int
            Identifier of the author on Skoob.

        Returns
        -------
        AuthorProfile
            Structured profile data for the requested author.

        Examples
        --------
        >>> service.get_by_id(1).name
        'Some Author'
        """

        url = f"{self.base_url}/autor/{author_id}"
        logger.info("Fetching author profile: %s", url)
        response = self.client.get(url)
        response.raise_for_status()
        soup = self.parse_html(response.text)
        return parse_author_profile(soup, self.base_url)

    # ------------------------------------------------------------------
    # Author books
    def get_books(self, author_id: int, page: int = 1) -> Pagination[BookSearchResult]:
        """Retrieve books written by the author.

        Parameters
        ----------
        author_id : int
            The author identifier.
        page : int, optional
            Pagination page, by default ``1``.

        Returns
        -------
        Pagination[BookSearchResult]
            Paginated list of books authored by the given ID.

        Examples
        --------
        >>> service.get_books(1).results[0].title
        'Book'
        """

        url = f"{self.base_url}/autor/livros/{author_id}/page:{page}"
        logger.info("Fetching books for author %s page %s", author_id, page)
        response = self.client.get(url)
        response.raise_for_status()
        soup = self.parse_html(response.text)

        books = [parse_author_book_div(div, self.base_url) for div in safe_find_all(soup, "div", {"class": "clivro livro-capa-mini"})]
        books = [b for b in books if b]

        total_span = safe_find(soup, "span", {"class": "badge badge-ativa"})
        total_text = get_tag_text(total_span).replace(".", "")
        total = int(total_text) if total_text.isdigit() else len(books)

        has_next = bool(safe_find(soup, "div", {"class": "proximo"}))

        return Pagination(
            results=books,
            total=total,
            page=page,
            limit=len(books),
            has_next_page=has_next,
        )


class AsyncAuthorService(AsyncBaseSkoobService):  # pragma: no cover - thin async wrapper
    """Asynchronous variant of :class:`AuthorService`."""

    def __init__(self, client: AsyncHTTPClient):
        super().__init__(client)

    async def search(self, query: str, page: int = 1) -> Pagination[AuthorSearchResult]:
        """Asynchronously search for authors by name.

        Parameters
        ----------
        query : str
            Term to look for.
        page : int, optional
            Page number for pagination, by default ``1``.

        Returns
        -------
        Pagination[AuthorSearchResult]
            Paginated list of authors matching the query.
        """

        url = f"{self.base_url}/autor/lista/busca:{query}/mpage:{page}"
        logger.info("Searching authors with query '%s' page %s", query, page)
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            soup = self.parse_html(response.text)
            author_blocks = []
            for div in safe_find_all(soup, "div"):
                style = str(div.get("style") or "")
                if "border-bottom:#ccc" in style and "margin-bottom:10px" in style:
                    author_blocks.append(div)
            results = [r for div in author_blocks if (r := parse_author_block(div, self.base_url))]
            total = extract_total_results(soup)
            has_next = bool(safe_find(soup, "div", {"class": "proximo"}))
            return Pagination(
                results=results,
                limit=len(results),
                page=page,
                total=total,
                has_next_page=has_next,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to search authors: %s", exc, exc_info=True)
            return Pagination(
                results=[],
                limit=0,
                page=page,
                total=0,
                has_next_page=False,
            )

    async def get_by_id(self, author_id: int) -> AuthorProfile:
        """Fetch an author's profile by identifier.

        Parameters
        ----------
        author_id : int
            Identifier of the author on Skoob.

        Returns
        -------
        AuthorProfile
            Structured profile data for the requested author.
        """

        url = f"{self.base_url}/autor/{author_id}"
        logger.info("Fetching author profile: %s", url)
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            soup = self.parse_html(response.text)
            return parse_author_profile(soup, self.base_url)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to fetch author profile %s: %s", author_id, exc, exc_info=True)
            raise ParsingError("Failed to fetch author profile.") from exc

    async def get_books(self, author_id: int, page: int = 1) -> Pagination[BookSearchResult]:
        """Fetch books written by the given author.

        Parameters
        ----------
        author_id : int
            The author identifier.
        page : int, optional
            Pagination page, by default ``1``.

        Returns
        -------
        Pagination[BookSearchResult]
            Paginated list of books authored by the given ID.
        """

        url = f"{self.base_url}/autor/livros/{author_id}/page:{page}"
        logger.info("Fetching books for author %s page %s", author_id, page)
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            soup = self.parse_html(response.text)
            books = [parse_author_book_div(div, self.base_url) for div in safe_find_all(soup, "div", {"class": "clivro livro-capa-mini"})]
            books = [b for b in books if b]
            total_span = safe_find(soup, "span", {"class": "badge badge-ativa"})
            total_text = get_tag_text(total_span).replace(".", "")
            total = int(total_text) if total_text.isdigit() else len(books)
            has_next = bool(safe_find(soup, "div", {"class": "proximo"}))
            return Pagination(
                results=books,
                total=total,
                page=page,
                limit=len(books),
                has_next_page=has_next,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error(
                "Failed to fetch books for author %s: %s",
                author_id,
                exc,
                exc_info=True,
            )
            return Pagination(
                results=[],
                total=0,
                page=page,
                limit=0,
                has_next_page=False,
            )

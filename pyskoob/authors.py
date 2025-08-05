"""Services for retrieving authors and their works from Skoob."""

import logging
from collections.abc import Callable
from typing import Any

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
from pyskoob.utils.sync_async import maybe_await, run_sync

logger = logging.getLogger(__name__)


class _AuthorServiceMixin:
    """Shared author retrieval logic for sync and async services.

    This mixin expects the following attributes to be provided by the base
    class:

    - ``client``: HTTP client (synchronous or asynchronous)
    - ``base_url``: Base URL for the Skoob API
    - ``parse_html``: HTML parsing function
    """

    client: Any
    base_url: str
    parse_html: Callable[[str], Any]

    async def _search(self, query: str, page: int = 1) -> Pagination[AuthorSearchResult]:
        """Fetch authors that match ``query``.

        Parameters
        ----------
        query : str
            Text to search for in author names.
        page : int, optional
            Result page number, by default ``1``.

        Returns
        -------
        Pagination[AuthorSearchResult]
            Paginated collection of matching authors.
        """

        url = f"{self.base_url}/autor/lista/busca:{query}/mpage:{page}"
        logger.info("Searching authors with query '%s' page %s", query, page)
        response = await maybe_await(self.client.get, url)
        response.raise_for_status()
        soup = self.parse_html(response.text)

        author_blocks = []
        for div in safe_find_all(soup, "div"):
            style = str(div.get("style") or "")
            if "border-bottom:#ccc" in style and "margin-bottom:10px" in style:
                author_blocks.append(div)

        results: list[AuthorSearchResult] = []
        for div in author_blocks:
            author = parse_author_block(div, self.base_url)
            if author is not None:
                results.append(author)
        total = extract_total_results(soup)
        has_next = bool(safe_find(soup, "div", {"class": "proximo"}))
        return Pagination(
            results=results,
            limit=len(results),
            page=page,
            total=total,
            has_next_page=has_next,
        )

    async def _get_by_id(self, author_id: int) -> AuthorProfile:
        """Retrieve an author's profile by ``author_id``.

        Parameters
        ----------
        author_id : int
            Unique author identifier.

        Returns
        -------
        AuthorProfile
            Parsed author profile information.
        """

        url = f"{self.base_url}/autor/{author_id}"
        logger.info("Fetching author profile: %s", url)
        response = await maybe_await(self.client.get, url)
        response.raise_for_status()
        soup = self.parse_html(response.text)
        return parse_author_profile(soup, self.base_url)

    async def _get_books(self, author_id: int, page: int = 1) -> Pagination[BookSearchResult]:
        """Retrieve books written by the author.

        Parameters
        ----------
        author_id : int
            Identifier of the author whose books will be listed.
        page : int, optional
            Result page number, by default ``1``.

        Returns
        -------
        Pagination[BookSearchResult]
            Paginated list of the author's books.
        """

        url = f"{self.base_url}/autor/livros/{author_id}/page:{page}"
        logger.info("Fetching books for author %s page %s", author_id, page)
        response = await maybe_await(self.client.get, url)
        response.raise_for_status()
        soup = self.parse_html(response.text)

        books: list[BookSearchResult] = []
        for div in safe_find_all(soup, "div", {"class": "clivro livro-capa-mini"}):
            book = parse_author_book_div(div, self.base_url)
            if book is not None:
                books.append(book)

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


class AuthorService(_AuthorServiceMixin, BaseSkoobService):
    """High level operations for retrieving authors."""

    def search(self, query: str, page: int = 1) -> Pagination[AuthorSearchResult]:
        """Synchronous wrapper around :meth:`_search`."""
        return run_sync(self._search(query, page))

    def get_by_id(self, author_id: int) -> AuthorProfile:
        """Synchronous wrapper around :meth:`_get_by_id`."""
        return run_sync(self._get_by_id(author_id))

    def get_books(self, author_id: int, page: int = 1) -> Pagination[BookSearchResult]:
        """Synchronous wrapper around :meth:`_get_books`."""
        return run_sync(self._get_books(author_id, page))


class AsyncAuthorService(_AuthorServiceMixin, AsyncBaseSkoobService):  # pragma: no cover - thin async wrapper
    """Asynchronous variant of :class:`AuthorService`."""

    def __init__(self, client: AsyncHTTPClient):
        super().__init__(client)

    async def search(self, query: str, page: int = 1) -> Pagination[AuthorSearchResult]:
        """Asynchronous wrapper around :meth:`_search`."""

        return await self._search(query, page)

    async def get_by_id(self, author_id: int) -> AuthorProfile:
        """Asynchronous wrapper around :meth:`_get_by_id`."""

        return await self._get_by_id(author_id)

    async def get_books(self, author_id: int, page: int = 1) -> Pagination[BookSearchResult]:
        """Asynchronous wrapper around :meth:`_get_books`."""

        return await self._get_books(author_id, page)

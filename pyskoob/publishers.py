"""Retrieve publisher information, books and authors from Skoob."""

import logging
from collections.abc import Callable
from typing import Any, cast

from bs4 import Tag

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
from pyskoob.utils.sync_async import maybe_await, run_sync

logger = logging.getLogger(__name__)


class _PublisherServiceMixin:
    client: Any
    base_url: str
    parse_html: Callable[[str], Any]

    async def _get_by_id(self, publisher_id: int) -> Publisher:
        url = f"{self.base_url}/editora/{publisher_id}"
        logger.info("Fetching publisher page: %s", url)
        response = await maybe_await(self.client.get, url)
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

    async def _get_authors(self, publisher_id: int, page: int = 1) -> Pagination[PublisherAuthor]:
        url = f"{self.base_url}/editora/autores/{publisher_id}/mpage:{page}"
        logger.info("Fetching publisher authors: %s", url)
        response = await maybe_await(self.client.get, url)
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

    async def _get_books(self, publisher_id: int, page: int = 1) -> Pagination[PublisherItem]:
        url = f"{self.base_url}/editora/livros/{publisher_id}/mpage:{page}"
        logger.info("Fetching publisher books: %s", url)
        response = await maybe_await(self.client.get, url)
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


class PublisherService(_PublisherServiceMixin, BaseSkoobService):
    """High level operations for retrieving publishers."""

    def get_by_id(self, publisher_id: int) -> Publisher:
        """Retrieve detailed information about a publisher."""
        return run_sync(self._get_by_id(publisher_id))

    def get_authors(self, publisher_id: int, page: int = 1) -> Pagination[PublisherAuthor]:
        """Retrieve authors associated with a publisher."""
        return run_sync(self._get_authors(publisher_id, page))

    def get_books(self, publisher_id: int, page: int = 1) -> Pagination[PublisherItem]:
        """Retrieve books published by the publisher."""
        return run_sync(self._get_books(publisher_id, page))


class AsyncPublisherService(_PublisherServiceMixin, AsyncBaseSkoobService):  # pragma: no cover - thin async wrapper
    """Asynchronous variant of :class:`PublisherService`."""

    def __init__(self, client: AsyncHTTPClient):
        super().__init__(client)

    async def get_by_id(self, publisher_id: int) -> Publisher:
        """Retrieve detailed information about a publisher."""
        return await self._get_by_id(publisher_id)

    async def get_authors(self, publisher_id: int, page: int = 1) -> Pagination[PublisherAuthor]:
        """Retrieve authors associated with a publisher."""
        return await self._get_authors(publisher_id, page)

    async def get_books(self, publisher_id: int, page: int = 1) -> Pagination[PublisherItem]:
        """Retrieve books published by a given publisher."""
        return await self._get_books(publisher_id, page)

from __future__ import annotations

from bs4 import BeautifulSoup

from pyskoob.http.client import AsyncHTTPClient
from pyskoob.http.httpx import HttpxAsyncClient


class AsyncBaseHttpService:
    """Base class for asynchronous HTTP services."""

    _base_url: str

    def __init__(self, client: AsyncHTTPClient, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    @property
    def client(self) -> AsyncHTTPClient:  # noqa: D401 - simple property
        """Return the HTTP client."""
        return self._client

    @property
    def base_url(self) -> str:  # noqa: D401 - simple property
        """Return the base URL for requests."""
        return self._base_url

    def parse_html(self, content: str) -> BeautifulSoup:
        """Parse HTML content into a :class:`BeautifulSoup` object."""
        return BeautifulSoup(content, "html.parser")


class AsyncBaseSkoobService(AsyncBaseHttpService):
    """Asynchronous variant of :class:`BaseSkoobService`."""

    def __init__(self, client: AsyncHTTPClient | None):
        super().__init__(client or HttpxAsyncClient(), "https://www.skoob.com.br")

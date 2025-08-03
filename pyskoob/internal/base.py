from types import TracebackType
from typing import Self

from bs4 import BeautifulSoup

from pyskoob.http.client import SyncHTTPClient
from pyskoob.http.httpx import HttpxSyncClient


class BaseHttpService:
    """
    A base class for HTTP services.

    Attributes
    ----------
    _base_url : str
        The base URL for the service.
    _client : SyncHTTPClient
        The HTTP client for making requests.
    """

    _base_url: str

    def __init__(self, client: SyncHTTPClient, base_url: str):
        """
        Initializes the BaseHttpService.

        Parameters
        ----------
        client : SyncHTTPClient
            The HTTP client to use for requests.
        base_url : str
            The base URL for the service.
        """
        self._client = client
        self._base_url = base_url

    @property
    def client(self) -> SyncHTTPClient:
        """
        The HTTPX client.

        Returns
        -------
        SyncHTTPClient
            The HTTP client instance.
        """
        return self._client

    @property
    def base_url(self) -> str:
        """
        The base URL for the service.

        Returns
        -------
        str
            The base URL.
        """
        return self._base_url

    def parse_html(self, content: str) -> BeautifulSoup:
        """
        Parses HTML content into a BeautifulSoup object.

        Parameters
        ----------
        content : str
            The HTML content to parse.

        Returns
        -------
        BeautifulSoup
            The parsed BeautifulSoup object.

        Examples
        --------
        >>> service.parse_html("<html></html>").name
        '[document]'
        """
        return BeautifulSoup(content, "html.parser")


class BaseSkoobService(BaseHttpService):
    """Base service tailored for Skoob endpoints.

    Parameters
    ----------
    client : SyncHTTPClient | None
        Existing synchronous HTTP client to use. If ``None``, a new
        :class:`HttpxSyncClient` is created internally.

    Notes
    -----
    When a client is created internally, resources are released by calling
    :meth:`close` or by using the service as a context manager.
    """

    _owns_client: bool

    def __init__(self, client: SyncHTTPClient | None):
        """Initialize the BaseSkoobService."""
        super().__init__(client or HttpxSyncClient(), "https://www.skoob.com.br")
        self._owns_client = client is None

    def close(self) -> None:
        """Close the internally created HTTP client, if any."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> Self:
        """Return the service instance for context manager support."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Ensure the owned HTTP client is closed on context exit."""
        self.close()

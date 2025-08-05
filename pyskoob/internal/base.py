from bs4 import BeautifulSoup

from pyskoob.http.client import SyncHTTPClient
from pyskoob.http.httpx import HttpxSyncClient


class BaseHttpService:
    """
    A base class for HTTP services.

    Attributes
    ----------
    base_url : str
        The base URL for the service.
    client : SyncHTTPClient
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
    """Base class for services that talk to the Skoob website.

    Attributes
    ----------
    base_url : str
        The base URL for Skoob endpoints.
    client : SyncHTTPClient
        The HTTP client used for requests.

    Notes
    -----
    This class preconfigures the base URL for Skoob endpoints and allows
    subclasses to reuse a shared synchronous HTTP client. If no client is
    provided, a :class:`~pyskoob.http.httpx.HttpxSyncClient` instance is
    created automatically.
    """

    def __init__(self, client: SyncHTTPClient | None):
        """
        Initializes the BaseSkoobService.

        Parameters
        ----------
        client : SyncHTTPClient | None
            The HTTP client to use for requests. If None, a new client is created.

        Examples
        --------
        >>> BaseSkoobService(httpx.Client())
        <BaseSkoobService ...>
        """
        super().__init__(client or HttpxSyncClient(), "https://www.skoob.com.br")

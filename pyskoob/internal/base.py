import httpx
from bs4 import BeautifulSoup


class BaseHttpService:
    """
    A base class for HTTP services.

    Attributes
    ----------
    _base_url : str
        The base URL for the service.
    _client : httpx.Client
        The HTTPX client for making requests.
    """
    _base_url: str

    def __init__(self, client: httpx.Client, base_url: str):
        """
        Initializes the BaseHttpService.

        Parameters
        ----------
        client : httpx.Client
            The HTTPX client to use for requests.
        base_url : str
            The base URL for the service.
        """
        self._client = client
        self._base_url = base_url

    @property
    def client(self) -> httpx.Client:
        """
        The HTTPX client.

        Returns
        -------
        httpx.Client
            The HTTPX client instance.
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
        """
        return BeautifulSoup(content, "html.parser")


class BaseSkoobService(BaseHttpService):
    def __init__(self, client: httpx.Client | None):
        """
        Initializes the BaseSkoobService.

        Parameters
        ----------
        client : httpx.Client | None
            The HTTPX client to use for requests. If None, a new client is created.
        """
        super().__init__(client or httpx.Client(), 'https://www.skoob.com.br')

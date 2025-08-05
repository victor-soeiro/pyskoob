from __future__ import annotations

from pyskoob.auth import AuthService
from pyskoob.authors import AuthorService
from pyskoob.books import BookService
from pyskoob.http.httpx import HttpxSyncClient
from pyskoob.profile import SkoobProfileService
from pyskoob.publishers import PublisherService
from pyskoob.users import UserService
from pyskoob.utils import RateLimiter


class SkoobClient:
    """Facade for interacting with Skoob services.

    Examples
    --------
    >>> with SkoobClient() as client:
    ...     client.auth.login_with_cookies("token")
    """

    def __init__(self, rate_limiter: RateLimiter | None = None) -> None:
        """Initializes the SkoobClient.

        Parameters
        ----------
        rate_limiter:
            Optional rate limiter used to throttle requests. If ``None``, a
            default limiter allowing one request per second is used.
        """

        self._client = HttpxSyncClient(rate_limiter=rate_limiter)
        self.auth = AuthService(self._client)
        self.books = BookService(self._client)
        self.authors = AuthorService(self._client)
        self.users = UserService(self._client, self.auth)
        self.me = SkoobProfileService(self._client, self.auth)
        self.publishers = PublisherService(self._client)

    def __enter__(self) -> SkoobClient:
        """
        Enter the runtime context for the SkoobClient.

        Returns
        -------
        SkoobClient
            The SkoobClient instance.

        Examples
        --------
        >>> with SkoobClient() as client:
        ...     pass
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool | None:
        """
        Exit the runtime context, closing the HTTPX client.

        Parameters
        ----------
        exc_type : type
            The exception type.
        exc_val : Exception
            The exception value.
        exc_tb : traceback
            The traceback object.

        Returns
        -------
        bool or None
            ``True`` to suppress the exception; otherwise ``None`` or ``False``
            to propagate it.

        Examples
        --------
        >>> client = SkoobClient()
        >>> client.__exit__(None, None, None)
        None
        """
        self._client.close()

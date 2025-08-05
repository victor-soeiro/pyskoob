"""Client facades bundling synchronous and asynchronous services."""

from __future__ import annotations

from types import TracebackType
from typing import Any, Literal

from pyskoob.auth import AsyncAuthService, AuthService
from pyskoob.authors import AsyncAuthorService, AuthorService
from pyskoob.books import AsyncBookService, BookService
from pyskoob.http.client import AsyncHTTPClient
from pyskoob.http.httpx import HttpxAsyncClient, HttpxSyncClient
from pyskoob.profile import AsyncSkoobProfileService, SkoobProfileService
from pyskoob.publishers import AsyncPublisherService, PublisherService
from pyskoob.users import AsyncUserService, UserService
from pyskoob.utils import RateLimiter


class SkoobClient:
    """Facade for interacting with Skoob services.

    Examples
    --------
    >>> with SkoobClient() as client:
    ...     client.auth.login_with_cookies("token")
    """

    def __init__(self, rate_limiter: RateLimiter | None = None, **kwargs: Any) -> None:
        """Initializes the SkoobClient.

        Parameters
        ----------
        rate_limiter:
            Optional rate limiter used to throttle requests. If ``None``, a
            default limiter allowing one request per second is used.
        **kwargs:
            Additional keyword arguments forwarded to ``httpx.Client`` when the
            underlying :class:`HttpxSyncClient` is constructed.
        """

        self._client = HttpxSyncClient(rate_limiter=rate_limiter, **kwargs)
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

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:
        """
        Exit the runtime context, closing the HTTPX client.

        Parameters
        ----------
        exc_type : type[BaseException] | None
            The exception type.
        exc_val : BaseException | None
            The exception value.
        exc_tb : TracebackType | None
            The traceback object.

        Returns
        -------
        Literal[False]
            Always returns ``False`` so exceptions are never suppressed.

        Examples
        --------
        >>> client = SkoobClient()
        >>> client.__exit__(None, None, None)
        False
        """
        self.close()
        return False

    def close(self) -> None:
        """Close the underlying HTTP client.

        Examples
        --------
        >>> client = SkoobClient()
        >>> client.close()
        """
        self._client.close()


class SkoobAsyncClient:
    """Facade for interacting with Skoob services asynchronously.

    Parameters
    ----------
    http_client:
        Optional pre-configured HTTP client implementing :class:`AsyncHTTPClient`.
        When provided, ``rate_limiter`` and ``client_kwargs`` are ignored.
    rate_limiter:
        Optional rate limiter used to throttle requests. When ``http_client`` is
        ``None``, a default limiter allowing one request per second is used.
    **client_kwargs:
        Additional keyword arguments forwarded to ``httpx.AsyncClient`` when the
        default client is constructed.
    """

    def __init__(
        self,
        http_client: AsyncHTTPClient | None = None,
        *,
        rate_limiter: RateLimiter | None = None,
        **client_kwargs: Any,
    ) -> None:
        if http_client is not None:
            self._client = http_client
        else:
            self._client = HttpxAsyncClient(rate_limiter=rate_limiter, **client_kwargs)
        self.auth = AsyncAuthService(self._client)
        self.books = AsyncBookService(self._client)
        self.authors = AsyncAuthorService(self._client)
        self.users = AsyncUserService(self._client, self.auth)
        self.me = AsyncSkoobProfileService(self._client, self.auth)
        self.publishers = AsyncPublisherService(self._client)

    async def __aenter__(self) -> SkoobAsyncClient:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> Literal[False]:
        """Exit the async runtime context, closing the HTTPX client.

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
        Literal[False]
            Always returns ``False`` so exceptions are never suppressed.
        """
        await self.close()
        return False

    async def close(self) -> None:
        """Close the underlying HTTP client.

        Examples
        --------
        >>> client = SkoobAsyncClient()
        >>> await client.close()
        """
        await self._client.close()

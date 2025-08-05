from __future__ import annotations

"""httpx-based implementations of the HTTP client protocols."""

from collections.abc import MutableMapping
from typing import Any

import httpx

from ..utils import RateLimiter
from .client import AsyncHTTPClient, HTTPResponse, SyncHTTPClient


class HttpxSyncClient(SyncHTTPClient):
    """Synchronous HTTP client built on :class:`httpx.Client`.

    Parameters
    ----------
    rate_limiter:
        Optional rate limiter used to throttle requests. If not provided a
        default limiter allowing one request per second is used.
    **kwargs:
        Additional arguments passed directly to ``httpx.Client``.
    """

    def __init__(self, rate_limiter: RateLimiter | None = None, **kwargs: Any) -> None:
        self._client = httpx.Client(**kwargs)
        self._rate_limiter = rate_limiter or RateLimiter()

    @property
    def cookies(self) -> MutableMapping[str, Any]:  # pragma: no cover - simple delegate
        return self._client.cookies

    def get(self, url: str, **kwargs: Any) -> HTTPResponse:
        self._rate_limiter.acquire()
        return self._client.get(url, **kwargs)

    def post(self, url: str, data: Any | None = None, **kwargs: Any) -> HTTPResponse:  # pragma: no cover - simple delegate
        """Send a POST request.

        Parameters
        ----------
        url:
            The request URL.
        data:
            Optional request payload. If ``data`` is ``bytes`` or ``str`` it is
            forwarded as ``content`` to avoid deprecation warnings from
            ``httpx``. Other types are passed through unchanged.
        **kwargs:
            Additional arguments forwarded to ``httpx.Client.post``.

        Returns
        -------
        HTTPResponse
            The HTTP response instance returned by ``httpx``.
        """

        self._rate_limiter.acquire()
        if isinstance(data, (str | bytes)):
            return self._client.post(url, content=data, **kwargs)

        return self._client.post(url, data=data, **kwargs)

    def close(self) -> None:
        self._client.close()


class HttpxAsyncClient(AsyncHTTPClient):
    """Asynchronous HTTP client built on :class:`httpx.AsyncClient`.

    Parameters
    ----------
    rate_limiter:
        Optional rate limiter used to throttle requests. If not provided a
        default limiter allowing one request per second is used.
    **kwargs:
        Additional arguments passed directly to ``httpx.AsyncClient``.
    """

    def __init__(self, rate_limiter: RateLimiter | None = None, **kwargs: Any) -> None:
        self._client = httpx.AsyncClient(**kwargs)
        self._rate_limiter = rate_limiter or RateLimiter()

    @property
    def cookies(self) -> MutableMapping[str, Any]:  # pragma: no cover - simple delegate
        return self._client.cookies

    async def get(self, url: str, **kwargs: Any) -> HTTPResponse:
        await self._rate_limiter.acquire_async()
        return await self._client.get(url, **kwargs)

    async def post(self, url: str, data: Any | None = None, **kwargs: Any) -> HTTPResponse:  # pragma: no cover - simple delegate
        """Send a POST request asynchronously.

        Parameters
        ----------
        url:
            The request URL.
        data:
            Optional request payload. If ``data`` is ``bytes`` or ``str`` it is
            forwarded as ``content`` to avoid deprecation warnings from
            ``httpx``. Other types are passed through unchanged.
        **kwargs:
            Additional arguments forwarded to ``httpx.AsyncClient.post``.

        Returns
        -------
        HTTPResponse
            The HTTP response instance returned by ``httpx``.
        """

        await self._rate_limiter.acquire_async()
        if isinstance(data, (str | bytes)):
            return await self._client.post(url, content=data, **kwargs)

        return await self._client.post(url, data=data, **kwargs)

    async def close(self) -> None:
        await self._client.aclose()

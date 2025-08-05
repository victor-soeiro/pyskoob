from __future__ import annotations

"""httpx-based implementations of the HTTP client protocols."""

from collections.abc import MutableMapping
from typing import Any

import httpx

from ..utils import ExponentialBackoff, RateLimiter
from .client import AsyncHTTPClient, HTTPResponse, SyncHTTPClient


class HttpxSyncClient(SyncHTTPClient):
    """Synchronous HTTP client built on :class:`httpx.Client`.

    Parameters
    ----------
    rate_limiter:
        Optional rate limiter used to throttle requests. If not provided a
        default limiter allowing one request per second is used.
    backoff:
        Optional backoff strategy used to retry transient failures. If not
        provided, a default exponential backoff with three retries is used.
    **kwargs:
        Additional arguments passed directly to ``httpx.Client``.
    """

    def __init__(
        self,
        rate_limiter: RateLimiter | None = None,
        backoff: ExponentialBackoff | None = None,
        **kwargs: Any,
    ) -> None:
        self._client = httpx.Client(**kwargs)
        self._rate_limiter = rate_limiter or RateLimiter()
        self._backoff = backoff or ExponentialBackoff()

    @property
    def cookies(self) -> MutableMapping[str, Any]:  # pragma: no cover - simple delegate
        return self._client.cookies

    def get(self, url: str, **kwargs: Any) -> HTTPResponse:
        if not hasattr(self, "_rate_limiter"):
            self._rate_limiter = RateLimiter()
        if not hasattr(self, "_backoff"):
            self._backoff = ExponentialBackoff()
        for attempt in range(self._backoff.max_retries + 1):
            self._rate_limiter.acquire()
            try:
                return self._client.get(url, **kwargs)
            except httpx.HTTPError:
                if attempt >= self._backoff.max_retries:
                    raise
                self._backoff.sleep(attempt)

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

        if not hasattr(self, "_rate_limiter"):
            self._rate_limiter = RateLimiter()
        if not hasattr(self, "_backoff"):
            self._backoff = ExponentialBackoff()
        for attempt in range(self._backoff.max_retries + 1):
            self._rate_limiter.acquire()
            try:
                if isinstance(data, (str | bytes)):
                    return self._client.post(url, content=data, **kwargs)
                return self._client.post(url, data=data, **kwargs)
            except httpx.HTTPError:
                if attempt >= self._backoff.max_retries:
                    raise
                self._backoff.sleep(attempt)

    def close(self) -> None:
        self._client.close()


class HttpxAsyncClient(AsyncHTTPClient):
    """Asynchronous HTTP client built on :class:`httpx.AsyncClient`.

    Parameters
    ----------
    rate_limiter:
        Optional rate limiter used to throttle requests. If not provided a
        default limiter allowing one request per second is used.
    backoff:
        Optional backoff strategy used to retry transient failures. If not
        provided, a default exponential backoff with three retries is used.
    **kwargs:
        Additional arguments passed directly to ``httpx.AsyncClient``.
    """

    def __init__(
        self,
        rate_limiter: RateLimiter | None = None,
        backoff: ExponentialBackoff | None = None,
        **kwargs: Any,
    ) -> None:
        self._client = httpx.AsyncClient(**kwargs)
        self._rate_limiter = rate_limiter or RateLimiter()
        self._backoff = backoff or ExponentialBackoff()

    @property
    def cookies(self) -> MutableMapping[str, Any]:  # pragma: no cover - simple delegate
        return self._client.cookies

    async def get(self, url: str, **kwargs: Any) -> HTTPResponse:
        if not hasattr(self, "_rate_limiter"):
            self._rate_limiter = RateLimiter()
        if not hasattr(self, "_backoff"):
            self._backoff = ExponentialBackoff()
        for attempt in range(self._backoff.max_retries + 1):
            await self._rate_limiter.acquire_async()
            try:
                return await self._client.get(url, **kwargs)
            except httpx.HTTPError:
                if attempt >= self._backoff.max_retries:
                    raise
                await self._backoff.sleep_async(attempt)

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

        if not hasattr(self, "_rate_limiter"):
            self._rate_limiter = RateLimiter()
        if not hasattr(self, "_backoff"):
            self._backoff = ExponentialBackoff()
        for attempt in range(self._backoff.max_retries + 1):
            await self._rate_limiter.acquire_async()
            try:
                if isinstance(data, (str | bytes)):
                    return await self._client.post(url, content=data, **kwargs)
                return await self._client.post(url, data=data, **kwargs)
            except httpx.HTTPError:
                if attempt >= self._backoff.max_retries:
                    raise
                await self._backoff.sleep_async(attempt)

    async def close(self) -> None:
        await self._client.aclose()

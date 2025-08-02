from __future__ import annotations

"""httpx-based implementations of the HTTP client protocols."""

from collections.abc import MutableMapping
from typing import Any

import httpx

from pyskoob.exceptions import HTTPClientError

from .client import AsyncHTTPClient, HTTPResponse, SyncHTTPClient


class HttpxSyncClient(SyncHTTPClient):
    """Synchronous HTTP client built on :class:`httpx.Client`.

    Parameters
    ----------
    **kwargs : Any
        Optional arguments passed directly to ``httpx.Client``.
    """

    def __init__(self, **kwargs: Any) -> None:
        self._client = httpx.Client(**kwargs)

    @property
    def cookies(self) -> MutableMapping[str, Any]:
        return self._client.cookies

    def get(self, url: str, **kwargs: Any) -> HTTPResponse:
        try:
            response = self._client.get(url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as exc:
            raise HTTPClientError(str(exc)) from exc

    def post(
        self, url: str, data: Any | None = None, **kwargs: Any
    ) -> HTTPResponse:
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

        try:
            if isinstance(data, (str | bytes)):
                response = self._client.post(url, content=data, **kwargs)
            else:
                response = self._client.post(url, data=data, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as exc:
            raise HTTPClientError(str(exc)) from exc

    def close(self) -> None:
        self._client.close()


class HttpxAsyncClient(AsyncHTTPClient):
    """Asynchronous HTTP client built on :class:`httpx.AsyncClient`.

    Parameters
    ----------
    **kwargs : Any
        Optional arguments passed directly to ``httpx.AsyncClient``.
    """

    def __init__(self, **kwargs: Any) -> None:
        self._client = httpx.AsyncClient(**kwargs)

    @property
    def cookies(self) -> MutableMapping[str, Any]:
        return self._client.cookies

    async def get(self, url: str, **kwargs: Any) -> HTTPResponse:
        try:
            response = await self._client.get(url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as exc:
            raise HTTPClientError(str(exc)) from exc

    async def post(
        self, url: str, data: Any | None = None, **kwargs: Any
    ) -> HTTPResponse:
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

        try:
            if isinstance(data, (str | bytes)):
                response = await self._client.post(url, content=data, **kwargs)
            else:
                response = await self._client.post(url, data=data, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as exc:
            raise HTTPClientError(str(exc)) from exc

    async def close(self) -> None:
        await self._client.aclose()

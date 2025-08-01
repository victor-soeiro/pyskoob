from __future__ import annotations

"""Protocol definitions for HTTP client abstractions."""

from typing import Any, Protocol


class HTTPResponse(Protocol):
    """Minimal response contract expected by the library.

    Implementations typically return the underlying response object from the
    HTTP library in use (for example :class:`httpx.Response`). Only the few
    methods accessed by the services are required here so that other clients can
    be adapted easily.
    """

    def raise_for_status(self) -> None:  # noqa: D401 - simple pass through
        """Proxy to the underlying client's raise_for_status method."""

    def json(self) -> Any:  # noqa: D401 - simple pass through
        """Return the response JSON body."""

    @property
    def text(self) -> str:  # noqa: D401 - simple pass through
        """Return the response text."""


class SyncHTTPClient(Protocol):
    """Protocol for synchronous HTTP clients.

    Notes
    -----
    Implementations must provide a ``cookies`` attribute and ``get``, ``post``
    and ``close`` methods with signatures compatible with ``httpx.Client``.
    """

    cookies: dict[str, Any]

    def get(self, url: str, **kwargs: Any) -> HTTPResponse:
        """Send a GET request."""

    def post(self, url: str, data: Any | None = None, **kwargs: Any) -> HTTPResponse:
        """Send a POST request."""

    def close(self) -> None:
        """Close the client and release resources."""


class AsyncHTTPClient(Protocol):
    """Protocol for asynchronous HTTP clients.

    Notes
    -----
    Implementations must provide asynchronous ``get`` and ``post`` methods
    returning objects that satisfy :class:`HTTPResponse`, along with an async
    ``close`` method and a ``cookies`` attribute.
    """

    cookies: dict[str, Any]

    async def get(self, url: str, **kwargs: Any) -> HTTPResponse:
        """Send an asynchronous GET request."""

    async def post(self, url: str, data: Any | None = None, **kwargs: Any) -> HTTPResponse:
        """Send an asynchronous POST request."""

    async def close(self) -> None:
        """Close the client and release resources."""

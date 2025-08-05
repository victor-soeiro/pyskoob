from collections.abc import MutableMapping
from typing import Any, cast

import httpx
import pytest

from pyskoob import RateLimiter, SkoobAsyncClient
from pyskoob.http.httpx import HttpxAsyncClient

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def test_async_client_context_manager(monkeypatch, anyio_backend):
    closed = False

    async def fake_aclose(self):
        nonlocal closed
        closed = True

    monkeypatch.setattr("httpx.AsyncClient.aclose", fake_aclose, raising=False)

    async with SkoobAsyncClient() as client:
        assert client.auth
        assert client.books
    assert closed


async def test_async_client_allows_configuration(anyio_backend):
    limiter = RateLimiter()
    async with SkoobAsyncClient(rate_limiter=limiter, timeout=5) as client:
        http_client = cast(HttpxAsyncClient, client._client)
        assert http_client._rate_limiter is limiter
        assert http_client._client.timeout == httpx.Timeout(5)


async def test_async_client_close_method(monkeypatch, anyio_backend):
    closed = False

    async def fake_aclose(self):
        nonlocal closed
        closed = True

    monkeypatch.setattr("httpx.AsyncClient.aclose", fake_aclose, raising=False)

    client = SkoobAsyncClient()
    await client.close()
    assert closed


async def test_async_client_exit_returns_false(monkeypatch, anyio_backend):
    closed = False

    async def fake_aclose(self):
        nonlocal closed
        closed = True

    monkeypatch.setattr("httpx.AsyncClient.aclose", fake_aclose, raising=False)

    client = SkoobAsyncClient()
    result = await client.__aexit__(None, None, None)
    assert result is False
    assert closed


class DummyAsyncClient:
    def __init__(self) -> None:
        self.closed = False
        self.cookies: MutableMapping[str, Any] = {}

    async def get(self, url: str, **kwargs: Any) -> Any:  # pragma: no cover - unused
        raise NotImplementedError

    async def post(self, url: str, data: Any | None = None, **kwargs: Any) -> Any:  # pragma: no cover - unused
        raise NotImplementedError

    async def close(self) -> None:
        self.closed = True


async def test_async_client_accepts_custom_http_client(anyio_backend):
    dummy = DummyAsyncClient()
    client = SkoobAsyncClient(http_client=dummy)
    assert client._client is dummy
    await client.close()
    assert dummy.closed

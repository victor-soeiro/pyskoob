import httpx
import pytest

from pyskoob import RateLimiter, SkoobAsyncClient

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
        assert client._client._rate_limiter is limiter
        assert client._client._client.timeout == httpx.Timeout(5)

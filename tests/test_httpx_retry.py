"""Tests for retry behaviour in HTTPX-based clients."""

import httpx
import pytest

from pyskoob.http.httpx import HttpxAsyncClient, HttpxSyncClient
from pyskoob.utils import RateLimiter, Retry


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class DummyLimiter(RateLimiter):
    """Limiter that never blocks."""

    def acquire(self) -> None:  # pragma: no cover - trivial
        return

    async def acquire_async(self) -> None:  # pragma: no cover - trivial
        return


def test_sync_client_retries_on_transport_error(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts = 0

    def fake_get(self: httpx.Client, url: str, **kwargs: object) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise httpx.TransportError("boom")
        return httpx.Response(200)

    monkeypatch.setattr(httpx.Client, "get", fake_get, raising=False)

    retry = Retry(max_attempts=3, base_delay=0, exceptions=(httpx.TransportError,))
    client = HttpxSyncClient(rate_limiter=DummyLimiter(), retry=retry)

    response = client.get("https://example.com")

    assert attempts == 3
    assert response.status_code == 200

    client.close()


@pytest.mark.anyio
async def test_async_client_retries_on_transport_error(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts = 0

    async def fake_get(self: httpx.AsyncClient, url: str, **kwargs: object) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise httpx.TransportError("boom")
        return httpx.Response(200)

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get, raising=False)

    retry = Retry(max_attempts=3, base_delay=0, exceptions=(httpx.TransportError,))
    client = HttpxAsyncClient(rate_limiter=DummyLimiter(), retry=retry)

    response = await client.get("https://example.com")

    assert attempts == 3
    assert response.status_code == 200

    await client.close()

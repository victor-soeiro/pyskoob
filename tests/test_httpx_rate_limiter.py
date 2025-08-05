"""Tests for rate limiter behavior in HTTPX-based clients."""

import httpx
import pytest

from pyskoob.http.httpx import HttpxAsyncClient, HttpxSyncClient


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class DummyLimiter:
    """Simple limiter that counts acquire calls."""

    def __init__(self) -> None:
        self.calls = 0

    def acquire(self) -> None:  # pragma: no cover - trivial increment
        self.calls += 1

    async def acquire_async(self) -> None:  # pragma: no cover - trivial increment
        self.calls += 1


def test_sync_client_reuses_existing_rate_limiter(monkeypatch: pytest.MonkeyPatch) -> None:
    limiter = DummyLimiter()
    client = HttpxSyncClient(rate_limiter=limiter)

    def fake_get(self: httpx.Client, url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(200)

    def fake_post(self: httpx.Client, url: str, data: object | None = None, **kwargs: object) -> httpx.Response:
        return httpx.Response(200)

    monkeypatch.setattr(httpx.Client, "get", fake_get, raising=False)
    monkeypatch.setattr(httpx.Client, "post", fake_post, raising=False)

    client.get("https://example.com")
    client.post("https://example.com")

    assert client._rate_limiter is limiter
    assert limiter.calls == 2
    client.close()


@pytest.mark.anyio
async def test_async_client_reuses_existing_rate_limiter(monkeypatch: pytest.MonkeyPatch) -> None:
    limiter = DummyLimiter()
    client = HttpxAsyncClient(rate_limiter=limiter)

    async def fake_get(self: httpx.AsyncClient, url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(200)

    async def fake_post(self: httpx.AsyncClient, url: str, data: object | None = None, **kwargs: object) -> httpx.Response:
        return httpx.Response(200)

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get, raising=False)
    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post, raising=False)

    await client.get("https://example.com")
    await client.post("https://example.com")

    assert client._rate_limiter is limiter
    assert limiter.calls == 2

    await client.close()

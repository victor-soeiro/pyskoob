from typing import cast

import httpx

from pyskoob import RateLimiter, SkoobClient
from pyskoob.http.httpx import HttpxSyncClient


def test_client_context_manager(monkeypatch):
    closed = False

    def fake_close(self):
        nonlocal closed
        closed = True

    monkeypatch.setattr("httpx.Client.close", fake_close, raising=False)

    with SkoobClient() as client:
        assert client.auth
        assert client.books
    assert closed


def test_client_explicit_close(monkeypatch):
    closed = False

    def fake_close(self):
        nonlocal closed
        closed = True

    monkeypatch.setattr("httpx.Client.close", fake_close, raising=False)

    client = SkoobClient()
    client.close()
    assert closed


def test_client_allows_configuration():
    limiter = RateLimiter()
    with SkoobClient(rate_limiter=limiter, timeout=5) as client:
        http_client = cast(HttpxSyncClient, client._client)
        assert http_client._rate_limiter is limiter
        assert http_client._client.timeout == httpx.Timeout(5)

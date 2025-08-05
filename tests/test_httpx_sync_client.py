import httpx
import pytest

from pyskoob.http.httpx import HttpxSyncClient
from pyskoob.utils import ExponentialBackoff


def test_sync_client_get_post_close() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(200, text="g")
        if request.method == "POST":
            return httpx.Response(200, text=request.content.decode())
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = HttpxSyncClient(transport=transport)
    resp = client.get("https://x")
    assert resp.text == "g"
    resp2 = client.post("https://x", data="p")
    assert resp2.text == "p"
    client.close()


def test_sync_client_retries_on_http_error() -> None:
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise httpx.TransportError("boom")
        return httpx.Response(200, text="ok")

    transport = httpx.MockTransport(handler)
    client = HttpxSyncClient(
        backoff=ExponentialBackoff(max_retries=1, base_delay=0),
        transport=transport,
    )
    resp = client.get("https://x")
    assert resp.text == "ok"
    assert call_count == 2


def test_sync_client_raises_after_retries() -> None:
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        raise httpx.TransportError("boom")

    transport = httpx.MockTransport(handler)
    client = HttpxSyncClient(
        backoff=ExponentialBackoff(max_retries=1, base_delay=0),
        transport=transport,
    )
    with pytest.raises(httpx.TransportError):
        client.get("https://x")
    assert call_count == 2

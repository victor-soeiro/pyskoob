import asyncio

import httpx
import pytest

from pyskoob.http.httpx import HttpxAsyncClient
from pyskoob.utils import ExponentialBackoff


def test_async_client_get_post_aclose() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(200, text="g")
        if request.method == "POST":
            return httpx.Response(200, text=request.content.decode())
        return httpx.Response(404)

    async def main():
        transport = httpx.MockTransport(handler)
        client = HttpxAsyncClient(transport=transport)
        resp = await client.get("https://x")
        assert resp.text == "g"
        resp2 = await client.post("https://x", data="p")
        assert resp2.text == "p"
        await client.close()

    asyncio.run(main())


def test_async_client_retries_on_http_error() -> None:
    calls = {"count": 0}

    async def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            raise httpx.TransportError("boom")
        return httpx.Response(200, text="ok")

    async def main() -> None:
        transport = httpx.MockTransport(handler)
        client = HttpxAsyncClient(
            backoff=ExponentialBackoff(max_retries=1, base_delay=0),
            transport=transport,
        )
        resp = await client.get("https://x")
        assert resp.text == "ok"
        assert calls["count"] == 2
        await client.close()

    asyncio.run(main())


def test_async_client_raises_after_retries() -> None:
    calls = {"count": 0}

    async def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        raise httpx.TransportError("boom")

    async def main() -> None:
        transport = httpx.MockTransport(handler)
        client = HttpxAsyncClient(
            backoff=ExponentialBackoff(max_retries=1, base_delay=0),
            transport=transport,
        )
        with pytest.raises(httpx.TransportError):
            await client.get("https://x")
        assert calls["count"] == 2
        await client.close()

    asyncio.run(main())

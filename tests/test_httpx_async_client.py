import asyncio

import httpx

from pyskoob.http.httpx import HttpxAsyncClient


def test_async_client_get_post_aclose():
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


def test_async_client_context_manager_closes():
    async def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover - simple handler
        return httpx.Response(200, text="ok")

    async def main() -> None:
        transport = httpx.MockTransport(handler)
        client = HttpxAsyncClient(transport=transport)
        async with client as ctx:
            resp = await ctx.get("https://x")
            assert resp.text == "ok"
        assert client._client.is_closed

    asyncio.run(main())

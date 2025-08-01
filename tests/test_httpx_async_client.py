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

import httpx

from pyskoob.http.httpx import HttpxSyncClient


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


def test_sync_client_context_manager_closes() -> None:
    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover - simple handler
        return httpx.Response(200, text="ok")

    transport = httpx.MockTransport(handler)
    client = HttpxSyncClient(transport=transport)
    with client as ctx:
        resp = ctx.get("https://x")
        assert resp.text == "ok"
    assert client._client.is_closed

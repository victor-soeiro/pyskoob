import httpx
import pytest
from conftest import make_user

from pyskoob import SkoobAsyncClient
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


async def test_login_with_cookies(monkeypatch):
    user_data = make_user().model_dump(by_alias=True, mode="json")

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("cookie") == "PHPSESSID=tok"
        return httpx.Response(200, json={"success": True, "response": user_data})

    transport = httpx.MockTransport(handler)
    http_client = HttpxAsyncClient(transport=transport)
    monkeypatch.setattr("pyskoob.client.HttpxAsyncClient", lambda: http_client)

    async with SkoobAsyncClient() as client:
        user = await client.auth.login_with_cookies("tok")
        assert user.id == 1
        assert http_client.cookies["PHPSESSID"] == "tok"
        client.auth.validate_login()


async def test_login_with_cookies_failure(monkeypatch):
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"success": False})

    transport = httpx.MockTransport(handler)
    http_client = HttpxAsyncClient(transport=transport)
    monkeypatch.setattr("pyskoob.client.HttpxAsyncClient", lambda: http_client)

    async with SkoobAsyncClient() as client:
        with pytest.raises(ConnectionError):
            await client.auth.login_with_cookies("tok")
        assert client.auth._is_logged_in is False


async def test_rate_limiter_invoked(monkeypatch):
    user_data = make_user().model_dump(by_alias=True, mode="json")
    called = False

    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"success": True, "response": user_data})

    transport = httpx.MockTransport(handler)
    http_client = HttpxAsyncClient(transport=transport)

    async def fake_acquire_async() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(http_client._rate_limiter, "acquire_async", fake_acquire_async)
    monkeypatch.setattr("pyskoob.client.HttpxAsyncClient", lambda: http_client)

    async with SkoobAsyncClient() as client:
        await client.auth.login_with_cookies("tok")
    assert called

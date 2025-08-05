import pytest

from pyskoob import SkoobAsyncClient

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


from pyskoob import SkoobClient


def test_client_context_manager(monkeypatch):
    closed = False

    def fake_close(self):
        nonlocal closed
        closed = True
    monkeypatch.setattr('httpx.Client.close', fake_close, raising=False)

    with SkoobClient() as client:
        assert client.auth
        assert client.books
    assert closed

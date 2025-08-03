from pyskoob.internal.base import BaseSkoobService


class DummyHttpxClient:
    def __init__(self) -> None:
        self.closed = False
        self.cookies = {}

    def get(self, url: str, **kwargs):  # pragma: no cover - unused stub
        raise RuntimeError("unexpected call")

    def post(self, url: str, data=None, **kwargs):  # pragma: no cover - unused stub
        raise RuntimeError("unexpected call")

    def close(self) -> None:
        self.closed = True


def test_service_closes_owned_client(monkeypatch):
    dummy = DummyHttpxClient()
    monkeypatch.setattr("pyskoob.internal.base.HttpxSyncClient", lambda: dummy, raising=False)
    service = BaseSkoobService(None)
    service.close()
    assert dummy.closed is True


def test_service_context_manager(monkeypatch):
    dummy = DummyHttpxClient()
    monkeypatch.setattr("pyskoob.internal.base.HttpxSyncClient", lambda: dummy, raising=False)
    with BaseSkoobService(None):
        pass
    assert dummy.closed is True


def test_service_does_not_close_external_client():
    dummy = DummyHttpxClient()
    service = BaseSkoobService(dummy)
    service.close()
    assert dummy.closed is False

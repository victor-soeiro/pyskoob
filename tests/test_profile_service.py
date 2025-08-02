from typing import cast

import pytest

from pyskoob.auth import AuthService
from pyskoob.http.client import SyncHTTPClient
from pyskoob.models.enums import BookLabel, BookShelf, BookStatus
from pyskoob.profile import SkoobProfileService


class DummyAuth:
    def validate_login(self):
        pass


class DummyResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


class DummyClient:
    def __init__(self, data):
        self.data = data
        self.called = []

    def get(self, url):
        self.called.append(url)
        return DummyResponse(self.data)


def make_service(success=True):
    client = DummyClient({"success": success})
    return (
        SkoobProfileService(cast(SyncHTTPClient, client), cast(AuthService, DummyAuth())),
        client,
    )


def test_rate_book_success():
    service, client = make_service(True)
    assert service.rate_book(1, 4.5) is True
    assert client.called


def test_rate_book_invalid_range():
    service, _ = make_service(True)
    with pytest.raises(ValueError):
        service.rate_book(1, 6)


def test_rate_book_failure():
    service, _ = make_service(False)
    with pytest.raises(RuntimeError):
        service.rate_book(1, 3)


def test_label_and_status_methods():
    service, client = make_service(True)
    assert service.add_book_label(1, BookLabel.FAVORITE)
    assert service.remove_book_label(1)
    assert service.update_book_status(1, BookStatus.READ)
    assert service.remove_book_status(1)
    assert service.change_book_shelf(1, BookShelf.BOOK)
    assert client.called  # ensure requests were made


def test_change_book_shelf_failure():
    service, _ = make_service(False)
    assert service.change_book_shelf(1, BookShelf.BOOK) is False

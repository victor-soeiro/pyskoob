import httpx
import pytest
from datetime import datetime
from typing import cast

from pyskoob.auth import AuthService
from pyskoob.models.user import User


class DummyResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


class DummyClient:
    def __init__(self, data=None):
        self.data = data or {"success": True}
        self.cookies = {}

    def post(self, url, data=None):
        return DummyResponse(self.data)


def _make_user() -> User:
    return User.model_validate(
        {
            "id": 1,
            "nome": "John",
            "apelido": "john",
            "abbr": "j",
            "url": "/john",
            "skoob": "john",
            "foto_mini": "http://a",
            "foto_pequena": "http://b",
            "foto_media": "http://c",
            "foto_grande": "http://d",
            "premium": False,
            "beta": False,
            "about": "",
            "ano": 2024,
            "mes": 1,
            "termo": datetime(2024, 1, 1),
            "estatisticas": {},
        }
    )


def test_login_with_cookies(monkeypatch):
    client = DummyClient()
    service = AuthService(cast(httpx.Client, client))
    monkeypatch.setattr(service, "get_my_info", lambda: _make_user())
    user = service.login_with_cookies("tok")
    assert service._is_logged_in is True
    assert client.cookies["PHPSESSID"] == "tok"
    assert user.id == 1


def test_validate_login(monkeypatch):
    service = AuthService(cast(httpx.Client, DummyClient()))
    with pytest.raises(PermissionError):
        service.validate_login()
    monkeypatch.setattr(service, "get_my_info", lambda: _make_user())
    service._is_logged_in = True
    service.validate_login()  # should not raise

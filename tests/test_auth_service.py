from typing import cast

import pytest
from conftest import DummyClient, DummyResponse, make_user

from pyskoob.auth import AuthService
from pyskoob.http.client import SyncHTTPClient
from pyskoob.models.user import User


def test_login_with_cookies(dummy_client: DummyClient, monkeypatch):
    service = AuthService(cast(SyncHTTPClient, dummy_client))

    async def make_user_async() -> User:
        return make_user()

    monkeypatch.setattr(service, "_get_my_info", make_user_async)
    user = service.login_with_cookies("tok")
    assert service._is_logged_in is True
    assert dummy_client.cookies["PHPSESSID"] == "tok"
    assert user.id == 1


def test_validate_login(dummy_auth: AuthService, monkeypatch):
    with pytest.raises(PermissionError):
        dummy_auth.validate_login()
    monkeypatch.setattr(dummy_auth, "get_my_info", make_user)
    dummy_auth._is_logged_in = True
    dummy_auth.validate_login()


def test_login_success(dummy_client: DummyClient, monkeypatch):
    dummy_client.json_data = {"success": True}
    service = AuthService(cast(SyncHTTPClient, dummy_client))

    async def make_user_async() -> User:
        return make_user()

    monkeypatch.setattr(service, "_get_my_info", make_user_async)
    user = service.login("a@b.com", "pass")
    assert user.name == "John" and service._is_logged_in


def test_login_bad_json(dummy_client: DummyClient):
    class BadResponse(DummyClient):
        def post(self, url: str, data=None):  # type: ignore[override]
            return DummyResponse(json_data=ValueError("bad"))

    bad_client = BadResponse()
    service = AuthService(cast(SyncHTTPClient, bad_client))
    with pytest.raises(ConnectionError):
        service.login("e", "p")


def test_login_failure(dummy_client: DummyClient):
    dummy_client.json_data = {"success": False, "message": "nope"}
    service = AuthService(cast(SyncHTTPClient, dummy_client))
    with pytest.raises(ConnectionError):
        service.login("e", "p")


def test_get_my_info_success(dummy_client: DummyClient):
    dummy_client.json_data = {"success": True, "response": make_user().model_dump(by_alias=True)}
    service = AuthService(cast(SyncHTTPClient, dummy_client))
    user = service.get_my_info()
    assert user.id == 1


def test_get_my_info_failure(dummy_client: DummyClient):
    dummy_client.json_data = {"success": False}
    service = AuthService(cast(SyncHTTPClient, dummy_client))
    with pytest.raises(ConnectionError):
        service.get_my_info()

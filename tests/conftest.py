from datetime import datetime
from typing import Any, cast

import pytest

from pyskoob.auth import AuthService
from pyskoob.http.client import SyncHTTPClient
from pyskoob.models.user import User


class DummyResponse:
    def __init__(self, text: str = "", json_data: Any | None = None):
        self._text = text
        self._json = json_data or {}

    def raise_for_status(self) -> None:  # pragma: no cover - simple stub
        pass

    def json(self) -> Any:
        if isinstance(self._json, Exception):
            raise self._json
        return self._json

    @property
    def text(self) -> str:
        return self._text


class DummyClient:
    def __init__(self, text: str = "", json_data: Any | None = None):
        self.text = text
        self.json_data = json_data or {}
        self.cookies: dict[str, Any] = {}
        self.called: list[Any] = []

    def get(self, url: str, **_: Any) -> DummyResponse:
        self.called.append(url)
        return DummyResponse(self.text, self.json_data)

    def post(self, url: str, data: Any | None = None, **_: Any) -> DummyResponse:
        self.called.append(url)
        return DummyResponse(self.text, self.json_data)

    def close(self) -> None:  # pragma: no cover - simple stub
        pass


@pytest.fixture
def dummy_client() -> DummyClient:
    return DummyClient()


@pytest.fixture
def dummy_auth(dummy_client: DummyClient) -> AuthService:
    return AuthService(cast(SyncHTTPClient, dummy_client))


@pytest.fixture
def logged_auth(dummy_client: DummyClient) -> AuthService:
    service = AuthService(cast(SyncHTTPClient, dummy_client))
    service._is_logged_in = True
    return service


def make_user() -> User:
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

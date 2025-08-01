import httpx
from conftest import make_user

from pyskoob import SkoobClient
from pyskoob.http.httpx import HttpxSyncClient


def test_login_and_search_flow(monkeypatch):
    user_data = make_user().model_dump(by_alias=True, mode="json")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/login":
            return httpx.Response(200, json={"success": True})
        if request.url.path == "/v1/user/stats:true":
            return httpx.Response(200, json={"success": True, "response": user_data})
        if request.url.path.startswith("/livro/lista/"):
            html = (
                "<div class='box_lista_busca_vertical'>"
                "<a class='capa-link-item' title='B' href='/livro/1-b-ed2.html'>"
                "<img src='https://img'></a></div>"
                "<div class='contador'>1 encontrados</div>"
            )
            return httpx.Response(200, text=html)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)

    def patched_init(self, **kwargs):
        self._client = httpx.Client(transport=transport)

    monkeypatch.setattr(HttpxSyncClient, "__init__", patched_init, raising=False)
    monkeypatch.setattr(HttpxSyncClient, "close", lambda self: None, raising=False)

    with SkoobClient() as client:
        user = client.auth.login("e", "p")
        results = client.books.search("test")
        assert user.id == 1
        assert results.total == 1 and results.results[0].book_id == 1

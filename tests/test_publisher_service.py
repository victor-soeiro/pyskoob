from typing import cast

from pyskoob.http.client import SyncHTTPClient
from pyskoob.publishers import PublisherService


class DummyClient:
    def __init__(self, text: str = ""):
        self.text = text
        self.called: list[str] = []

    def get(self, url: str, **_: str):
        self.called.append(url)
        class R:
            def __init__(self, t: str):
                self.text = t
            def raise_for_status(self):
                pass
        return R(self.text)

    def close(self):  # pragma: no cover - simple stub
        pass


def make_service(html: str = "") -> tuple[PublisherService, DummyClient]:
    client = DummyClient(text=html)
    service = PublisherService(cast(SyncHTTPClient, client))
    return service, client


def test_get_by_id():
    html = (
        "<h2>Arqueiro</h2>"
        "<div id='historico'>Desc</div>"
        "<a href='http://site' >Site oficial</a>"
        "<div id='vt_estatisticas'>"
        "<span>Seguidores</span><span>10</span>"
        "<span>Avalia\xe7\xf5es</span><span>4,5 / 20</span>"
        "<i class='icon-male'></i><span>30%</span>"
        "<i class='icon-female'></i><span>70%</span>"
        "</div>"
        "<div id='livros_lancamentos'>"
        "<div class='livro-capa-mini'><a href='/b1-ed1' title='B'><img src='i.jpg'></a></div>"
        "</div>"
    )
    service, client = make_service(html)
    pub = service.get_by_id(1)
    assert pub.name == "Arqueiro"
    assert pub.website == "http://site"
    assert pub.stats.followers == 10
    assert pub.stats.average_rating == 4.5
    assert pub.stats.ratings == 20
    assert pub.last_releases[0].title == "B"
    assert client.called[0].endswith("/editora/1")


def test_get_authors_and_books():
    authors_html = (
        "<div class='box_autor'><a href='/a1'><img src='a.jpg'></a><h3>A</h3></div>"
        "<div class='proximo'></div>"
    )
    service, client = make_service(authors_html)
    res = service.get_authors(1)
    assert res.results[0].name == "A"
    assert res.has_next_page is True

    books_html = (
        "<div class='box_livro'><a class='capa-link-item' href='/b1' title='B'><img src='b.jpg'></a></div>"
        "<div class='proximo'></div>"
    )
    client.text = books_html
    books = service.get_books(1)
    assert books.results[0].title == "B"
    assert books.has_next_page is True

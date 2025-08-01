from typing import cast

from conftest import DummyClient

from pyskoob.authors import AuthorService
from pyskoob.http.client import SyncHTTPClient


def make_service(html: str = ""):
    client = DummyClient(text=html)
    return AuthorService(cast(SyncHTTPClient, client)), client


def test_parse_search_result():
    html = (
        "<div style='border-bottom:#ccc 1px dotted; margin-bottom:10px;'>"
        "<div><img class='img-rounded' src='img.jpg'/></div>"
        "<a href='/autor/1-john'>John</a><i>nick</i>"
        "<div class='autor-item-detalhe-2'>"
        "<span> <i class='icon-book'></i> 3 publicacoes</span>"
        "<span> | </span><span>2 leitores</span>"
        "<span> | </span><span>5 seguidores</span>"
        "</div></div><div class='contador'>1 encontrados</div>"
    )
    service, _ = make_service(html)
    result = service.search("john")
    assert result.total == 1
    author = result.results[0]
    assert author.name == "John"
    assert author.nickname == "nick"
    assert author.books == 3
    assert author.readers == 2
    assert author.followers == 5
    assert author.img_url == "img.jpg"

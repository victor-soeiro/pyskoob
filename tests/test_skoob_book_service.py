from typing import cast

from bs4 import BeautifulSoup

from pyskoob.books import BookService
from pyskoob.http.client import SyncHTTPClient
from pyskoob.models.enums import BookUserStatus


class DummyClient:
    def __init__(self, text='', json_data=None):
        self.text = text
        self.json_data = json_data or {}
        self.called = []

    def get(self, url):
        self.called.append(url)
        return self

    def raise_for_status(self):
        pass

    def json(self):
        return self.json_data


def make_service(html='', json_data=None):
    client = DummyClient(text=html, json_data=json_data)
    return BookService(cast(SyncHTTPClient, client)), client


def test_extract_helpers():
    html = '''<div class="book">
        <a class="capa-link-item" title="T" href="/book/1-titleed2.html"><img src="https://img/x.jpg"></a>
        <div class="detalhes-2-sub"><div><span>1234567890123</span><span>Pub</span></div></div>
        <div class="star-mini"><strong>4,0</strong></div>
    </div>'''
    soup = BeautifulSoup(html, 'html.parser')
    service, _ = make_service()
    book_div = soup.div
    assert book_div is not None
    result = service._parse_search_result(book_div)
    assert result is not None
    assert result.title == 'T'
    assert result.edition_id == 2
    assert result.publisher == 'Pub'
    assert result.isbn == '1234567890123'
    assert service._extract_rating(book_div, 'T') == 4.0
    total_html = BeautifulSoup(
        '<div class="contador">3 encontrados</div>',
        'html.parser',
    )
    assert service._extract_total_results(total_html) == 3


def test_clean_book_json_data():
    service, _ = make_service()
    data = {
        'url': '/path',
        'isbn': '0',
        'autor': 'n\xc3\xa3o especificado',
        'serie': '',
        'volume': '0',
        'mes': '',
        'img_url': 'https://img',
        'generos': []
    }
    service._clean_book_json_data(data)
    assert data['isbn'] is None
    assert data['url'].startswith('https://')


def test_search_and_reviews_and_users():
    search_html = (
        "<div class=\"box_lista_busca_vertical\">\n"
        "<a class=\"capa-link-item\" title=\"B\" href=\"/book/10-b-ed20.html\"><img src=\"https://x\"></a>\n"
        "<div class=\"contador\">1 encontrados</div>"
    )
    service, client = make_service(html=search_html)
    results = service.search('q')
    assert results.total == 1 and results.results[0].book_id == 10

    reviews_html = (
        "<div id=\"pg-livro-menu-principal-container\"><a href=\"/book/10-b-ed20.html\"></a></div>"
        "<div id=\"resenha1\"><a href='/usuario/5-user'></a>"
        "<a href='/livro/10-b-ed20.html'></a><star-rating rate=\"3\"/>"
        "<div id=\"resenhac1\"><span>01/01/2020</span>Great</div></div>"
    )
    client.text = reviews_html
    revs = service.get_reviews(10)
    assert revs.results[0].rating == 3

    users_html = '<div class="livro-leitor-container"><a href="/usuario/7-user"></a></div>'
    client.text = users_html
    users = service.get_users_by_status(10, BookUserStatus.READ)
    assert users.results == [7]

from typing import cast

import httpx

from pyskoob.auth import AuthService
from pyskoob.models.enums import BookcaseOption, UsersRelation
from pyskoob.users import UserService


class DummyAuth:
    def validate_login(self):
        pass


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
    auth = DummyAuth()
    return (
        UserService(cast(httpx.Client, client), cast(AuthService, auth)),
        client,
    )


def test_get_read_stats_and_bookcase():
    json_data = {
        'response': {
            'ano': 2024,
            'lido': 1,
            'paginas_lidas': 10,
            'paginas_total': 100,
            'percentual_lido': 10,
            'total': 2,
            'velocidade_dia': 1,
            'velocidade_ideal': 2,
        }
    }
    service, client = make_service(json_data=json_data)
    stats = service.get_read_stats(5)
    assert stats.year == 2024

    bookcase_json = {
        'response': [
            {
                'edicao': {'livro_id': 1, 'id': 2},
                'ranking': 3,
                'favorito': True,
                'desejado': False,
                'troco': False,
                'tenho': True,
                'emprestei': False,
                'meta': None,
                'paginas_lidas': 0,
            }
        ],
        'paging': {'next_page': None},
    }
    client.json_data = bookcase_json
    books = service.get_bookcase(5, BookcaseOption.READ)
    assert books.results[0].book_id == 1


def test_search_and_relations_and_reviews():
    html = (
        '<div style="border: 1px solid #e4e4e4"><a href="/usuario/10-john">John</a></div>'
        '<div class="contador">1 encontrados</div>'
    )
    service, client = make_service(html=html)
    res = service.search('john')
    assert res.total == 1 and res.results[0].id == 10

    relations_html = '<div class="usuarios-mini-lista-txt"><a href="/usuario/20-doe"></a></div>'
    client.text = relations_html
    rel = service.get_relations(10, UsersRelation.FOLLOWERS)
    assert rel.results == [20]

    reviews_html = (
        "<div id='resenha1'><a href='/usuario/u'></a>"
        "<a href='/livro/1ed2.html'></a>"
        "<div id='resenhac1'><span>02/02/2020</span><p>Nice</p></div>"
        "<star-rating rate='5'/></div>"
    )
    client.text = reviews_html
    rev = service.get_reviews(10)
    assert rev.results[0].rating == 5

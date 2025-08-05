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
        "<div><a href='/autor/1-john'><img class='img-rounded' src='img.jpg'/></a></div>"
        "<strong><a href='/autor/1-john'>John</a></strong><i>nick</i>"
        "<div class='autor-item-detalhe-2'></div></div>"
        "<div class='contador'>1 encontrados</div>"
    )
    service, _ = make_service(html)
    result = service.search("john")
    assert result.total == 1
    author = result.results[0]
    assert author.id == 1
    assert author.name == "John"
    assert author.nickname == "nick"
    assert author.url.endswith("/autor/1-john")
    assert author.img_url == "img.jpg"


def test_get_by_id_parses_profile():
    html = (
        "<div style='float:left;'><img class='img-rounded' src='p.jpg'></div>"
        "<div id='autor-icones'><a href='http://site'><span class='icon-earth'></span></a></div>"
        "<div id='box-descricao'><div id='box-nome'><h1 class='given-name'>A</h1></div>"
        "<div id='livro-perfil-status02'><div class='span3'><div class='bg_green'><span class='rating'>4,8</span></div>"
        "<div><span>info</span><span>100 avalia\xe7\xf5es</span></div></div>"
        "<div class='bar'><a>LIVROS</a><b><a class='text_blue'>10</a></b></div>"
        "<div class='bar'><a>LEITORES</a><b><a class='text_blue'>20</a></b></div>"
        "<div class='bar'><a>SEGUIDORES</a><b><a class='text_blue'>30</a></b></div></div>"
        "<div id='box-generos'><b>Nascimento: </b>01/01/2000 | "
        "<b>Local: </b><span class='adr'>Brasil<span class='locality'> - SP - "
        "Sao Paulo</span></span></div>"
        "<div id='livro-perfil-sinopse-txt'>Desc</div>"
        "<div class='genero-box'><div class='genero-item'>Fantasia</div></div></div>"
        "<div class='span4' style='width:200px'><div><img src='5_estrela.gif' alt='5'/><div></div><div>80%</div></div>"
        "<div><img src='4_estrela.gif' alt='4'/><div></div><div>20%</div></div></div>"
        "<div class='span3' style='width:80px'><div class='row-fluid'><i class='icon-male'></i><span>60%</span></div>"
        "<div class='row-fluid'><i class='icon-female'></i><span>40%</span></div></div>"
        "<div class='perfil-box'><ul class='ul-lancamentos'><div class='clivro livro-capa-mini' id='10'>"
        "<a href='/b1-ed10.html' title='B1'><img src='c1.jpg'></a></div></ul></div>"
        "<div id='livro-perfil-videos'><div class='livro-perfil-videos-cont'>"
        "<a href='/v1'><img src='v1.jpg' alt='V1'></a><a>V1</a></div></div>"
        "<div id='box-info-cad'><div class='box-info-cad-user'><div class='box-info-cad-date'>"
        "<a href='/usuario/1-a'>A1</a><br/>cadastrou em: <br>01/01/2020</div></div>"
        "<div class='box-info-cad-user'><div class='box-info-cad-date'>"
        "<a href='/usuario/2-b'>B1</a><br/>editou em: <br>02/02/2020</div></div>"
        "<div class='box-info-cad-user'><div class='box-info-cad-date'>"
        "<a href='/usuario/3-c'>C1</a><br/>aprovou em: <br>03/03/2020</div></div></div>"
    )
    service, _ = make_service(html)
    profile = service.get_by_id(1)
    assert profile.name == "A"
    assert profile.photo_url == "p.jpg"
    assert profile.links == {"earth": "http://site"}
    assert profile.stats.followers == 30
    assert profile.stats.readers == 20
    assert profile.stats.ratings == 100
    assert profile.stats.average_rating == 4.8
    assert profile.stats.star_ratings["5"] == 80.0
    assert profile.gender_percentages == {"male": 60.0, "female": 40.0}
    assert profile.birth_date == "01/01/2000"
    loc = profile.location
    assert loc is not None and loc.startswith("Brasil")
    assert profile.tags == ["Fantasia"]
    assert profile.books[0].title == "B1"
    assert profile.videos[0].title == "V1"
    assert profile.created_by == "A1"
    assert profile.edited_by == "B1"
    assert profile.approved_by == "C1"


def test_get_books_pagination():
    html = (
        "<div class='clivro livro-capa-mini' id='10'><a href='/b1-ed10.html' title='B1'><img src='i1.jpg'></a></div>"
        "<span class='badge badge-ativa'>2</span><div class='proximo'></div>"
    )
    service, _ = make_service(html)
    res = service.get_books(1)
    book = res.results[0]
    assert book.title == "B1"
    assert book.edition_id == 10
    assert book.book_id == 1
    assert res.total == 2
    assert res.has_next_page is True

from pyskoob.utils import skoob_parser_utils as spu


def test_get_book_id_from_url():
    assert spu.get_book_id_from_url("https://www.skoob.com.br/123-title") == "123"
    url = "https://www.skoob.com.br/title-123ed456.html"
    assert spu.get_book_id_from_url(url) == "123"
    url_with_query = "https://www.skoob.com.br/livro/123-ed10.html?ref=foo"
    assert spu.get_book_id_from_url(url_with_query) == "123"


def test_get_book_edition_and_user_id():
    url = "https://www.skoob.com.br/title-123ed456.html"
    assert spu.get_book_edition_id_from_url(url) == "456"
    url_with_query = "https://www.skoob.com.br/livro/123-ed456.html?foo=bar"
    assert spu.get_book_edition_id_from_url(url_with_query) == "456"
    assert spu.get_user_id_from_url("https://www.skoob.com.br/usuario/55-name/?x=y") == "55"


def test_get_author_id_from_url():
    assert spu.get_author_id_from_url("https://www.skoob.com.br/autor/77-john") == "77"
    assert spu.get_author_id_from_url("https://www.skoob.com.br/autor/77-john/?ref=bar") == "77"

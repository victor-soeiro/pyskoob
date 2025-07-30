from bs4 import BeautifulSoup

from pyskoob.utils import bs4_utils


def test_safe_find_and_find_all():
    html = '<div><span id="x">Hi</span><span>Bye</span></div>'
    soup = BeautifulSoup(html, 'html.parser')
    result = bs4_utils.safe_find(soup, 'span', {'id': 'x'})
    assert result is not None
    assert result.text == 'Hi'
    assert bs4_utils.safe_find(None, 'span') is None

    spans = bs4_utils.safe_find_all(soup, 'span')
    assert len(spans) == 2
    assert bs4_utils.safe_find_all(None, 'div') == []


def test_get_tag_text_and_attr():
    soup = BeautifulSoup('<a href="/foo">Link</a>', 'html.parser')
    link = soup.a
    assert bs4_utils.get_tag_text(link) == 'Link'
    assert bs4_utils.get_tag_text(None) == ''
    assert bs4_utils.get_tag_attr(link, 'href') == '/foo'
    assert bs4_utils.get_tag_attr(None, 'href', 'default') == 'default'

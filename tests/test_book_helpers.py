from datetime import datetime
from typing import cast

import pytest
from bs4 import BeautifulSoup
from conftest import DummyClient

from pyskoob.books import BookService
from pyskoob.http.client import SyncHTTPClient
from pyskoob.parsers.books import (
    extract_edition_id_from_reviews_page,
    extract_publisher_and_isbn,
    extract_review_date_and_text,
    extract_user_ids_from_html,
)


def make_service(html: str = ""):
    client = DummyClient(text=html)
    return BookService(cast(SyncHTTPClient, client)), client


@pytest.mark.parametrize(
    "html,expected",
    [
        (
            "<div class='detalhes-2-sub'><div><span>1234567890123</span><span>Pub</span></div></div>",
            ("Pub", "1234567890123"),
        ),
        (
            "<div class='detalhes-2-sub'><div><span>1234567890123</span></div></div>",
            (None, "1234567890123"),
        ),
        (
            "<div class='detalhes-2-sub'><div><span>|</span><span>Pub</span></div></div>",
            (None, None),
        ),
        ("<div></div>", (None, None)),
    ],
)
def test_extract_publisher_and_isbn(html, expected):
    service, _ = make_service()
    soup = BeautifulSoup(html, "html.parser")
    result = extract_publisher_and_isbn(soup)
    assert result == expected


def test_extract_user_ids_and_edition_id():
    html_users = (
        "<div class='livro-leitor-container'><a href='/usuario/1-a'></a></div>"
        "<div class='livro-leitor-container'><a href='/usuario/2-b'></a></div>"
        "<div class='livro-leitor-container'><span>No link</span></div>"
    )
    service, _ = make_service()
    soup = BeautifulSoup(html_users, "html.parser")
    ids = extract_user_ids_from_html(soup)
    assert ids == [1, 2]

    html_reviews = "<div id='pg-livro-menu-principal-container'><a href='/livro/10-ed5.html'></a></div>"
    soup = BeautifulSoup(html_reviews, "html.parser")
    edition = extract_edition_id_from_reviews_page(soup)
    assert edition == 5
    assert extract_edition_id_from_reviews_page(BeautifulSoup("<div></div>", "html.parser")) is None


@pytest.mark.parametrize(
    "html,date,text",
    [
        ("<div id='c'><span>01/01/2020</span>Great</div>", datetime(2020, 1, 1), "Great"),
        ("<div id='c'><span>bad</span>Nice</div>", None, "Nice"),
        ("<div id='c'>Only</div>", None, "Only"),
    ],
)
def test_extract_review_date_and_text(html, date, text):
    service, _ = make_service()
    soup = BeautifulSoup(html, "html.parser")
    result_date, result_text = extract_review_date_and_text(soup.div, 1)
    assert result_date == date
    assert result_text == text

from __future__ import annotations

import logging
import re
from datetime import datetime
from urllib.parse import urlparse, urlunparse

from bs4 import Tag

from pyskoob.models.book import BookReview, BookSearchResult
from pyskoob.utils.bs4_utils import (
    get_tag_attr,
    get_tag_text,
    safe_find,
    safe_find_all,
)
from pyskoob.utils.skoob_parser_utils import (
    get_book_edition_id_from_url,
    get_book_id_from_url,
    get_user_id_from_url,
)

logger = logging.getLogger(__name__)


def extract_user_ids_from_html(soup: Tag) -> list[int]:
    users_html = safe_find_all(soup, "div", {"class": "livro-leitor-container"})
    users_id: list[int] = []
    for user_div in users_html:
        user_link = safe_find(user_div, "a")
        href = get_tag_attr(user_link, "href")
        if href:
            user_id = get_user_id_from_url(href)
            if user_id:
                users_id.append(int(user_id))
            else:  # pragma: no cover - malformed URL
                logger.warning("Could not extract user ID from URL: %s", href)
        else:
            logger.warning("Skipping user_div due to missing 'a' tag or href attribute.")
    return users_id


def extract_edition_id_from_reviews_page(soup: Tag) -> int | None:
    menu_div = safe_find(soup, "div", {"id": "pg-livro-menu-principal-container"})
    menu_div_a = safe_find(menu_div, "a") if menu_div else None
    href = get_tag_attr(menu_div_a, "href")
    if href:
        extracted_edition_id = get_book_edition_id_from_url(href)
        if extracted_edition_id:
            return int(extracted_edition_id)
        logger.warning("Could not extract edition_id from URL: %s", href)  # pragma: no cover
    return None


def parse_review(r: Tag, book_id: int, edition_id: int | None) -> BookReview | None:
    review_id_str = get_tag_attr(r, "id")
    review_id = int(review_id_str.replace("resenha", "")) if review_id_str else None
    if review_id is None:
        logger.warning("Skipping review due to missing or invalid ID: %s", get_tag_attr(r, "id"))  # pragma: no cover
        return None
    user_link = safe_find(r, "a", {"href": re.compile(r"/usuario/")})
    user_url = get_tag_attr(user_link, "href")
    user_id = int(get_user_id_from_url(user_url)) if user_url else None
    if user_id is None:
        logger.warning("Skipping review %s due to missing user ID.", review_id)  # pragma: no cover
        return None
    star_tag = safe_find(r, "star-rating")
    rating = float(get_tag_attr(star_tag, "rate", "0")) if star_tag else 0.0
    comment_div = safe_find(r, "div", {"id": re.compile(r"resenhac\d+")})
    date, review_text = extract_review_date_and_text(comment_div, review_id)
    return BookReview(
        review_id=review_id,
        book_id=book_id,
        edition_id=edition_id,
        user_id=user_id,
        rating=rating,
        review_text=review_text,
        reviewed_at=date,
    )


def extract_review_date_and_text(comment_div: Tag | None, review_id: int) -> tuple[datetime | None, str]:
    date = None
    review_text = ""
    if comment_div:
        span = safe_find(comment_div, "span")
        date_str = get_tag_text(span)
        if date_str:
            try:
                date = datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                date = None
        content_parts = []
        for child in span.next_siblings if span else []:
            if hasattr(child, "get_text"):
                text = child.get_text(separator="\n", strip=True)
                if text:
                    content_parts.append(text)
        if not content_parts and comment_div:
            content_parts.append(comment_div.get_text(separator="\n", strip=True))
        review_text = "\n".join(filter(None, content_parts)).strip()
    return date, review_text


def parse_search_result(book_div: Tag, base_url: str) -> BookSearchResult | None:
    container = safe_find(book_div, "a", {"class": "capa-link-item"})
    if not container:
        logger.warning("Skipping book_div due to missing 'capa-link-item' container.")  # pragma: no cover
        return None
    title = get_tag_attr(container, "title")
    book_url = f"{base_url}{get_tag_attr(container, 'href')}"
    img_url = extract_img_url(container)
    try:
        book_id = int(get_book_id_from_url(book_url))
        edition_id = int(get_book_edition_id_from_url(book_url))
    except (ValueError, TypeError):  # pragma: no cover - defensive
        logger.warning("Skipping book_div due to invalid book/edition id in url: %s", book_url)
        return None
    publisher, isbn = extract_publisher_and_isbn(book_div)
    rating = extract_rating(book_div, title)
    return BookSearchResult(
        edition_id=edition_id,
        book_id=book_id,
        title=title,
        publisher=publisher,
        isbn=isbn,
        url=book_url,
        cover_url=img_url,
        rating=rating,
    )


def extract_img_url(container: Tag | str) -> str:
    """Normalize image URL from a tag or raw string."""
    src = ""
    if isinstance(container, Tag) and container.img and isinstance(container.img, Tag):
        src = get_tag_attr(container.img, "src") or ""
    elif isinstance(container, str):
        src = container
    if src:
        parsed = urlparse(src, scheme="https")
        if parsed.netloc:
            return urlunparse(parsed)
        if src.startswith("//"):
            return f"https:{src}"
    return ""


def extract_publisher_and_isbn(book_div: Tag) -> tuple[str | None, str | None]:
    detalhes2sub = safe_find(book_div, "div", {"class": "detalhes-2-sub"})
    detalhes2sub_div = detalhes2sub.div if detalhes2sub else None
    spans = safe_find_all(detalhes2sub_div, "span") if detalhes2sub_div else []
    cleaned_spans = [text for span in spans if (text := span.get_text(strip=True)) and text != "|"]
    isbn_pattern = re.compile(r"^\d{9,13}$|^B0[A-Z0-9]{8,}$")
    isbn: str | None = None
    publisher: str | None = None
    if cleaned_spans:
        if isbn_pattern.match(cleaned_spans[0]):
            isbn = cleaned_spans[0]
        if len(cleaned_spans) > 1:
            publisher = cleaned_spans[1]
    return publisher, isbn


def extract_rating(book_div: Tag, title: str) -> float | None:
    star_mini = safe_find(book_div, "div", {"class": "star-mini"})
    if star_mini:
        strong_tag = safe_find(star_mini, "strong")
        rating_text = get_tag_text(strong_tag)
        if rating_text:
            try:
                return float(rating_text.replace(",", "."))
            except ValueError:  # pragma: no cover - invalid rating
                logger.warning("Could not parse rating '%s' for book '%s'. Setting to None.", rating_text, title)
    return None


def extract_total_results(soup: Tag) -> int:
    total_results_tag = safe_find(soup, "div", {"class": "contador"})
    if total_results_tag:
        total_results_text = get_tag_text(total_results_tag)
        match = re.search(r"(\d+)\s+encontrados", total_results_text)
        if match:
            return int(match.group(1))
    return 0  # pragma: no cover - default when pattern missing


def clean_book_json_data(json_data: dict, base_url: str) -> dict:
    """Return a cleaned copy of raw book data.

    Parameters
    ----------
    json_data : dict
        Raw book data as returned by the Skoob API.
    base_url : str
        Base URL used to convert relative links to absolute ones.

    Returns
    -------
    dict
        A new dictionary with normalized fields and cleaned values.
    """
    data = json_data.copy()
    data["url"] = f"{base_url}{data['url']}"
    data["isbn"] = None if str(data.get("isbn", "0")) == "0" else data["isbn"]
    data["autor"] = None if data.get("autor", "").lower() == "não especificado" else data["autor"]
    data["serie"] = data.get("serie") or None
    data["volume"] = None if not data.get("volume") or str(data["volume"]) == "0" else str(data["volume"])
    data["mes"] = None if not data.get("mes") or str(data["mes"]).strip() == "" else data["mes"]
    img_url = data.get("img_url", "")
    data["cover_url"] = extract_img_url(img_url)
    generos = data.get("generos")
    data["generos"] = generos if generos else None
    return data

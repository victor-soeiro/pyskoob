from __future__ import annotations

import re

from bs4 import Tag

from pyskoob.models.author import AuthorBook, AuthorProfile, AuthorSearchResult, AuthorStats, AuthorVideo
from pyskoob.models.book import BookSearchResult
from pyskoob.utils.bs4_utils import (
    get_tag_attr,
    get_tag_text,
    safe_find,
    safe_find_all,
)
from pyskoob.utils.skoob_parser_utils import (
    get_author_id_from_url,
    get_book_id_from_url,
)


def parse_author_block(div: Tag, base_url: str) -> AuthorSearchResult | None:
    img_tag = safe_find(div, "img", {"class": "img-rounded"})
    links = [a for a in safe_find_all(div, "a", {"href": re.compile(r"/autor/\d+-")}) if get_tag_attr(a, "href")]
    link_tag = next((a for a in links if get_tag_text(a)), None)
    if not (img_tag and link_tag):
        return None  # pragma: no cover - malformed author block
    href = get_tag_attr(link_tag, "href")
    return AuthorSearchResult(
        id=int(get_author_id_from_url(href)),
        name=get_tag_text(link_tag),
        url=f"{base_url}{href}",
        nickname=get_tag_text(safe_find(div, "i")),
        img_url=get_tag_attr(img_tag, "src"),
    )


def extract_total_results(soup: Tag) -> int:
    contador = safe_find(soup, "div", {"class": "contador"})
    match = re.search(r"(\d+)", get_tag_text(contador))
    return int(match.group(1)) if match else 0


def parse_author_profile(soup: Tag, base_url: str) -> AuthorProfile:  # noqa: C901
    name = get_tag_text(safe_find(soup, "h1", {"class": "given-name"}))
    photo_url = get_tag_attr(safe_find(soup, "img", {"class": "img-rounded"}), "src")

    links: dict[str, str] = {}
    for a in safe_find_all(safe_find(soup, "div", {"id": "autor-icones"}), "a"):
        span = safe_find(a, "span")
        cls = get_tag_attr(span, "class", "")
        if isinstance(cls, list):
            cls = cls[0]
        key = str(cls).replace("icon-", "")
        href = get_tag_attr(a, "href")
        if href:
            links[key] = href

    box_generos = safe_find(soup, "div", {"id": "box-generos"})
    birth_date = None
    location = None
    if box_generos:
        birth_b = box_generos.find("b", string=lambda s: s and "Nascimento" in s)
        if birth_b and birth_b.next_sibling:
            birth_date = str(birth_b.next_sibling).strip(" |")
        loc_b = box_generos.find("b", string=lambda s: s and "Local" in s)
        if loc_b and loc_b.next_sibling:
            loc_tag = loc_b.next_sibling
            if isinstance(loc_tag, Tag):
                location = get_tag_text(loc_tag)
            else:  # pragma: no cover - defensive
                location = str(loc_tag).strip()

    description = get_tag_text(safe_find(soup, "div", {"id": "livro-perfil-sinopse-txt"}))
    tags = [get_tag_text(t) for t in safe_find_all(soup, "div", {"class": "genero-item"})]

    stats_div = safe_find(soup, "div", {"id": "livro-perfil-status02"})
    followers = readers = ratings = None
    average_rating = None
    if stats_div:
        rating_span = safe_find(stats_div, "span", {"class": "rating"})
        rating_text = get_tag_text(rating_span).replace(",", ".")
        average_rating = float(rating_text) if rating_text else None
        aval_span = stats_div.find("span", string=lambda t: t and "avalia" in t.lower())
        if aval_span:
            aval_match = re.search(r"(\d+)", get_tag_text(aval_span).replace(".", ""))
            ratings = int(aval_match.group(1)) if aval_match else None
        for bar in safe_find_all(stats_div, "div", {"class": "bar"}):
            label = get_tag_text(safe_find(bar, "a")).lower()
            value_text = get_tag_text(safe_find(bar, "b")).replace(".", "")
            value = int(value_text) if value_text.isdigit() else None
            if "leitores" in label:
                readers = value
            elif "seguidores" in label:
                followers = value

    star_ratings: dict[str, float] = {}
    for img in safe_find_all(soup, "img", {"src": re.compile("estrela")}):
        alt = get_tag_attr(img, "alt")
        percent_tag = img.find_next("div", string=re.compile("%"))
        if alt and percent_tag:
            star_ratings[alt] = float(get_tag_text(percent_tag).replace("%", ""))

    male = female = None
    male_icon = safe_find(soup, "i", {"class": re.compile("icon-male")})
    if male_icon:
        male_text = get_tag_text(male_icon.find_next("span")).replace("%", "")
        male = float(male_text) if male_text else None
    female_icon = safe_find(soup, "i", {"class": re.compile("icon-female")})
    if female_icon:
        female_text = get_tag_text(female_icon.find_next("span")).replace("%", "")
        female = float(female_text) if female_text else None
    gender: dict[str, float] = {}
    if male is not None:
        gender["male"] = male
    if female is not None:
        gender["female"] = female

    books = [
        AuthorBook(
            url=f"{base_url}{get_tag_attr(a, 'href')}",
            title=get_tag_attr(a, "title"),
            img_url=get_tag_attr(safe_find(div, "img"), "src"),
        )
        for div in safe_find_all(soup, "div", {"class": "clivro livro-capa-mini"})
        if (a := safe_find(div, "a"))
    ]

    videos = [
        AuthorVideo(
            url=f"{base_url}{get_tag_attr(a, 'href')}",
            thumbnail_url=get_tag_attr(safe_find(a, "img"), "src"),
            title=get_tag_attr(safe_find(a, "img"), "alt") or get_tag_text(a),
        )
        for a in [safe_find(div, "a") for div in safe_find_all(soup, "div", {"class": "livro-perfil-videos-cont"})]
        if a
    ]

    created_at = created_by = edited_at = edited_by = approved_at = approved_by = None
    info_div = safe_find(soup, "div", {"id": "box-info-cad"})
    if info_div:
        for box in safe_find_all(info_div, "div", {"class": "box-info-cad-user"}):
            date_div = safe_find(box, "div", {"class": "box-info-cad-date"})
            user_link = safe_find(date_div, "a")
            user_name = get_tag_text(user_link)
            text = get_tag_text(date_div)
            if "cadastrou" in text:
                created_by = user_name
                created_at = text.split("cadastrou em:")[-1].strip()
            elif "editou" in text:
                edited_by = user_name
                edited_at = text.split("editou em:")[-1].strip()
            elif "aprovou" in text:
                approved_by = user_name
                approved_at = text.split("aprovou em:")[-1].strip()

    stats = AuthorStats(
        followers=followers,
        readers=readers,
        ratings=ratings,
        average_rating=average_rating,
        star_ratings=star_ratings,
    )

    return AuthorProfile(
        name=name,
        photo_url=photo_url,
        links=links,
        description=description,
        tags=tags,
        birth_date=birth_date,
        location=location,
        gender_percentages=gender,
        books=books,
        videos=videos,
        stats=stats,
        created_at=created_at,
        created_by=created_by,
        edited_at=edited_at,
        edited_by=edited_by,
        approved_at=approved_at,
        approved_by=approved_by,
    )


def parse_author_book_div(div: Tag, base_url: str) -> BookSearchResult | None:
    anchor = safe_find(div, "a")
    if not anchor:
        return None  # pragma: no cover - missing anchor
    href = get_tag_attr(anchor, "href")
    img = safe_find(anchor, "img")
    title = get_tag_attr(anchor, "title") or get_tag_text(anchor)
    edition_id_text = get_tag_attr(div, "id")
    try:
        edition_id = int(edition_id_text) if edition_id_text else int(get_book_id_from_url(href))
        book_id = int(get_book_id_from_url(href)) if href else 0
    except ValueError:  # pragma: no cover - defensive
        return None
    return BookSearchResult(
        edition_id=edition_id,
        book_id=book_id,
        title=title,
        url=f"{base_url}{href}",
        cover_url=get_tag_attr(img, "src"),
    )

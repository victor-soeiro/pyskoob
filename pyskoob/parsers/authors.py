from __future__ import annotations

import re

"""Parser helpers for author-related pages on Skoob."""

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
    """Parse a search result block for an author.

    The ``div`` is expected to contain an ``img`` with class ``img-rounded``
    and an anchor linking to ``/autor/<id>-``. The parser extracts the
    author's numeric ID, display name, profile URL, nickname and avatar URL
    into an :class:`AuthorSearchResult`.

    Parameters
    ----------
    div : Tag
        HTML container representing a single search result.
    base_url : str
        Base URL used to build absolute links.

    Returns
    -------
    AuthorSearchResult or None
        Structured data for the author or ``None`` if required elements are
        missing.
    """

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
    """Extract the total number of author search results.

    The counter appears inside ``div.contador`` as text like ``"123"``. This
    helper isolates the numeric portion and returns it as an integer.

    Parameters
    ----------
    soup : Tag
        Root ``BeautifulSoup`` tag for the search page.

    Returns
    -------
    int
        Number of results reported by the page, or ``0`` when the counter is
        missing.
    """

    contador = safe_find(soup, "div", {"class": "contador"})
    match = re.search(r"(\d+)", get_tag_text(contador))
    return int(match.group(1)) if match else 0


def extract_author_links(soup: Tag) -> dict[str, str]:
    """Collect external links from an author's profile.

    The profile exposes social links inside ``div#autor-icones``. Each anchor
    wraps a ``span`` whose class name starts with ``icon-`` (for example,
    ``icon-facebook``). The function builds a dictionary mapping the icon name
    without the prefix to the corresponding absolute URL.

    Parameters
    ----------
    soup : Tag
        Parsed author profile page.

    Returns
    -------
    dict of str to str
        Mapping of social network identifiers to URLs.
    """

    links: dict[str, str] = {}
    icons_div = safe_find(soup, "div", {"id": "autor-icones"})
    for a in safe_find_all(icons_div, "a"):
        span = safe_find(a, "span")
        cls = get_tag_attr(span, "class", "")
        if isinstance(cls, list):
            cls = cls[0]
        key = str(cls).replace("icon-", "")
        href = get_tag_attr(a, "href")
        if href:
            links[key] = href
    return links


def extract_author_info(soup: Tag) -> tuple[str | None, str | None]:
    """Extract birth date and hometown from the profile sidebar.

    The ``div#box-generos`` section contains ``<b>Nascimento</b>`` and
    ``<b>Local</b>`` labels followed by text nodes with the desired
    information.

    Parameters
    ----------
    soup : Tag
        Parsed author profile.

    Returns
    -------
    tuple of (str or None, str or None)
        Birth date string and location string when available.
    """

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
            location = get_tag_text(loc_tag) if isinstance(loc_tag, Tag) else str(loc_tag).strip()
    return birth_date, location


def _parse_rating_summary(
    stats_div: Tag | None,
) -> tuple[int | None, int | None, int | None, float | None]:
    """Extract high-level rating numbers from the author stats block.

    Parameters
    ----------
    stats_div : Tag | None
        Container holding the rating information. May be ``None`` when the
        profile lacks a stats section.

    Returns
    -------
    tuple[int | None, int | None, int | None, float | None]
        A tuple containing, respectively, the number of followers, readers,
        ratings and the average rating. Each element is ``None`` when the
        corresponding value cannot be determined.
    """


def extract_author_stats(soup: Tag) -> AuthorStats:
    """Extract readership and rating statistics for an author.

    Statistics appear inside ``div#livro-perfil-status02`` and include follower
    counts, reader counts, number of ratings and the overall average rating.
    The star rating distribution is determined by reading percentages next to
    star icons.

    Parameters
    ----------
    soup : Tag
        Parsed author profile.

    Returns
    -------
    AuthorStats
        Dataclass with follower counts, ratings information and star
        distribution.
    """

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

    return followers, readers, ratings, average_rating


def _parse_star_distribution(soup: Tag) -> dict[str, float]:
    """Extract the percentage distribution for each star rating.

    Parameters
    ----------
    soup : Tag
        Parsed HTML of the author profile page.

    Returns
    -------
    dict[str, float]
        Mapping of the star label (e.g., ``"5 estrelas"``) to the percentage of
        ratings with that value.
    """

    star_ratings: dict[str, float] = {}
    for img in safe_find_all(soup, "img", {"src": re.compile("estrela")}):
        alt = get_tag_attr(img, "alt")
        percent_tag = img.find_next("div", string=re.compile("%"))
        if alt and percent_tag:
            star_ratings[alt] = float(get_tag_text(percent_tag).replace("%", ""))
    return star_ratings


def extract_author_stats(soup: Tag) -> AuthorStats:
    """Parse follower counts and rating information from the profile.

    Parameters
    ----------
    soup : Tag
        Parsed HTML of the author profile page.

    Returns
    -------
    AuthorStats
        Data model containing follower counts, reader counts, number of
        ratings, average rating and star distribution.
    """

    stats_div = safe_find(soup, "div", {"id": "livro-perfil-status02"})
    followers, readers, ratings, average_rating = _parse_rating_summary(stats_div)
    star_ratings = _parse_star_distribution(soup)
    return AuthorStats(
        followers=followers,
        readers=readers,
        ratings=ratings,
        average_rating=average_rating,
        star_ratings=star_ratings,
    )


def extract_gender_percentages(soup: Tag) -> dict[str, float]:
    """Extract gender distribution percentages for readers.

    Percentages are displayed next to icons with classes ``icon-male`` and
    ``icon-female`` on the profile page.

    Parameters
    ----------
    soup : Tag
        Parsed author profile.

    Returns
    -------
    dict of str to float
        Mapping containing ``"male"`` and/or ``"female"`` keys when present.
    """

    gender: dict[str, float] = {}
    male_icon = safe_find(soup, "i", {"class": re.compile("icon-male")})
    if male_icon:
        male_text = get_tag_text(male_icon.find_next("span")).replace("%", "")
        if male_text:
            gender["male"] = float(male_text)
    female_icon = safe_find(soup, "i", {"class": re.compile("icon-female")})
    if female_icon:
        female_text = get_tag_text(female_icon.find_next("span")).replace("%", "")
        if female_text:
            gender["female"] = float(female_text)
    return gender


def extract_author_books(soup: Tag, base_url: str) -> list[AuthorBook]:
    """Extract minimal book information from an author's bibliography.

    Each book is represented by ``div.clivro livro-capa-mini`` containing a
    link and thumbnail. Only the book URL, title and image URL are returned.

    Parameters
    ----------
    soup : Tag
        Parsed author profile page.
    base_url : str
        Base URL used to build absolute links.

    Returns
    -------
    list of AuthorBook
        Lightweight representation of the author's books.
    """

    return [
        AuthorBook(
            url=f"{base_url}{get_tag_attr(a, 'href')}",
            title=get_tag_attr(a, "title"),
            img_url=get_tag_attr(safe_find(div, "img"), "src"),
        )
        for div in safe_find_all(soup, "div", {"class": "clivro livro-capa-mini"})
        if (a := safe_find(div, "a"))
    ]


def extract_author_videos(soup: Tag, base_url: str) -> list[AuthorVideo]:
    """Extract videos related to the author.

    Videos appear in ``div.livro-perfil-videos-cont`` containers and provide a
    link with a thumbnail image. The parser returns a list of video URLs,
    thumbnails and titles.

    Parameters
    ----------
    soup : Tag
        Parsed author profile page.
    base_url : str
        Base URL used to build absolute links.

    Returns
    -------
    list of AuthorVideo
        Video information referenced on the page.
    """

    return [
        AuthorVideo(
            url=f"{base_url}{get_tag_attr(a, 'href')}",
            thumbnail_url=get_tag_attr(safe_find(a, "img"), "src"),
            title=get_tag_attr(safe_find(a, "img"), "alt") or get_tag_text(a),
        )
        for a in [safe_find(div, "a") for div in safe_find_all(soup, "div", {"class": "livro-perfil-videos-cont"})]
        if a
    ]


def extract_author_metadata(
    soup: Tag,
) -> tuple[str | None, str | None, str | None, str | None, str | None, str | None]:
    """Extract creation, edition and approval metadata from the profile.

    The ``div#box-info-cad`` section lists entries describing when and by whom
    the profile was created, edited and approved. This function extracts those
    usernames and timestamps.

    Parameters
    ----------
    soup : Tag
        Parsed author profile.

    Returns
    -------
    tuple
        ``(created_at, created_by, edited_at, edited_by, approved_at, approved_by)``
        strings, each ``None`` when not available.
    """

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
    return created_at, created_by, edited_at, edited_by, approved_at, approved_by


def parse_author_profile(soup: Tag, base_url: str) -> AuthorProfile:
    """Parse an author profile page into a data model.

    Parameters
    ----------
    soup : Tag
        Parsed HTML of the author profile page.
    base_url : str
        Base URL used to convert relative links to absolute ones.

    Returns
    -------
    AuthorProfile
        Structured representation of the author profile.
    """

    name = get_tag_text(safe_find(soup, "h1", {"class": "given-name"}))
    photo_url = get_tag_attr(safe_find(soup, "img", {"class": "img-rounded"}), "src")
    links = extract_author_links(soup)
    birth_date, location = extract_author_info(soup)
    description = get_tag_text(safe_find(soup, "div", {"id": "livro-perfil-sinopse-txt"}))
    tags = [get_tag_text(t) for t in safe_find_all(soup, "div", {"class": "genero-item"})]
    stats = extract_author_stats(soup)
    gender = extract_gender_percentages(soup)
    books = extract_author_books(soup, base_url)
    videos = extract_author_videos(soup, base_url)
    (
        created_at,
        created_by,
        edited_at,
        edited_by,
        approved_at,
        approved_by,
    ) = extract_author_metadata(soup)
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
    """Parse a book listing within an author's page."""

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

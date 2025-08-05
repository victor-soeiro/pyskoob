from __future__ import annotations

"""Parser helpers for publisher-related pages on Skoob."""

from bs4 import Tag

from pyskoob.models.publisher import PublisherAuthor, PublisherItem, PublisherStats
from pyskoob.utils.bs4_utils import get_tag_attr, get_tag_text, safe_find


def parse_stats(div: Tag | None) -> PublisherStats:
    """Parse follower, rating and gender statistics for a publisher.

    The stats block displays follower counts, average rating with total
    evaluations and the male/female reader percentages. Missing elements are
    represented as ``None`` in the returned dataclass.

    Parameters
    ----------
    div : Tag or None
        Container with the statistics section.

    Returns
    -------
    PublisherStats
        Dataclass populated with the extracted values.
    """

    if not div:
        return PublisherStats()  # pragma: no cover - default empty stats
    followers = avg = ratings = male = female = None
    seg_span = div.find("span", string=lambda text: bool(text and "Seguidor" in text))
    if seg_span:
        followers_text = get_tag_text(seg_span.find_next("span")).replace(".", "")
        followers = int(followers_text) if followers_text.isdigit() else None
    aval_span = div.find("span", string=lambda text: bool(text and "Avalia" in text))
    if aval_span:
        rating_info = get_tag_text(aval_span.find_next("span"))
        if "/" in rating_info:
            rating_part, total_part = (p.strip() for p in rating_info.split("/"))
            avg = float(rating_part.replace(",", ".")) if rating_part else None
            clean_total = total_part.replace(".", "")
            ratings = int(clean_total) if clean_total.isdigit() else None
    male_icon = div.find("i", {"class": "icon-male"})
    if male_icon:
        male_text = get_tag_text(male_icon.find_next("span")).replace("%", "")
        male = int(male_text) if male_text.isdigit() else None
    female_icon = div.find("i", {"class": "icon-female"})
    if female_icon:
        female_text = get_tag_text(female_icon.find_next("span")).replace("%", "")
        female = int(female_text) if female_text.isdigit() else None
    return PublisherStats(
        followers=followers,
        average_rating=avg,
        ratings=ratings,
        male_percentage=male,
        female_percentage=female,
    )


def parse_book(div: Tag, base_url: str) -> PublisherItem:
    """Parse a book entry listed on a publisher page.

    Each book block contains an anchor with the book link and an ``img`` tag
    for the cover. Only the URL, title and image URL are captured.

    Parameters
    ----------
    div : Tag
        Container representing a single book.
    base_url : str
        Base URL used to expand the book link.

    Returns
    -------
    PublisherItem
        Lightweight representation of the book.
    """

    anchor = safe_find(div, "a")
    img_tag = safe_find(anchor, "img")
    return PublisherItem(
        url=f"{base_url}{get_tag_attr(anchor, 'href')}",
        title=get_tag_attr(anchor, "title"),
        img_url=get_tag_attr(img_tag, "src"),
    )


def parse_author(div: Tag, base_url: str) -> PublisherAuthor:
    """Parse an author entry from a publisher page.

    The entry includes a link with the author's profile image and a heading
    containing the name. The parser returns the absolute profile URL, author
    name and image URL.

    Parameters
    ----------
    div : Tag
        Container representing a single author.
    base_url : str
        Base URL used to expand the author link.

    Returns
    -------
    PublisherAuthor
        Structured author information extracted from the block.
    """

    anchor = safe_find(div, "a")
    name_tag = safe_find(div, "h3")
    img_tag = safe_find(anchor, "img")
    return PublisherAuthor(
        url=f"{base_url}{get_tag_attr(anchor, 'href')}",
        name=get_tag_text(name_tag),
        img_url=get_tag_attr(img_tag, "src"),
    )

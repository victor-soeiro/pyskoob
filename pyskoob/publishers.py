import logging
from typing import cast

from bs4 import Tag

from pyskoob.exceptions import ParsingError
from pyskoob.internal.base import BaseSkoobService
from pyskoob.models.pagination import Pagination
from pyskoob.models.publisher import (
    Publisher,
    PublisherAuthor,
    PublisherItem,
    PublisherStats,
)
from pyskoob.utils.bs4_utils import (
    get_tag_attr,
    get_tag_text,
    safe_find,
    safe_find_all,
)

logger = logging.getLogger(__name__)


class PublisherService(BaseSkoobService):
    """High level operations for retrieving publishers."""

    def get_by_id(self, publisher_id: int) -> Publisher:
        url = f"{self.base_url}/editora/{publisher_id}"
        logger.info("Fetching publisher page: %s", url)
        try:
            response = self.client.get(url)
            response.raise_for_status()
            soup = self.parse_html(response.text)
            name = get_tag_text(safe_find(soup, "h2")) or get_tag_text(soup.title)
            description = get_tag_text(safe_find(soup, "div", {"id": "historico"}))
            site_link = cast(Tag | None, soup.find("a", string="Site oficial"))
            website = get_tag_attr(site_link, "href")
            stats = self._parse_stats(safe_find(soup, "div", {"id": "vt_estatisticas"}))
            releases_div = safe_find(soup, "div", {"id": "livros_lancamentos"})
            releases = [self._parse_book(div) for div in safe_find_all(releases_div, "div", {"class": "livro-capa-mini"})]
            return Publisher(
                id=publisher_id,
                name=name,
                description=description,
                website=website,
                stats=stats,
                last_releases=releases,
            )
        except Exception as exc:  # pragma: no cover - unexpected
            logger.error("Failed to parse publisher page: %s", exc, exc_info=True)
            raise ParsingError("Failed to parse publisher page") from exc

    def get_authors(self, publisher_id: int, page: int = 1) -> Pagination[PublisherAuthor]:
        url = f"{self.base_url}/editora/autores/{publisher_id}/mpage:{page}"
        logger.info("Fetching publisher authors: %s", url)
        try:
            response = self.client.get(url)
            response.raise_for_status()
            soup = self.parse_html(response.text)
            authors = [self._parse_author(div) for div in safe_find_all(soup, "div", {"class": "box_autor"})]
            next_page = bool(safe_find(soup, "div", {"class": "proximo"}))
            return Pagination(
                results=authors,
                limit=len(authors),
                page=page,
                total=len(authors),
                has_next_page=next_page,
            )
        except Exception as exc:  # pragma: no cover - unexpected
            logger.error("Failed to parse publisher authors: %s", exc, exc_info=True)
            raise ParsingError("Failed to parse publisher authors") from exc

    def get_books(self, publisher_id: int, page: int = 1) -> Pagination[PublisherItem]:
        url = f"{self.base_url}/editora/livros/{publisher_id}/mpage:{page}"
        logger.info("Fetching publisher books: %s", url)
        try:
            response = self.client.get(url)
            response.raise_for_status()
            soup = self.parse_html(response.text)
            books = [self._parse_book(div) for div in safe_find_all(soup, "div", {"class": "box_livro"})]
            next_page = bool(safe_find(soup, "div", {"class": "proximo"}))
            return Pagination(
                results=books,
                limit=len(books),
                page=page,
                total=len(books),
                has_next_page=next_page,
            )
        except Exception as exc:  # pragma: no cover - unexpected
            logger.error("Failed to parse publisher books: %s", exc, exc_info=True)
            raise ParsingError("Failed to parse publisher books") from exc

    # Helpers
    def _parse_stats(self, div: Tag | None) -> PublisherStats:
        if not div:
            return PublisherStats()
        followers = None
        avg = None
        ratings = None
        male = None
        female = None
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

    def _parse_book(self, div: Tag) -> PublisherItem:
        anchor = safe_find(div, "a")
        img_tag = safe_find(anchor, "img")
        return PublisherItem(
            url=f"{self.base_url}{get_tag_attr(anchor, 'href')}",
            title=get_tag_attr(anchor, "title"),
            img_url=get_tag_attr(img_tag, "src"),
        )

    def _parse_author(self, div: Tag) -> PublisherAuthor:
        anchor = safe_find(div, "a")
        name_tag = safe_find(div, "h3")
        img_tag = safe_find(anchor, "img")
        return PublisherAuthor(
            url=f"{self.base_url}{get_tag_attr(anchor, 'href')}",
            name=get_tag_text(name_tag),
            img_url=get_tag_attr(img_tag, "src"),
        )

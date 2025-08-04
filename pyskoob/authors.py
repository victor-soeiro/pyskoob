import logging
import re

from bs4 import Tag

from pyskoob.internal.base import BaseSkoobService
from pyskoob.models.author import AuthorBook, AuthorProfile, AuthorSearchResult, AuthorStats, AuthorVideo
from pyskoob.models.book import BookSearchResult
from pyskoob.models.pagination import Pagination
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

logger = logging.getLogger(__name__)


class AuthorService(BaseSkoobService):
    """High level operations for retrieving authors.

    The service scrapes HTML pages from Skoob to return author search results.

    Examples
    --------
    >>> service = AuthorService(None)
    >>> service.search("john").results
    []
    """

    def search(self, query: str, page: int = 1) -> Pagination[AuthorSearchResult]:
        """Search for authors by name.

        Parameters
        ----------
        query : str
            Term to look for.
        page : int, optional
            Page number for pagination, by default ``1``.

        Returns
        -------
        Pagination[AuthorSearchResult]
            Paginated list of authors matching the query.

        Examples
        --------
        >>> service.search("john").total
        0
        """
        url = f"{self.base_url}/autor/lista/busca:{query}/mpage:{page}"
        logger.info("Searching authors with query '%s' page %s", query, page)
        response = self.client.get(url)
        response.raise_for_status()
        soup = self.parse_html(response.text)

        author_blocks = []
        for div in safe_find_all(soup, "div"):
            style = str(div.get("style") or "")
            if "border-bottom:#ccc" in style and "margin-bottom:10px" in style:
                author_blocks.append(div)

        results = [r for div in author_blocks if (r := self._parse_author_block(div))]
        total = self._extract_total_results(soup)
        has_next = bool(safe_find(soup, "div", {"class": "proximo"}))
        return Pagination(
            results=results,
            limit=len(results),
            page=page,
            total=total,
            has_next_page=has_next,
        )

    def _parse_author_block(self, div: Tag) -> AuthorSearchResult | None:
        """Parse a single author listing block.

        Parameters
        ----------
        div : Tag
            The HTML ``div`` containing the author information.

        Returns
        -------
        AuthorSearchResult or None
            Parsed author data or ``None`` if required fields are missing.
        """
        img_tag = safe_find(div, "img", {"class": "img-rounded"})
        links = [a for a in safe_find_all(div, "a", {"href": re.compile(r"/autor/\d+-")}) if get_tag_attr(a, "href")]
        link_tag = next((a for a in links if get_tag_text(a)), None)
        if not (img_tag and link_tag):
            return None
        href = get_tag_attr(link_tag, "href")
        return AuthorSearchResult(
            id=int(get_author_id_from_url(href)),
            name=get_tag_text(link_tag),
            url=f"{self.base_url}{href}",
            nickname=get_tag_text(safe_find(div, "i")),
            img_url=get_tag_attr(img_tag, "src"),
        )

    @staticmethod
    def _extract_total_results(soup: Tag) -> int:
        """Extract the total number of results from the page.

        Parameters
        ----------
        soup : Tag
            Parsed search results page.

        Returns
        -------
        int
            Total number of authors found or ``0`` if unavailable.

        Examples
        --------
        >>> AuthorService._extract_total_results(
        ...     BeautifulSoup("<div class='contador'>1 encontrados</div>", 'html.parser')
        ... )
        1
        """
        contador = safe_find(soup, "div", {"class": "contador"})
        match = re.search(r"(\d+)", get_tag_text(contador))
        return int(match.group(1)) if match else 0

    # ------------------------------------------------------------------
    # Author profile
    def get_by_id(self, author_id: int) -> AuthorProfile:
        """Retrieve detailed information about an author.

        Parameters
        ----------
        author_id : int
            Identifier of the author on Skoob.

        Returns
        -------
        AuthorProfile
            Structured profile data for the requested author.

        Examples
        --------
        >>> service.get_by_id(1).name
        'Some Author'
        """

        url = f"{self.base_url}/autor/{author_id}"
        logger.info("Fetching author profile: %s", url)
        response = self.client.get(url)
        response.raise_for_status()
        soup = self.parse_html(response.text)
        return self._parse_author_profile(soup)

    def _parse_author_profile(self, soup: Tag) -> AuthorProfile:  # noqa: C901
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
                if "livros" in label:
                    # count ignored but kept for completeness
                    pass
                elif "leitores" in label:
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
                url=f"{self.base_url}{get_tag_attr(a, 'href')}",
                title=get_tag_attr(a, "title"),
                img_url=get_tag_attr(safe_find(div, "img"), "src"),
            )
            for div in safe_find_all(soup, "div", {"class": "clivro livro-capa-mini"})
            if (a := safe_find(div, "a"))
        ]

        videos = [
            AuthorVideo(
                url=f"{self.base_url}{get_tag_attr(a, 'href')}",
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

    # ------------------------------------------------------------------
    # Author books
    def get_books(self, author_id: int, page: int = 1) -> Pagination[BookSearchResult]:
        """Retrieve books written by the author.

        Parameters
        ----------
        author_id : int
            The author identifier.
        page : int, optional
            Pagination page, by default ``1``.

        Returns
        -------
        Pagination[BookSearchResult]
            Paginated list of books authored by the given ID.

        Examples
        --------
        >>> service.get_books(1).results[0].title
        'Book'
        """

        url = f"{self.base_url}/autor/livros/{author_id}/page:{page}"
        logger.info("Fetching books for author %s page %s", author_id, page)
        response = self.client.get(url)
        response.raise_for_status()
        soup = self.parse_html(response.text)

        books = [self._parse_book_div(div) for div in safe_find_all(soup, "div", {"class": "clivro livro-capa-mini"})]
        books = [b for b in books if b]

        total_span = safe_find(soup, "span", {"class": "badge badge-ativa"})
        total_text = get_tag_text(total_span).replace(".", "")
        total = int(total_text) if total_text.isdigit() else len(books)

        has_next = bool(safe_find(soup, "div", {"class": "proximo"}))

        return Pagination(
            results=books,
            total=total,
            page=page,
            limit=len(books),
            has_next_page=has_next,
        )

    def _parse_book_div(self, div: Tag) -> BookSearchResult | None:
        anchor = safe_find(div, "a")
        if not anchor:
            return None
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
            url=f"{self.base_url}{href}",
            cover_url=get_tag_attr(img, "src"),
        )

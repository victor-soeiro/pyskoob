import logging
import re

from bs4 import Tag

from pyskoob.internal.base import BaseSkoobService
from pyskoob.models.author import AuthorSearchResult
from pyskoob.models.pagination import Pagination
from pyskoob.utils.bs4_utils import get_tag_attr, get_tag_text, safe_find, safe_find_all

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
        link_tag = safe_find(div, "a", {"href": re.compile(r"/autor/\d+-")})
        details = safe_find(div, "div", {"class": "autor-item-detalhe-2"})
        if not (img_tag and link_tag and details):
            return None
        spans = [get_tag_text(s) for s in safe_find_all(details, "span") if get_tag_text(s)]
        numbers = [self._to_int(s) for s in spans if re.search(r"\d", s)]
        if len(numbers) < 3:
            return None
        return AuthorSearchResult(
            name=get_tag_text(link_tag),
            url=f"{self.base_url}{get_tag_attr(link_tag, 'href')}",
            nickname=get_tag_text(safe_find(div, "i")),
            books=numbers[0],
            readers=numbers[1],
            followers=numbers[2],
            img_url=get_tag_attr(img_tag, "src"),
        )

    @staticmethod
    def _to_int(text: str) -> int:
        """Convert a string with digits to an integer.

        Parameters
        ----------
        text : str
            Text containing digits.

        Returns
        -------
        int
            Integer extracted from ``text`` or ``0`` if none found.
        """
        digits = re.search(r"(\d+[\.\d]*)", text)
        return int(digits.group(1).replace(".", "")) if digits else 0

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

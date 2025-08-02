import logging
import re
from datetime import datetime

from bs4 import Tag

from pyskoob.exceptions import HTTPClientError, ParsingError
from pyskoob.internal.base import BaseSkoobService
from pyskoob.models.book import Book, BookReview, BookSearchResult
from pyskoob.models.enums import BookSearch, BookUserStatus
from pyskoob.models.pagination import Pagination
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


class BookService(BaseSkoobService):
    """High level operations for retrieving and searching books.

    The service parses HTML and JSON responses from Skoob and exposes
    helpers to fetch book details, reviews and user lists. It can be used
    independently from authentication, but other services may combine it
    with :class:`AuthService` to operate on the authenticated user's data.
    """

    def search(
        self,
        query: str,
        search_by: BookSearch = BookSearch.TITLE,
        page: int = 1,
    ) -> Pagination[BookSearchResult]:
        """
        Searches for books by query and type.

        Parameters
        ----------
        query : str
            The search query string.
        search_by : BookSearch, optional
            The type of search (title, author, etc.), by default
            ``BookSearch.TITLE``.
        page : int, optional
            The page number for pagination, by default 1.

        Returns
        -------
        Pagination[BookSearchResult]
            A paginated list of search results.

        Raises
        ------
        ParsingError
            If the HTML structure changes and parsing fails.

        Examples
        --------
        >>> service.search("Duna").results[0].title
        'Duna'
        """
        url = f"{self.base_url}/livro/lista/busca:{query}/tipo:{search_by.value}/mpage:{page}"
        logger.info(f"Searching for books with query: '{query}' on page {page}")
        try:
            response = self.client.get(url)
            soup = self.parse_html(response.text)

            limit = 30
            results: list[BookSearchResult | None] = [
                self._parse_search_result(book_div) for book_div in safe_find_all(soup, "div", {"class": "box_lista_busca_vertical"})
            ]
            cleaned_results: list[BookSearchResult] = [i for i in results if i]

            total_results = self._extract_total_results(soup)
            next_page_link = True if page * limit < total_results else False
        except (AttributeError, ValueError, IndexError, TypeError) as e:
            logger.error(f"Failed to parse book search results: {e}", exc_info=True)
            raise ParsingError("Failed to parse book search results.") from e
        except HTTPClientError as e:
            logger.error(
                f"HTTP error occurred during book search: {e}",
                exc_info=True,
            )
            raise ParsingError(
                "HTTP error occurred during book search."
            ) from e

        logger.info(
            "Found %s books on page %s, total %s results.",
            len(results),
            page,
            total_results,
        )
        return Pagination[BookSearchResult](
            results=cleaned_results,
            limit=30,
            page=page,
            total=total_results,
            has_next_page=next_page_link,
        )

    def get_by_id(self, edition_id: int) -> Book:
        """
        Retrieves a book by its edition ID.

        Parameters
        ----------
        edition_id : int
            The edition ID of the book.

        Returns
        -------
        Book
            Book object populated with detailed information.

        Raises
        ------
        FileNotFoundError
            If no book is found with the given edition_id.
        ParsingError
            If parsing or HTTP errors occur.

        Examples
        --------
        >>> service.get_by_id(1).title
        'Some Book'
        """
        logger.info(f"Getting book by edition_id: {edition_id}")
        url = f"{self.base_url}/v1/book/{edition_id}/stats:true"
        try:
            response = self.client.get(url)
            json_data = response.json().get("response")
            if not json_data:
                cod_description = response.json().get("cod_description", "No description provided.")
                error_msg = f"No data found for edition_id {edition_id}. Description: {cod_description}"
                logger.warning(error_msg)
                raise FileNotFoundError(error_msg)
            self._clean_book_json_data(json_data)
            book = Book.model_validate(json_data)
            logger.info(
                "Successfully retrieved book: '%s' (Edition ID: %s)",
                book.title,
                edition_id,
            )
            return book
        except FileNotFoundError:
            raise
        except HTTPClientError as e:
            logger.error(
                f"HTTP error retrieving book for edition_id {edition_id}: {e}",
                exc_info=True,
            )
            raise ParsingError(
                f"HTTP error retrieving book for edition_id {edition_id}."
            ) from e
        except (KeyError, ValueError, TypeError) as e:
            logger.error(
                f"Failed to parse book data for edition_id {edition_id}: {e}",
                exc_info=True,
            )
            raise ParsingError(
                f"Failed to parse book data for edition_id {edition_id}."
            ) from e

    def get_reviews(self, book_id: int, edition_id: int | None = None, page: int = 1) -> Pagination[BookReview]:
        """
        Retrieves reviews for a book.

        Parameters
        ----------
        book_id : int
            Book ID for which to retrieve reviews.
        edition_id : int or None, optional
            Specific edition ID, or auto-detected if None.
        page : int, optional
            Page number for pagination, by default 1.

        Returns
        -------
        Pagination[BookReview]
            A paginated list of reviews for the book.

        Raises
        ------
        ParsingError
            If the HTML structure changes or parsing fails.

        Examples
        --------
        >>> service.get_reviews(123).results
        [...]
        """
        url = f"{self.base_url}/livro/resenhas/{book_id}/mpage:{page}/limit:50"
        if edition_id:
            url += f"/edition:{edition_id}"
        logger.info(f"Getting reviews for book_id: {book_id}, page: {page}")
        try:
            response = self.client.get(url)
            soup = self.parse_html(response.text)
            if edition_id is None:
                edition_id = self._extract_edition_id_from_reviews_page(soup)
            book_reviews = [
                review
                for review in (
                    self._parse_review(r, book_id, edition_id) for r in safe_find_all(soup, "div", {"id": re.compile(r"resenha\d+")})
                )
                if review is not None
            ]
            next_page_link = safe_find(soup, "a", {"class": "proximo"})
        except (AttributeError, ValueError, IndexError, TypeError) as e:
            logger.error(f"Failed to parse book reviews: {e}", exc_info=True)
            raise ParsingError("Failed to parse book reviews.") from e
        except HTTPClientError as e:
            logger.error(
                f"HTTP error occurred during review fetching: {e}",
                exc_info=True,
            )
            raise ParsingError(
                "HTTP error occurred during review fetching."
            ) from e

        logger.info(f"Found {len(book_reviews)} reviews on page {page}.")
        return Pagination[BookReview](
            results=book_reviews,
            limit=50,
            page=page,
            total=len(book_reviews),
            has_next_page=next_page_link is not None,
        )

    def get_users_by_status(
        self,
        book_id: int,
        status: BookUserStatus,
        edition_id: int | None = None,
        limit: int = 500,
        page: int = 1,
    ) -> Pagination[int]:
        """
        Retrieves users who have a book with a specific status.

        Parameters
        ----------
        book_id : int
            The ID of the book.
        status : BookUserStatus
            The status of the book in the user's shelf.
        edition_id : int or None, optional
            The edition ID of the book, by default None.
        limit : int, optional
            The number of users to retrieve per page, by default 500.
        page : int, optional
            The page number for pagination, by default 1.

        Returns
        -------
        Pagination[int]
            A paginated list of user IDs.

        Raises
        ------
        ParsingError
            If the HTML structure changes and parsing fails.

        Examples
        --------
        >>> service.get_users_by_status(1, BookUserStatus.READERS).results[:3]
        [1, 2, 3]
        """
        url = f"{self.base_url}/livro/leitores/{status.value}/{book_id}/limit:{limit}/page:{page}"
        if edition_id:
            url += f"/edition:{edition_id}"
        logger.info(
            "Getting users for book_id: %s with status '%s' on page %s",
            book_id,
            status.value,
            page,
        )
        try:
            response = self.client.get(url)
            soup = self.parse_html(response.text)
            users_id = self._extract_user_ids_from_html(soup)
            next_page_link = safe_find(soup, "a", {"class": "proximo"})
        except (AttributeError, ValueError, IndexError, TypeError) as e:
            logger.error(f"Failed to parse users by status: {e}", exc_info=True)
            raise ParsingError("Failed to parse users by status.") from e
        except HTTPClientError as e:
            logger.error(
                "HTTP error occurred during user status fetching: %s",
                e,
                exc_info=True,
            )
            raise ParsingError(
                "HTTP error occurred during user status fetching."
            ) from e
        logger.info(
            "Found %s users on page %s.",
            len(users_id),
            page,
        )
        return Pagination[int](
            results=users_id,
            limit=limit,
            page=page,
            total=len(users_id),
            has_next_page=next_page_link is not None,
        )

    def _extract_user_ids_from_html(self, soup) -> list[int]:
        """
        Extracts user IDs from the user list HTML soup.

        Parameters
        ----------
        soup : Tag
            BeautifulSoup Tag containing the user list.

        Returns
        -------
        list of int
            List of user IDs found on the page.

        Examples
        --------
        >>> html = (
        ...     "<div class='livro-leitor-container'>"
        ...     "<a href='/usuario/1-name'></a></div>"
        ... )
        >>> service._extract_user_ids_from_html(
        ...     BeautifulSoup(html, 'html.parser')
        ... )
        [1]
        """
        users_html = safe_find_all(soup, "div", {"class": "livro-leitor-container"})
        users_id = []
        for user_div in users_html:
            user_link = safe_find(user_div, "a")
            href = get_tag_attr(user_link, "href")
            if href:
                user_id = get_user_id_from_url(href)
                if user_id:
                    users_id.append(int(user_id))
                else:
                    logger.warning(f"Could not extract user ID from URL: {href}")
            else:
                logger.warning("Skipping user_div due to missing 'a' tag or href attribute.")
        return users_id

    def _extract_edition_id_from_reviews_page(self, soup) -> int | None:
        """
        Extracts the edition ID from the reviews page if not provided.

        Parameters
        ----------
        soup : Tag
            BeautifulSoup object of the reviews page.

        Returns
        -------
        int or None
            Edition ID or None if not found.

        Examples
        --------
        >>> html = (
        ...     "<div id='pg-livro-menu-principal-container'>"
        ...     "<a href='/livro/1-ed3'></a></div>"
        ... )
        >>> service._extract_edition_id_from_reviews_page(
        ...     BeautifulSoup(html, 'html.parser')
        ... )
        3
        """
        menu_div = safe_find(soup, "div", {"id": "pg-livro-menu-principal-container"})
        menu_div_a = safe_find(menu_div, "a") if menu_div else None
        href = get_tag_attr(menu_div_a, "href")
        if href:
            extracted_edition_id = get_book_edition_id_from_url(href)
            if extracted_edition_id:
                return int(extracted_edition_id)
            else:
                logger.warning(f"Could not extract edition_id from URL: {href}")
        return None

    def _parse_review(
        self,
        r: Tag,
        book_id: int,
        edition_id: int | None,
    ) -> BookReview | None:
        """
        Parses a single review div into a BookReview object.

        Parameters
        ----------
        r : Tag
            BeautifulSoup Tag for the review.
        book_id : int
            The book ID.
        edition_id : int or None
            The edition ID.

        Returns
        -------
        BookReview or None
            Parsed review or None if incomplete.

        Examples
        --------
        >>> html = "<div id='resenha1'></div>"
        >>> service._parse_review(
        ...     BeautifulSoup(html, 'html.parser'),
        ...     1,
        ...     None,
        ... )
        ... # doctest: +ELLIPSIS
        """
        review_id_str = get_tag_attr(r, "id")
        review_id = int(review_id_str.replace("resenha", "")) if review_id_str else None
        if review_id is None:
            logger.warning(f"Skipping review due to missing or invalid ID: {get_tag_attr(r, 'id')}")
            return None
        user_link = safe_find(r, "a", {"href": re.compile(r"/usuario/")})
        user_url = get_tag_attr(user_link, "href")
        user_id = int(get_user_id_from_url(user_url)) if user_url else None
        if user_id is None:
            logger.warning(f"Skipping review {review_id} due to missing user ID.")
            return None
        star_tag = safe_find(r, "star-rating")
        rating = float(get_tag_attr(star_tag, "rate")) if star_tag and get_tag_attr(star_tag, "rate") else 0.0
        comment_div = safe_find(r, "div", {"id": re.compile(r"resenhac\d+")})
        date, review_text = self._extract_review_date_and_text(comment_div, review_id)
        return BookReview(
            review_id=review_id,
            book_id=book_id,
            edition_id=edition_id,
            user_id=user_id,
            rating=rating,
            review_text=review_text,
            reviewed_at=date,
        )

    def _extract_review_date_and_text(self, comment_div: Tag | None, review_id: int) -> tuple[datetime | None, str]:
        """
        Extracts the review date and text from the comment div.

        Parameters
        ----------
        comment_div : Tag
            BeautifulSoup Tag containing the review comment.
        review_id : int
            ID of the review (for logging purposes).

        Returns
        -------
        tuple of (datetime or None, str)
            Parsed review date (if found) and review text.

        Examples
        --------
        >>> soup = BeautifulSoup(
        ...     '<span>01/01/2020</span> Great',
        ...     'html.parser',
        ... )
        >>> service._extract_review_date_and_text(soup, 1)[1]
        'Great'
        """
        date = None
        review_text = ""
        if comment_div:
            date_span = safe_find(comment_div, "span")
            date_text = get_tag_text(date_span, strip=True)
            if date_text:
                try:
                    date = datetime.strptime(date_text, "%d/%m/%Y")
                except ValueError:
                    logger.warning(f"Could not parse date '{date_text}' for review {review_id}. Setting to None.")
            content_parts = []
            if date_span:
                for sibling in date_span.next_siblings:
                    if isinstance(sibling, Tag):
                        content_parts.append(sibling.get_text(separator="\n", strip=True))
                    elif isinstance(sibling, str):
                        stripped_text = sibling.strip()
                        if stripped_text:
                            content_parts.append(stripped_text)
            else:
                content_parts.append(comment_div.get_text(separator="\n", strip=True))
            review_text = "\n".join(filter(None, content_parts)).strip()
        return date, review_text

    def _parse_search_result(self, book_div: Tag) -> BookSearchResult | None:
        """
        Parses a single book search result div into a BookSearchResult object.

        Parameters
        ----------
        book_div : Tag
            BeautifulSoup Tag for a single search result.

        Returns
        -------
        BookSearchResult or None
            Parsed result or None if data is incomplete.

        Examples
        --------
        >>> html = "<a class='capa-link-item' title='X' href='/livro/1-ed2'></a>"
        >>> service._parse_search_result(BeautifulSoup(html, 'html.parser'))
        BookSearchResult(...)
        """
        container = safe_find(book_div, "a", {"class": "capa-link-item"})
        if not container:
            logger.warning("Skipping book_div due to missing 'capa-link-item' container.")
            return None

        title = get_tag_attr(container, "title")
        book_url = f"{self.base_url}{get_tag_attr(container, 'href')}"
        img_url = self._extract_img_url(container)
        try:
            book_id = int(get_book_id_from_url(book_url))
            edition_id = int(get_book_edition_id_from_url(book_url))
        except ValueError:
            logger.warning(
                f"Skipping book_div due to invalid book/edition id in url: {book_url}"
            )
            return None

        publisher, isbn = self._extract_publisher_and_isbn(book_div)
        rating = self._extract_rating(book_div, title)
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

    def _extract_img_url(self, container: Tag) -> str:
        """
        Extracts the image URL from the book cover container.

        Parameters
        ----------
        container : Tag
            BeautifulSoup Tag for the image container.

        Returns
        -------
        str
            URL of the book cover image or an empty string if not found.

        Examples
        --------
        >>> html = "<a><img src='https://img.com/c.jpg'></a>"
        >>> service._extract_img_url(BeautifulSoup(html, 'html.parser').a)
        'https://img.com/c.jpg'
        """
        if container.img and isinstance(container.img, Tag):
            src = get_tag_attr(container.img, "src")
            if src and "https" in src:
                return f"https{src.split('https')[-1].strip()}"
        return ""

    def _extract_publisher_and_isbn(self, book_div: Tag) -> tuple[str | None, str | None]:
        """
        Extracts publisher and ISBN information from a book search result div.

        Parameters
        ----------
        book_div : Tag
            BeautifulSoup Tag for the book search result.

        Returns
        -------
        tuple of (str or None, str or None)
            Publisher and ISBN string or None if not found.

        Examples
        --------
        >>> html = "<div class='detalhes-2-sub'><div><span>Editora</span></div></div>"
        >>> service._extract_publisher_and_isbn(BeautifulSoup(html, 'html.parser'))
        ('Editora', None)
        """
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

    def _extract_rating(self, book_div: Tag, title: str) -> float | None:
        """
        Extracts the rating value from a search result div.

        Parameters
        ----------
        book_div : Tag
            BeautifulSoup Tag for the book search result.
        title : str
            Title of the book (for logging purposes).

        Returns
        -------
        float or None
            The rating or None if not found or parsing fails.

        Examples
        --------
        >>> html = "<div class='star-mini'><strong>4,5</strong></div>"
        >>> service._extract_rating(BeautifulSoup(html, 'html.parser'), 'Example')
        4.5
        """
        star_mini = safe_find(book_div, "div", {"class": "star-mini"})
        if star_mini:
            strong_tag = safe_find(star_mini, "strong")
            rating_text = get_tag_text(strong_tag)
            if rating_text:
                try:
                    return float(rating_text.replace(",", "."))
                except ValueError:
                    logger.warning(f"Could not parse rating '{rating_text}' for book '{title}'. Setting to None.")
        return None

    def _extract_total_results(self, soup) -> int:
        """
        Extracts the total number of search results from the soup.

        Parameters
        ----------
        soup : Tag
            Parsed BeautifulSoup object of the search result page.

        Returns
        -------
        int
            Total number of results, or 0 if not found.

        Examples
        --------
        >>> service._extract_total_results(BeautifulSoup("<div class='contador'>1 encontrados</div>", 'html.parser'))
        1
        """
        total_results_tag = safe_find(soup, "div", {"class": "contador"})
        if total_results_tag:
            total_results_text = get_tag_text(total_results_tag)
            match = re.search(r"(\d+)\s+encontrados", total_results_text)
            if match:
                return int(match.group(1))
        return 0

    def _clean_book_json_data(self, json_data: dict) -> None:
        """
        Cleans and normalizes the JSON data returned from the API before model validation.

        Parameters
        ----------
        json_data : dict
            Dictionary from the API response, modified in place.

        Returns
        -------
        None

        Examples
        --------
        >>> data = {"url": "/book", "isbn": "0"}
        >>> service._clean_book_json_data(data)
        >>> data["cover_url"]
        ''
        """
        json_data["url"] = f"{self.base_url}{json_data['url']}"
        json_data["isbn"] = None if str(json_data.get("isbn", "0")) == "0" else json_data["isbn"]
        json_data["autor"] = None if json_data.get("autor", "").lower() == "não especificado" else json_data["autor"]
        json_data["serie"] = json_data.get("serie") or None
        json_data["volume"] = None if not json_data.get("volume") or str(json_data["volume"]) == "0" else str(json_data["volume"])
        json_data["mes"] = None if not json_data.get("mes") or str(json_data["mes"]).strip() == "" else json_data["mes"]
        img_url = json_data.get("img_url", "")
        json_data["cover_url"] = f"https{img_url.split('https')[-1].strip()}" if img_url and "https" in img_url else ""
        generos = json_data.get("generos")
        json_data["generos"] = generos if generos else None

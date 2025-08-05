"""Services for searching and retrieving books from Skoob."""

import logging
import re

from pydantic import ValidationError

from pyskoob.exceptions import ParsingError, RequestError
from pyskoob.http.client import AsyncHTTPClient
from pyskoob.internal.async_base import AsyncBaseSkoobService
from pyskoob.internal.base import BaseSkoobService
from pyskoob.models.book import Book, BookReview, BookSearchResult
from pyskoob.models.enums import BookSearch, BookUserStatus
from pyskoob.models.pagination import Pagination
from pyskoob.parsers.books import (
    clean_book_json_data,
    extract_edition_id_from_reviews_page,
    extract_total_results,
    extract_user_ids_from_html,
    parse_review,
    parse_search_result,
)
from pyskoob.utils.bs4_utils import (
    safe_find,
    safe_find_all,
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
        RequestError
            If the HTTP request fails.
        ParsingError
            If the HTML structure changes and parsing fails.

        Examples
        --------
        >>> service.search("Duna").results[0].title
        'Duna'
        """
        url = f"{self.base_url}/livro/lista/busca:{query}/tipo:{search_by.value}/mpage:{page}"
        logger.info("Searching for books with query: '%s' on page %s", query, page)
        try:
            response = self.client.get(url)
            response.raise_for_status()
        except Exception as e:
            logger.error("Request error during book search: %s", e, exc_info=True)
            raise RequestError("Failed to search books.") from e

        try:
            soup = self.parse_html(response.text)
            limit = 30
            results = [
                parse_search_result(book_div, self.base_url)
                for book_div in safe_find_all(soup, "div", {"class": "box_lista_busca_vertical"})
            ]
            cleaned_results: list[BookSearchResult] = [i for i in results if i]
            total_results = extract_total_results(soup)
            next_page_link = True if page * limit < total_results else False
        except (AttributeError, ValueError, IndexError, TypeError) as e:  # pragma: no cover - defensive
            logger.error("Failed to parse book search results: %s", e, exc_info=True)
            raise ParsingError("Failed to parse book search results.") from e
        except Exception as e:  # pragma: no cover - unexpected
            logger.error(
                "An unexpected error occurred during book search: %s",
                e,
                exc_info=True,
            )
            raise ParsingError("An unexpected error occurred during book search.") from e

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
        RequestError
            If the HTTP request fails.
        ParsingError
            If parsing of the response fails.

        Examples
        --------
        >>> service.get_by_id(1).title
        'Some Book'
        """
        logger.info("Getting book by edition_id: %s", edition_id)
        url = f"{self.base_url}/v1/book/{edition_id}/stats:true"
        try:
            response = self.client.get(url)
            response.raise_for_status()
        except Exception as e:
            logger.error(
                "Request error retrieving book for edition_id %s: %s",
                edition_id,
                e,
                exc_info=True,
            )
            raise RequestError(f"Failed to retrieve book for edition_id {edition_id}.") from e

        try:
            data = response.json()
            json_data = data.get("response")
            if not json_data:
                cod_description = data.get("cod_description", "No description provided.")
                error_msg = f"No data found for edition_id {edition_id}. Description: {cod_description}"
                logger.warning(error_msg)
                raise FileNotFoundError(error_msg)
            json_data = clean_book_json_data(json_data, self.base_url)
            book = Book.model_validate(json_data)
            logger.info(
                "Successfully retrieved book: '%s' (Edition ID: %s)",
                book.title,
                edition_id,
            )
            return book
        except FileNotFoundError:
            raise
        except (AttributeError, ValueError, IndexError, TypeError, ValidationError) as e:  # pragma: no cover - defensive
            logger.error(
                "Failed to parse book for edition_id %s: %s",
                edition_id,
                e,
                exc_info=True,
            )
            raise ParsingError(f"Failed to retrieve book for edition_id {edition_id}.") from e

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
        logger.info("Getting reviews for book_id: %s, page: %s", book_id, page)
        try:
            response = self.client.get(url)
            response.raise_for_status()
            soup = self.parse_html(response.text)
            if edition_id is None:
                edition_id = extract_edition_id_from_reviews_page(soup)
            book_reviews = [
                review
                for review in (parse_review(r, book_id, edition_id) for r in safe_find_all(soup, "div", {"id": re.compile(r"resenha\d+")}))
                if review is not None
            ]
            next_page_link = safe_find(soup, "a", {"class": "proximo"})
        except (AttributeError, ValueError, IndexError, TypeError) as e:  # pragma: no cover - defensive
            logger.error("Failed to parse book reviews: %s", e, exc_info=True)
            raise ParsingError("Failed to parse book reviews.") from e
        except Exception as e:  # pragma: no cover - unexpected
            logger.error(
                "An unexpected error occurred during review fetching: %s",
                e,
                exc_info=True,
            )
            raise ParsingError("An unexpected error occurred during review fetching.") from e
        logger.info("Found %s reviews on page %s.", len(book_reviews), page)
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
            response.raise_for_status()
            soup = self.parse_html(response.text)
            users_id = extract_user_ids_from_html(soup)
            next_page_link = safe_find(soup, "a", {"class": "proximo"})
        except (AttributeError, ValueError, IndexError, TypeError) as e:  # pragma: no cover - defensive
            logger.error("Failed to parse users by status: %s", e, exc_info=True)
            raise ParsingError("Failed to parse users by status.") from e
        except Exception as e:  # pragma: no cover - unexpected
            logger.error(
                "An unexpected error occurred during user status fetching: %s",
                e,
                exc_info=True,
            )
            raise ParsingError("An unexpected error occurred during user status fetching.") from e
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


class AsyncBookService(AsyncBaseSkoobService):  # pragma: no cover - thin async wrapper
    """Asynchronous variant of :class:`BookService`."""

    def __init__(self, client: AsyncHTTPClient):
        super().__init__(client)

    async def search(self, query: str, search_by: BookSearch = BookSearch.TITLE, page: int = 1) -> Pagination[BookSearchResult]:
        """Asynchronously search for books by query and type.

        Parameters
        ----------
        query : str
            The search query string.
        search_by : BookSearch, optional
            Type of search (title, author, etc.), by default ``BookSearch.TITLE``.
        page : int, optional
            Page number for pagination, by default ``1``.

        Returns
        -------
        Pagination[BookSearchResult]
            Paginated list of search results.
        """

        url = f"{self.base_url}/livro/lista/busca:{query}/tipo:{search_by.value}/mpage:{page}"
        logger.info("Searching for books with query: '%s' on page %s", query, page)
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            soup = self.parse_html(response.text)
            limit = 30
            results = [
                parse_search_result(book_div, self.base_url)
                for book_div in safe_find_all(soup, "div", {"class": "box_lista_busca_vertical"})
            ]
            cleaned_results: list[BookSearchResult] = [i for i in results if i]
            total_results = extract_total_results(soup)
            next_page_link = True if page * limit < total_results else False
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
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to search books: %s", exc, exc_info=True)
            return Pagination[BookSearchResult](
                results=[],
                limit=30,
                page=page,
                total=0,
                has_next_page=False,
            )

    async def get_by_id(self, edition_id: int) -> Book:
        """Retrieve a book by its edition ID asynchronously.

        Parameters
        ----------
        edition_id : int
            The edition identifier of the book.

        Returns
        -------
        Book
            The book details for the given edition.
        """

        logger.info("Getting book by edition_id: %s", edition_id)
        url = f"{self.base_url}/v1/book/{edition_id}/stats:true"
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            json_data = data.get("response")
            if not json_data:
                cod_description = data.get("cod_description", "No description provided.")
                error_msg = f"No data found for edition_id {edition_id}. Description: {cod_description}"
                logger.warning(error_msg)
                raise FileNotFoundError(error_msg)
            json_data = clean_book_json_data(json_data, self.base_url)
            book = Book.model_validate(json_data)
            logger.info(
                "Successfully retrieved book: '%s' (Edition ID: %s)",
                book.title,
                edition_id,
            )
            return book
        except FileNotFoundError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            logger.error(
                "Failed to retrieve book for edition_id %s: %s",
                edition_id,
                exc,
                exc_info=True,
            )
            raise ParsingError("Failed to retrieve book.") from exc

    async def get_reviews(self, book_id: int, edition_id: int | None = None, page: int = 1) -> Pagination[BookReview]:
        """Retrieve book reviews asynchronously.

        Parameters
        ----------
        book_id : int
            Identifier of the book.
        edition_id : int, optional
            Specific edition to filter reviews, by default ``None``.
        page : int, optional
            Pagination page, by default ``1``.

        Returns
        -------
        Pagination[BookReview]
            Paginated list of book reviews.
        """

        url = f"{self.base_url}/livro/resenhas/{book_id}/mpage:{page}/limit:50"
        if edition_id:
            url += f"/edition:{edition_id}"
        logger.info("Getting reviews for book_id: %s, page: %s", book_id, page)
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            soup = self.parse_html(response.text)
            if edition_id is None:
                edition_id = extract_edition_id_from_reviews_page(soup)
            book_reviews = [
                review
                for review in (parse_review(r, book_id, edition_id) for r in safe_find_all(soup, "div", {"id": re.compile(r"resenha\d+")}))
                if review is not None
            ]
            next_page_link = safe_find(soup, "a", {"class": "proximo"})
            logger.info("Found %s reviews on page %s.", len(book_reviews), page)
            return Pagination[BookReview](
                results=book_reviews,
                limit=50,
                page=page,
                total=len(book_reviews),
                has_next_page=next_page_link is not None,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error(
                "Failed to retrieve book reviews for book_id %s: %s",
                book_id,
                exc,
                exc_info=True,
            )
            raise ParsingError("Failed to retrieve book reviews.") from exc

    async def get_users_by_status(
        self,
        book_id: int,
        status: BookUserStatus,
        edition_id: int | None = None,
        limit: int = 500,
        page: int = 1,
    ) -> Pagination[int]:
        """Retrieve user IDs who marked the book with a given status.

        Parameters
        ----------
        book_id : int
            Identifier of the book.
        status : BookUserStatus
            User status to filter by (read, reading, etc.).
        edition_id : int, optional
            Specific edition to filter, by default ``None``.
        limit : int, optional
            Maximum number of users per page, by default ``500``.
        page : int, optional
            Page number for pagination, by default ``1``.

        Returns
        -------
        Pagination[int]
            Paginated list of user IDs.
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
            response = await self.client.get(url)
            response.raise_for_status()
            soup = self.parse_html(response.text)
            users_id = extract_user_ids_from_html(soup)
            next_page_link = safe_find(soup, "a", {"class": "proximo"})
            logger.info("Found %s users on page %s.", len(users_id), page)
            return Pagination[int](
                results=users_id,
                limit=limit,
                page=page,
                total=len(users_id),
                has_next_page=next_page_link is not None,
            )
        except (AttributeError, ValueError, IndexError, TypeError) as exc:  # pragma: no cover - defensive
            logger.error("Failed to parse users by status: %s", exc, exc_info=True)
            raise ParsingError("Failed to parse users by status.") from exc
        except Exception as exc:  # pragma: no cover - unexpected
            logger.error(
                "An unexpected error occurred while retrieving users by status: %s",
                exc,
                exc_info=True,
            )
            raise ParsingError("An unexpected error occurred while retrieving users by status.") from exc

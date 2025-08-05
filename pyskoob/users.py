"""Services for retrieving and manipulating Skoob user data."""

import logging
import re
from datetime import datetime

from bs4 import BeautifulSoup

from pyskoob.auth import AsyncAuthService, AuthService
from pyskoob.exceptions import ParsingError
from pyskoob.http.client import AsyncHTTPClient, SyncHTTPClient
from pyskoob.internal.async_authenticated import AsyncAuthenticatedService
from pyskoob.internal.authenticated import AuthenticatedService
from pyskoob.models.book import BookReview
from pyskoob.models.enums import (
    BookcaseOption,
    BrazilianState,
    UserGender,
    UsersRelation,
)
from pyskoob.models.pagination import Pagination
from pyskoob.models.user import User, UserBook, UserReadStats, UserSearch
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


class UserService(AuthenticatedService):
    """Fetch user profiles, books and friends from Skoob."""

    def __init__(self, client: SyncHTTPClient, auth_service: AuthService):
        """Initialize the service with dependencies.

        The service depends on :class:`AuthService` to validate the current
        session before performing operations that require authentication such
        as retrieving your own profile or editing bookshelf information.

        Parameters
        ----------
        client : SyncHTTPClient
            The HTTP client to use for requests.
        auth_service : AuthService
            The authentication service.
        """
        super().__init__(client, auth_service)

    def get_by_id(self, user_id: int) -> User:
        """
        Retrieves a user by their ID.

        Parameters
        ----------
        user_id : int
            The ID of the user.

        Returns
        -------
        User
            The user's information.

        Raises
        ------
        FileNotFoundError
            If the user with the given ID is not found.

        Examples
        --------
        >>> service.get_by_id(1).name
        'Example'
        """
        self._validate_login()
        logger.info(f"Getting user by id: {user_id}")
        url = f"{self.base_url}/v1/user/{user_id}/stats:true"
        response = self.client.get(url)
        response.raise_for_status()

        json_data = response.json()
        if not json_data.get("success"):
            logger.warning(f"User with ID {user_id} not found.")
            raise FileNotFoundError(f"User with ID {user_id} not found.")

        user_data = json_data["response"]
        user_data["profile_url"] = self.base_url + user_data["url"]  # patch field for alias
        user = User.model_validate(user_data)
        logger.info(f"Successfully retrieved user: '{user.name}'")
        return user

    def get_relations(self, user_id: int, relation: UsersRelation, page: int = 1) -> Pagination[int]:
        """
        Retrieves a user's relations (friends, followers, following).

        Parameters
        ----------
        user_id : int
            The ID of the user.
        relation : UsersRelation
            The type of relation to retrieve.
        page : int, optional
            The page number for pagination, by default 1.

        Returns
        -------
        Pagination[int]
            A paginated list of user IDs.

        Raises
        ------
        ParsingError
            If the HTML structure of the page changes and parsing fails.

        Examples
        --------
        >>> service.get_relations(1, UsersRelation.FRIENDS).results
        [2, 3]
        """
        self._validate_login()
        url = f"{self.base_url}/{relation.value}/listar/{user_id}/page:{page}/limit:100"
        logger.info(f"Getting '{relation.value}' for user_id: {user_id}, page: {page}")
        response = self.client.get(url)
        response.raise_for_status()

        soup = self.parse_html(response.text)
        try:
            users_html = safe_find_all(soup, "div", {"class": "usuarios-mini-lista-txt"})
            users_id = [int(get_user_id_from_url(get_tag_attr(i.a, "href"))) for i in users_html if i.find("a") and getattr(i, "a", None)]
            next_page_link = safe_find(soup, "div", {"class": "proximo"})
        except (AttributeError, ValueError, IndexError) as e:  # pragma: no cover - defensive
            logger.error(f"Failed to parse user relations: {e}")
            raise ParsingError("Failed to parse user relations.") from e

        logger.info(f"Found {len(users_id)} users on page {page}.")
        return Pagination(
            results=users_id,
            limit=100,
            page=page,
            total=len(users_id),  # Placeholder, actual total is not easily available
            has_next_page=bool(next_page_link),
        )

    def get_reviews(self, user_id: int, page: int = 1) -> Pagination[BookReview]:
        """
        Retrieves reviews made by a user.

        Parameters
        ----------
        user_id : int
            The ID of the user.
        page : int, optional
            The page number for pagination, by default 1.

        Returns
        -------
        Pagination[BookReview]
            A paginated list of book reviews.

        Raises
        ------
        ParsingError
            If the HTML structure of the page changes and parsing fails.
        """
        self._validate_login()
        url = f"{self.base_url}/estante/resenhas/{user_id}/mpage:{page}/limit:50"
        logger.info(f"Getting reviews for user_id: {user_id}, page: {page}")
        response = self.client.get(url)
        response.raise_for_status()

        user_reviews: list[BookReview] = []
        soup = self.parse_html(response.text)
        try:
            reviews_html = safe_find_all(soup, "div", {"id": re.compile(r"resenha\d+")})
            for review_elem in reviews_html:
                review_id = int(get_tag_attr(review_elem, "id").replace("resenha", ""))
                book_anchor = safe_find(review_elem, "a", {"href": re.compile(r".*\d+ed\d+.html")})
                book_url = get_tag_attr(book_anchor, "href")
                book_id = int(get_book_id_from_url(book_url))
                edition_id = int(get_book_edition_id_from_url(book_url))
                star_rating = safe_find(review_elem, "star-rating")
                rating = float(get_tag_attr(star_rating, "rate", "0"))
                comment = safe_find(review_elem, "div", {"id": re.compile(r"resenhac\d+")})
                date_str = get_tag_text(safe_find(comment, "span"))
                date = None
                if date_str:
                    try:
                        date = datetime.strptime(date_str, "%d/%m/%Y")
                    except ValueError:
                        date = None
                review_text = ""
                if comment:
                    span = safe_find(comment, "span")
                    if span:
                        siblings = [get_tag_text(sib) for sib in span.next_siblings if hasattr(sib, "get_text")]
                        review_text = "\n".join(siblings).strip()
                user_reviews.append(
                    BookReview(
                        review_id=review_id,
                        book_id=book_id,
                        edition_id=edition_id,
                        user_id=user_id,
                        rating=rating,
                        review_text=review_text,
                        reviewed_at=date,
                    )
                )
            next_page_link = safe_find(soup, "a", {"string": " Próxima"})
        except (AttributeError, ValueError, IndexError) as e:  # pragma: no cover - defensive
            logger.error(f"Failed to parse user reviews: {e}")
            raise ParsingError("Failed to parse user reviews.") from e

        logger.info(f"Found {len(user_reviews)} reviews on page {page}.")
        return Pagination(
            results=user_reviews,
            limit=50,
            page=page,
            total=len(user_reviews),  # Placeholder, actual total is not easily available
            has_next_page=bool(next_page_link),
        )

    def get_read_stats(self, user_id: int) -> UserReadStats:
        """
        Retrieves reading statistics for a user.

        Parameters
        ----------
        user_id : int
            The ID of the user.

        Returns
        -------
        UserReadStats
            The user's reading statistics.
        """
        self._validate_login()
        logger.info(f"Getting read stats for user_id: {user_id}")
        url = f"{self.base_url}/v1/meta_stats/{user_id}"

        response = self.client.get(url)
        response.raise_for_status()

        json_data = response.json().get("response", {})

        stats = UserReadStats(
            user_id=user_id,
            year=json_data.get("ano"),
            books_read=json_data.get("lido"),
            pages_read=json_data.get("paginas_lidas"),
            total_pages=json_data.get("paginas_total"),
            percent_complete=json_data.get("percentual_lido"),
            books_total=json_data.get("total"),
            reading_speed=json_data.get("velocidade_dia"),
            ideal_reading_speed=json_data.get("velocidade_ideal"),
        )
        logger.info(f"Successfully retrieved read stats for user_id: {user_id}")
        return stats

    def get_bookcase(self, user_id: int, bookcase_option: BookcaseOption, page: int = 1) -> Pagination[UserBook]:
        """
        Retrieves a user's bookcase.

        Parameters
        ----------
        user_id : int
            The ID of the user.
        bookcase_option : BookcaseOption
            The type of bookcase to retrieve.
        page : int, optional
            The page number for pagination, by default 1.

        Returns
        -------
        Pagination[UserBook]
            A paginated list of books in the user's bookcase.
        """
        self._validate_login()
        url = f"{self.base_url}/v1/bookcase/books/{user_id}/shelf_id:{bookcase_option.value}/page:{page}/limit:100"
        logger.info(f"Getting bookcase for user_id: {user_id}, option: '{bookcase_option.name}', page: {page}")
        response = self.client.get(url)
        response.raise_for_status()

        json_data = response.json()
        next_page = json_data.get("paging", {}).get("next_page")
        results = []
        for r in json_data.get("response", []):
            edicao = r.get("edicao", {})
            results.append(
                UserBook(
                    user_id=user_id,
                    book_id=edicao.get("livro_id"),
                    edition_id=edicao.get("id"),
                    rating=r.get("ranking"),
                    is_favorite=r.get("favorito"),
                    is_wishlist=r.get("desejado"),
                    is_tradable=r.get("troco"),
                    is_owned=r.get("tenho"),
                    is_loaned=r.get("emprestei"),
                    reading_goal_year=r.get("meta"),
                    pages_read=r.get("paginas_lidas"),
                )
            )

        logger.info(f"Found {len(results)} books on page {page}.")
        return Pagination(
            limit=100,
            results=results,
            total=len(results),  # Placeholder, actual total is not easily available
            has_next_page=bool(next_page),
            page=page,
        )

    def search(
        self,
        query: str,
        gender: UserGender | None = None,
        state: BrazilianState | None = None,
        page: int = 1,
        limit: int = 100,
    ) -> Pagination[UserSearch]:
        """Search for users on Skoob.

        Parameters
        ----------
        query : str
            The search query for usernames or names.
        gender : UserGender, optional
            Optional gender filter (M/F), by default ``None``.
        state : BrazilianState, optional
            Optional state filter (e.g., ``SP``), by default ``None``.
        page : int, optional
            Page number to fetch, by default ``1``.
        limit : int, optional
            Number of users per page, by default ``100``.

        Returns
        -------
        Pagination[UserSearch]
            A paginated list of users matching the criteria.

        Raises
        ------
        ParsingError
            If the HTML structure is invalid or parsing fails.

        Examples
        --------
        >>> service.search("example").page
        1
        """
        self._validate_login()

        url = f"{self.base_url}/usuario/lista/busca:{query}/mpage:{page}/limit:{limit}"
        if gender:
            url += f"/sexo:{gender.value}"
        if state:
            url += f"/uf:{state.value}"

        response = self.client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        try:
            user_divs = safe_find_all(
                soup,
                "div",
                attrs={"style": re.compile(r"border: 1px solid #e4e4e4")},
            )
            results: list[UserSearch] = []

            for div in user_divs:
                anchor = safe_find(div, "a", attrs={"href": re.compile(r"^/usuario/\d+-")})
                if not anchor:
                    continue  # pragma: no cover - defensive

                href = get_tag_attr(anchor, "href")
                full_url = f"{self.base_url}{href}"
                match = re.search(r"/usuario/(\d+)-([\w\.\-]+)", href)
                if not match:
                    continue  # pragma: no cover - defensive

                user_id = int(match.group(1))
                username = match.group(2)
                name = get_tag_text(anchor)

                logger.debug(
                    "User ID: %s / Username: %s / Name: %s / URL: %s",
                    user_id,
                    username,
                    name,
                    full_url,
                )

                results.append(
                    UserSearch(
                        id=user_id,
                        username=username,
                        name=name,
                        url=full_url,
                    )
                )

            total_tag = safe_find(soup, "div", {"class": "contador"})
            total_text = get_tag_text(total_tag)
            total = int(total_text.split("encontrados")[0].strip()) if "encontrados" in total_text else 0

            next_page = safe_find(soup, "a", {"class": "proximo"})
            has_next = next_page is not None

            return Pagination[UserSearch](
                results=results,
                page=page,
                total=total,
                limit=limit,
                has_next_page=has_next,
            )

        except Exception as e:  # pragma: no cover - defensive
            raise ParsingError("Failed to parse user search results.") from e


class AsyncUserService(AsyncAuthenticatedService):  # pragma: no cover - thin async wrapper
    """Asynchronous variant of :class:`UserService`.

    Fetch user profiles, books and friends from Skoob asynchronously.

    The service depends on :class:`AsyncAuthService` to validate the current
    session before performing operations that require authentication such as
    retrieving your own profile or editing bookshelf information.
    """

    def __init__(self, client: AsyncHTTPClient, auth_service: AsyncAuthService):
        super().__init__(client, auth_service)

    async def get_by_id(self, user_id: int) -> User:
        """Retrieve a user by their ID asynchronously.

        Parameters
        ----------
        user_id : int
            The ID of the user.

        Returns
        -------
        User
            The user's information.

        Raises
        ------
        FileNotFoundError
            If the user with the given ID is not found.
        """
        self._validate_login()
        logger.info(f"Getting user by id: {user_id}")
        url = f"{self.base_url}/v1/user/{user_id}/stats:true"
        response = await self.client.get(url)
        response.raise_for_status()
        json_data = response.json()
        if not json_data.get("success"):
            logger.warning(f"User with ID {user_id} not found.")
            raise FileNotFoundError(f"User with ID {user_id} not found.")
        user_data = json_data["response"]
        user_data["profile_url"] = self.base_url + user_data["url"]
        user = User.model_validate(user_data)
        logger.info(f"Successfully retrieved user: '{user.name}'")
        return user

    async def get_relations(self, user_id: int, relation: UsersRelation, page: int = 1) -> Pagination[int]:
        """Retrieve a user's relations (friends, followers, following).

        Parameters
        ----------
        user_id : int
            The ID of the user.
        relation : UsersRelation
            The type of relation to retrieve.
        page : int, optional
            The page number for pagination, by default ``1``.

        Returns
        -------
        Pagination[int]
            A paginated list of user IDs.

        Raises
        ------
        ParsingError
            If the HTML structure of the page changes and parsing fails.
        """
        self._validate_login()
        url = f"{self.base_url}/{relation.value}/listar/{user_id}/page:{page}/limit:100"
        logger.info(f"Getting '{relation.value}' for user_id: {user_id}, page: {page}")
        response = await self.client.get(url)
        response.raise_for_status()
        soup = self.parse_html(response.text)
        try:
            users_html = safe_find_all(soup, "div", {"class": "usuarios-mini-lista-txt"})
            users_id = [int(get_user_id_from_url(get_tag_attr(i.a, "href"))) for i in users_html if i.find("a") and getattr(i, "a", None)]
            next_page_link = safe_find(soup, "div", {"class": "proximo"})
        except (AttributeError, ValueError, IndexError) as e:
            logger.error(f"Failed to parse user relations: {e}")
            raise ParsingError("Failed to parse user relations.") from e
        logger.info(f"Found {len(users_id)} users on page {page}.")
        return Pagination(
            results=users_id,
            limit=100,
            page=page,
            total=len(users_id),
            has_next_page=bool(next_page_link),
        )

    async def get_reviews(self, user_id: int, page: int = 1) -> Pagination[BookReview]:
        """Retrieve reviews made by a user.

        Parameters
        ----------
        user_id : int
            The ID of the user.
        page : int, optional
            The page number for pagination, by default ``1``.

        Returns
        -------
        Pagination[BookReview]
            A paginated list of book reviews.

        Raises
        ------
        ParsingError
            If the HTML structure of the page changes and parsing fails.
        """
        self._validate_login()
        url = f"{self.base_url}/estante/resenhas/{user_id}/mpage:{page}/limit:50"
        logger.info(f"Getting reviews for user_id: {user_id}, page: {page}")
        response = await self.client.get(url)
        response.raise_for_status()
        user_reviews: list[BookReview] = []
        soup = self.parse_html(response.text)
        try:
            reviews_html = safe_find_all(soup, "div", {"id": re.compile(r"resenha\d+")})
            for review_elem in reviews_html:
                review_id = int(get_tag_attr(review_elem, "id").replace("resenha", ""))
                book_anchor = safe_find(review_elem, "a", {"href": re.compile(r".*\d+ed\d+.html")})
                book_url = get_tag_attr(book_anchor, "href")
                book_id = int(get_book_id_from_url(book_url))
                edition_id = int(get_book_edition_id_from_url(book_url))
                star_rating = safe_find(review_elem, "star-rating")
                rating = float(get_tag_attr(star_rating, "rate", "0"))
                comment = safe_find(review_elem, "div", {"id": re.compile(r"resenhac\d+")})
                date_str = get_tag_text(safe_find(comment, "span"))
                date = None
                if date_str:
                    try:
                        date = datetime.strptime(date_str, "%d/%m/%Y")
                    except ValueError:
                        date = None
                review_text = ""
                if comment:
                    span = safe_find(comment, "span")
                    if span:
                        siblings = [get_tag_text(sib) for sib in span.next_siblings if hasattr(sib, "get_text")]
                        review_text = "\n".join(siblings).strip()
                user_reviews.append(
                    BookReview(
                        review_id=review_id,
                        book_id=book_id,
                        edition_id=edition_id,
                        user_id=user_id,
                        rating=rating,
                        review_text=review_text,
                        reviewed_at=date,
                    )
                )
            next_page_link = safe_find(soup, "a", {"string": " Próxima"})
        except (AttributeError, ValueError, IndexError) as e:
            logger.error(f"Failed to parse user reviews: {e}")
            raise ParsingError("Failed to parse user reviews.") from e
        logger.info(f"Found {len(user_reviews)} reviews on page {page}.")
        return Pagination(
            results=user_reviews,
            limit=50,
            page=page,
            total=len(user_reviews),
            has_next_page=bool(next_page_link),
        )

    async def get_read_stats(self, user_id: int) -> UserReadStats:
        """Retrieve reading statistics for a user.

        Parameters
        ----------
        user_id : int
            The ID of the user.

        Returns
        -------
        UserReadStats
            The user's reading statistics.
        """
        self._validate_login()
        logger.info(f"Getting read stats for user_id: {user_id}")
        url = f"{self.base_url}/v1/meta_stats/{user_id}"
        response = await self.client.get(url)
        response.raise_for_status()
        json_data = response.json().get("response", {})
        stats = UserReadStats(
            user_id=user_id,
            year=json_data.get("ano"),
            books_read=json_data.get("lido"),
            pages_read=json_data.get("paginas_lidas"),
            total_pages=json_data.get("paginas_total"),
            percent_complete=json_data.get("percentual_lido"),
            books_total=json_data.get("total"),
            reading_speed=json_data.get("velocidade_dia"),
            ideal_reading_speed=json_data.get("velocidade_ideal"),
        )
        logger.info(f"Successfully retrieved read stats for user_id: {user_id}")
        return stats

    async def get_bookcase(self, user_id: int, bookcase_option: BookcaseOption, page: int = 1) -> Pagination[UserBook]:
        """Retrieve a user's bookcase.

        Parameters
        ----------
        user_id : int
            The ID of the user.
        bookcase_option : BookcaseOption
            The type of bookcase to retrieve.
        page : int, optional
            The page number for pagination, by default ``1``.

        Returns
        -------
        Pagination[UserBook]
            A paginated list of books in the user's bookcase.
        """
        self._validate_login()
        url = f"{self.base_url}/v1/bookcase/books/{user_id}/shelf_id:{bookcase_option.value}/page:{page}/limit:100"
        logger.info(f"Getting bookcase for user_id: {user_id}, option: '{bookcase_option.name}', page: {page}")
        response = await self.client.get(url)
        response.raise_for_status()
        json_data = response.json()
        next_page = json_data.get("paging", {}).get("next_page")
        results = []
        for r in json_data.get("response", []):
            edicao = r.get("edicao", {})
            results.append(
                UserBook(
                    user_id=user_id,
                    book_id=edicao.get("livro_id"),
                    edition_id=edicao.get("id"),
                    rating=r.get("ranking"),
                    is_favorite=r.get("favorito"),
                    is_wishlist=r.get("desejado"),
                    is_tradable=r.get("troco"),
                    is_owned=r.get("tenho"),
                    is_loaned=r.get("emprestei"),
                    reading_goal_year=r.get("meta"),
                    pages_read=r.get("paginas_lidas"),
                )
            )
        logger.info(f"Found {len(results)} books on page {page}.")
        return Pagination(
            limit=100,
            results=results,
            total=len(results),
            has_next_page=bool(next_page),
            page=page,
        )

    async def search(
        self,
        query: str,
        gender: UserGender | None = None,
        state: BrazilianState | None = None,
        page: int = 1,
        limit: int = 100,
    ) -> Pagination[UserSearch]:
        """Search for users on Skoob.

        Parameters
        ----------
        query : str
            The search query for usernames or names.
        gender : UserGender, optional
            Optional gender filter (M/F), by default ``None``.
        state : BrazilianState, optional
            Optional state filter, by default ``None``.
        page : int, optional
            Page number to fetch, by default ``1``.
        limit : int, optional
            Number of users per page, by default ``100``.

        Returns
        -------
        Pagination[UserSearch]
            A paginated list of users matching the criteria.

        Raises
        ------
        ParsingError
            If the HTML structure is invalid or parsing fails.
        """
        self._validate_login()
        url = f"{self.base_url}/usuario/lista/busca:{query}/mpage:{page}/limit:{limit}"
        if gender:
            url += f"/sexo:{gender.value}"
        if state:
            url += f"/uf:{state.value}"
        response = await self.client.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            user_divs = safe_find_all(
                soup,
                "div",
                attrs={"style": re.compile(r"border: 1px solid #e4e4e4")},
            )
            results: list[UserSearch] = []
            for div in user_divs:
                anchor = safe_find(div, "a", attrs={"href": re.compile(r"^/usuario/\d+-")})
                if not anchor:
                    continue
                href = get_tag_attr(anchor, "href")
                full_url = f"{self.base_url}{href}"
                match = re.search(r"/usuario/(\d+)-([\w\.\-]+)", href)
                if not match:
                    continue
                user_id = int(match.group(1))
                username = match.group(2)
                name = get_tag_text(anchor)
                results.append(
                    UserSearch(
                        id=user_id,
                        username=username,
                        name=name,
                        url=full_url,
                    )
                )
            total_tag = safe_find(soup, "div", {"class": "contador"})
            total_text = get_tag_text(total_tag)
            total = int(total_text.split("encontrados")[0].strip()) if "encontrados" in total_text else 0
            next_page = safe_find(soup, "a", {"class": "proximo"})
            has_next = next_page is not None
            return Pagination[UserSearch](
                results=results,
                page=page,
                total=total,
                limit=limit,
                has_next_page=has_next,
            )
        except Exception as e:  # pragma: no cover - unlikely
            raise ParsingError("Failed to parse user search results.") from e

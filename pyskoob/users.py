"""Services for retrieving and manipulating Skoob user data."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from datetime import datetime
from typing import Any

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
from pyskoob.utils.sync_async import maybe_await, run_sync

logger = logging.getLogger(__name__)


class _UserServiceMixin:
    """Shared user retrieval logic for sync and async services."""

    client: Any
    base_url: str
    parse_html: Callable[[str], Any]
    _validate_login: Callable[[], Any]

    async def _get_by_id(self, user_id: int) -> User:
        await maybe_await(self._validate_login)
        logger.info("Getting user by id: %s", user_id)
        url = f"{self.base_url}/v1/user/{user_id}/stats:true"
        response = await maybe_await(self.client.get, url)
        response.raise_for_status()
        json_data = response.json()
        if not json_data.get("success"):
            logger.warning("User with ID %s not found.", user_id)
            raise FileNotFoundError(f"User with ID {user_id} not found.")
        user_data = json_data["response"]
        user_data["profile_url"] = self.base_url + user_data["url"]
        user = User.model_validate(user_data)
        logger.info("Successfully retrieved user: '%s'", user.name)
        return user

    async def _get_relations(self, user_id: int, relation: UsersRelation, page: int = 1) -> Pagination[int]:
        await maybe_await(self._validate_login)
        url = f"{self.base_url}/{relation.value}/listar/{user_id}/page:{page}/limit:100"
        logger.info("Getting '%s' for user_id: %s, page: %s", relation.value, user_id, page)
        response = await maybe_await(self.client.get, url)
        response.raise_for_status()
        soup = self.parse_html(response.text)
        try:
            users_html = safe_find_all(soup, "div", {"class": "usuarios-mini-lista-txt"})
            users_id = [int(get_user_id_from_url(get_tag_attr(i.a, "href"))) for i in users_html if i.find("a") and getattr(i, "a", None)]
            next_page_link = safe_find(soup, "div", {"class": "proximo"})
        except (AttributeError, ValueError, IndexError) as e:  # pragma: no cover - defensive
            logger.exception("Failed to parse user relations: %s", e)
            raise ParsingError("Failed to parse user relations.") from e
        logger.info("Found %s users on page %s.", len(users_id), page)
        return Pagination(
            results=users_id,
            limit=100,
            page=page,
            total=len(users_id),
            has_next_page=bool(next_page_link),
        )

    async def _get_reviews(self, user_id: int, page: int = 1) -> Pagination[BookReview]:
        await maybe_await(self._validate_login)
        url = f"{self.base_url}/estante/resenhas/{user_id}/mpage:{page}/limit:50"
        logger.info("Getting reviews for user_id: %s, page: %s", user_id, page)
        response = await maybe_await(self.client.get, url)
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
            logger.exception("Failed to parse user reviews: %s", e)
            raise ParsingError("Failed to parse user reviews.") from e
        logger.info("Found %s reviews on page %s.", len(user_reviews), page)
        return Pagination(
            results=user_reviews,
            limit=50,
            page=page,
            total=len(user_reviews),
            has_next_page=bool(next_page_link),
        )

    async def _get_read_stats(self, user_id: int) -> UserReadStats:
        await maybe_await(self._validate_login)
        logger.info("Getting read stats for user_id: %s", user_id)
        url = f"{self.base_url}/v1/meta_stats/{user_id}"
        response = await maybe_await(self.client.get, url)
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
        logger.info("Successfully retrieved read stats for user_id: %s", user_id)
        return stats

    async def _get_bookcase(self, user_id: int, bookcase_option: BookcaseOption, page: int = 1) -> Pagination[UserBook]:
        await maybe_await(self._validate_login)
        url = f"{self.base_url}/v1/bookcase/books/{user_id}/shelf_id:{bookcase_option.value}/page:{page}/limit:100"
        logger.info(
            "Getting bookcase for user_id: %s, option: '%s', page: %s",
            user_id,
            bookcase_option.name,
            page,
        )
        response = await maybe_await(self.client.get, url)
        response.raise_for_status()
        json_data = response.json()
        next_page = json_data.get("paging", {}).get("next_page")
        results: list[UserBook] = []
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
        logger.info("Found %s books on page %s.", len(results), page)
        return Pagination(
            limit=100,
            results=results,
            total=len(results),
            has_next_page=bool(next_page),
            page=page,
        )

    async def _search(
        self,
        query: str,
        gender: UserGender | None = None,
        state: BrazilianState | None = None,
        page: int = 1,
        limit: int = 100,
    ) -> Pagination[UserSearch]:
        await maybe_await(self._validate_login)
        url = f"{self.base_url}/usuario/lista/busca:{query}/mpage:{page}/limit:{limit}"
        if gender:
            url += f"/sexo:{gender.value}"
        if state:
            url += f"/uf:{state.value}"
        response = await maybe_await(self.client.get, url)
        response.raise_for_status()
        soup = self.parse_html(response.text)
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


class UserService(_UserServiceMixin, AuthenticatedService):
    """Fetch user profiles, books and friends from Skoob."""

    def __init__(self, client: SyncHTTPClient, auth_service: AuthService):
        """Initialize the service with dependencies."""

        super().__init__(client, auth_service)

    def get_by_id(self, user_id: int) -> User:
        """Retrieve a user by their ID."""

        return run_sync(self._get_by_id(user_id))

    def get_relations(self, user_id: int, relation: UsersRelation, page: int = 1) -> Pagination[int]:
        """Retrieve a user's relations."""

        return run_sync(self._get_relations(user_id, relation, page))

    def get_reviews(self, user_id: int, page: int = 1) -> Pagination[BookReview]:
        """Retrieve reviews made by a user."""

        return run_sync(self._get_reviews(user_id, page))

    def get_read_stats(self, user_id: int) -> UserReadStats:
        """Retrieve reading statistics for a user."""

        return run_sync(self._get_read_stats(user_id))

    def get_bookcase(self, user_id: int, bookcase_option: BookcaseOption, page: int = 1) -> Pagination[UserBook]:
        """Retrieve a user's bookcase."""

        return run_sync(self._get_bookcase(user_id, bookcase_option, page))

    def search(
        self,
        query: str,
        gender: UserGender | None = None,
        state: BrazilianState | None = None,
        page: int = 1,
        limit: int = 100,
    ) -> Pagination[UserSearch]:
        """Search for users on Skoob."""

        return run_sync(self._search(query, gender, state, page, limit))


class AsyncUserService(_UserServiceMixin, AsyncAuthenticatedService):  # pragma: no cover - thin async wrapper
    """Asynchronous variant of :class:`UserService`."""

    def __init__(self, client: AsyncHTTPClient, auth_service: AsyncAuthService):
        super().__init__(client, auth_service)

    async def get_by_id(self, user_id: int) -> User:
        """Retrieve a user by their ID."""

        return await self._get_by_id(user_id)

    async def get_relations(self, user_id: int, relation: UsersRelation, page: int = 1) -> Pagination[int]:
        """Retrieve a user's relations."""

        return await self._get_relations(user_id, relation, page)

    async def get_reviews(self, user_id: int, page: int = 1) -> Pagination[BookReview]:
        """Retrieve reviews made by a user."""

        return await self._get_reviews(user_id, page)

    async def get_read_stats(self, user_id: int) -> UserReadStats:
        """Retrieve reading statistics for a user."""

        return await self._get_read_stats(user_id)

    async def get_bookcase(self, user_id: int, bookcase_option: BookcaseOption, page: int = 1) -> Pagination[UserBook]:
        """Retrieve a user's bookcase."""

        return await self._get_bookcase(user_id, bookcase_option, page)

    async def search(
        self,
        query: str,
        gender: UserGender | None = None,
        state: BrazilianState | None = None,
        page: int = 1,
        limit: int = 100,
    ) -> Pagination[UserSearch]:
        """Search for users on Skoob."""

        return await self._search(query, gender, state, page, limit)

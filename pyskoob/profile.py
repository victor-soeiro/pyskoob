"""Profile management helpers for authenticated Skoob users."""

import logging
from collections.abc import Callable
from typing import Any

from pyskoob.auth import AsyncAuthService, AuthService
from pyskoob.http.client import AsyncHTTPClient, SyncHTTPClient
from pyskoob.internal.async_authenticated import AsyncAuthenticatedService
from pyskoob.internal.authenticated import AuthenticatedService
from pyskoob.models.enums import BookLabel, BookShelf, BookStatus
from pyskoob.utils.sync_async import maybe_await, run_sync

logger = logging.getLogger(__name__)


class _ProfileServiceMixin:
    """Shared profile actions for sync and async services."""

    client: Any
    base_url: str
    _validate_login: Callable[[], Any]

    async def _add_book_label(self, edition_id: int, label: BookLabel) -> bool:
        await maybe_await(self._validate_login)
        url = f"{self.base_url}/v1/label_add/{edition_id}/{label.value}"
        response = await maybe_await(self.client.get, url)
        response.raise_for_status()
        return response.json().get("success", False)

    async def _remove_book_label(self, edition_id: int) -> bool:
        await maybe_await(self._validate_login)
        url = f"{self.base_url}/v1/label_del/{edition_id}"
        response = await maybe_await(self.client.get, url)
        response.raise_for_status()
        return response.json().get("success", False)

    async def _update_book_status(self, edition_id: int, status: BookStatus) -> bool:
        await maybe_await(self._validate_login)
        url = f"{self.base_url}/v1/shelf_add/{edition_id}/{status.value}"
        response = await maybe_await(self.client.get, url)
        response.raise_for_status()
        return response.json().get("success", False)

    async def _remove_book_status(self, edition_id: int) -> bool:
        await maybe_await(self._validate_login)
        url = f"{self.base_url}/v1/shelf_del/{edition_id}"
        response = await maybe_await(self.client.get, url)
        response.raise_for_status()
        return response.json().get("success", False)

    async def _change_book_shelf(self, edition_id: int, bookshelf: BookShelf) -> bool:
        await maybe_await(self._validate_login)
        url = f"{self.base_url}/estante/prateleira/{edition_id}/{bookshelf.value}"
        response = await maybe_await(self.client.get, url)
        response.raise_for_status()
        return response.json().get("success", False)

    async def _rate_book(self, edition_id: int, ranking: float) -> bool:
        await maybe_await(self._validate_login)
        if not (0 <= ranking <= 5):
            raise ValueError("Rating must be between 0 and 5.")
        url = f"{self.base_url}/v1/book_rate/{edition_id}/{ranking}"
        response = await maybe_await(self.client.get, url)
        response.raise_for_status()
        if not response.json().get("success"):
            raise RuntimeError("Failed to rate the book.")
        return True


class SkoobProfileService(_ProfileServiceMixin, AuthenticatedService):
    """Perform profile-related actions such as labeling and rating books."""

    def __init__(self, client: SyncHTTPClient, auth_service: AuthService):
        """Initialize the service with dependencies.

        This service requires an authenticated session via
        :class:`AuthService` and is typically used alongside
        :class:`UserService` when manipulating the logged user's bookshelf
        and other profile metadata.

        Parameters
        ----------
        client : SyncHTTPClient
            The HTTP client to use for requests.
        auth_service : AuthService
            The authentication service.
        """
        super().__init__(client, auth_service)

    def add_book_label(self, edition_id: int, label: BookLabel) -> bool:
        """
        Adds a label to a book.

        Parameters
        ----------
        edition_id : int
            The edition ID of the book.
        label : BookLabel
            The label to add.

        Returns
        -------
        bool
            True if the label was added successfully, False otherwise.

        Examples
        --------
        >>> service.add_book_label(10, BookLabel.FAVORITE)
        True
        """
        return run_sync(self._add_book_label(edition_id, label))

    def remove_book_label(self, edition_id: int) -> bool:
        """
        Removes a label from a book.

        Parameters
        ----------
        edition_id : int
            The edition ID of the book.

        Returns
        -------
        bool
            True if the label was removed successfully, False otherwise.

        Examples
        --------
        >>> service.remove_book_label(10)
        True
        """
        return run_sync(self._remove_book_label(edition_id))

    def update_book_status(self, edition_id: int, status: BookStatus) -> bool:
        """
        Updates the status of a book.

        Parameters
        ----------
        edition_id : int
            The edition ID of the book.
        status : BookStatus
            The new status for the book.

        Returns
        -------
        bool
            True if the status was updated successfully, False otherwise.

        Examples
        --------
        >>> service.update_book_status(10, BookStatus.READ)
        True
        """
        return run_sync(self._update_book_status(edition_id, status))

    def remove_book_status(self, edition_id: int) -> bool:
        """
        Removes the status of a book.

        Parameters
        ----------
        edition_id : int
            The edition ID of the book.

        Returns
        -------
        bool
            True if the status was removed successfully, False otherwise.

        Examples
        --------
        >>> service.remove_book_status(10)
        True
        """
        return run_sync(self._remove_book_status(edition_id))

    def change_book_shelf(self, edition_id: int, bookshelf: BookShelf) -> bool:
        """
        Changes the bookshelf of a book.

        Parameters
        ----------
        edition_id : int
            The edition ID of the book.
        bookshelf : BookShelf
            The new bookshelf for the book.

        Returns
        -------
        bool
            True if the bookshelf was changed successfully, False otherwise.

        Examples
        --------
        >>> service.change_book_shelf(10, BookShelf.FAVORITES)
        True
        """
        return run_sync(self._change_book_shelf(edition_id, bookshelf))

    def rate_book(self, edition_id: int, ranking: float) -> bool:
        """
        Rates a book.

        Parameters
        ----------
        edition_id : int
            The edition ID of the book.
        ranking : float
            The rating to give to the book (from 0 to 5).

        Returns
        -------
        bool
            True if the book was rated successfully.

        Raises
        ------
        ValueError
            If the rating is not between 0 and 5.
        RuntimeError
            If it fails to rate the book.

        Examples
        --------
        >>> service.rate_book(10, 4.5)
        True
        """
        return run_sync(self._rate_book(edition_id, ranking))


class AsyncSkoobProfileService(_ProfileServiceMixin, AsyncAuthenticatedService):  # pragma: no cover - thin async wrapper
    """Asynchronous variant of :class:`SkoobProfileService`."""

    def __init__(self, client: AsyncHTTPClient, auth_service: AsyncAuthService):
        super().__init__(client, auth_service)

    async def add_book_label(self, edition_id: int, label: BookLabel) -> bool:
        """Add a label to a book in the authenticated profile."""

        return await self._add_book_label(edition_id, label)

    async def remove_book_label(self, edition_id: int) -> bool:
        """Remove a label from a book in the authenticated profile."""

        return await self._remove_book_label(edition_id)

    async def update_book_status(self, edition_id: int, status: BookStatus) -> bool:
        """Update the user's status for a book."""

        return await self._update_book_status(edition_id, status)

    async def remove_book_status(self, edition_id: int) -> bool:
        """Remove the user's status for a book."""

        return await self._remove_book_status(edition_id)

    async def change_book_shelf(self, edition_id: int, bookshelf: BookShelf) -> bool:
        """Move a book to a different bookshelf."""

        return await self._change_book_shelf(edition_id, bookshelf)

    async def rate_book(self, edition_id: int, ranking: float) -> bool:
        """Rate a book in the authenticated profile."""

        return await self._rate_book(edition_id, ranking)

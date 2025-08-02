import logging

from pyskoob.auth import AuthService
from pyskoob.http.client import SyncHTTPClient
from pyskoob.internal.base import BaseSkoobService
from pyskoob.models.enums import BookLabel, BookShelf, BookStatus

logger = logging.getLogger(__name__)


class SkoobProfileService(BaseSkoobService):
    def __init__(self, client: SyncHTTPClient, auth_service: AuthService):
        """Perform profile-related actions such as labeling and rating books.

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
        super().__init__(client)
        self._auth_service = auth_service

    def _validate_login(self) -> None:
        """Ensure the session is authenticated before making requests.

        Raises
        ------
        PermissionError
            If the user is not logged in.

        Examples
        --------
        >>> service._validate_login()
        None
        """
        self._auth_service.validate_login()

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
        self._validate_login()
        url = f"{self.base_url}/v1/label_add/{edition_id}/{label.value}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json().get("success", False)

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
        self._validate_login()
        url = f"{self.base_url}/v1/label_del/{edition_id}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json().get("success", False)

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
        self._validate_login()
        url = f"{self.base_url}/v1/shelf_add/{edition_id}/{status.value}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json().get("success", False)

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
        self._validate_login()
        url = f"{self.base_url}/v1/shelf_del/{edition_id}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json().get("success", False)

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
        self._validate_login()
        url = f"{self.base_url}/estante/prateleira/{edition_id}/{bookshelf.value}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json().get("success", False)

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
        self._validate_login()
        if not (0 <= ranking <= 5):
            raise ValueError("Rating must be between 0 and 5.")

        url = f"{self.base_url}/v1/book_rate/{edition_id}/{ranking}"
        response = self.client.get(url)
        response.raise_for_status()

        if not response.json().get("success"):
            raise RuntimeError("Failed to rate the book.")
        return True

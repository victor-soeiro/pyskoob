from __future__ import annotations

from typing import TYPE_CHECKING

from pyskoob.http.client import SyncHTTPClient
from pyskoob.internal.base import BaseSkoobService

if TYPE_CHECKING:
    from pyskoob.auth import AuthService


class AuthenticatedService(BaseSkoobService):
    """Base class for services that require an authenticated session.

    This class stores a reference to :class:`AuthService` and exposes the
    :meth:`_validate_login` helper so subclasses can easily ensure the user is
    logged in before performing any request.
    """

    def __init__(self, client: SyncHTTPClient, auth_service: AuthService):
        """Initialize the service with an HTTP client and an auth dependency.

        Parameters
        ----------
        client : SyncHTTPClient
            The HTTP client to use for requests.
        auth_service : AuthService
            The authentication service responsible for login state.
        """
        super().__init__(client)
        self._auth_service = auth_service

    def _validate_login(self) -> None:
        """Ensure the current session is authenticated.

        Raises
        ------
        PermissionError
            If the user is not logged in.
        """
        self._auth_service.validate_login()

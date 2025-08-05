"""Authentication helpers and session management for Skoob."""

from __future__ import annotations

import logging
from typing import Any

from pyskoob.http.client import AsyncHTTPClient, SyncHTTPClient
from pyskoob.internal.async_base import AsyncBaseSkoobService
from pyskoob.internal.base import BaseSkoobService
from pyskoob.models.user import User
from pyskoob.utils.sync_async import maybe_await, run_sync

logger = logging.getLogger(__name__)


class _AuthServiceMixin:
    """Shared authentication logic for sync and async services."""

    client: Any
    base_url: str

    _is_logged_in: bool

    async def _login_with_cookies(self, session_token: str) -> User:
        """Authenticate using an existing session token.

        Parameters
        ----------
        session_token : str
            Value of the ``PHPSESSID`` cookie obtained from the browser.

        Returns
        -------
        User
            Authenticated user information.

        Raises
        ------
        ConnectionError
            If the session token is invalid or user information cannot be retrieved.
        """

        logger.info("Attempting to log in with session token.")
        self.client.cookies.update({"PHPSESSID": session_token})
        user = await self._get_my_info()
        self._is_logged_in = True
        logger.info("Successfully logged in as user: '%s'", user.name)
        return user

    async def _login(self, email: str, password: str) -> User:
        """Authenticate using email and password.

        Parameters
        ----------
        email : str
            Account email address.
        password : str
            Account password.

        Returns
        -------
        User
            Authenticated user information.

        Raises
        ------
        ConnectionError
            If the credentials are invalid or the response cannot be parsed.
        """

        logger.info("Attempting to log in with email and password.")
        url = f"{self.base_url}/v1/login"
        data = {
            "data[Usuario][email]": email,
            "data[Usuario][senha]": password,
            "data[Login][automatico]": True,
        }
        response = await maybe_await(self.client.post, url, data=data)
        response.raise_for_status()
        try:
            json_data = response.json()
        except ValueError as exc:
            logger.error("Login response was not valid JSON")
            raise ConnectionError("Invalid response format") from exc
        if not json_data.get("success", False):
            logger.error("Login failed: %s", json_data.get("message", "Unknown error"))
            raise ConnectionError(f"Failed to login: {json_data.get('message', 'Unknown error')}")
        self._is_logged_in = True
        user = await self._get_my_info()
        logger.info("Successfully logged in as user: '%s'", user.name)
        return user

    async def _get_my_info(self) -> User:
        """Retrieve information about the authenticated user.

        Returns
        -------
        User
            Authenticated user details.

        Raises
        ------
        ConnectionError
            If the service cannot retrieve the user information.
        """

        logger.info("Getting authenticated user's information.")
        url = f"{self.base_url}/v1/user/stats:true"
        response = await maybe_await(self.client.get, url)
        response.raise_for_status()
        json_data = response.json()
        if not json_data.get("success"):
            logger.error("Failed to retrieve user information. The session token might be invalid.")
            raise ConnectionError("Failed to retrieve user information. The session token might be invalid.")
        user_data = json_data["response"]
        user_data["profile_url"] = self.base_url + user_data["url"]
        user = User.model_validate(user_data)
        logger.info("Successfully retrieved user: '%s'", user.name)
        return user

    def _validate_login(self) -> None:
        """Ensure that a user has been authenticated.

        Raises
        ------
        PermissionError
            If the service has not been authenticated yet.
        """

        logger.debug("Validating login status.")
        if not self._is_logged_in:
            logger.warning("Validation failed: User is not logged in.")
            raise PermissionError("User is not logged in. Please authenticate first using 'login' or 'login_with_cookies'.")
        logger.debug("Validation successful: User is logged in.")


class AuthService(_AuthServiceMixin, BaseSkoobService):
    """Handle authentication with Skoob and track login state."""

    def __init__(self, client: SyncHTTPClient):
        """Manage Skoob authentication and session validation."""

        super().__init__(client)
        self._is_logged_in = False

    def login_with_cookies(self, session_token: str) -> User:
        """Log in using a pre-existing session token.

        Parameters
        ----------
        session_token : str
            Value of the ``PHPSESSID`` cookie obtained from the browser.

        Returns
        -------
        User
            Authenticated user information.
        """

        return run_sync(self._login_with_cookies(session_token))

    def login(self, email: str, password: str) -> User:
        """Log in with email and password.

        Parameters
        ----------
        email : str
            Account email address.
        password : str
            Account password.

        Returns
        -------
        User
            Authenticated user information.
        """

        return run_sync(self._login(email, password))

    def get_my_info(self) -> User:
        """Retrieve information about the authenticated user.

        Returns
        -------
        User
            Authenticated user details.
        """

        return run_sync(self._get_my_info())

    def validate_login(self) -> None:
        """Validate that the current session is authenticated.

        Raises
        ------
        PermissionError
            If the service has not been authenticated yet.
        """

        self._validate_login()


class AsyncAuthService(_AuthServiceMixin, AsyncBaseSkoobService):  # pragma: no cover - thin async wrapper
    """Asynchronous authentication service."""

    def __init__(self, client: AsyncHTTPClient):
        super().__init__(client)
        self._is_logged_in = False

    async def login_with_cookies(self, session_token: str) -> User:
        """Log in using a pre-existing session token.

        Parameters
        ----------
        session_token : str
            Value of the ``PHPSESSID`` cookie obtained from the browser.

        Returns
        -------
        User
            Authenticated user information.
        """

        return await self._login_with_cookies(session_token)

    async def login(self, email: str, password: str) -> User:
        """Log in with email and password.

        Parameters
        ----------
        email : str
            Account email address.
        password : str
            Account password.

        Returns
        -------
        User
            Authenticated user information.
        """

        return await self._login(email, password)

    async def get_my_info(self) -> User:
        """Retrieve information about the authenticated user.

        Returns
        -------
        User
            Authenticated user details.
        """

        return await self._get_my_info()

    async def validate_login(self) -> None:
        """Validate that the current session is authenticated.

        Raises
        ------
        PermissionError
            If the service has not been authenticated yet.
        """

        self._validate_login()

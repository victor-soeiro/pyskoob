import logging

from pyskoob.http.client import SyncHTTPClient
from pyskoob.internal.base import BaseSkoobService
from pyskoob.models.user import User

logger = logging.getLogger(__name__)


class AuthService(BaseSkoobService):
    def __init__(self, client: SyncHTTPClient):
        """Manage Skoob authentication and session validation.

        The service wraps the login workflow and stores the session state so
        other services (such as :class:`UserService` or
        :class:`SkoobProfileService`) can verify that requests are
        authenticated before accessing user data.

        Parameters
        ----------
        client : SyncHTTPClient
            The HTTP client to use for requests.

        Examples
        --------
        >>> import httpx
        >>> service = AuthService(httpx.Client())
        """
        super().__init__(client)
        self._is_logged_in = False

    def login_with_cookies(self, session_token: str) -> User:
        """
        Logs in the user using a session token.

        Parameters
        ----------
        session_token : str
            The PHPSESSID token from Skoob.

        Returns
        -------
        User
            The authenticated user's information.

        Examples
        --------
        >>> service.login_with_cookies("PHPSESSID=abc123")
        User(name='example')
        """
        logger.info("Attempting to log in with session token.")
        self.client.cookies.update({"PHPSESSID": session_token})
        user = self.get_my_info()
        self._is_logged_in = True
        logger.info("Successfully logged in as user: '%s'", user.name)
        return user

    def login(self, email: str, password: str) -> User:
        """
        Logs in the user using email and password.

        Parameters
        ----------
        email : str
            The user's email address.
        password : str
            The user's password.

        Returns
        -------
        User
            The authenticated user's information.

        Raises
        ------
        ConnectionError
            If authentication fails or the session cannot be established.

        Examples
        --------
        >>> service.login("user@example.com", "password")
        User(name='example')
        """
        logger.info("Attempting to log in with email and password.")
        url = f"{self.base_url}/v1/login"
        data = {
            "data[Usuario][email]": email,
            "data[Usuario][senha]": password,
            "data[Login][automatico]": True,
        }

        response = self.client.post(url, data=data)
        response.raise_for_status()

        try:
            json_data = response.json()
        except ValueError as exc:
            logger.error(
                "Login response was not valid JSON: %s",
                exc,
                exc_info=True,
            )
            raise ConnectionError("Invalid response format") from exc
        if not json_data.get("success", False):
            logger.error(
                "Login failed: %s", json_data.get("message", "Unknown error")
            )
            raise ConnectionError(
                "Failed to login: {}".format(
                    json_data.get("message", "Unknown error")
                )
            )

        self._is_logged_in = True
        user = self.get_my_info()
        logger.info("Successfully logged in as user: '%s'", user.name)
        return user

    def get_my_info(self) -> User:
        """
        Retrieves the authenticated user's information.

        Returns
        -------
        User
            The authenticated user's information.

        Raises
        ------
        ConnectionError
            If it fails to retrieve user information.

        Examples
        --------
        >>> service.get_my_info().name
        'Example User'
        """
        logger.info("Getting authenticated user's information.")
        url = f"{self.base_url}/v1/user/stats:true"
        response = self.client.get(url)
        response.raise_for_status()

        json_data = response.json()
        if not json_data.get("success"):
            logger.error(
                "Failed to retrieve user information. "
                "The session token might be invalid."
            )
            raise ConnectionError(
                "Failed to retrieve user information. "
                "The session token might be invalid."
            )

        user_data = json_data["response"]
        user_data["profile_url"] = (
            self.base_url + user_data["url"]
        )  # patch field for alias
        user = User.model_validate(user_data)
        logger.info("Successfully retrieved user: '%s'", user.name)
        return user

    def validate_login(self) -> None:
        """
        Validates if the user is logged in.

        Raises
        ------
        PermissionError
            If the user is not logged in.

        Examples
        --------
        >>> service.validate_login()
        None
        """
        logger.debug("Validating login status.")
        if not self._is_logged_in:
            logger.warning("Validation failed: User is not logged in.")
            raise PermissionError(
                "User is not logged in. "
                "Please call 'login_with_cookies' first."
            )
        logger.debug("Validation successful: User is logged in.")

from pyskoob.auth import AuthService
from pyskoob.books import BookService
from pyskoob.http.httpx import HttpxSyncClient
from pyskoob.profile import SkoobProfileService
from pyskoob.users import UserService


class SkoobClient:
    """Facade for interacting with Skoob services.

    Examples
    --------
    >>> with SkoobClient() as client:
    ...     client.auth.login_with_cookies("token")
    """

    def __init__(self):
        """
        Initializes the SkoobClient.
        """
        self._client = HttpxSyncClient()
        self.auth = AuthService(self._client)
        self.books = BookService(self._client)
        self.users = UserService(self._client, self.auth)
        self.me = SkoobProfileService(self._client, self.auth)

    def __enter__(self):
        """
        Enter the runtime context for the SkoobClient.

        Returns
        -------
        SkoobClient
            The SkoobClient instance.

        Examples
        --------
        >>> with SkoobClient() as client:
        ...     pass
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context, closing the HTTPX client.

        Parameters
        ----------
        exc_type : type
            The exception type.
        exc_val : Exception
            The exception value.
        exc_tb : traceback
            The traceback object.

        Examples
        --------
        >>> client = SkoobClient()
        >>> client.__exit__(None, None, None)
        None
        """
        self._client.close()

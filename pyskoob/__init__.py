"""Public API for the PySkoob package.

This module re-exports the most commonly used classes so that users can simply
import from ``pyskoob``. Everything listed in ``__all__`` is considered stable
and will not change without a deprecation period.
"""

__version__ = "0.1.12"

from . import models
from .auth import AuthService
from .authors import AuthorService
from .books import BookService
from .client import SkoobClient
from .exceptions import ParsingError
from .http.httpx import HttpxAsyncClient, HttpxSyncClient
from .profile import SkoobProfileService
from .publishers import PublisherService
from .users import UserService

__all__ = [
    "AuthService",
    "AuthorService",
    "BookService",
    "HttpxAsyncClient",
    "HttpxSyncClient",
    "PublisherService",
    "SkoobClient",
    "SkoobProfileService",
    "UserService",
    "models",
    "ParsingError",
    "__version__",
]

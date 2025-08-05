"""Public API for the PySkoob package.

This module re-exports the most commonly used classes so that users can simply
import from ``pyskoob``. Everything listed in ``__all__`` is considered stable
and will not change without a deprecation period.
"""

__version__ = "0.1.20"

from . import models
from .auth import AsyncAuthService, AuthService
from .authors import AsyncAuthorService, AuthorService
from .books import AsyncBookService, BookService
from .client import SkoobAsyncClient, SkoobClient
from .exceptions import ParsingError
from .http.httpx import HttpxAsyncClient, HttpxSyncClient
from .profile import AsyncSkoobProfileService, SkoobProfileService
from .publishers import AsyncPublisherService, PublisherService
from .users import AsyncUserService, UserService
from .utils import ExponentialBackoff, RateLimiter

__all__ = [
    "AuthService",
    "AsyncAuthService",
    "AuthorService",
    "AsyncAuthorService",
    "BookService",
    "AsyncBookService",
    "HttpxAsyncClient",
    "HttpxSyncClient",
    "PublisherService",
    "AsyncPublisherService",
    "SkoobClient",
    "SkoobAsyncClient",
    "SkoobProfileService",
    "AsyncSkoobProfileService",
    "UserService",
    "AsyncUserService",
    "models",
    "ParsingError",
    "RateLimiter",
    "ExponentialBackoff",
    "__version__",
]

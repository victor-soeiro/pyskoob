from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Pagination(BaseModel, Generic[T]):
    """Generic container for paginated API responses.

    Attributes
    ----------
    results : list[T]
        Items returned for the current page.
    total : int
        Total number of items available.
    page : int
        Current page index starting at ``1``.
    limit : int
        Maximum number of items per page.
    has_next_page : bool
        ``True`` if more pages are available.
    """

    results: list[T]
    total: int
    page: int
    limit: int
    has_next_page: bool

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Pagination(BaseModel, Generic[T]):
    results: list[T]
    total: int
    page: int
    limit: int
    has_next_page: bool

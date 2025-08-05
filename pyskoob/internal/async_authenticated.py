from __future__ import annotations

"""Authentication-aware base classes for async services."""

from typing import TYPE_CHECKING

from pyskoob.http.client import AsyncHTTPClient
from pyskoob.internal.async_base import AsyncBaseSkoobService

if TYPE_CHECKING:
    from pyskoob.auth import AsyncAuthService


class AsyncAuthenticatedService(AsyncBaseSkoobService):  # pragma: no cover - thin async base
    """Base class for async services requiring authentication."""

    def __init__(self, client: AsyncHTTPClient, auth_service: AsyncAuthService):
        super().__init__(client)
        self._auth_service = auth_service

    async def _validate_login(self) -> None:
        """Ensure the current session is authenticated."""
        await self._auth_service.validate_login()

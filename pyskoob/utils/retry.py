from __future__ import annotations

"""Utilities for retrying operations with exponential backoff."""

import asyncio
import time
from collections.abc import Awaitable, Callable, Iterable
from typing import Any


class Retry:
    """Retry a callable with exponential backoff on specified exceptions.

    Parameters
    ----------
    max_attempts:
        Maximum number of attempts before giving up. Defaults to ``3``.
    base_delay:
        Initial delay in seconds used for the exponential backoff calculation.
        The delay for each retry is ``base_delay * 2**(attempt - 1)`` where
        ``attempt`` starts at ``1`` for the first retry. Defaults to ``0.5``.
    exceptions:
        Iterable of exception types that should trigger a retry. By default all
        exceptions are retried.
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 0.5,
        exceptions: Iterable[type[Exception]] | None = None,
    ) -> None:
        self._max_attempts = max_attempts
        self._base_delay = base_delay
        self._exceptions = tuple(exceptions or (Exception,))

    def _sleep(self, attempt: int) -> None:
        delay = self._base_delay * (2 ** (attempt - 1))
        if delay > 0:
            time.sleep(delay)

    async def _sleep_async(self, attempt: int) -> None:
        delay = self._base_delay * (2 ** (attempt - 1))
        if delay > 0:
            await asyncio.sleep(delay)

    def run(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute ``func`` with retries on failure.

        The function is called immediately. If it raises one of the configured
        exceptions the call is retried using exponential backoff.
        """
        attempt = 0
        while True:
            try:
                return func(*args, **kwargs)
            except self._exceptions:
                attempt += 1
                if attempt >= self._max_attempts:
                    raise
                self._sleep(attempt)

    async def run_async(
        self,
        func: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Asynchronous variant of :meth:`run`."""
        attempt = 0
        while True:
            try:
                return await func(*args, **kwargs)
            except self._exceptions:
                attempt += 1
                if attempt >= self._max_attempts:
                    raise
                await self._sleep_async(attempt)

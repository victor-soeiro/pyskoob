from __future__ import annotations

"""Utilities for throttling requests to the Skoob API."""

import asyncio
import time
from collections import deque
from threading import Lock


class RateLimiter:
    """Enforce a maximum number of calls within a time window.

    Parameters
    ----------
    max_calls:
        Maximum number of allowed calls within the given ``period``.
        Defaults to ``1``.
    period:
        Time window in seconds in which ``max_calls`` are permitted.
        Defaults to ``1.0``.

    Notes
    -----
    The limiter is thread-safe and provides both synchronous and asynchronous
    acquire methods. The asynchronous variant uses :func:`asyncio.sleep` to
    avoid blocking the event loop.
    """

    def __init__(self, max_calls: int = 1, period: float = 1.0) -> None:
        self._max_calls = max_calls
        self._period = period
        self._calls: deque[float] = deque()
        self._lock = Lock()
        self._async_lock = asyncio.Lock()

    def _trim(self, now: float) -> None:
        while self._calls and now - self._calls[0] >= self._period:
            self._calls.popleft()

    def acquire(self) -> None:
        """Block until the next call is permitted."""
        with self._lock:
            now = time.monotonic()
            self._trim(now)
            if len(self._calls) >= self._max_calls:
                sleep_for = self._period - (now - self._calls[0])
                time.sleep(sleep_for)
                now = time.monotonic()
                self._trim(now)
            self._calls.append(now)

    async def acquire_async(self) -> None:
        """Asynchronous variant of :meth:`acquire`."""
        async with self._async_lock:
            now = time.monotonic()
            self._trim(now)
            if len(self._calls) >= self._max_calls:
                sleep_for = self._period - (now - self._calls[0])
                await asyncio.sleep(sleep_for)
                now = time.monotonic()
                self._trim(now)
            self._calls.append(now)

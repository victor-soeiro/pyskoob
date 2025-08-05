from __future__ import annotations

"""Exponential backoff helpers."""

import asyncio
import time


class ExponentialBackoff:
    """Utility implementing exponential backoff delays.

    Parameters
    ----------
    max_retries:
        Number of retry attempts before giving up.
    base_delay:
        Initial delay in seconds for the first retry.
    factor:
        Multiplicative factor applied to the delay after each retry.
    max_delay:
        Upper bound for the calculated delay in seconds.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 0.1,
        factor: float = 2.0,
        max_delay: float = 60.0,
    ) -> None:
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.factor = factor
        self.max_delay = max_delay

    def _compute_delay(self, attempt: int) -> float:
        delay = self.base_delay * (self.factor**attempt)
        return min(delay, self.max_delay)

    def sleep(self, attempt: int) -> None:
        """Sleep for the delay associated with ``attempt``."""
        time.sleep(self._compute_delay(attempt))

    async def sleep_async(self, attempt: int) -> None:
        """Asynchronously sleep for the delay associated with ``attempt``."""
        await asyncio.sleep(self._compute_delay(attempt))


__all__ = ["ExponentialBackoff"]

"""Utilities to bridge synchronous and asynchronous execution.

This module provides helpers to call functions that may be synchronous or
asynchronous without duplicating logic in service implementations.
"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

T = TypeVar("T")


async def maybe_await(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Call ``func`` and await the result if it returns an awaitable."""
    result = func(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


def run_sync(awaitable: Coroutine[Any, Any, T]) -> T:
    """Synchronously run a coroutine using ``asyncio.run``.

    Note
    ----
    This helper should only be used when no event loop is already running.
    Calling it from within an active loop will raise :class:`RuntimeError`.
    For such environments, consider using ``nest_asyncio`` or executing the
    coroutine in a separate thread.
    """

    return asyncio.run(awaitable)

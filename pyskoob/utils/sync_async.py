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

    Notes
    -----
    ``asyncio.run`` raises a generic :class:`RuntimeError` when invoked while
    an event loop is already running. This helper performs an explicit check so
    callers receive a descriptive error message instead of the generic one.

    Raises
    ------
    RuntimeError
        If an event loop is currently running. In that case, consider awaiting
        the coroutine directly or running it in a separate thread.
    """

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        pass
    else:
        raise RuntimeError(
            "run_sync() cannot be called from an active event loop. Use 'await' directly or run the coroutine in a separate thread."
        )

    return asyncio.run(awaitable)

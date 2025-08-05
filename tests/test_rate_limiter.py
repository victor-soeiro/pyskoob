import asyncio
import time

from pyskoob.utils import RateLimiter


def test_rate_limiter_blocks_synchronously() -> None:
    limiter = RateLimiter(max_calls=2, period=0.05)
    start = time.monotonic()
    for _ in range(3):
        limiter.acquire()
    elapsed = time.monotonic() - start
    assert elapsed >= 0.05


def test_rate_limiter_blocks_asynchronously() -> None:
    limiter = RateLimiter(max_calls=2, period=0.05)

    async def run() -> float:
        start = time.monotonic()
        for _ in range(3):
            await limiter.acquire_async()
        return time.monotonic() - start

    elapsed = asyncio.run(run())
    assert elapsed >= 0.05


def test_rate_limiter_default_is_one_per_second() -> None:
    limiter = RateLimiter()
    start = time.monotonic()
    limiter.acquire()
    limiter.acquire()
    elapsed = time.monotonic() - start
    assert elapsed >= 1.0

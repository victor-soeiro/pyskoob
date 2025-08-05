import asyncio
import threading
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


def test_rate_limiter_releases_lock_during_sleep() -> None:
    limiter = RateLimiter(max_calls=1, period=0.05)
    limiter.acquire()

    def target() -> None:
        limiter.acquire()

    thread = threading.Thread(target=target)
    thread.start()
    time.sleep(0.01)
    acquired = limiter._lock.acquire(blocking=False)
    if acquired:
        limiter._lock.release()
    thread.join()
    assert acquired


def test_rate_limiter_releases_async_lock_during_sleep() -> None:
    limiter = RateLimiter(max_calls=1, period=0.05)

    async def run() -> bool:
        await limiter.acquire_async()
        task = asyncio.create_task(limiter.acquire_async())
        await asyncio.sleep(0.01)
        unlocked = not limiter._async_lock.locked()
        await task
        return unlocked

    assert asyncio.run(run())

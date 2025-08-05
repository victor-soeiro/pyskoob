import asyncio
import threading
import time
from threading import Barrier, Thread

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


def test_rate_limiter_is_thread_safe() -> None:
    limiter = RateLimiter(max_calls=2, period=0.05)
    barrier = Barrier(4)
    times: list[float] = []

    def worker() -> None:
        barrier.wait()
        limiter.acquire()
        times.append(time.monotonic())

    threads = [Thread(target=worker) for _ in range(3)]
    for thread in threads:
        thread.start()
    start = time.monotonic()
    barrier.wait()
    for thread in threads:
        thread.join()

    results = sorted(t - start for t in times)
    assert results[2] - results[0] >= 0.05


def test_rate_limiter_is_async_thread_safe() -> None:
    limiter = RateLimiter(max_calls=2, period=0.05)

    async def run() -> list[float]:
        start_event = asyncio.Event()
        times: list[float] = []

        async def worker() -> None:
            await start_event.wait()
            await limiter.acquire_async()
            times.append(time.monotonic())

        tasks = [asyncio.create_task(worker()) for _ in range(3)]
        start = time.monotonic()
        start_event.set()
        await asyncio.gather(*tasks)
        return sorted(t - start for t in times)

    results = asyncio.run(run())
    assert results[2] - results[0] >= 0.05


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

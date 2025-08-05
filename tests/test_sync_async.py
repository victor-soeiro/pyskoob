import pytest

from pyskoob.utils.sync_async import run_sync


@pytest.fixture
def anyio_backend() -> str:  # noqa: D401 (no docstring for fixture)
    return "asyncio"


async def _returns(value: int) -> int:
    return value


def test_run_sync_runs_coroutine() -> None:
    assert run_sync(_returns(1)) == 1


@pytest.mark.anyio
async def test_run_sync_errors_when_loop_running(anyio_backend: str) -> None:
    coro = _returns(1)
    with pytest.raises(RuntimeError, match=r"run_sync\(\) cannot be called"):
        run_sync(coro)
    coro.close()

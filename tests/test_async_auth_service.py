import pytest

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def test_validate_login(dummy_async_auth):
    with pytest.raises(PermissionError):
        await dummy_async_auth.validate_login()
    dummy_async_auth._is_logged_in = True
    await dummy_async_auth.validate_login()

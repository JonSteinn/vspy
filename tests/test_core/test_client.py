import pytest
from httpx import HTTPStatusError
from pytest_httpx import HTTPXMock

from vspy.core.clients import AsyncClient


@pytest.mark.asyncio
async def test_async_client_get(httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="https://www.foo.is", content="abcd")
    r = await AsyncClient().get("https://www.foo.is")
    assert r == "abcd"


@pytest.mark.asyncio
async def test_async_client_get_json(httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="https://www.foo.is", content='{"a": "b"}')
    r = await AsyncClient().get_json("https://www.foo.is")
    assert r["a"] == "b"


@pytest.mark.asyncio
async def test_async_client_get_status_error(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://www.foo.is", content="Not Found", status_code=404
    )
    with pytest.raises(HTTPStatusError):
        _ = await AsyncClient().get_json("https://www.foo.is")

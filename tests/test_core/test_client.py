import asyncio
import operator

import pytest
from httpx import HTTPStatusError
from pytest_httpx import HTTPXMock

from tests.testutils.helpers import get_pypi_url_and_res
from tests.testutils.mocks import py_partial_page
from vspy.core.clients import (
    AsyncClient,
    PyPiClient,
    PythonVersionClient,
    fetch_all_requests_data,
)


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


@pytest.mark.asyncio
async def test_async_pypi_request(httpx_mock: HTTPXMock):
    packages = [("vspy", "0.1.0"), ("numpy", "33.2.6"), ("flask", "13.0.15")]
    data = [get_pypi_url_and_res(*package) for package in packages]
    for url, res in data:
        httpx_mock.add_response(url=url, json=res)

    pypi_cli = PyPiClient(AsyncClient())
    res = await asyncio.gather(
        *pypi_cli.get_version_tasks(map(operator.itemgetter(0), packages))
    )
    assert all(a == b for a, b in zip(res, packages))


@pytest.mark.asyncio
async def test_python_version_client(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://www.python.org/downloads/", content=py_partial_page
    )
    py_cli = PythonVersionClient(AsyncClient())
    (res,) = await asyncio.gather(*(py_cli.active_python3_version_task(),))
    assert set(res) == set(f"3.{x}" for x in range(7, 11))


@pytest.mark.asyncio
async def test_python_all_reqs(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://www.python.org/downloads/", content=py_partial_page
    )
    packages = [("mypck", "0.0.1"), ("mypck2", "19.7.3")]
    data = [get_pypi_url_and_res(*package) for package in packages]
    for url, res in data:
        httpx_mock.add_response(url=url, json=res)
    pcks, pys = await fetch_all_requests_data(map(operator.itemgetter(0), packages))
    assert set(pys) == set(f"3.{x}" for x in range(7, 11))
    assert pcks["mypck"] == "0.0.1"
    assert pcks["mypck2"] == "19.7.3"

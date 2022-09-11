import asyncio
import operator

import pytest
from httpx import HTTPStatusError
from pytest_httpx import HTTPXMock

from tests.testutils.helpers import get_pypi_url_and_res
from vspy.core.clients import (
    AsyncClient,
    PyPiClient,
    PythonVersionClient,
    fetch_all_requests_data,
)

py_partial_page = """<html><body><div class="row active-release-list-widget"> <h2 class="widget-title">Active Python Releases</h2> <p class="success-quote"><a href="https://devguide.python.org/#status-of-python-branches">For more information visit the Python Developer's Guide</a>.</p><div class="list-row-headings"><span class="release-version">Python version</span><span class="release-status">Maintenance status</span><span class="release-start">First released</span><span class="release-end">End of support</span><span class="release-pep">Release schedule</span></div><ol class="list-row-container menu"><li><span class="release-version">3.10</span><span class="release-status">bugfix</span><span class="release-start">2021-10-04</span><span class="release-end">2026-10</span><span class="release-pep"><a href="https://www.python.org/dev/peps/pep-0619">PEP 619</a></span></li><li><span class="release-version">3.9</span><span class="release-status">security</span><span class="release-start">2020-10-05</span><span class="release-end">2025-10</span><span class="release-pep"><a href="https://www.python.org/dev/peps/pep-0596">PEP 596</a></span></li><li><span class="release-version">3.8</span><span class="release-status">security</span><span class="release-start">2019-10-14</span><span class="release-end">2024-10</span><span class="release-pep"><a href="https://www.python.org/dev/peps/pep-0569">PEP 569</a></span></li><li><span class="release-version">3.7</span><span class="release-status">security</span><span class="release-start">2018-06-27</span><span class="release-end">2023-06-27</span><span class="release-pep"><a href="https://www.python.org/dev/peps/pep-0537">PEP 537</a></span></li><li><span class="release-version">2.7</span><span class="release-status">end-of-life</span><span class="release-start">2010-07-03</span><span class="release-end">2020-01-01</span><span class="release-pep"><a href="https://www.python.org/dev/peps/pep-0373">PEP 373</a></span></li></ol></div></body></html>"""


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

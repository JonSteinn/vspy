import abc
import asyncio
from typing import Awaitable, Dict, Iterable, List, Optional, Protocol, Tuple

import httpx
from bs4 import BeautifulSoup


class Client(Protocol):
    """Base client."""

    @abc.abstractmethod
    async def get_json(self, url: str) -> dict:
        """Get request promise to the url, deserialized as a json."""

    @abc.abstractmethod
    async def get(self, url: str) -> str:
        """Get request promise to the url, raw content as string."""


class AsyncClient(Client):
    """Async client to make multiple requests."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient()

    async def _get(self, url: str) -> httpx.Response:
        res = await self._client.get(url)
        res.raise_for_status()
        return res

    async def get_json(self, url: str) -> dict:
        json: dict = (await self._get(url)).json()
        return json

    async def get(self, url: str) -> str:
        return (await self._get(url)).text


class PyPiClient:
    """A client that fetched PyPi package versions."""

    def __init__(self, client: Client) -> None:
        self._client = client

    async def get_version(self, package: str) -> Tuple[str, str]:
        """Fetch the latest version of a given package."""
        json = await self._client.get_json(f"https://pypi.org/pypi/{package}/json")
        version: str = json.get("info", {}).get("version", "")
        return (package, version)

    def get_version_tasks(
        self, packages: Iterable[str]
    ) -> Iterable[Awaitable[Tuple[str, str]]]:
        """Create tasks for fetching versions for all packages."""
        return (asyncio.create_task(self.get_version(package)) for package in packages)


class PythonVersionClient:
    """Client for fetching active python versions."""

    def __init__(self, client: Client) -> None:
        self._client = client

    async def active_python3_version(self) -> List[str]:
        """Get the current active python versions."""
        soup = BeautifulSoup(
            await self._client.get("https://www.python.org/downloads/"), "html.parser"
        )
        return [
            span.text
            for span in soup.select(
                "div.row.active-release-list-widget > ol > li > span.release-version"
            )
            if span.text and not span.text.startswith("2")
        ]

    def active_python3_version_task(self) -> Awaitable[List[str]]:
        """A task wrapper for `active_python3_version`."""
        return asyncio.create_task(self.active_python3_version())


async def fetch_all_requests_data(
    packages: Iterable[str], client: Optional[Client] = None
) -> Tuple[Dict[str, str], List[str]]:
    """Perform all the client calls."""
    if not client:
        client = AsyncClient()
    pypi_cli = PyPiClient(client)
    py_cli = PythonVersionClient(client)
    res = await asyncio.gather(
        *pypi_cli.get_version_tasks(packages), py_cli.active_python3_version_task()
    )
    py_vers: List[str] = res.pop()
    return dict(res), py_vers

import asyncio
import pathlib
import uuid
from random import randint
from tempfile import TemporaryDirectory
from typing import Dict, List, Tuple

from vspy.core.file_io import path_from_root, read_file


def get_pypi_url_and_res(
    package: str, version: str
) -> Tuple[str, Dict[str, Dict[str, str]]]:
    return f"https://pypi.org/pypi/{package}/json", {"info": {"version": version}}


class TempFile(TemporaryDirectory):
    def __init__(self, number_of_files: int) -> None:
        super().__init__()
        self._number_of_files = number_of_files

    def __enter__(self) -> Tuple[str, List[pathlib.Path]]:
        dir_name = super().__enter__()
        dir_path = pathlib.Path(dir_name)
        files = [
            dir_path.joinpath(str(uuid.uuid4())) for _ in range(self._number_of_files)
        ]
        for file in files:
            file.touch()
        return (dir_name, files)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        super().__exit__(exc_type, exc_value, exc_traceback)


def vers_gen():
    version = [0, 0, 1]
    while True:
        version[randint(0, 2)] += randint(1, 5)
        yield ".".join(map(str, version))


def static_file(file_name: str) -> pathlib.Path:
    return path_from_root("vspy", "resources", "static", file_name)


async def compare_against_static(path: pathlib.Path, static_name: str) -> bool:
    a, b = await asyncio.gather(read_file(path), read_file(static_file(static_name)))
    return a == b

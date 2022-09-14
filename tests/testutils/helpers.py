import pathlib
from tempfile import TemporaryFile
from typing import Dict, Tuple

from vspy.core.utils import is_windows


def get_pypi_url_and_res(
    package: str, version: str
) -> Tuple[str, Dict[str, Dict[str, str]]]:
    return f"https://pypi.org/pypi/{package}/json", {"info": {"version": version}}


def _temp_file():
    if is_windows():
        return TemporaryFile(delete=False)
    return TemporaryFile()


class TempFileCtx:
    def __init__(self) -> None:
        file = _temp_file()
        file.close()
        self._path = pathlib.Path(file.name)

    def __enter__(self) -> pathlib.Path:
        return self._path

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._path.unlink()

import pathlib
import uuid
from tempfile import TemporaryDirectory
from typing import Dict, List, Tuple


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

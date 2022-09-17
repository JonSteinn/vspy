import sys
from io import StringIO
from typing import Dict, Iterable, List

from vspy.core.args import Arguments


class MockInput:
    @classmethod
    def from_iterable(cls, inputs: Iterable[str]) -> "MockInput":
        return cls(*inputs)

    def __init__(self, *args: str) -> None:
        self._original_sys_in = sys.stdin
        self._sys_in = StringIO("".join(f"{inp}\n" for inp in args))

    def __enter__(self):
        sys.stdin = self._sys_in

    def __exit__(self, exc_type, exc_value, exc_traceback):
        sys.stdin = self._original_sys_in


class MockOutput:
    def __init__(self) -> None:
        self._original_sys_out = sys.stdout
        self._io = StringIO()

    @property
    def input(self) -> str:
        return self._io.getvalue()

    def __enter__(self):
        sys.stdout = self._io
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        sys.stdout = self._original_sys_out


class MockArgs:
    @classmethod
    def from_iterable(cls, inputs: Iterable[str]) -> "MockArgs":
        return cls(*inputs)

    def __init__(self, *args: str) -> None:
        self.original = sys.argv
        self.args = args

    def __enter__(self):
        sys.argv = ["name", *self.args]

    def __exit__(self, exc_type, exc_value, exc_traceback):
        sys.argv = self.original


class MockArguments(Arguments):
    def __init__(
        self,
        target: str,
        name: str,
        debug: bool = False,
        description: str = "",
        repository: str = "",
        author: str = "",
        email: str = "",
        keywords: str = "",
        dev_packages: Dict[str, str] = {},
        py_versions: List[str] = [],
    ) -> None:
        self._debug = debug
        self._target = target
        self._name = name
        self._description = description
        self._repository = repository
        self._author = author
        self._email = email
        self._keywords = keywords
        self.dev_packages = dev_packages
        self.py_versions = py_versions

    @property
    def debug(self) -> bool:
        return self._debug

    @property
    def target(self) -> str:
        return self._target

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def repository(self) -> str:
        return self._repository

    @property
    def author(self) -> str:
        return self._author

    @property
    def email(self) -> str:
        return self._email

    @property
    def keywords(self) -> str:
        return self._keywords


py_partial_page = """<html><body><div class="row active-release-list-widget"> <h2 class="widget-title">Active Python Releases</h2> <p class="success-quote"><a href="https://devguide.python.org/#status-of-python-branches">For more information visit the Python Developer's Guide</a>.</p><div class="list-row-headings"><span class="release-version">Python version</span><span class="release-status">Maintenance status</span><span class="release-start">First released</span><span class="release-end">End of support</span><span class="release-pep">Release schedule</span></div><ol class="list-row-container menu"><li><span class="release-version">3.10</span><span class="release-status">bugfix</span><span class="release-start">2021-10-04</span><span class="release-end">2026-10</span><span class="release-pep"><a href="https://www.python.org/dev/peps/pep-0619">PEP 619</a></span></li><li><span class="release-version">3.9</span><span class="release-status">security</span><span class="release-start">2020-10-05</span><span class="release-end">2025-10</span><span class="release-pep"><a href="https://www.python.org/dev/peps/pep-0596">PEP 596</a></span></li><li><span class="release-version">3.8</span><span class="release-status">security</span><span class="release-start">2019-10-14</span><span class="release-end">2024-10</span><span class="release-pep"><a href="https://www.python.org/dev/peps/pep-0569">PEP 569</a></span></li><li><span class="release-version">3.7</span><span class="release-status">security</span><span class="release-start">2018-06-27</span><span class="release-end">2023-06-27</span><span class="release-pep"><a href="https://www.python.org/dev/peps/pep-0537">PEP 537</a></span></li><li><span class="release-version">2.7</span><span class="release-status">end-of-life</span><span class="release-start">2010-07-03</span><span class="release-end">2020-01-01</span><span class="release-pep"><a href="https://www.python.org/dev/peps/pep-0373">PEP 373</a></span></li></ol></div></body></html>"""

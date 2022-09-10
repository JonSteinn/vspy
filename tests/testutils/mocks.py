import sys
from io import StringIO
from typing import Iterable


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

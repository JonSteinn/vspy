import os
import pathlib
import shutil
import warnings
from asyncio.proactor_events import _ProactorBasePipeTransport
from functools import wraps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vspy.core.type_hints import ProactorDelType, WarnCallback


def silence_event_loop_closed() -> None:
    """Silence the `Event loop is closed` bug."""

    def _do_nothing(_self: _ProactorBasePipeTransport) -> None:
        pass

    def _silence_event_loop_closed(func: "ProactorDelType") -> "ProactorDelType":
        @wraps(func)
        def wrapper(
            self: _ProactorBasePipeTransport,
            _warn: "WarnCallback" = warnings.warn,
        ) -> None:
            try:
                return func(self, _warn)
            except RuntimeError as exc:
                if str(exc) != "Event loop is closed":
                    raise
                return _do_nothing(self)

        return wrapper

    def _wrapped() -> "ProactorDelType":
        return _silence_event_loop_closed(_ProactorBasePipeTransport.__del__)

    _ProactorBasePipeTransport.__del__ = _wrapped()  # type: ignore


def is_windows() -> bool:
    """Check if the operating system who is running this is Windows."""
    return os.name == "nt"


def is_empty_folder(path: str) -> bool:
    """Check if path points to an empty folder."""
    if not os.path.isdir(path):
        return False
    with os.scandir(path) as iterator:
        return any(iterator)


def clean_dir(path: pathlib.Path) -> None:
    """Remove all children of a given directory."""
    for name in path.iterdir():
        if name.is_file():
            name.unlink()
        elif name.is_dir():
            shutil.rmtree(name.as_posix())

import os
import pathlib
import shutil
import warnings
from asyncio.proactor_events import _ProactorBasePipeTransport
from functools import wraps
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from asyncio.proactor_events import _WarnCallbackProtocol

    from mypy_extensions import DefaultArg

    DelType = Callable[
        [_ProactorBasePipeTransport, DefaultArg("_WarnCallbackProtocol")], None
    ]


def silence_event_loop_closed() -> None:
    """Silence the `Event loop is closed` bug."""

    def _do_nothing(_self: _ProactorBasePipeTransport) -> None:
        pass

    def _silence_event_loop_closed(func: "DelType") -> "DelType":
        @wraps(func)
        def wrapper(
            self: _ProactorBasePipeTransport,
            _warn: "_WarnCallbackProtocol" = warnings.warn,
        ) -> None:
            try:
                return func(self, _warn)
            except RuntimeError as exc:
                if str(exc) != "Event loop is closed":
                    raise
                return _do_nothing(self)

        return wrapper

    def _wrapped() -> "DelType":
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


def clean_dir(path: str) -> None:
    """Remove all children of a given directory."""
    root = pathlib.Path(path)
    for name in root.iterdir():
        if name.is_file():
            name.unlink()
        elif name.is_dir():
            shutil.rmtree(name.as_posix())

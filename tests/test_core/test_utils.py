import pathlib
import platform
from asyncio.proactor_events import _ProactorBasePipeTransport
from tempfile import TemporaryDirectory

import pytest

from vspy.core.utils import (
    clean_dir,
    is_empty_folder,
    is_windows,
    silence_event_loop_closed,
)


def test_is_empty_folder_and_clean_dir():
    with TemporaryDirectory() as tmpdir:
        assert is_empty_folder(tmpdir)
        tmp = pathlib.Path(tmpdir)
        file = tmp.joinpath("stuff.txt")
        file.touch()
        assert not is_empty_folder(str(file))
        assert not is_empty_folder(tmpdir)
        tmp.joinpath("subdir").mkdir()
        tmp.joinpath("subdir", "subdir_file").touch()
        assert not is_empty_folder(tmpdir)
        clean_dir(tmp)
        assert is_empty_folder(tmp)


def test_is_windows():
    assert {"Windows": is_windows()}.get(platform.system(), not is_windows())


def test_silence_event_loop_closed():
    def mock_stuff_no_exception(*args):
        return 3

    def mock_stuff_wanted_exception(*args):
        raise RuntimeError("Some other err")

    def mock_stuff_unwanted_exception(*args):
        raise RuntimeError("Event loop is closed")

    class _X:
        def __init__(self) -> None:
            self.connection_made = None

    class _Y:
        def call_soon(*args):
            pass

    trans = _ProactorBasePipeTransport(_Y(), 2, _X())

    _ProactorBasePipeTransport.__del__ = mock_stuff_no_exception
    silence_event_loop_closed()
    assert trans.__del__() == 3

    with pytest.raises(RuntimeError):
        _ProactorBasePipeTransport.__del__ = mock_stuff_wanted_exception
        silence_event_loop_closed()
        trans.__del__()

    _ProactorBasePipeTransport.__del__ = mock_stuff_unwanted_exception
    silence_event_loop_closed()
    assert trans.__del__() is None

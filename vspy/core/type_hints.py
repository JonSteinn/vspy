from asyncio.proactor_events import _ProactorBasePipeTransport, _WarnCallbackProtocol
from typing import TYPE_CHECKING, Callable, Dict, Iterable, List, Tuple, Union

from mypy_extensions import DefaultArg

if TYPE_CHECKING:
    from vspy.core.file_io import FileWriteJob

ProactorDelType = Callable[
    [_ProactorBasePipeTransport, DefaultArg(_WarnCallbackProtocol)], None
]

TemplateArgs = Dict[str, Union[str, List[str], Dict[str, str]]]


ArgMap = Dict[str, Union[str, bool]]

WarnCallback = _WarnCallbackProtocol

ConfigData = Tuple[List[str], Iterable["FileWriteJob"]]

JobJson = Dict[str, Union[str, bool]]

from asyncio.proactor_events import _ProactorBasePipeTransport
from typing import TYPE_CHECKING, Callable, Dict, List, Union

from mypy_extensions import DefaultArg

if TYPE_CHECKING:
    from asyncio.proactor_events import _WarnCallbackProtocol

TemplateArgs = Dict[str, Union[str, List[str], Dict[str, str]]]

ProactorDelType = Callable[
    [_ProactorBasePipeTransport, DefaultArg("_WarnCallbackProtocol")], None
]

ArgMap = Dict[str, Union[str, bool]]

from asyncio.proactor_events import _ProactorBasePipeTransport
from typing import TYPE_CHECKING, Callable, Dict, List, Union

if TYPE_CHECKING:
    from asyncio.proactor_events import _WarnCallbackProtocol

    from mypy_extensions import DefaultArg

    ProactorDelType = Callable[
        [_ProactorBasePipeTransport, DefaultArg("_WarnCallbackProtocol")], None
    ]
else:
    ProactorDelType = Callable

TemplateArgs = Dict[str, Union[str, List[str], Dict[str, str]]]


ArgMap = Dict[str, Union[str, bool]]

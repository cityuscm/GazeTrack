from typing import NewType

from aioreactive.subject import AsyncMultiSubject

ClientList = NewType("ClientList", dict[str, tuple[str, str]])
NDISourceStream = NewType("NDISourceStream", AsyncMultiSubject[str])
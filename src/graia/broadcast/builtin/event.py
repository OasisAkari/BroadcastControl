from pydantic import BaseModel  # pylint: disable=no-name-in-module

from ..entities.dispatcher import BaseDispatcher
from ..entities.event import BaseEvent
from ..abstract.interfaces.dispatcher import IDispatcherInterface


class ExceptionThrowed(BaseEvent, BaseModel):
    exception: Exception
    event: BaseEvent

    class Dispatcher(BaseDispatcher):
        @staticmethod
        def catch(interface: IDispatcherInterface):
            if interface.annotation == interface.event.exception.__class__:
                return interface.event.exception
            if interface.name == "event":
                return interface.event.event

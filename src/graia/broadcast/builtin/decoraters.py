from graia.broadcast.utilles import isasyncgen, iscoroutinefunction, isgenerator
from ..entities.decorater import Decorater
from typing import Callable, ContextManager, Any, Hashable
from ..entities.signatures import Force
from ..interfaces.decorater import DecoraterInterface
import inspect
from ..exceptions import InvaildContextTarget


class Depend(Decorater):
    pre = True
    depend_callable: Callable
    cache: bool = False

    def __init__(self, callable, *, cache=False):
        self.cache = cache
        self.depend_callable = callable

    def __repr__(self) -> str:
        return "<Depend target={0}>".format(self.depend_callable)

    async def target(self, interface: DecoraterInterface):
        if self.cache:
            attempt = interface.local_storage.get(self.depend_callable)
            if attempt:
                yield Force(attempt)
                return
        result = await interface.dispatcher_interface.broadcast.Executor(
            target=self.depend_callable,
            event=interface.event,
            post_exception_event=True,
            use_inline_generator=True,
        )

        result_is_asyncgen = [inspect.isasyncgen, isasyncgen][
            isinstance(result, Hashable)
        ](result)
        result_is_generator = [inspect.isgenerator, isgenerator][
            isinstance(result, Hashable)
        ](result)
        if result_is_asyncgen or (
            result_is_generator and not iscoroutinefunction(self.depend_callable)
        ):
            if result_is_generator(result):
                for i in result:
                    yield Force(i)
            elif result_is_asyncgen(result):
                async for i in result:
                    yield Force(i)
        else:
            if self.cache:
                interface.local_storage[self.depend_callable] = result
            yield Force(result)
            return


class Middleware(Decorater):
    pre = True
    context_target: Any

    def __init__(self, context_target: ContextManager):
        self.context_target = context_target

    async def target(self, interface: DecoraterInterface):
        if all(
            [
                hasattr(self.context_target, "__aenter__"),
                hasattr(self.context_target, "__aexit__"),
            ]
        ):
            async with self.context_target as mw_value:
                yield mw_value
        elif all(
            [
                hasattr(self.context_target, "__enter__"),
                hasattr(self.context_target, "__exit__"),
            ]
        ):
            with self.context_target as mw_value:
                yield mw_value
        else:
            raise InvaildContextTarget(
                self.context_target, "is not vaild as a context target."
            )

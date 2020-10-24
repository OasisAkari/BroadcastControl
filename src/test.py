from graia.broadcast.entities.event import BaseEvent
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from graia.broadcast.protocols.executor import ExecutorProtocol
from graia.broadcast.entities.listener import Listener
from graia.broadcast import Broadcast
from graia.broadcast.entities.decorater import Decorater
from graia.broadcast.builtin.decoraters import Depend, Middleware
from graia.broadcast.interfaces.decorater import DecoraterInterface
from graia.broadcast.exceptions import PropagationCancelled
import random
from devtools import debug
import asyncio
import time
import objgraph

#print(objgraph.most_common_types(20))

class D1(BaseDispatcher):
    @staticmethod
    def catch(interface: DispatcherInterface):
        if interface.annotation == "123":
            return random.random()

class D2(BaseDispatcher):
    mixin = [D1]
    @staticmethod
    async def catch(interface: DispatcherInterface):
        if interface.annotation == "13":
            r = await interface.execute_with(interface.name, "123", interface.default)
            return r

class TestEvent(BaseEvent):
    class Dispatcher(BaseDispatcher):
        mixin = [D2]

        @staticmethod
        def catch(interface: DispatcherInterface):
            if interface.name == "u":
                yield 1
            elif interface.annotation == str:
                yield 12

event = TestEvent()
loop = asyncio.get_event_loop()
#loop.set_debug(True)
broadcast = Broadcast(loop=loop, debug_flag=True)


@broadcast.receiver(TestEvent)
def test():
    pass

async def main(start):
    print("将在 5 s 后开始测试.")
    for i in range(1, 6):
        print(i)
        await asyncio.sleep(1)
    print("测试开始.", start)
    for _ in range(100000):
        broadcast.postEvent(TestEvent())
    end = time.time()
    print(f"事件广播完毕, 总共 10w 个, 当前时间: {end}, 用时: {end - start - 5}")

start = time.time()
loop.run_until_complete(main(start))

end = time.time()
print(f"测试结束, 15s 后退出, 用时 {end - start - 5}")
loop.run_until_complete(asyncio.sleep(15))
import objgraph
#print(objgraph.most_common_types(20))
#import pdb; pdb.set_trace()
#print(broadcast.dispatcher_interface.execution_contexts[0].dispatchers)
dii = objgraph.by_type("DecoraterInterface")
print(len(dii))
#import pdb; pdb.set_trace()
print("退出....", time.time() - start)
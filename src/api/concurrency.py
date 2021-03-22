import asyncio
from queue import Queue
from typing import Optional


async def wait_for(b, interval=0.1):
    while not b():
        await asyncio.sleep(interval)


async def with_callback(send, callback):
    callback(await send())


class TaskQueue(Queue):

    def __init__(self, tasks: list, transient_queue=Queue()):
        super(TaskQueue, self).__init__()
        self.tasks = tasks
        self.task_index = 0
        self.transient_queue = transient_queue

    def get(self, **kwargs):
        if self.transient_queue.empty():
            if len(self.tasks) > 0:
                if self.task_index >= len(self.tasks):
                    self.task_index = 0
                task = self.tasks[self.task_index]
                self.task_index += 1
                return task
            else:
                raise Exception("empty")
        else:
            return self.transient_queue.get()

    def put(self, item, block: bool = ..., timeout: Optional[float] = ...) -> None:
        print("put")
        self.transient_queue.put(item, block, timeout)

    def empty(self) -> bool:
        return len(self.tasks) == 0 and self.transient_queue.empty()


async def worker_while(queue: Queue, condition, interval=0.1, on_start=None, on_stop=None):
    if on_start is not None:
        await on_start
    print("started")
    print(condition())
    while condition():
        if not queue.empty():
            print("message")
            await asyncio.wait([queue.get()(), wait_for(lambda: not condition(), interval)],
                               return_when=asyncio.FIRST_COMPLETED)
        await asyncio.sleep(interval)
    print("ending")
    if on_stop is not None:
        await on_stop


async def worker_while_closeable(queue: Queue, condition, closeable, interval=0.1):
    c = None

    async def start():
        c = await closeable()

    return await worker_while(queue, condition, interval=interval, on_start=start, on_stop=lambda: c.close())

from queue import Queue
import asyncio
import threading


_loop = None


def init():
    global _loop
    _loop = asyncio.new_event_loop()
    worker_thread = threading.Thread(target=_thread_entry_point, args=(_loop,))
    worker_thread.start()


def exit():
    global _loop
    _loop.call_soon_threadsafe(_loop.stop)


def _thread_entry_point(loop):
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


def perform(f):
    _loop.call_soon_threadsafe(f)


def perform_async(f):
    _loop.call_soon_threadsafe(lambda: _loop.create_task(f))


class Collector:
    def __init__(self, async_generator):
        self.__queue = Queue()
        self.__finished = False
        self.__collect_elements_in_background(async_generator)

    def __collect_elements_in_background(self, async_generator):
        async def collect():
            async for element in async_generator:
                self.__queue.put(element)
            self.__finished = True

        perform_async(collect())

    @property
    def items_available(self):
        return not self.__queue.empty()

    @property
    def finished(self):
        return self.__finished

    def retrieve(self):
        return self.__queue.get()
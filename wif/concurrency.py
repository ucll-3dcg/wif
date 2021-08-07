from queue import Queue
import asyncio
from threading import Thread


class Channel:
    def __init__(self):
        self.__queue = Queue()
        self.__closed = False

    def send(self, item):
        self.__queue.put(item)

    def receive(self):
        return self.__queue.get()

    @property
    def empty(self):
        return self.__queue.empty()

    def close(self):
        self.__closed = True

    @property
    def finished(self):
        return self.__closed and self.empty

    @property
    def items(self):
        while not self.finished:
            while not self.empty:
                yield self.receive()


def run_in_background(func):
    Thread(target=func).start()


def run_coroutine_in_background(coroutine):
    loop = asyncio.new_event_loop()

    def threadproc():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coroutine)

    Thread(target=threadproc).start()


def generate_in_background(generator):
    channel = Channel()

    def threadproc():
        for item in generator:
            channel.send(item)
        channel.close()

    run_in_background(threadproc)
    return channel

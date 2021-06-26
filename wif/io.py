import asyncio
import aiofile
import base64
import struct
from PIL import Image
import sys
import re
import threading
from queue import Queue


async def read_blocks(path, block_size):
    if path == 'STDIN':
        while True:
            block = sys.stdin.read(block_size)
            if not block:
                break
            yield block
    else:
        async with aiofile.async_open(path, 'r') as stream:
            while True:
                block = await stream.read(block_size)
                if not block:
                    break
                yield block


async def read_frames(blocks):
    '''
    Finds blocks delimited by <<< >>>
    '''
    regex = re.compile(r'\s*<<<(.*?)>>>\s*(.*)', re.MULTILINE | re.DOTALL)
    buffer = ''

    async for block in blocks:
        buffer += block
        match = re.match(regex, buffer)

        while match:
            block = match.group(1)
            buffer = match.group(2)

            # Decode base64
            decoded = base64.b64decode(block)

            if len(decoded) == 4:
                break
            else:
                yield decoded

            match = re.match(regex, buffer)


async def frame_to_image(frame):
    '''
    Takes frame data and turns it into an image.
    '''
    # Read two little endian 32 bit integers
    width, height = struct.unpack('<2I', frame[:8])

    # Read groups of 3 unsigned chars
    pixels = list(struct.iter_unpack("3B", frame[8:]))

    # Create image
    image = Image.new('RGB', (width, height))

    # Get pixel buffer
    image_buffer = image.load()

    # Write pixels to buffer
    for y in range(height):
        for x in range(width):
            i = y * width + x
            image_buffer[x, y] = pixels[i]

    # Return image
    return image


async def read_images(blocks):
    async for frame in read_frames(blocks):
        image = await frame_to_image(frame)
        yield image


def _thread_entry_point(loop):
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


_loop = None


def init():
    global _loop
    _loop = asyncio.new_event_loop()
    worker_thread = threading.Thread(target=_thread_entry_point, args=(_loop,))
    worker_thread.start()


def exit():
    global _loop
    _loop.call_soon_threadsafe(_loop.stop)


def read_images_in_background(blocks):
    queue = Queue()

    async def read():
        async for image in read_images(blocks):
            queue.put(image)

    _loop.call_soon_threadsafe(lambda: _loop.create_task(read()))
    return queue

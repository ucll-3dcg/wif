import asyncio
import base64
import struct
from PIL import Image
import sys
import re
import threading
from queue import Queue


def read_blocks(stream, block_size=5000000):
    '''
    Finds blocks delimited by <<< >>>
    '''
    regex = re.compile(r'\s*<<<(.*?)>>>\s*(.*)', re.MULTILINE | re.DOTALL)
    buffer = ''
    end_reached = False

    while not end_reached:
        data = stream.read(block_size)

        if not data:
            print("Unexpected EOF")
            sys.exit(-1)

        buffer += data

        match = re.match(regex, buffer)

        while match:
            block = match.group(1)
            buffer = match.group(2)

            # Decode base64
            decoded = base64.b64decode(block)

            if len(decoded) == 4:
                end_reached = True
            else:
                yield decoded

            match = re.match(regex, buffer)


def frame_to_image(frame):
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


def read_frames(stream):
    for block in read_blocks(stream):
        yield frame_to_image(block)


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


def read_frames_in_background(stream):
    queue = Queue()

    def read():
        for frame in read_frames(stream):
            queue.put(frame)

    _loop.call_soon_threadsafe(read)
    return queue

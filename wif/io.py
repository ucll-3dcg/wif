import aiofile
import base64
import struct
from PIL import Image
import sys
import re


async def read_blocks_from_stdin(block_size=500000):
    while True:
        block = sys.stdin.read(block_size)
        if not block:
            break
        yield block


async def read_blocks_from_file(path, block_size=500000):
    async with aiofile.async_open(path, 'r') as stream:
        async for block in read_blocks_from_async_stream(stream):
            yield block


async def read_blocks_from_sync_stream(stream, block_size=500000):
    while True:
        block = stream.read(block_size)
        if not block:
            break
        yield block


async def read_blocks_from_async_stream(stream, block_size=500000):
    while True:
        data = await stream.read(block_size)
        if not data:
            break
        if not isinstance(data, str):
            data = data.decode('ascii')
        yield data


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
            frame = match.group(1)
            buffer = match.group(2)

            # Decode base64
            decoded = await _base64_decode(frame)

            if len(decoded) == 4:
                break
            else:
                yield decoded

            match = re.match(regex, buffer)


async def _base64_decode(block):
    return base64.b64decode(block)


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

import base64
import struct
from PIL import Image
import sys
import re


def read_blocks(stream, block_size = 10000):
    '''
    Finds blocks delimited by <<< >>>
    '''
    buffer = ''

    while True:
        data = stream.read(block_size)
        buffer += data

        match = re.match(r'\s*<<<(.*)>>>(.*)', buffer, re.MULTILINE | re.DOTALL)

        while match:
            block = match.group(1)
            buffer = match.group(2)

            yield block

            match = re.match(r'\s*<<<(.*)>>>(.*)', buffer, re.MULTILINE | re.DOTALL)

        if not data:
            break


def block_to_image(block):
    '''
    Takes a block of data, base64-decodes it and turns it into an image.
    '''
    # Decode base64
    decoded = base64.b64decode(block)

    # Read two little endian 32 bit integers
    width, height = struct.unpack('<2I', decoded[:8])

    # Read groups of 3 unsigned chars
    pixels = list(struct.iter_unpack("3B", decoded[8:]))

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
        image = block_to_image(block)
        image.save(sys.stdout.buffer, format=args.format)
        image.close()

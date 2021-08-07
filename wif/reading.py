import base64
import struct
from PIL import Image
import re
import wif.concurrency
import subprocess


def read_blocks_from_stream(stream):
    block_size = 500000

    while True:
        block = stream.read(block_size)
        if not block:
            break
        yield block


def read_blocks_from_file(path, block_size=500000):
    block_size = 500000

    with open(path) as stream:
        while True:
            block = stream.read(block_size)
            if not block:
                break
            yield block


def read_frames(blocks):
    '''
    Finds blocks delimited by <<< >>>
    '''
    regex = re.compile(r'\s*<<<(.*?)>>>\s*(.*)', re.MULTILINE | re.DOTALL)
    buffer = ''

    for block in blocks:
        buffer += block
        match = re.match(regex, buffer)

        while match:
            frame = match.group(1)
            buffer = match.group(2)

            # Decode base64
            decoded = base64.b64decode(frame)

            if len(decoded) == 4:
                break
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


def read_images(blocks):
    for frame in read_frames(blocks):
        image = frame_to_image(frame)
        yield image


def read_lines_from_stream(stream):
    while True:
        line = stream.readline()
        if not line:
            break
        if not isinstance(line, str):
            line = line.decode('ascii')
        yield line


def open_subprocess(command, input):
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    process.stdin.write(input.encode('ascii'))
    process.stdin.close()

    return (process.stdout, process.stderr)

    # stdout_data = read_blocks_from_stream(process.stdout)
    # stderr_data = read_messages_from_stream(process.stderr)

    # stdout_channel = wif.concurrency.generate_in_background(stdout_data)
    # stderr_channel = wif.concurrency.generate_in_background(stderr_data)

    # return (stdout_channel, stderr_channel)

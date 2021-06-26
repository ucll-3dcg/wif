#!/usr/bin/env python

import asyncio
import aiofile
from wif.io import read_images, read_images_in_background, read_blocks
import wif.io
import wif.bgworker
from wif.viewer import ViewerApplication
from wif.gui import StudioApplication
from wif.version import __version__
import contextlib
import argparse
import tkinter as tk
import sys
import re
import cv2
import numpy
from itertools import islice



@contextlib.contextmanager
def open_output_stream(filename):
    if filename == 'STDOUT':
        yield sys.stdout.buffer
    else:
        with open(filename, 'wb') as file:
            yield file


def extract(args):
    def filename(index):
        return re.sub('%d', str(index).rjust(5, '0'), args.output)

    with open_input_stream(args.input) as stream:
        for index, image in enumerate(read_frames(stream)):
            with open_output_stream(filename(index)) as out:
                image.save(out, format=args.format)


async def info(args):
    blocks = read_blocks(args.input, 500000)
    sizes = []
    async for image in read_images(blocks):
        sizes.append((image.width, image.height))
        image.close()
    if len(set(sizes)) == 1:
        width = sizes[0][0]
        height = sizes[0][1]
        print(f"{len(sizes)} frames, each has size {width}x{height}")
    else:
        for index, size in enumerate(sizes):
            print(f"Frame {index} has size {size[0]}x{size[1]}")


async def viewer(args):
    root = tk.Tk()
    blocks = read_blocks(args.input, 500000)
    ViewerApplication(root, blocks).mainloop()


async def gui(args):
    StudioApplication().mainloop()


def convert(args):
    writer = None
    for index, pil_image in enumerate(read_frames(sys.stdin)):
        if not writer:
            codec = cv2.VideoWriter_fourcc(*'avc1')
            writer = cv2.VideoWriter(args.output, codec, 30, pil_image.size)
        converted = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)
        writer.write(converted)
    writer.release()


def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=lambda args: parser.print_help())
    subparsers = parser.add_subparsers()

    parser.add_argument('--version', action='version', version=__version__)

    subparser = subparsers.add_parser('frames', help='extract frames from the wif into separate files')
    subparser.add_argument('--format', type=str, default='png')
    subparser.add_argument('-i', '--input', type=str, default='STDIN')
    subparser.add_argument('-o', '--output', type=str, default='frame%d.png')
    subparser.set_defaults(func=extract)

    subparser = subparsers.add_parser('info', help='prints information about the given WIF file')
    subparser.add_argument('input', type=str, default='STDIN', nargs='?')
    subparser.set_defaults(func=info)

    subparser = subparsers.add_parser('view', help='opens viewer')
    subparser.add_argument('input', type=str, default='STDIN')
    subparser.set_defaults(func=viewer)

    subparser = subparsers.add_parser('gui', help='opens GUI')
    subparser.set_defaults(func=gui)

    subparser = subparsers.add_parser('movie', help='converts from STDIN to movie')
    subparser.add_argument('output', type=str)
    subparser.set_defaults(func=convert)

    args = parser.parse_args()

    wif.bgworker.init()
    try:
        asyncio.run(args.func(args))
    finally:
        wif.bgworker.exit()

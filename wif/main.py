#!/usr/bin/env python

import asyncio
import aiofile
from wif.io import read_images, read_blocks
import wif.io
import wif.bgworker
from wif.viewer import Viewer
from wif.gui import StudioApplication
from wif.version import __version__
import wif.raytracer
import contextlib
import argparse
import tkinter as tk
import sys
import re
import cv2
import numpy


@contextlib.contextmanager
def open_output_stream(filename):
    if filename == 'STDOUT':
        yield sys.stdout.buffer
    else:
        with open(filename, 'wb') as file:
            yield file


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
    Viewer(root, blocks).mainloop()


async def gui(args):
    StudioApplication().mainloop()


async def convert(args):
    writer = None
    blocks = wif.io.read_blocks(sys.stdin, 500000)
    images = wif.io.read_images(blocks)

    async for image in images:
        if not writer:
            codec = cv2.VideoWriter_fourcc(*'avc1')
            writer = cv2.VideoWriter(args.output, codec, 30, image.size)
        converted = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
        writer.write(converted)
    if writer:
        writer.release()


async def _render_to_wif(args):
    input = args.input
    output = args.output
    quiet = args.quiet

    async def write_to_wif(stream):
        with open(output, 'wb') as file:
            async for block in wif.io.read_blocks_from_async_stream(stream):
                file.write(block)

    async def write_to_mp4(stream):
        blocks = wif.io.read_blocks_from_async_stream(stream)
        images = wif.io.read_images(blocks)
        writer = None
        async for image in images:
            if not writer:
                codec = cv2.VideoWriter_fourcc(*'avc1')
                writer = cv2.VideoWriter(output, codec, 30, image.size)
            converted = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
            writer.write(converted)
        if writer:
            writer.release()

    async def print_messages(stream):
        while True:
            data = await stream.readline()
            if not quiet:
                print(data.decode('ascii'), end='')
            if not data:
                break

    if input == '-':
        script = sys.stdin.read()
    else:
        with open(input) as file:
            script = file.read()

    if output.endswith('.wif'):
        stdout_receiver = write_to_wif
    else:
        stdout_receiver = write_to_mp4

    await wif.raytracer.render_script(
        script,
        stdout_receiver=stdout_receiver,
        stderr_receiver=print_messages)


def _process_command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=lambda args: parser.print_help())
    subparsers = parser.add_subparsers()

    parser.add_argument('--version', action='version', version=__version__)

    subparser = subparsers.add_parser('info', help='prints information about the given WIF file')
    subparser.add_argument('input', type=str, default='STDIN', nargs='?')
    subparser.set_defaults(func=info)

    subparser = subparsers.add_parser('view', help='opens viewer')
    subparser.add_argument('input', type=str, default='STDIN')
    subparser.set_defaults(func=viewer)

    subparser = subparsers.add_parser('gui', help='opens GUI')
    subparser.set_defaults(func=gui)

    subparser = subparsers.add_parser('movie', help='converts from STDIN to mp4')
    subparser.add_argument('output', type=str)
    subparser.set_defaults(func=convert)

    subparser = subparsers.add_parser('render', help='renders script and saves as wif')
    subparser.add_argument('input', type=str)
    subparser.add_argument('output', type=str)
    subparser.add_argument('-q', '--quiet', action='store_true')
    subparser.set_defaults(func=_render_to_wif)

    subparser = subparsers.add_parser('test', help='test')
    subparser.set_defaults(func=_test)

    args = parser.parse_args()

    wif.bgworker.init()
    try:
        asyncio.run(args.func(args))
    finally:
        wif.bgworker.exit()


async def _test(args):
    filename = 'g:/temp/zoom.chai'
    with open(filename) as file:
        script = file.read()
    await wif.raytracer.render_script(script)


def main():
    _process_command_line_arguments()

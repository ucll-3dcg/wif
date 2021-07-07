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
    pass


def _process_command_line_arguments():
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

    subparser = subparsers.add_parser('movie', help='converts from STDIN to mp4')
    subparser.add_argument('output', type=str)
    subparser.set_defaults(func=convert)

    subparser = subparsers.add_parser('render', help='converts from STDIN to wif')
    subparser.add_argument('output', type=str)
    subparser.set_defaults(func=_render_to_wif)

    args = parser.parse_args()

    wif.bgworker.init()
    try:
        asyncio.run(args.func(args))
    finally:
        wif.bgworker.exit()



def main():
    _process_command_line_arguments()

    # filename = 'g:/temp/zoom.chai'
    # with open(filename) as file:
    #     script = file.read()
    # asyncio.run(wif.raytracer.render_script(script))
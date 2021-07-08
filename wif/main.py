#!/usr/bin/env python

import asyncio
from wif.io import read_blocks_from_file, read_blocks_from_stdin, read_images
import wif.io
import wif.bgworker
import wif.viewer
from wif.gui import StudioApplication
from wif.version import __version__
import wif.raytracer
import contextlib
import argparse
import tkinter as tk
import sys
import cv2
import numpy
import os


@contextlib.contextmanager
def open_output_stream(filename):
    if filename == 'STDOUT':
        yield sys.stdout.buffer
    else:
        with open(filename, 'wb') as file:
            yield file


async def info(args):
    if args.input == '-':
        blocks = read_blocks_from_stdin(500000)
    else:
        read_blocks_from_file(args.input, 500000)
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


async def gui(args):
    StudioApplication().mainloop()


def _read_script(input):
    if input == ':chai':
        return sys.stdin.read()
    else:
        with open(input) as file:
            return file.read()


def create_message_printer(output_stream):
    async def printer(input_stream):
        while True:
            data = await input_stream.readline()
            print(data.decode('ascii'), end='', file=output_stream)
            if not data:
                break
    return printer


async def _chai_to_wif(args):
    async def write_to_wif(stream):
        with open(args.output, 'w') as file:
            async for block in wif.io.read_blocks_from_async_stream(stream):
                file.write(block)

    output_stream = os.devnull if args.quiet else sys.stdout
    print_messages = create_message_printer(output_stream)
    script = _read_script(args.input)

    await wif.raytracer.render_script(
        script,
        stdout_receiver=write_to_wif,
        stderr_receiver=print_messages)


async def _create_mp4(images, output):
    writer = None
    async for image in images:
        if not writer:
            codec = cv2.VideoWriter_fourcc(*'avc1')
            writer = cv2.VideoWriter(output, codec, 30, image.size)
        converted = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
        writer.write(converted)
    if writer:
        writer.release()


async def _chai_to_mp4(args):
    async def write_to_mp4(stream):
        blocks = wif.io.read_blocks_from_async_stream(stream)
        images = wif.io.read_images(blocks)
        await _create_mp4(images, args.output)

    output_stream = os.devnull if args.quiet else sys.stdout
    print_messages = create_message_printer(output_stream)
    script = _read_script(args.input)

    await wif.raytracer.render_script(
        script,
        stdout_receiver=write_to_mp4,
        stderr_receiver=print_messages)


async def _chai_to_gui(args):
    script = _read_script(args.input)
    image_collector = wif.raytracer.render_script_to_collector(script)

    root = tk.Tk()
    wif.viewer.Viewer(root, image_collector).mainloop()


async def _wif_to_mp4(args):
    if args.input == '-':
        blocks = read_blocks_from_stdin()
    else:
        blocks = read_blocks_from_file(args.input)
    images = wif.io.read_images(blocks)
    await _create_mp4(images, args.output)


async def _wif_to_gui(args):
    root = tk.Tk()
    if args.input == '-':
        blocks = read_blocks_from_stdin()
    else:
        blocks = read_blocks_from_file(args.input)
    images = read_images(blocks)
    gui_images = wif.viewer.convert_images(images)
    collector = wif.bgworker.Collector(gui_images)
    wif.viewer.Viewer(root, collector).mainloop()


async def _convert(args):
    input = args.input
    output = args.output

    if input.endswith('chai'):
        if output.endswith('wif'):
            await _chai_to_wif(args)
        elif output.endswith('mp4'):
            await _chai_to_mp4(args)
        elif output == 'gui':
            await _chai_to_gui(args)
        else:
            print('Unsupported conversion')
    elif input.endswith('wif'):
        if output.endswith('mp4'):
            await _wif_to_mp4(args)
        elif output == 'gui':
            await _wif_to_gui(args)
        else:
            print('Unsupported conversion')
    else:
        print('Unsupported conversion')


def _process_command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=lambda args: parser.print_help())
    subparsers = parser.add_subparsers()

    parser.add_argument('--version', action='version', version=__version__)

    subparser = subparsers.add_parser('info', help='prints information about the given WIF file')
    subparser.add_argument('input', type=str, default='STDIN', nargs='?')
    subparser.set_defaults(func=info)

    subparser = subparsers.add_parser('gui', help='opens GUI')
    subparser.set_defaults(func=gui)

    subparser = subparsers.add_parser('convert', help='converts between file formats')
    subparser.add_argument('input', type=str)
    subparser.add_argument('output', type=str)
    subparser.add_argument('-q', '--quiet', action='store_true')
    subparser.set_defaults(func=_convert)

    args = parser.parse_args()

    wif.bgworker.init()
    try:
        asyncio.run(args.func(args))
    finally:
        wif.bgworker.exit()


def main():
    _process_command_line_arguments()

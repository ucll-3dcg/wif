#!/usr/bin/env python

import asyncio
import wif.reading
import wif.config
import wif.gui.imgview
from wif.gui.studio import ViewerWindow
from wif.gui.studio import StudioApplication
from wif.version import __version__
import wif.raytracer
import wif.concurrency
import contextlib
import argparse
import sys
import os
from threading import Thread


@contextlib.contextmanager
def open_output_stream(filename):
    if filename == 'STDOUT':
        yield sys.stdout.buffer
    else:
        with open(filename, 'wb') as file:
            yield file


async def info(args):
    if args.input == '-':
        blocks = wif.reading.read_blocks_from_stream()
    else:
        blocks = wif.reading.read_blocks_from_file(args.input)
    sizes = []
    for image in wif.reading.read_images(blocks):
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
    script = _read_script(args.input)
    (blocks, messages) = wif.raytracer.invoke_raytracer(script)

    def print_messages():
        for message in messages:
            print(message, end="")

    def write_blocks():
        with open(args.output, 'w') as file:
            for block in blocks:
                file.write(block)

    t1 = Thread(target=print_messages).start()
    t2 = Thread(target=write_blocks).start()

    t1.join()
    t2.join()


async def _chai_to_mp4(args):
    script = _read_script(args.input)
    target_filename = args.output
    images, _ = wif.raytracer.raytrace(script, ignore_messages=True)
    wif.encoding.create_mp4(images, target_filename)


async def _chai_to_gui(args):
    script = _read_script(args.input)
    images, messages = wif.raytracer.raytrace(script)
    ViewerWindow(None, images, messages).mainloop()


async def _wif_to_mp4(args):
    if args.input == '-':
        blocks = wif.reading.read_blocks_from_stream(sys.stdin)
    else:
        blocks = wif.reading.read_blocks_from_file(args.input)
    images = wif.reading.read_images(blocks)
    wif.encoding.create_mp4(images, args.output)


async def _wif_to_gui(args):
    if args.input == '-':
        blocks = wif.reading.read_blocks_from_stdin()
    else:
        blocks = wif.reading.read_blocks_from_file(args.input)
    images = wif.reading.read_images(blocks)
    ViewerWindow(None, images).mainloop()


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


async def _configure(args):
    if not args.setting:
        print(f'Configuration file can be found at {wif.config.get_configuration_path()}')
    elif not args.value:
        print(wif.config.configuration[args.setting])
    else:
        setting = args.setting
        value = args.value
        if setting == 'raytracer':
            if os.path.exists(value):
                absolute_path = os.path.abspath(value)
                wif.config.configuration['raytracer'] = absolute_path
        elif setting == 'block_size':
            wif.config.configuration['block_size'] = int(value)
        else:
            raise KeyError(f'Unrecognized configuration setting {setting}')
        wif.config.write()


async def _delete_configuration_file(args):
    wif.config.reset_configuration()


def _process_command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=gui)
    parser.add_argument('--version', action='version', version=__version__)

    subparsers = parser.add_subparsers()

    subparser = subparsers.add_parser('info', help='prints information about the given WIF file')
    subparser.add_argument('input', type=str, default='STDIN', nargs='?')
    subparser.set_defaults(func=info)

    subparser = subparsers.add_parser('gui', help='opens GUI')
    subparser.set_defaults(func=gui)

    subparser = subparsers.add_parser('convert', help='converts between formats')
    subparser.add_argument('input', type=str)
    subparser.add_argument('output', type=str)
    subparser.add_argument('-q', '--quiet', action='store_true')
    subparser.set_defaults(func=_convert)

    subparser = subparsers.add_parser('config', help='configure')
    subparser.add_argument('setting', type=str, nargs='?')
    subparser.add_argument('value', type=str, nargs='?')
    subparser.set_defaults(func=_configure)

    subparser = subparsers.add_parser('delconfig', help='delete configuration file')
    subparser.set_defaults(func=_delete_configuration_file)

    args = parser.parse_args()
    asyncio.run(args.func(args))


def main():
    wif.config.init()
    _process_command_line_arguments()

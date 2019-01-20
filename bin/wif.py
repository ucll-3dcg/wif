#!/usr/bin/env python

import argparse
import base64
import struct
from PIL import Image
import sys
import re



def studio_convert(args):
    buffer = ''

    while True:
        data = sys.stdin.read(10000)
        buffer += data

        match = re.match(r'\s*<<<(.*)>>>(.*)', buffer, re.MULTILINE | re.DOTALL)

        while match:
            b64frame = match.group(1)
            buffer = match.group(2)
            frame = base64.b64decode(b64frame)

            width, height = struct.unpack('<2I', frame[:8])
            pixels = list(struct.iter_unpack("3B", frame[8:]))

            image = Image.new('RGB', (width, height))
            image_buffer = image.load()

            for y in range(height):
                for x in range(width):
                    i = y * width + x
                    image_buffer[x, y] = pixels[i]

            image.save(sys.stdout.buffer, format=args.format)

            match = re.match(r'\s*<<<(.*)>>>(.*)', buffer, re.MULTILINE | re.DOTALL)


        if not data:
            break



parser = argparse.ArgumentParser(prog='wif')
subparsers = parser.add_subparsers(help='sub-command help')

studio_parser = subparsers.add_parser('studio-convert', help='converts WIF outputted by 3D Studio')
studio_parser.add_argument('--format', type=str, default='png')
studio_parser.set_defaults(func=studio_convert)

args = parser.parse_args(sys.argv[1:])
args.func(args)

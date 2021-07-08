import asyncio
from sys import stderr
import wif.viewer
from wif.bgworker import Collector, perform_async
import wif.io


RAYTRACER = r"G:\repos\ucll\3dcg\raytracer\raytracer\x64\Release\raytracer.exe"


async def render_script(script, stdout_processor, stderr_processor):
    wif.io.open_subprocess(
        RAYTRACER,
        '-s',
        '-',
        stdout_processor=stdout_processor,
        stderr_processor=stderr_processor)


def render_script_to_collector(script):
    collector = Collector()

    async def send_to_collector(stream):
        blocks = wif.io.read_blocks_from_async_stream(stream)
        images = wif.io.read_images(blocks)
        gui_images = wif.viewer.convert_images(images)
        collector.collect_in_background(gui_images)

    async def process_messages(stream):
        await stream.read()

    render = render_script(
        script,
        stdout_receiver=send_to_collector,
        stderr_receiver=process_messages)

    perform_async(render)

    return collector
